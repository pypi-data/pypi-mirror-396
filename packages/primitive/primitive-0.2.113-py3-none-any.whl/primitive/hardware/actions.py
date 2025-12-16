import csv
import io
import json
import platform
import subprocess
import typing
from dataclasses import dataclass
from datetime import datetime
from shutil import which
from socket import AddressFamily
from typing import Dict, List, Optional

import click
import psutil
from aiohttp import client_exceptions
from gql import gql
from loguru import logger
from primitive.utils.asgiref.sync import sync_to_async

from primitive.__about__ import __version__
from primitive.graphql.relay import from_base64
from primitive.messaging.actions import MESSAGE_TYPES
from primitive.utils.memory_size import MemorySize
from primitive.utils.networking import find_available_port

from ..utils.auth import guard
from ..utils.config import update_config_file
from ..utils.exceptions import P_CLI_100
from .graphql.mutations import (
    hardware_certificate_create_mutation,
    hardware_checkin_mutation,
    hardware_update_mutation,
    hardware_update_system_info_mutation,
    register_child_hardware_mutation,
    register_hardware_mutation,
    unregister_hardware_mutation,
)
from .graphql.queries import (
    hardware_details,
    hardware_details_with_controller,
    hardware_list,
    hardware_secret,
    hardware_with_parent_list,
    nested_children_hardware_list,
)
from primitive.graphql.sdk import handle_mutation_response

if typing.TYPE_CHECKING:
    pass


from primitive.hardware.android import AndroidDevice, list_devices
from primitive.utils.actions import BaseAction
from primitive.utils.shell import does_executable_exist
from primitive.utils.ssh import start_port_forward


@dataclass
class CertificateCreateResult:
    certificate_id: str
    certificate_pem: str


