import asyncio
import os
import shutil
import time
import typing
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path, PurePath
from typing import Dict, List, TypedDict

from loguru import logger

from primitive.agent.pxe import pxe_boot
from primitive.utils.asgiref.sync import sync_to_async
from primitive.utils.cache import get_artifacts_cache, get_logs_cache, get_sources_cache
from primitive.utils.logging import fmt, log_context
from primitive.utils.psutil import kill_process_and_children
from primitive.utils.ssh import wait_for_ssh

if typing.TYPE_CHECKING:
    import primitive.client

BUFFER_SIZE = 4096


class Task(TypedDict):
    label: str
    workdir: str
    tags: Dict
    cmd: str


class JobConfig(TypedDict):
    requires: List[str]
    executes: List[Task]
    stores: List[str]


class LogLevel(Enum):
    INFO = "INFO"
    ERROR = "ERROR"
    WARNING = "WARNING"


class Runner:
    def __init__(
        self,
        primitive: "primitive.client.Primitive",
        job_run: Dict,
        target_hardware_id: str | None = None,
        max_log_size: int = 10 * 1024 * 1024,  # 10MB
    ) -> None:
        self.primitive = primitive
        self.job = job_run["job"]
        self.job_run = job_run
        self.job_settings = job_run["jobSettings"]
        self.hardware = self.primitive.hardware.get_own_hardware_details()
        self.hardware_secret = None
        self.target_hardware_id = target_hardware_id
        self.target_hardware: dict | None = None
        self.target_hardware_secret = None
        self.config = job_run["jobSettings"]["config"]
        self.initial_env = {}
        self.modified_env = {}
        self.file_logger = None

        # If max_log_size set to <= 0, disable file logging
        if max_log_size > 0:
            log_name = f"{self.job['slug']}_{self.job_run['jobRunNumber']}_{{time}}.primitive.log"

            self.file_logger = logger.add(
                Path(get_logs_cache(self.job_run["id"]) / log_name),
                rotation=max_log_size,
                format=fmt,
                backtrace=True,
            )

        hardware_secret = self.primitive.hardware.get_hardware_secret(
            hardware_id=self.hardware["id"]
        )
        self.hardware_secret = {
            k: v for k, v in hardware_secret.items() if v is not None
        }

        if self.target_hardware_id is not None:
            self.target_hardware = self.primitive.hardware.get_hardware_details(
                id=self.target_hardware_id
            )
            target_hardware_secret = self.primitive.hardware.get_hardware_secret(
                hardware_id=self.target_hardware_id
            )
            self.target_hardware_secret = {
                k: v for k, v in target_hardware_secret.items() if v is not None
            }

    @log_context(label="setup")
    def setup(self) -> None:
        # Attempt to download the job source code
        git_repo_full_name = self.job_run["gitCommit"]["repoFullName"]
        git_ref = self.job_run["gitCommit"]["sha"]
        logger.info(f"Downloading repository {git_repo_full_name} at ref {git_ref}")

        github_access_token = self.primitive.jobs.github_access_token_for_job_run(
            self.job_run["id"]
        )

        downloaded_git_repository_dir = (
            self.primitive.git.download_git_repository_at_ref(
                git_repo_full_name=git_repo_full_name,
                git_ref=git_ref,
                github_access_token=github_access_token,
                destination=get_sources_cache(),
            )
        )

        self.source_dir = downloaded_git_repository_dir.joinpath(
            self.job_settings["rootDirectory"]
        )

        # Setup initial process environment
        self.initial_env = os.environ
        self.initial_env = {
            **self.initial_env,
            **self.primitive.jobs.get_job_secrets_for_job_run(self.job_run["id"]),
        }

        # Set Primitive-related environment variables that the current client has
        if not os.environ.get("PRIMITIVE_HOST") and self.primitive.host is not None:
            self.initial_env["PRIMITIVE_HOST"] = str(self.primitive.host)
        if not os.environ.get("PRIMITIVE_TOKEN") and self.primitive.token is not None:
            self.initial_env["PRIMITIVE_TOKEN"] = str(self.primitive.token)
        if (
            not os.environ.get("PRIMITIVE_TRANSPORT")
            and self.primitive.transport is not None
        ):
            self.initial_env["PRIMITIVE_TRANSPORT"] = str(self.primitive.transport)

        self.initial_env["PRIMITIVE_SOURCE_DIR"] = str(self.source_dir)
        self.initial_env["PRIMITIVE_GIT_SHA"] = str(self.job_run["gitCommit"]["sha"])
        self.initial_env["PRIMITIVE_GIT_BRANCH"] = str(
            self.job_run["gitCommit"]["branch"]
        )
        self.initial_env["PRIMITIVE_GIT_REPO"] = str(
            self.job_run["gitCommit"]["repoFullName"]
        )

        if "VIRTUAL_ENV" in self.initial_env:
            del self.initial_env["VIRTUAL_ENV"]
        if "SHELL" in self.initial_env:
            self.initial_env["SHELL"] = "/bin/bash"

    @log_context(label="execute")
    def execute_job_run(self) -> None:
        self.modified_env = {**self.initial_env}
        task_failed = False
        cancelled = False
        timed_out = False

        for task in self.config["executes"]:
            # Everything inside this loop should be contextualized with the task label
            # this way we aren't jumping back and forth between the task label and "execute"
            with logger.contextualize(label=task["label"]):
                # the get status check here is to ensure that if cancel is called
                # while one task is running, we do not run any OTHER labeled tasks
                # THIS is required for MULTI STEP JOBS
                status = self.primitive.jobs.get_job_status(self.job_run["id"])
                status_value = status.data["jobRun"]["status"]
                conclusion_value = status.data["jobRun"]["conclusion"]

                if status_value == "completed" and conclusion_value == "cancelled":
                    cancelled = True
                    break
                if status_value == "completed" and conclusion_value == "timed_out":
                    timed_out = True
                    break

                # Everything within this block should be contextualized as user logs
                with logger.contextualize(type="user"):
                    with asyncio.Runner() as async_runner:
                        if task_failed := async_runner.run(self.run_task(task)):
                            break

        # FOR NONE MULTI STEP JOBS
        # we still have to check that the job was cancelled here as well
        with logger.contextualize(label="conclusion"):
            status = self.primitive.jobs.get_job_status(self.job_run["id"])
            status_value = status.data["jobRun"]["status"]
            conclusion_value = status.data["jobRun"]["conclusion"]
            if status_value == "completed" and conclusion_value == "cancelled":
                cancelled = True
            if status_value == "completed" and conclusion_value == "timed_out":
                timed_out = True

            if cancelled:
                logger.warning("Job cancelled by user")
                return

            if timed_out:
                logger.error("Job timed out")
                return

            conclusion = "success"
            if task_failed:
                conclusion = "failure"
            else:
                logger.success(f"Completed {self.job['slug']} job")

            self.primitive.jobs.job_run_update(
                self.job_run["id"],
                status="request_completed",
                conclusion=conclusion,
            )

    def get_number_of_files_produced(self) -> int:
        """Returns the number of files produced by the job."""
        number_of_files_produced = 0

        # Logs can be produced even if no artifact stores are created for the job run.
        job_run_logs_cache = get_logs_cache(self.job_run["id"])
        has_walk = getattr(job_run_logs_cache, "walk", None)
        if has_walk:
            log_files = [
                file
                for _, _, current_path_files in job_run_logs_cache.walk()
                for file in current_path_files
            ]
        else:
            log_files = [
                file
                for _, _, current_path_files in os.walk(job_run_logs_cache)
                for file in current_path_files
            ]

        number_of_files_produced += len(log_files)

        if "stores" not in self.config:
            return number_of_files_produced

        job_run_artifacts_cache = get_artifacts_cache(self.job_run["id"])
        has_walk = getattr(job_run_artifacts_cache, "walk", None)
        if has_walk:
            artifact_files = [
                file
                for _, _, current_path_files in job_run_artifacts_cache.walk()
                for file in current_path_files
            ]
        else:
            artifact_files = [
                file
                for _, _, current_path_files in os.walk(job_run_artifacts_cache)
                for file in current_path_files
            ]

        number_of_files_produced += len(artifact_files)

        return number_of_files_produced

    async def run_task(self, task: Task) -> bool:
        logger.info(f"Running step '{task['label']}'")
        commands = task["cmd"].strip().split("\n")

        for i, cmd in enumerate(commands):
            if cmd.strip() == "":
                continue
            if cmd.strip().startswith("#"):
                logger.debug(f"Skipping comment line: {cmd.strip()}")
                continue
            if cmd == "oobpowercycle":
                logger.info("Performing out-of-band power cycle")
                from primitive.network.redfish import RedfishClient

                # if this job was run against itself, it can call it's own BMC
                # if the job settings specified requires_controller=True, then
                # we need the bmc information for the TARGET machine for the execution machine (controller)
                # to run the Redfish commands against
                bmc_host = None
                bmc_username = None
                bmc_password = None
                if self.hardware and self.hardware_secret:
                    bmc_host = self.hardware.get("defaultBmcIpv4Address", None)
                    bmc_username = self.hardware_secret.get("bmcUsername", None)
                    bmc_password = self.hardware_secret.get("bmcPassword", "")

                if self.target_hardware and self.target_hardware_secret:
                    bmc_host = self.target_hardware.get("defaultBmcIpv4Address", None)
                    bmc_username = self.target_hardware_secret.get("bmcUsername", None)
                    bmc_password = self.target_hardware_secret.get("bmcPassword", "")

                if bmc_host is None:
                    logger.error(
                        "No BMC host found in target hardware secret for out-of-band power cycle"
                    )
                    if self.target_hardware:
                        logger.error(
                            f"Attempted to get BMC information from target hardware {self.target_hardware.get('slug')}"
                        )
                    else:
                        logger.error(
                            f"Attempted to get BMC information from own hardware {self.hardware.get('slug')}"
                        )
                    return True

                if bmc_username is None:
                    logger.error(
                        "No BMC username found in target hardware secret for out-of-band power cycle"
                    )
                    return True

                if hardware_id := self.hardware.get("id", None):
                    await self.primitive.hardware.aupdate_hardware(
                        hardware_id=hardware_id,
                        is_online=False,
                        is_rebooting=True,
                        start_rebooting_at=str(datetime.now(timezone.utc)),
                        requires_operating_system_installation=False,
                    )
                    logger.info(
                        f"{self.hardware.get('slug')} rebooting via out-of-band management."
                    )

                redfish = RedfishClient(
                    host=bmc_host, username=bmc_username, password=bmc_password
                )
                redfish.compute_system_reset(system_id="1", reset_type="ForceRestart")

                if self.target_hardware_id:
                    await self.primitive.hardware.aupdate_hardware(
                        hardware_id=self.target_hardware_id,
                        is_online=False,
                        is_rebooting=True,
                        start_rebooting_at=str(datetime.now(timezone.utc)),
                        requires_operating_system_installation=False,
                    )
                    logger.info(
                        f"Target {self.target_hardware.get('slug', None)} rebooting via out-of-band management. Controller job is over."
                    )
                continue

            if (
                cmd == "pxeboot"
                and self.target_hardware is not None
                and self.target_hardware_secret
            ):
                logger.info("Setting next boot to PXE and rebooting")

                organization_id = self.target_hardware.get("organization", {}).get("id")
                operating_system_slug = self.target_hardware.get(
                    "defaultOperatingSystem", {}
                ).get("slug")

                iso_filename = self.target_hardware.get("defaultOperatingSystem")[
                    "isoFile"
                ].get("fileName")

                # TODO dynamically obtain this later
                file_server_hostname = "192.168.10.1:9999"

                target_mac_address = self.target_hardware.get("defaultMacAddress", "")
                target_username = self.target_hardware_secret.get("username", "")
                target_password = self.target_hardware_secret.get("password", "")
                target_machine_name = self.target_hardware.get("slug", "")
                target_auth_token = None

                create_token_result = await self.primitive.auth.acreate_token(
                    key_name=f"pxe-boot-{self.target_hardware['slug']}-{int(time.time())}"
                )
                if create_token_result and create_token_result.data:
                    try:
                        target_auth_token = create_token_result.data[
                            "authenticationTokenCreate"
                        ]["key"]
                    except (KeyError, TypeError):
                        target_auth_token = None

                if not target_auth_token:
                    logger.error("Failed to create authentication token for PXE boot")
                    return True

                await sync_to_async(
                    self.primitive.operating_systems._prepare_operating_system_for_pxe
                )(
                    organization_id=organization_id,
                    operating_system_slug=operating_system_slug,
                    iso_filename=iso_filename,
                    file_server_hostname=file_server_hostname,
                    target_mac_address=target_mac_address,
                    target_username=target_username,
                    target_password=target_password,
                    target_machine_name=target_machine_name,
                    target_auth_token=target_auth_token,
                )
                pxe_boot(
                    target_hardware_secret=self.target_hardware_secret,
                    bmc_hostname=self.target_hardware.get(
                        "defaultBmcIpv4Address", None
                    ),
                    target_hostname=self.target_hardware.get(
                        "defaultIpv4Address", None
                    ),
                )

                if self.target_hardware_id:
                    await self.primitive.hardware.aupdate_hardware(
                        hardware_id=self.target_hardware_id,
                        is_online=False,
                        is_rebooting=True,
                        start_rebooting_at=str(datetime.now(timezone.utc)),
                    )
                    logger.info(
                        "Box rebooting, waiting 30 seconds before beginning SSH connection."
                    )
                    time.sleep(30)
                    wait_for_ssh(
                        hostname=self.target_hardware.get("defaultIpv4Address", None),
                        username=self.target_hardware_secret.get("username"),
                        password=self.target_hardware_secret.get("password"),
                        port=22,
                    )
                    logger.info("PXE boot successful, SSH is now available")
                    await self.primitive.hardware.aupdate_hardware(
                        hardware_id=self.target_hardware_id,
                        is_online=True,
                        is_rebooting=False,
                    )
                continue

            # if target hardware id and target hardware secret were populated, ssh onto the target to run the command
            if self.target_hardware_secret and self.target_hardware:
                username = self.target_hardware_secret.get("username")
                password = self.target_hardware_secret.get("password")
                hostname = self.target_hardware.get("defaultIpv4Address", None)

                command_args = [
                    "sshpass",
                    "-p",
                    password,
                    "ssh",
                    "-o",
                    "StrictHostKeyChecking=no",
                    "-o",
                    "UserKnownHostsFile=/dev/null",
                    "-o",
                    "IdentitiesOnly=yes",
                    f"{username}@{hostname}",
                    "--",
                    f"{cmd}",
                ]
                print(" ".join(command_args))
            else:
                command_args = ["/bin/bash", "--login", "-c", cmd]

            logger.info(
                f"Executing command {i + 1}/{len(commands)}: {cmd} at {self.source_dir / task.get('workdir', '')}"
            )

            process = await asyncio.create_subprocess_exec(
                *command_args,
                env=self.modified_env,
                cwd=str(Path(self.source_dir / task.get("workdir", ""))),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                while process.pid is None:
                    logger.debug(
                        f"Waiting for process PID to be set for command {i + 1}/{len(commands)}: {cmd}"
                    )
                    await asyncio.sleep(1)
                logger.debug(f"Process started with PID {process.pid} for command")
                await self.primitive.jobs.ajob_run_update(
                    id=self.job_run["id"],
                    parent_pid=process.pid,
                )
            except ValueError:
                logger.error(
                    f"Failed to update job run {self.job_run['id']} with process PID {process.pid}"
                )
                kill_process_and_children(pid=process.pid)
                return False

            await asyncio.gather(
                self.log_cmd(stream=process.stdout, level=LogLevel.INFO),
                self.log_cmd(stream=process.stderr, level=LogLevel.ERROR),
            )

            returncode = await process.wait()

            logger.info(
                f"Finished executing command {i + 1}/{len(commands)}: {cmd} with return code {returncode}"
            )

            if returncode > 0:
                logger.error(
                    f"Task {task['label']} failed on '{cmd}' with return code {returncode}"
                )
                return True

        logger.success(f"Completed {task['label']} task")
        return False

    async def log_cmd(
        self,
        stream: asyncio.StreamReader | None,
        level: LogLevel,
    ):
        buffer = bytearray()
        while stream and not stream.at_eof():
            chunk = await stream.read(BUFFER_SIZE)
            if not chunk:
                break
            buffer += chunk
            while b"\n" in buffer:
                line, _, buffer = buffer.partition(b"\n")
                logger.log(level.value, line.decode(errors="replace"))
        if buffer:
            logger.log(level.value, buffer.decode(errors="replace"))

    @log_context(label="cleanup")
    def cleanup(self) -> None:
        if stores := self.config.get("stores"):
            for glob in stores:
                # Glob relative to the source directory
                matches = self.source_dir.rglob(glob)

                for match in matches:
                    relative_path = PurePath(match).relative_to(self.source_dir)
                    dest = Path(get_artifacts_cache(self.job_run["id"]) / relative_path)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    Path(match).replace(dest)

        shutil.rmtree(path=self.source_dir)

        number_of_files_produced = self.get_number_of_files_produced()
        logger.info(
            f"Produced {number_of_files_produced} files for {self.job['slug']} job"
        )
        self.primitive.jobs.job_run_update(
            self.job_run["id"],
            number_of_files_produced=number_of_files_produced,
        )

        logger.remove(self.file_logger)