class Hardware(BaseAction):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.status_cache = {}
        self.children = []

    def _get_darwin_system_profiler_values(self) -> Dict[str, str]:
        system_profiler_hardware_data_type = subprocess.check_output(
            ["system_profiler", "SPHardwareDataType", "-json"]
        )
        system_profiler_hardware_data = json.loads(system_profiler_hardware_data_type)
        data_type = system_profiler_hardware_data.get("SPHardwareDataType")[0]
        return {
            "apple_model_name": data_type.get("machine_model"),
            "apple_model_identifier": data_type.get("machine_name"),
            "apple_model_number": data_type.get("model_number"),
            "physical_memory": data_type.get("physical_memory"),
            "apple_serial_number": data_type.get("serial_number"),
        }

    def _get_supported_metal_device(self) -> int | None:
        """
        Checks if metal hardware is supported. If so, the index
        of the supported metal device is returned
        """
        supported_metal_device = None
        is_system_profiler_available = bool(which("system_profiler"))
        if is_system_profiler_available:
            system_profiler_display_data_type_command = (
                "system_profiler SPDisplaysDataType -json"
            )
            try:
                system_profiler_display_data_type_output = subprocess.check_output(
                    system_profiler_display_data_type_command.split(" ")
                )
            except subprocess.CalledProcessError as exception:
                message = f"Error running system_profiler: {exception}"
                logger.exception(message)
                return supported_metal_device

            try:
                system_profiler_display_data_type_json = json.loads(
                    system_profiler_display_data_type_output
                )
            except json.JSONDecodeError as exception:
                message = f"Error decoding JSON: {exception}"
                logger.exception(message)
                return supported_metal_device

            # Checks if any attached displays have metal support
            # Note, other devices here could be AMD GPUs or unconfigured Nvidia GPUs
            for index, display in enumerate(
                system_profiler_display_data_type_json["SPDisplaysDataType"]
            ):
                if "spdisplays_mtlgpufamilysupport" in display:
                    supported_metal_device = index
                    return supported_metal_device

        return supported_metal_device

    def _get_gpu_config(self) -> List:
        """
        For Nvidia based systems, nvidia-smi will be used to profile the gpu/s.
        For Metal based systems, we will gather information from SPDisplaysDataType.
        """
        gpu_config = []

        # Check nvidia gpu availability
        is_nvidia_smi_available = bool(which("nvidia-smi"))
        if is_nvidia_smi_available:
            nvidia_smi_query_gpu_csv_command = "nvidia-smi --query-gpu=gpu_name,driver_version,memory.total --format=csv"  # noqa
            try:
                nvidia_smi_query_gpu_csv_output = subprocess.check_output(
                    nvidia_smi_query_gpu_csv_command.split(" "),
                    stderr=subprocess.STDOUT,
                )
            except subprocess.CalledProcessError as exception:
                output_text = (exception.output or b"").decode("utf-8", errors="ignore")
                if "No devices were found" in output_text:
                    logger.info(
                        "nvidia-smi reports no devices were found; skipping Nvidia GPU profiling."
                    )
                    nvidia_smi_query_gpu_csv_output = None
                else:
                    message = f"Command {nvidia_smi_query_gpu_csv_command} failed with exception: {exception}"
                    logger.exception(message)
                    raise exception

            if nvidia_smi_query_gpu_csv_output:
                try:
                    nvidia_smi_query_gpu_csv_decoded = (
                        nvidia_smi_query_gpu_csv_output.decode("utf-8")
                        .replace("\r", "")
                        .replace(", ", ",")
                        .lstrip("\n")
                    )
                except UnicodeDecodeError as exception:
                    message = f"Error decoding: {exception}"
                    logger.exception(message)
                    raise exception

                nvidia_smi_query_gpu_csv_dict_reader = csv.DictReader(
                    io.StringIO(nvidia_smi_query_gpu_csv_decoded)
                )

                for gpu_info in nvidia_smi_query_gpu_csv_dict_reader:
                    # Refactor key into B
                    memory_total_in_mebibytes = gpu_info.pop("memory.total [MiB]")
                    memory_size = MemorySize(memory_total_in_mebibytes)
                    gpu_info["memory_total"] = memory_size.to_bytes()

                    gpu_config.append(gpu_info)

        if platform.system() == "Darwin":
            # Check Metal gpu availability
            supported_metal_device = self._get_supported_metal_device()
            if supported_metal_device is not None:
                # Since Apple's SoC contains Metal,
                # we query the system itself for total memory
                system_profiler_hardware_data_type_command = (
                    "system_profiler SPHardwareDataType -json"
                )

                try:
                    system_profiler_hardware_data_type_output = subprocess.check_output(
                        system_profiler_hardware_data_type_command.split(" ")
                    )
                except subprocess.CalledProcessError as exception:
                    message = f"Error running {system_profiler_hardware_data_type_command}: {exception}"  # noqa
                    logger.exception(message)
                    raise exception

                try:
                    system_profiler_hardware_data_type_json = json.loads(
                        system_profiler_hardware_data_type_output
                    )
                except json.JSONDecodeError as exception:
                    message = f"Error decoding JSON: {exception}"  # noqa
                    logger.exception(message)
                    raise exception

                metal_device_json = system_profiler_hardware_data_type_json[
                    "SPHardwareDataType"
                ][supported_metal_device]

                gpu_info = {}
                gpu_info["name"] = metal_device_json.get("chip_type")

                # Refactor key into B
                physical_memory = metal_device_json.get("physical_memory")
                memory_size = MemorySize(physical_memory)
                gpu_info["memory_total"] = memory_size.to_bytes()

                gpu_config.append(gpu_info)

        return gpu_config

    def _get_network_interfaces(self) -> Dict[str, str]:
        os_family = platform.system()
        network_interfaces = {}
        for interface, addresses in psutil.net_if_addrs().items():
            if (
                interface in ["lo", "lo0", "awdl0", "llw0"]
                or interface.startswith("utun")
                or interface.startswith("bridge")
            ):
                continue

            network_interfaces[interface] = {}
            for address in addresses:
                # get linux's mac address
                if os_family == "Linux" and address.family == AddressFamily.AF_PACKET:
                    mac_address = address.address
                    if mac_address and mac_address != "00:00:00:00:00:00":
                        network_interfaces[interface]["mac_address"] = mac_address
                if os_family == "Darwin" and address.family == AddressFamily.AF_LINK:
                    mac_address = address.address
                    if mac_address and mac_address != "00:00:00:00:00:00":
                        network_interfaces[interface]["mac_address"] = mac_address
                elif address.family == AddressFamily.AF_INET:
                    ip_address = address.address
                    if ip_address and ip_address != "127.0.0.1":
                        network_interfaces[interface]["ip_address"] = ip_address
        return network_interfaces

    def _get_windows_computer_service_product_values(self) -> Dict[str, str]:
        windows_computer_service_product_csv_command = (
            "cmd.exe /C wmic csproduct get Name, Vendor, Version, UUID /format:csv"
        )
        windows_computer_service_product_csv_output = subprocess.check_output(
            windows_computer_service_product_csv_command.split(" "),
            stderr=subprocess.DEVNULL,
        )
        windows_computer_service_product_csv_decoded = (
            windows_computer_service_product_csv_output.decode("utf-8")
            .replace("\r", "")
            .lstrip("\n")
        )
        windows_computer_service_product_dict = csv.DictReader(
            io.StringIO(windows_computer_service_product_csv_decoded)
        )
        csp_info = list(windows_computer_service_product_dict)[0]
        return {
            "windows_model_name": csp_info.get("Name", ""),
            "windows_model_vendor": csp_info.get("Vendor", ""),
            "windows_model_version": csp_info.get("Version", ""),
            "windows_model_uuid": csp_info.get("UUID", ""),
        }

    def _get_windows_cpu_values(self) -> Dict[str, str]:
        windows_cpu_csv_command = (
            "cmd.exe /C wmic cpu get Name, MaxClockSpeed /format:csv"  # noqa
        )
        windows_cpu_csv_output = subprocess.check_output(
            windows_cpu_csv_command.split(" "),
            stderr=subprocess.DEVNULL,
        )
        windows_cpu_csv_decoded = (
            windows_cpu_csv_output.decode("utf-8").replace("\r", "").lstrip("\n")
        )
        windows_cpu_dict = csv.DictReader(io.StringIO(windows_cpu_csv_decoded))
        cpu_info = list(windows_cpu_dict)[0]
        return {
            "cpu_brand": cpu_info.get("Name", "").strip(),
            "cpu_max_clock_speed": cpu_info.get("MaxClockSpeed", ""),
        }

    def _get_ubuntu_values(self) -> Dict[str, str]:
        get_machine_id_command = "cat /etc/machine-id"
        machine_id = subprocess.check_output(
            get_machine_id_command.split(" "),
            stderr=subprocess.DEVNULL,
        ).decode("utf-8")
        if machine_id:
            return {"linux_machine_id": machine_id}
        return {}

    def _get_homebrew_installed(self):
        try:
            raw = json.loads(
                subprocess.check_output(["brew", "info", "--json=v2", "--installed"])
            )

            if isinstance(raw, Dict):
                raw_formulae = raw.get("formulae", [])
                raw_casks = raw.get("casks", [])

                formulae = []
                casks = []

                if isinstance(raw_formulae, List):
                    for raw_formula in raw_formulae:
                        try:
                            formulae.append(
                                {
                                    "full_name": raw_formula["full_name"],
                                    "tap": raw_formula["tap"],
                                    "version": raw_formula["versions"]["stable"],
                                }
                            )
                        except Exception:
                            pass

                if isinstance(raw_casks, List):
                    for raw_cask in raw_casks:
                        try:
                            casks.append(
                                {
                                    "full_token": raw_cask["full_token"],
                                    "name": raw_cask["name"][0],
                                    "version": raw_cask["installed"],
                                }
                            )
                        except Exception:
                            pass

                return {
                    "formulae": formulae,
                    "casks": casks,
                }
        except Exception:
            pass

    def _get_darwin_md_application(self, application_path: str):
        lines = (
            subprocess.check_output(
                [
                    "mdls",
                    "-name",
                    "kMDItemDisplayName",
                    "-name",
                    "kMDItemVersion",
                    "-name",
                    "kMDItemCFBundleIdentifier",
                    application_path,
                ]
            )
            .strip()
            .decode("utf-8")
            .split("\n")
        )

        item = {
            "path": application_path,
        }

        for line in lines:
            raw_key, raw_value = line.split(" = ")

            key = raw_key.strip()

            if raw_value == "(null)":
                item[key] = None
            elif raw_value.startswith('"') and raw_value.endswith('"'):
                item[key] = raw_value[1:-1]

        return item

    def _get_darwin_md_applications(self):
        import concurrent.futures

        try:
            application_paths = (
                subprocess.check_output(["mdfind", "kMDItemKind == 'Application'"])
                .strip()
                .decode("utf-8")
                .split("\n")
            )

            with concurrent.futures.ThreadPoolExecutor() as executor:
                return list(
                    executor.map(self._get_darwin_md_application, application_paths)
                )

        except Exception:
            pass

    def _get_fedora_installed_packages(self):
        try:
            lines = (
                subprocess.check_output(
                    [
                        "dnf",
                        "repoquery",
                        "--installed",
                        "--qf",
                        "%{name} , %{version}\n",
                    ]
                )
                .decode("utf-8")
                .strip()
                .split("\n")
            )

            items = []

            for line in lines:
                try:
                    name, version = line.split(" , ")

                    items.append(
                        {
                            "name": name,
                            "version": version,
                        }
                    )
                except Exception:
                    pass
            return items
        except Exception:
            pass

    def _get_ubuntu_installed_packages(self):
        try:
            lines = (
                subprocess.check_output(
                    ["apt", "list", "--installed"],
                    stderr=subprocess.DEVNULL,
                )
                .decode("utf-8")
                .strip()
                .split("\n")
            )

            lines.pop()

            items = []

            for line in lines:
                try:
                    columns = line.split()

                    if len(columns) < 2:
                        continue

                    name, version, *_ = columns
                    items.append(
                        {
                            "name": name.split("/")[0],
                            "version": version,
                        }
                    )
                except Exception:
                    pass

            return items

        except Exception:
            pass

    def get_system_info(self, with_installed_applications: bool = False):
        os_family = platform.system()
        system_info = {}
        if os_family == "Darwin":
            system_info = {**system_info, **self._get_darwin_system_profiler_values()}
            system_info["cpu_brand"] = (
                subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"])
                .strip()
                .decode("utf-8")
            )
            system_info["apple_mac_os_version"] = platform.mac_ver()[0]
            system_info["homebrew_installed"] = self._get_homebrew_installed()

            if with_installed_applications:
                system_info["darwin_md_applications"] = (
                    self._get_darwin_md_applications()
                )

        elif os_family == "Linux":
            # Support for Linux-based VMs in Windows
            if "WSL2" in platform.platform():
                system_info = {
                    **system_info,
                    **self._get_windows_computer_service_product_values(),
                    **self._get_windows_cpu_values(),
                }
            else:
                system_info = {**system_info, **self._get_ubuntu_values()}
                system_info["linux_release"] = platform.freedesktop_os_release()

                match system_info["linux_release"]["ID"]:
                    case "ubuntu":
                        system_info["ubuntu_installed_packages"] = (
                            self._get_ubuntu_installed_packages()
                        )
                    case "fedora":
                        system_info["fedora_installed_packages"] = (
                            self._get_fedora_installed_packages()
                        )

        elif os_family == "Windows":
            system_info = {
                **system_info,
                **self._get_windows_computer_service_product_values(),
                **self._get_windows_cpu_values(),
            }

        system_info["name"] = platform.node()
        system_info["os_family"] = os_family
        system_info["os_release"] = platform.release()
        system_info["os_version"] = platform.version()
        system_info["platform"] = platform.platform()
        system_info["processor"] = platform.processor()
        system_info["machine"] = platform.machine()
        system_info["architecture"] = platform.architecture()[0]
        system_info["cpu_cores"] = str(platform.os.cpu_count())  # type: ignore exits
        system_info["gpu_config"] = self._get_gpu_config()
        system_info["network_interfaces"] = self._get_network_interfaces()

        return system_info

    @guard
    def certificate_create(
        self, hardware_id: str, csr_pem: str
    ) -> CertificateCreateResult:
        mutation = gql(hardware_certificate_create_mutation)
        variables = {
            "input": {
                "hardwareId": hardware_id,
                "csrPem": csr_pem,
            }
        }

        if not self.primitive.session:
            raise Exception("No active session available for certificate creation")

        result = self.primitive.session.execute(
            mutation,
            variable_values=variables,
            get_execution_result=True,
        )

        if result.errors:
            message = " ".join([error.message for error in result.errors])
            raise Exception(message)

        if not result.data:
            raise Exception(
                "No data received from hardware certificate creation request"
            )

        hardware_certificate_create = result.data["hardwareCertificateCreate"]

        if hardware_certificate_create["__typename"] == "OperationInfo":
            messages = hardware_certificate_create["messages"]
            message = " ".join([error["message"] for error in messages])
            raise Exception(message)

        return CertificateCreateResult(
            certificate_id=hardware_certificate_create["id"],
            certificate_pem=hardware_certificate_create["certificatePem"],
        )

    @guard
    def register(self, organization_id: Optional[str] = None):
        system_info = self.get_system_info()
        mutation = gql(register_hardware_mutation)
        input = {"systemInfo": system_info}
        if organization_id:
            input["organizationId"] = organization_id
        variables = {"input": input}
        result = self.primitive.session.execute(
            mutation, variable_values=variables, get_execution_result=True
        )
        if messages := result.data.get("registerHardware").get("messages"):
            for message in messages:
                if message.get("kind") == "ERROR":
                    logger.error(message.get("message"))
                else:
                    logger.debug(message.get("message"))
            return False

        fingerprint = result.data.get("registerHardware").get("fingerprint")

        self.primitive.host_config["fingerprint"] = fingerprint
        self.primitive.full_config[self.primitive.host] = self.primitive.host_config
        update_config_file(new_config=self.primitive.full_config)

        # then check in that the hardware, validate that it is saved correctly
        # and headers are set correctly
        self.primitive.get_host_config()
        self.check_in_http(is_healthy=True)
        for child in self._list_local_children():
            self.register_child(child=child)
        return result

    @guard
    def unregister(self, organization_id: Optional[str] = None):
        mutation = gql(unregister_hardware_mutation)
        input = {
            "fingerprint": self.primitive.host_config.get("fingerprint"),
        }
        variables = {"input": input}
        result = self.primitive.session.execute(
            mutation, variable_values=variables, get_execution_result=True
        )

        if messages := result.data.get("unregisterHardware").get("messages"):
            for message in messages:
                if message.get("kind") == "ERROR":
                    logger.error(message.get("message"))
                else:
                    logger.debug(message.get("message"))
            return False

        return result

    @guard
    def update_hardware_system_info(self):
        """
        Updates hardware system information and returns the GraphQL response.

        Returns:
            dict: GraphQL response
        Raises:
            Exception: If no fingerprint is found or an error occurs
        """

        fingerprint = self.primitive.host_config.get("fingerprint", None)
        if not fingerprint:
            message = (
                "No fingerprint found. Please register: primitive hardware register"
            )
            raise Exception(message)

        system_info = self.get_system_info()
        new_state = {
            "systemInfo": system_info,
        }

        mutation = gql(hardware_update_system_info_mutation)

        input = new_state
        variables = {"input": input}
        try:
            result = self.primitive.session.execute(
                mutation, variable_values=variables, get_execution_result=True
            )
        except client_exceptions.ClientConnectorError as exception:
            message = "Failed to update hardware system info! "
            logger.exception(message)
            raise exception

        message = "Updated hardware system info successfully! "
        logger.info(message)

        return result

    def check_in(
        self,
        is_healthy: bool = True,
        is_quarantined: bool = False,
        is_available: bool = False,
        is_online: bool = True,
        stopping_agent: Optional[bool] = False,
        http: bool = False,
    ):
        if not http and self.primitive.messaging.ready:
            message = {
                "is_healthy": is_healthy,
                "is_quarantined": is_quarantined,
                "is_available": is_available,
                "is_online": is_online,
            }
            self.primitive.messaging.send_message(
                message_type=MESSAGE_TYPES.CHECK_IN, message=message
            )
        else:
            self.check_in_http(
                is_healthy=is_healthy,
                is_quarantined=is_quarantined,
                is_available=is_available,
                is_online=is_online,
                stopping_agent=stopping_agent,
            )

    @guard
    def check_in_http(
        self,
        is_healthy: bool = True,
        is_quarantined: bool = False,
        is_available: bool = False,
        is_online: bool = True,
        fingerprint: Optional[str] = None,
        stopping_agent: Optional[bool] = False,
    ):
        # if no fingerprint supplied from argument try from the host_config
        if not fingerprint:
            fingerprint = self.primitive.host_config.get("fingerprint", None)

        if not fingerprint:
            message = (
                "No fingerprint found. Please register: primitive hardware register"
            )
            raise Exception(message)

        new_state = {
            "isHealthy": is_healthy,
            "isQuarantined": is_quarantined,
            "isAvailable": is_available,
            "isOnline": is_online,
        }

        mutation = gql(hardware_checkin_mutation)
        input = {**new_state}
        if fingerprint:
            input["fingerprint"] = fingerprint
        variables = {"input": input}
        try:
            result = self.primitive.session.execute(
                mutation, variable_values=variables, get_execution_result=True
            )
            checkin_success = result.data.get("checkIn").get("lastCheckIn")
            if messages := result.data.get("checkIn").get("messages"):
                for message in messages:
                    if message.get("kind") == "ERROR":
                        logger.error(message.get("message"))
                    else:
                        logger.debug(message.get("message"))

            if checkin_success:
                if fingerprint in self.status_cache:
                    previous_status = self.status_cache[fingerprint]
                else:
                    logger.error("No previous status found.")
                    previous_status = {
                        "isHealthy": False,
                        "isQuarantined": False,
                        "isAvailable": False,
                        "isOnline": False,
                    }
                self.status_cache[fingerprint] = new_state.copy()

                message = f"Checked in successfully for {fingerprint}: "
                is_new_status = False
                for key, value in new_state.items():
                    if value != previous_status.get(key, None):
                        is_new_status = True
                        if value is True:
                            message = (
                                message
                                + click.style(f"{key}: ")
                                + click.style("💤")
                                + click.style(" ==> ✅ ", fg="green")
                            )
                        else:
                            message = (
                                message
                                + click.style(f"{key}: ")
                                + click.style("✅")
                                + click.style(" ==> 💤 ", fg="yellow")
                            )
                if is_new_status is False:
                    message += "No changes."
                logger.info(message)
            else:
                message = "Failed to check in!"
                raise Exception(message)
            return result
        except client_exceptions.ClientConnectorError as exception:
            if not stopping_agent:
                message = "Failed to check in! "
                logger.error(message)
                raise exception
            else:
                raise P_CLI_100

    @guard
    def get_hardware_list(
        self,
        fingerprint: Optional[str] = None,
        id: Optional[str] = None,
        slug: Optional[str] = None,
        nested_children: Optional[bool] = False,
        parent: Optional[bool] = False,
    ):
        query = gql(hardware_list)
        if parent:
            query = gql(hardware_with_parent_list)
        if nested_children:
            query = gql(nested_children_hardware_list)

        filters = {
            "isRegistered": {"exact": True},
        }
        if fingerprint is not None:
            filters["fingerprint"] = {"exact": fingerprint}
        if slug is not None:
            filters["slug"] = {"exact": slug}
        if id is not None:
            filters["id"] = id
        # if nested_children is True:
        #     filters["hasParent"] = {"exact": False}

        variables = {
            "filters": filters,
        }
        result = self.primitive.session.execute(
            query, variable_values=variables, get_execution_result=True
        )

        return result

    @guard
    async def aget_hardware_list(
        self,
        fingerprint: Optional[str] = None,
        id: Optional[str] = None,
        slug: Optional[str] = None,
        nested_children: Optional[bool] = False,
        parent: Optional[bool] = False,
    ):
        query = gql(hardware_list)
        if parent:
            query = gql(hardware_with_parent_list)
        if nested_children:
            query = gql(nested_children_hardware_list)

        filters = {
            "isRegistered": {"exact": True},
        }
        if fingerprint is not None:
            filters["fingerprint"] = {"exact": fingerprint}
        if slug is not None:
            filters["slug"] = {"exact": slug}
        if id is not None:
            filters["id"] = {"exact": id}
        # if nested_children is True:
        #     filters["hasParent"] = {"exact": False}

        variables = {
            "filters": filters,
        }
        result = await self.primitive.session.execute_async(
            query, variable_values=variables, get_execution_result=True
        )

        return result

    @guard
    def get_hardware_details(
        self,
        fingerprint: Optional[str] = None,
        id: Optional[str] = None,
        slug: Optional[str] = None,
        with_controller: bool = False,
    ):
        query = gql(hardware_details)
        if with_controller:
            query = gql(hardware_details_with_controller)

        filters = {}
        if fingerprint is not None:
            filters["fingerprint"] = {"exact": fingerprint}
        if slug is not None:
            filters["slug"] = {"exact": slug}
        if id is not None:
            filters["id"] = id

        variables = {
            "first": 1,
            "filters": filters,
        }
        result = self.primitive.session.execute(
            query, variable_values=variables, get_execution_result=True
        )
        if edges := result.data["hardwareList"]["edges"]:
            return edges[0]["node"]
        else:
            raise Exception(f"No hardware found with {filters}")

    def get_own_hardware_details(self):
        hardware_list_result = self.get_hardware_list(
            fingerprint=self.primitive.host_config.get("fingerprint"),
            nested_children=True,
        )
        if len(hardware_list_result.data.get("hardwareList").get("edges", [])) == 0:
            raise Exception(
                "No hardware found with fingerprint: "
                f"{self.primitive.host_config.get('fingerprint')}. "
                "Please register: primitive hardware register"
            )

        hardware = (
            hardware_list_result.data.get("hardwareList").get("edges")[0].get("node")
        )
        return hardware

    def get_parent_hardware_details(self):
        hardware_list_result = self.get_hardware_list(
            fingerprint=self.primitive.host_config.get("fingerprint"), parent=True
        )
        if len(hardware_list_result.data.get("hardwareList").get("edges", [])) == 0:
            logger.warning(
                "No hardware found with fingerprint: "
                f"{self.primitive.host_config.get('fingerprint')}. "
                "Please register: primitive hardware register"
            )

        hardware = (
            hardware_list_result.data.get("hardwareList").get("edges")[0].get("node")
        )
        parent = hardware.get("parent", None)
        if not parent:
            logger.warning("No parent network device found.")
        return parent

    async def aget_parent_hardware_details(self):
        hardware_list_result = await self.aget_hardware_list(
            fingerprint=self.primitive.host_config.get("fingerprint"), parent=True
        )
        if len(hardware_list_result.data.get("hardwareList").get("edges", [])) == 0:
            logger.warning(
                "No hardware found with fingerprint: "
                f"{self.primitive.host_config.get('fingerprint')}. "
                "Please register: primitive hardware register"
            )

        hardware = (
            hardware_list_result.data.get("hardwareList").get("edges")[0].get("node")
        )
        parent = hardware.get("parent", None)
        if not parent:
            logger.warning("No parent network device found.")
        return parent

    def get_hardware_from_slug_or_id(
        self, hardware_identifier: str, with_controller: bool = False
    ):
        is_id = False
        is_slug = False
        id = None
        # first check if the hardware_identifier is a slug or ID
        try:
            type_name, id = from_base64(hardware_identifier)

            is_id = True
            if type_name == "Hardware":
                is_hardware_type = True
            else:
                raise Exception(
                    f"ID was not for Hardware, you supplied an ID for a {type_name}"
                )

        except ValueError:
            is_slug = True

        hardware = None

        if is_id and is_hardware_type:
            hardware = self.get_hardware_details(id=id, with_controller=with_controller)
        elif is_slug:
            hardware = self.get_hardware_details(
                slug=hardware_identifier, with_controller=with_controller
            )

        return hardware

    async def aget_hardware_from_slug_or_id(
        self, hardware_identifier: str, with_controller: bool = False
    ):
        return await sync_to_async(self.get_hardware_from_slug_or_id)(
            hardware_identifier, with_controller
        )

    @guard
    def get_hardware_secret(self, hardware_id: str):
        query = gql(hardware_secret)
        variables = {"hardwareId": hardware_id}
        result = self.primitive.session.execute(
            query, variable_values=variables, get_execution_result=True
        )

        secret = result.data.get("hardwareSecret", {})
        return secret

    @guard
    async def aget_hardware_secret(self, hardware_id: str):
        query = gql(hardware_secret)
        variables = {"hardwareId": hardware_id}
        result = await self.primitive.session.execute_async(
            query, variable_values=variables, get_execution_result=True
        )

        secret = result.data.get("hardwareSecret", {})
        return secret

    @guard
    def get_and_set_switch_info(self):
        parent = self.get_parent_hardware_details()
        if not parent:
            return

        parent_secret = self.get_hardware_secret(hardware_id=parent.get("id"))
        self.primitive.network.switch_connection_info = {
            "vendor": parent.get("manufacturer", {}).get("slug"),
            "hostname": parent.get("defaultIpv4Address", None),
            "username": parent_secret.get("username"),
            "password": parent_secret.get("password"),
        }

    @guard
    async def aget_and_set_switch_info(self):
        parent = await self.aget_parent_hardware_details()
        if not parent:
            return

        parent_secret = await self.aget_hardware_secret(hardware_id=parent.get("id"))
        self.primitive.network.switch_connection_info = {
            "vendor": parent.get("manufacturer", {}).get("slug"),
            "hostname": parent.get("defaultIpv4Address", None),
            "username": parent_secret.get("username"),
            "password": parent_secret.get("password"),
        }

    @guard
    def register_child(self, child: AndroidDevice):
        system_info = child.system_info
        mutation = gql(register_child_hardware_mutation)
        input = {"childSystemInfo": system_info}
        variables = {"input": input}
        result = self.primitive.session.execute(
            mutation, variable_values=variables, get_execution_result=True
        )

        if messages := result.data.get("registerChildHardware").get("messages"):
            for message in messages:
                if message.get("kind") == "ERROR":
                    logger.error(message.get("message"))
                else:
                    logger.debug(message.get("message"))
            return False
        return result

    def _list_local_children(self) -> List[AndroidDevice]:
        if does_executable_exist("adb"):
            self.children: List[AndroidDevice] = list_devices()
        return self.children

    @guard
    def _remove_child(self):
        pass

    @guard
    def _sync_children(self, hardware: Optional[Dict[str, str]] = None):
        # get the existing children if any from the hardware details
        # get the latest children from the node
        # compare the two and update the node with the latest children
        # remove any children from remote that are not in the latest children
        if not hardware:
            hardware = self.primitive.hardware.get_own_hardware_details()
        if not hardware:
            logger.error("No hardware found.")
            return

        remote_children = hardware.get("children", [])
        local_children = self.primitive.hardware._list_local_children()

        new_child_registered = False
        # need to register new children that were not previously registered
        if len(remote_children) < len(local_children):
            logger.info("New children found.")
            for local_child in local_children:
                found = False
                for remote_child in remote_children:
                    if remote_child["slug"] == local_child.slug:
                        found = True
                        break
                if not found:
                    try:
                        logger.info(f"Registering new child: {local_child.slug}")
                        self.primitive.hardware.register_child(child=local_child)
                        new_child_registered = True
                    except Exception as exception:
                        logger.exception(f"Error registering new children: {exception}")

        # if a new child was registered, get the fresh state of the world
        if new_child_registered:
            hardware = self.primitive.hardware.get_own_hardware_details()
            remote_children = hardware.get("children", [])

        try:
            # need to check in children that had been previously registered
            # TODO: this is where, once you've got the local children you run a
            # predefined health check. online != healthy
            for remote_child in remote_children:
                # if the remote_child is not in the local_children, then it is offline
                found = False
                for local_child in local_children:
                    if remote_child["slug"] == local_child.slug:
                        is_available = True
                        if remote_child["activeReservation"] is not None:
                            if (
                                remote_child["activeReservation"]["id"]
                                and remote_child["isAvailable"]
                            ):
                                is_available = False

                        self.primitive.hardware.check_in_http(
                            is_available=is_available,
                            is_healthy=True,
                            is_online=True,
                            fingerprint=remote_child["fingerprint"],
                        )
                        found = True
                        break
                if not found:
                    logger.info(
                        f"Remote child {remote_child['slug']}, not found in local children. Setting offline."
                    )
                    self.primitive.hardware.check_in_http(
                        is_available=False,
                        is_healthy=False,
                        is_online=False,
                        fingerprint=remote_child["fingerprint"],
                    )

        except Exception as exception:
            logger.exception(f"Error checking in children: {exception}")

    def push_metrics(self):
        if self.primitive.messaging.ready:
            self.primitive.messaging.send_message(
                message_type=MESSAGE_TYPES.METRICS,
                message=self.get_metrics(),
            )

    def get_metrics(self):
        cpu_percent = psutil.cpu_percent(interval=1, percpu=False)
        virtual_memory = psutil.virtual_memory()
        disk_usage = psutil.disk_usage("/")

        metrics = {
            "cpu_percent": cpu_percent,
            "memory_percent": virtual_memory.percent,
            "memory_total": virtual_memory.total,
            "memory_available": virtual_memory.available,
            "memory_used": virtual_memory.used,
            "memory_free": virtual_memory.free,
            "disk_percent": disk_usage.percent,
            "disk_total": disk_usage.total,
            "disk_used": disk_usage.used,
            "disk_free": disk_usage.free,
        }
        return metrics

    @guard
    def update_hardware(
        self,
        hardware_id: str,
        is_online: Optional[bool] = None,
        is_rebooting: Optional[bool] = None,
        start_rebooting_at: Optional[datetime] = None,
        requires_operating_system_installation: Optional[bool] = None,
    ):
        new_state: dict = {
            "id": hardware_id,
        }
        if is_online is not None:
            new_state["isOnline"] = is_online
        if is_rebooting is not None:
            new_state["isRebooting"] = is_rebooting
        if start_rebooting_at is not None:
            new_state["startRebootingAt"] = start_rebooting_at
        if requires_operating_system_installation is not None:
            new_state["requiresOperatingSystemInstallation"] = (
                requires_operating_system_installation
            )

        mutation = gql(hardware_update_mutation)

        input = new_state
        variables = {"input": input}

        try:
            result = self.primitive.session.execute(
                document=mutation, variable_values=variables, get_execution_result=True
            )
            handle_mutation_response(
                mutation=mutation,
                result=result,
            )
            return result
        except client_exceptions.ClientConnectorError as exception:
            message = "Failed to update hardware! "
            logger.exception(message)
            raise exception

    @guard
    async def aupdate_hardware(
        self,
        hardware_id: str,
        is_online: Optional[bool] = None,
        is_rebooting: Optional[bool] = None,
        start_rebooting_at: Optional[str] = None,
        requires_operating_system_installation: Optional[bool] = None,
    ):
        new_state: dict = {
            "id": hardware_id,
        }
        if is_online is not None:
            new_state["isOnline"] = is_online
        if is_rebooting is not None:
            new_state["isRebooting"] = is_rebooting
        if start_rebooting_at is not None:
            new_state["startRebootingAt"] = start_rebooting_at
        if requires_operating_system_installation is not None:
            new_state["requiresOperatingSystemInstallation"] = (
                requires_operating_system_installation
            )

        mutation = gql(hardware_update_mutation)

        input = new_state
        variables = {"input": input}

        try:
            result = await self.primitive.session.execute_async(
                document=mutation, variable_values=variables, get_execution_result=True
            )
            handle_mutation_response(
                mutation=mutation,
                result=result,
            )
            return result
        except client_exceptions.ClientConnectorError as exception:
            message = "Failed to update hardware! "
            logger.exception(message)
            raise exception

    def push_own_system_info(self):
        if self.primitive.messaging.ready:
            message = {"system_info": self.primitive.hardware.get_system_info()}
            self.primitive.messaging.send_message(
                message_type=MESSAGE_TYPES.SYSTEM_INFO,
                message=message,
            )

    def start_bmc_tunnel(
        self,
        hardware_identifier: str,
        local_hostname: str = "127.0.0.1",
        local_port=8080,
        hostname_override: Optional[str] = None,
    ) -> None:
        hardware = self.get_hardware_from_slug_or_id(
            hardware_identifier=hardware_identifier, with_controller=True
        )
        if not hardware:
            raise Exception(f"No hardware found for {hardware_identifier}")

        active_reservation = hardware.get("activeReservation", None)
        if not active_reservation:
            raise Exception("No active reservation found for hardware.")

        target_hardware_secret = self.primitive.hardware.get_hardware_secret(
            hardware_id=hardware.get("id")
        )
        target_hardware_secret = {
            k: v for k, v in target_hardware_secret.items() if v is not None
        }

        hostname = hardware.get("defaultIpv4Address", None)
        username = target_hardware_secret.get("username")
        password = target_hardware_secret.get("password")
        port = target_hardware_secret.get("port", 22)
        keyfile = target_hardware_secret.get("keyfile", None)

        controller = hardware.get("controller", None)
        if controller:
            # if there is a controller, use that as the actual connection info
            controller_hardware_secret = self.primitive.hardware.get_hardware_secret(
                hardware_id=hardware.get("controller", {}).get("id")
            )
            controller_hardware_secret = {
                k: v for k, v in controller_hardware_secret.items() if v is not None
            }
            hostname = controller.get("defaultIpv4Address", hostname)
            username = controller_hardware_secret.get("username", username)
            password = controller_hardware_secret.get("password", password)
            port = controller_hardware_secret.get("port", port)
            keyfile = controller_hardware_secret.get("keyfile", keyfile)

        remote_hostname = hostname
        remote_port = 443
        # after remote_hostname is set, apply any hostname override for this machine to connect to, before making the tunnel
        if hostname_override:
            hostname = hostname_override

        if bmc_hostname := hardware.get("defaultBmcIpv4Address", None):
            if not bmc_hostname:
                raise Exception("No BMC hostname found for hardware.")
            remote_hostname = bmc_hostname

        local_port = find_available_port(start_port=local_port)

        connection_details_url = f"{self.primitive.host_config.get('transport', 'https')}://{self.primitive.host.replace('api', 'app')}/{hardware.get('organization').get('slug')}/hardware/{hardware.get('slug')}?connectionType=BMC#connectionDetails"
        if "localhost:8000" in connection_details_url:
            connection_details_url = connection_details_url.replace(
                "localhost:8000", "localhost:3000"
            )
        target_tty_url = f"https://{local_hostname}:{local_port}/cgi/url_redirect.cgi?url_name=man_ikvm_html5_bootstrap"

        logger.info(f"Primitive CLI {__version__}")
        logger.info(f"  ○ BMC Connection Details:    {connection_details_url}")
        logger.info(
            f"  ○ BMC UI:                    https://{local_hostname}:{local_port}"
        )
        logger.info(f"  ○ Target Web TTY:            {target_tty_url}")

        start_port_forward(
            hostname=hostname,
            username=username,
            password=password,
            keyfile=keyfile,
            port=port,
            local_hostname=local_hostname,
            local_port=local_port,
            remote_hostname=remote_hostname,
            remote_port=remote_port,
        )
