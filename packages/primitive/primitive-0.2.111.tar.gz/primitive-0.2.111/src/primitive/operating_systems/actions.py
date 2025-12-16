import os
import shutil
from enum import Enum
from pathlib import Path
from shutil import copy2, copytree, rmtree
import subprocess
from typing import Optional
from urllib.request import urlopen

import requests
from gql import gql
from loguru import logger

from primitive.graphql.relay import from_base64
from primitive.operating_systems.exceptions import P_CLI_200, P_CLI_201
from primitive.operating_systems.graphql.mutations import (
    operating_system_create_mutation,
    operating_system_update_mutation,
    operating_system_delete_mutation,
)
from primitive.operating_systems.graphql.queries import operating_system_list_query
from primitive.utils.actions import BaseAction
from primitive.utils.auth import guard
from primitive.utils.cache import get_operating_systems_cache
from primitive.utils.checksums import calculate_sha256, get_checksum_from_file
from primitive.utils.text import slugify


class OperatingSystems(BaseAction):
    def __init__(self, primitive):
        super().__init__(primitive)
        self.operating_systems_key_prefix = "operating-systems"
        self.remote_operating_systems = {
            "ubuntu-24-04-3-desktop-amd64": {
                "slug": "ubuntu-24-04-3-desktop-amd64",
                "iso": "https://releases.ubuntu.com/24.04.3/ubuntu-24.04.3-desktop-amd64.iso",
                "checksum": "https://releases.ubuntu.com/24.04.3/SHA256SUMS",
                "checksum_file_type": self.OperatingSystemChecksumFileType.SHA256SUMS,
            },
            "ubuntu-24-04-3-live-server-amd64": {
                "slug": "ubuntu-24-04-3-live-server-amd64",
                "iso": "https://releases.ubuntu.com/24.04.3/ubuntu-24.04.3-live-server-amd64.iso",
                "checksum": "https://releases.ubuntu.com/24.04.3/SHA256SUMS",
                "checksum_file_type": self.OperatingSystemChecksumFileType.SHA256SUMS,
            },
            "rocky-10-0-x86-64": {
                "slug": "rocky-10-0-x86-64",
                "iso": "https://download.rockylinux.org/pub/rocky/10/isos/x86_64/Rocky-10.0-x86_64-dvd1.iso",
                "checksum": "https://download.rockylinux.org/pub/rocky/10/isos/x86_64/CHECKSUM",
                "checksum_file_type": self.OperatingSystemChecksumFileType.SHA256SUMS,
            },
            "rocky-10-0-aarch64": {
                "slug": "rocky-10-0-aarch64",
                "iso": "https://download.rockylinux.org/pub/rocky/10/isos/aarch64/Rocky-10.0-aarch64-dvd1.iso",
                "checksum": "https://download.rockylinux.org/pub/rocky/10/isos/aarch64/CHECKSUM",
                "checksum_file_type": self.OperatingSystemChecksumFileType.SHA256SUMS,
            },
        }

    class OperatingSystemChecksumFileType(Enum):
        SHA256SUMS = "SHA256SUMS"

    def get_slug_or_id(
        self,
        operating_system_identifier: str,
    ):
        is_id = False
        is_slug = False
        id = None
        slug = None
        # first check if the operating_system_identifier is a slug or ID
        try:
            type_name, id = from_base64(operating_system_identifier)

            is_id = True
            if type_name == "OperatingSystem":
                pass
            else:
                raise Exception(
                    f"ID was not for OperatingSystem, you supplied an ID for a {type_name}"
                )

        except ValueError:
            is_slug = True
            slug = operating_system_identifier

        return {
            "is_slug": is_slug,
            "slug": slug,
            "is_id": is_id,
            "id": id,
        }

    def list_remotes(self):
        return self.remote_operating_systems.values()

    def get_remote_info(self, slug: str):
        return self.remote_operating_systems[slug]

    def _download_remote_operating_system_iso(
        self, remote_operating_system_name: str, directory: str | None = None
    ):
        cache_dir = Path(directory) if directory else get_operating_systems_cache()
        operating_system_dir = Path(cache_dir / remote_operating_system_name)
        iso_dir = Path(operating_system_dir / "iso")
        os.makedirs(iso_dir, exist_ok=True)

        operating_system_info = self.remote_operating_systems[
            remote_operating_system_name
        ]
        iso_remote_url = operating_system_info["iso"]
        iso_filename = iso_remote_url.split("/")[-1]
        iso_file_path = Path(iso_dir / iso_filename)

        if iso_file_path.exists() and iso_file_path.is_file():
            logger.info("Operating system iso already downloaded.")
            return iso_file_path

        logger.info(
            f"Downloading operating system '{remote_operating_system_name}' iso. This may take a few minutes..."
        )
        logger.info(f"Destination {iso_file_path}")

        session = requests.Session()
        with session.get(iso_remote_url, stream=True) as response:
            response.raise_for_status()
            with open(iso_file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        f.flush()

        logger.info(
            f"Successfully downloaded operating system iso to '{iso_file_path}'."
        )

        return iso_file_path

    def _download_remote_operating_system_checksum(
        self, remote_operating_system_name: str, directory: str | None = None
    ):
        cache_dir = Path(directory) if directory else get_operating_systems_cache()
        operating_system_dir = Path(cache_dir / remote_operating_system_name)
        checksum_dir = Path(operating_system_dir / "checksum")
        os.makedirs(checksum_dir, exist_ok=True)

        operating_system_info = self.remote_operating_systems[
            remote_operating_system_name
        ]
        checksum_filename = operating_system_info["checksum"].split("/")[-1]

        checksum_file_path = Path(checksum_dir / checksum_filename)
        if checksum_file_path.exists() and checksum_file_path.is_file():
            logger.info("Operating system checksum already downloaded.")
            return checksum_file_path

        logger.info(
            f"Downloading operating system '{remote_operating_system_name}' checksum."
        )
        logger.info(f"Destination {checksum_file_path}")

        checksum_response = urlopen(operating_system_info["checksum"])
        checksum_file_content = checksum_response.read()
        with open(checksum_file_path, "wb") as f:
            f.write(checksum_file_content)

        logger.info(f"Successfully downloaded checksum to '{checksum_file_path}'.")

        return checksum_file_path

    def download_remote(
        self, remote_operating_system_name: str, directory: str | None = None
    ):
        remote_operating_system_names = list(self.remote_operating_systems.keys())

        if remote_operating_system_name not in remote_operating_system_names:
            logger.error(
                f"No such remote operating system '{remote_operating_system_name}'. Run 'primitive remotes operating-systems list' for available operating systems."
            )
            raise ValueError(
                f"No such remote operating system '{remote_operating_system_name}'."
            )

        try:
            iso_file_path = self._download_remote_operating_system_iso(
                remote_operating_system_name,
                directory=directory,
            )
            checksum_file_path = self._download_remote_operating_system_checksum(
                remote_operating_system_name,
                directory=directory,
            )

        except (Exception, KeyboardInterrupt) as exception:
            if isinstance(exception, KeyboardInterrupt):
                logger.info("Cleaning up partial files")
            else:
                logger.error(
                    "An error occurred during remote download, cleaning up partial files"
                )

            self._remove_partial_files(
                operating_system=remote_operating_system_name, directory=directory
            )
            raise

        logger.info("Validating iso checksum")
        checksum_valid = self.primitive.operating_systems._validate_checksum(
            remote_operating_system_name,
            str(iso_file_path),
            str(checksum_file_path),
        )

        if not checksum_valid:
            raise Exception(
                "Checksums did not match:  file may have been corrupted during download."
                + f"\nTry deleting the directory {get_operating_systems_cache()}/{remote_operating_system_name} and running this command again."
            )

        logger.info("Checksum valid")

        return iso_file_path, checksum_file_path

    def _remove_partial_files(
        self, operating_system: str, directory: str | None = None
    ):
        cache_dir = Path(directory) if directory else get_operating_systems_cache()
        operating_system_dir = cache_dir / operating_system
        if operating_system_dir.exists():
            rmtree(operating_system_dir)

    def _validate_checksum(
        self,
        operating_system_name: str,
        iso_file_path: str,
        checksum_file_path: str,
        checksum_file_type: OperatingSystemChecksumFileType | None = None,
    ):
        checksum_file_type = (
            checksum_file_type
            if checksum_file_type
            else self.get_remote_info(operating_system_name)["checksum_file_type"]
        )

        match checksum_file_type:
            case self.OperatingSystemChecksumFileType.SHA256SUMS:
                return self._validate_sha256_sums_checksum(
                    iso_file_path, checksum_file_path
                )
            case _:
                logger.error(f"Invalid checksum file type: {checksum_file_type}")
                raise ValueError(f"Invalid checksum file type: {checksum_file_type}")

    def _validate_sha256_sums_checksum(self, iso_file_path, checksum_file_path):
        iso_file_name = Path(iso_file_path).name

        remote_checksum = get_checksum_from_file(checksum_file_path, iso_file_name)
        local_checksum = calculate_sha256(iso_file_path)
        return remote_checksum == local_checksum

    def _upload_iso_file(
        self,
        iso_file_path: Path,
        organization_id: str,
        operating_system_slug: str,
        is_global: Optional[bool] = False,
    ):
        iso_upload_result = self.primitive.files.upload_file_direct(
            path=iso_file_path,
            organization_id=organization_id,
            key_prefix=f"{self.operating_systems_key_prefix}/{operating_system_slug}",
            is_global=is_global,
        )

        if not iso_upload_result or iso_upload_result.data is None:
            logger.error("Unable to upload iso file")
            raise Exception("Unable to upload iso file")

        iso_upload_data = iso_upload_result.data
        iso_file_id = iso_upload_data.get("fileUpdate", {}).get("id")

        if not iso_file_id:
            logger.error("Unable to upload iso file")
            raise Exception("Unable to upload iso file")

        return iso_file_id

    def _upload_checksum_file(
        self,
        checksum_file_path: Path,
        organization_id: str,
        operating_system_slug: str,
        is_global: bool = False,
    ):
        checksum_upload_response = self.primitive.files.upload_file_via_api(
            path=checksum_file_path,
            organization_id=organization_id,
            key_prefix=f"{self.operating_systems_key_prefix}/{operating_system_slug}",
            is_global=is_global,
        )

        if not checksum_upload_response.ok:
            logger.error("Unable to upload checksum file")
            raise Exception("Unable to upload checksum file")

        checksum_file_id = (
            checksum_upload_response.json()
            .get("data", {})
            .get("fileUpload", {})
            .get("id", {})
        )

        if not checksum_file_id:
            logger.error("Unable to upload checksum file")
            raise Exception("Unable to upload checksum file")

        return checksum_file_id

    @guard
    def create(
        self,
        slug: str,
        iso_file: str,
        checksum_file: str,
        checksum_file_type: str,
        organization_id: str,
        is_global: bool = False,
        overwrite: bool = False,
    ):
        formatted_slug = slugify(slug)
        is_slug_available, operating_system_id = (
            self.primitive.operating_systems._is_slug_available(
                slug=formatted_slug,
                organization_id=organization_id,
                is_global=is_global,
            )
        )

        if not is_slug_available and not overwrite:
            raise P_CLI_200()

        is_known_checksum_file_type = (
            checksum_file_type
            in self.primitive.operating_systems.OperatingSystemChecksumFileType._value2member_map_
        )

        if not is_known_checksum_file_type:
            raise Exception(
                f"Operating system checksum file type {checksum_file_type} is not supported."
                + f" Supported types are: {''.join([type.value for type in self.primitive.operating_systems.OperatingSystemChecksumFileType])}"
            )

        iso_file_path = Path(iso_file)
        checksum_file_path = Path(checksum_file)

        if not iso_file_path.is_file():
            raise Exception(
                f"ISO file {iso_file_path} does not exist or is not a file."
            )

        if not checksum_file_path.is_file():
            raise Exception(
                f"Checksum file {checksum_file_path} does not exist or is not a file."
            )

        logger.info("Uploading iso file. This may take a while...")
        iso_file_id = self.primitive.operating_systems._upload_iso_file(
            iso_file_path=iso_file_path,
            organization_id=organization_id,
            operating_system_slug=formatted_slug,
            is_global=is_global,
        )

        logger.info("Uploading checksum file")
        checksum_file_id = self.primitive.operating_systems._upload_checksum_file(
            checksum_file_path=checksum_file_path,
            organization_id=organization_id,
            operating_system_slug=formatted_slug,
            is_global=is_global,
        )

        if overwrite and operating_system_id:
            logger.info(f"Found existing operating system with slug {formatted_slug}")
            logger.info("Updating operating system.")
            operating_system_update_response = self.primitive.operating_systems.update(
                operating_system_id=operating_system_id,
                checksum_file_id=checksum_file_id,
                checksum_file_type=checksum_file_type,
                iso_file_id=iso_file_id,
            )

            if "id" not in operating_system_update_response:
                raise Exception("Failed to update operating system")
            return operating_system_update_response

        else:
            logger.info("Creating operating system.")
            operating_system_create_response = (
                self.primitive.operating_systems._create_query(
                    slug=formatted_slug,
                    checksum_file_id=checksum_file_id,
                    checksum_file_type=checksum_file_type,
                    organization_id=organization_id,
                    iso_file_id=iso_file_id,
                    is_global=is_global,
                )
            )

            if "id" not in operating_system_create_response:
                raise Exception("Failed to create operating system")
            return operating_system_create_response

    @guard
    def _create_query(
        self,
        slug: str,
        organization_id: str,
        checksum_file_id: str,
        checksum_file_type: str,
        iso_file_id: str,
        is_global: bool = False,
    ):
        mutation = gql(operating_system_create_mutation)
        input = {
            "slug": slug,
            "organizationId": organization_id,
            "checksumFileId": checksum_file_id,
            "checksumFileType": checksum_file_type,
            "isoFileId": iso_file_id,
            "isGlobal": is_global,
        }
        variables = {"input": input}
        result = self.primitive.session.execute(
            mutation, variable_values=variables, get_execution_result=True
        )
        return result.data.get("operatingSystemCreate")

    @guard
    def update(
        self,
        operating_system_id: str,
        checksum_file_id: str | None = None,
        checksum_file_type: str | None = None,
        iso_file_id: str | None = None,
    ):
        mutation = gql(operating_system_update_mutation)
        input = {
            "id": operating_system_id,
            "checksumFileId": checksum_file_id,
            "checksumFileType": checksum_file_type,
            "isoFileId": iso_file_id,
        }
        variables = {"input": input}
        result = self.primitive.session.execute(
            mutation, variable_values=variables, get_execution_result=True
        )
        return result.data.get("operatingSystemUpdate")

    @guard
    def list(
        self,
        organization_id: str | None = None,
        slug: str | None = None,
        id: str | None = None,
        is_global: bool = False,
    ):
        query = gql(operating_system_list_query)

        variables = {"filters": {}}

        if organization_id and not is_global:
            variables["filters"]["organization"] = {"id": organization_id}

        if is_global:
            variables["filters"]["isGlobal"] = {"exact": True}

        if slug:
            variables["filters"]["slug"] = {"exact": slug}

        if id:
            variables["filters"]["id"] = id

        result = self.primitive.session.execute(
            query, variable_values=variables, get_execution_result=True
        )

        edges = result.data.get("operatingSystemList").get("edges", [])

        nodes = [edge.get("node") for edge in edges]

        return nodes

    @guard
    def _delete_query(self, id: str):
        mutation = gql(operating_system_delete_mutation)

        result = self.primitive.session.execute(
            mutation, variable_values={"input": {"id": id}}, get_execution_result=True
        )

        return result.data.get("operatingSystemDelete")

    @guard
    def delete(
        self,
        slug: str = None,
        id: str = None,
        organization_id: str = None,
        is_global: bool = False,
    ):
        if not slug and not id:
            raise Exception("operating_systems.delete - slug or id is required")

        get_args = {}

        if slug:
            get_args["slug"] = slug
        else:
            get_args["id"] = id

        if is_global:
            get_args["is_global"] = is_global
        else:
            get_args["organization_id"] = organization_id

        operating_system = self.primitive.operating_systems.get(**get_args)

        return self._delete_query(id=operating_system["id"])

    @guard
    def _get_organization_or_global_operating_system(
        self, organization_id: str, slug: str | None = None, id: str | None = None
    ):
        try:
            operating_system = self.primitive.operating_systems.get(
                organization_id=organization_id, slug=slug, id=id
            )
            return operating_system, False
        except P_CLI_201:
            # If the operating system isn't found in the users org, check the global primitive operating systems
            operating_system = self.primitive.operating_systems.get(
                slug=slug, id=id, is_global=True
            )
            return operating_system, True

    @guard
    async def _aget_organization_or_global_operating_system(
        self, organization_id: str, slug: str | None = None, id: str | None = None
    ):
        try:
            operating_system = await self.primitive.operating_systems.aget(
                organization_id=organization_id, slug=slug, id=id
            )
            return operating_system, False
        except P_CLI_201:
            # If the operating system isn't found in the users org, check the global primitive operating systems
            operating_system = self.primitive.operating_systems.get(
                slug=slug, id=id, is_global=True
            )
            return operating_system, True

    @guard
    def download(
        self,
        organization_id: str,
        id: str | None = None,
        slug: str | None = None,
        directory: str | None = None,
        overwrite: bool = False,
    ):
        operating_system, is_global = self._get_organization_or_global_operating_system(
            organization_id=organization_id, slug=slug, id=id
        )

        is_cached, path = self.primitive.operating_systems.is_operating_system_cached(
            slug=operating_system["slug"],
            directory=directory,
        )

        if is_cached and not overwrite:
            logger.info("Operating system already exists in cache, aborting download.")
            logger.info(path)
            return path

        download_directory = (
            Path(directory) / operating_system["slug"]
            if directory
            else (get_operating_systems_cache() / operating_system["slug"])
        )
        checksum_directory = download_directory / "checksum"
        checksum_file_path = (
            checksum_directory / operating_system["checksumFile"]["fileName"]
        )
        iso_directory = download_directory / "iso"
        iso_file_path = iso_directory / operating_system["isoFile"]["fileName"]

        try:
            if not iso_directory.exists():
                iso_directory.mkdir(parents=True)

            if not checksum_directory.exists():
                checksum_directory.mkdir(parents=True)

            download_file_args = (
                {"organization_id": organization_id}
                if not is_global
                else {"global_file": True}
            )

            logger.info(
                f"Downloading operating system iso to cache {download_directory}"
            )
            self.primitive.files.download_file(
                file_id=operating_system["isoFile"]["id"],
                output_path=iso_directory,
                **download_file_args,
            )

            logger.info(
                f"Downloading operating system checksum to cache {download_directory}"
            )
            self.primitive.files.download_file(
                file_id=operating_system["checksumFile"]["id"],
                output_path=checksum_directory,
                **download_file_args,
            )
        except (Exception, KeyboardInterrupt) as exception:
            if isinstance(exception, KeyboardInterrupt):
                logger.info("Cleaning up partial files")
            else:
                logger.error(
                    "An error occurred during remote download, cleaning up partial files"
                )
            self._remove_partial_files(
                operating_system=operating_system["slug"], directory=directory
            )
            raise

        logger.info("Validating iso checksum")
        checksum_file_type = (
            self.primitive.operating_systems.OperatingSystemChecksumFileType[
                operating_system["checksumFileType"]
            ]
        )
        checksum_valid = self.primitive.operating_systems._validate_checksum(
            operating_system["slug"],
            iso_file_path,
            checksum_file_path,
            checksum_file_type=checksum_file_type,
        )

        if not checksum_valid:
            raise Exception(
                "Checksums did not match:  file may have been corrupted during download."
                + f"\nTry deleting the directory {get_operating_systems_cache()}/{operating_system['slug']} and running this command again."
            )

        return download_directory

    def uncache(
        self,
        operating_system_name: str,
    ):
        shutil.rmtree(f"{get_operating_systems_cache()}/{operating_system_name}")

    @guard
    def get(
        self,
        organization_id: str | None = None,
        slug: str | None = None,
        id: str | None = None,
        is_global: bool = False,
    ):
        if not (slug or id):
            raise Exception("Slug or id must be provided.")
        if slug and id:
            raise Exception("Only one of slug or id must be provided.")

        operating_systems = self.list(
            organization_id=organization_id, slug=slug, id=id, is_global=is_global
        )

        if len(operating_systems) == 0:
            if slug:
                raise P_CLI_201(f"No operating system found for slug {slug}.")
            else:
                raise P_CLI_201(f"No operating system found for ID {id}.")

        return operating_systems[0]

    @guard
    def _is_slug_available(self, slug: str, organization_id: str, is_global: bool):
        formatted_slug = slugify(slug)

        query = gql(operating_system_list_query)

        filters = {
            "slug": {"exact": formatted_slug},
        }

        if is_global:
            filters["isGlobal"] = {"exact": True}
        else:
            filters["organization"] = {"id": organization_id}

        variables = {"filters": filters}

        result = self.primitive.session.execute(
            query, variable_values=variables, get_execution_result=True
        )

        count = result.data.get("operatingSystemList").get("totalCount")

        operating_system_id = None
        if edges := result.data.get("operatingSystemList").get("edges", []):
            operating_system_id = edges[0].get("node", {}).get("id")

        return (count == 0, operating_system_id)

    def is_operating_system_cached(self, slug: str, directory: str | None = None):
        cache_dir = Path(directory) if directory else get_operating_systems_cache()
        cache_path = cache_dir / slug

        return cache_path.exists(), cache_path

    def is_operating_system_cached_for_pxe(self, slug: str, iso_filename: str):
        return False
        # pxe_os_path = Path(f"/var/www/html/pxe/operating-systems/{slug}/")
        # pxe_vmlinuz_path = Path(pxe_os_path / "vmlinuz")
        # pxe_initrd_path = Path(pxe_os_path / "initrd")
        # pxe_iso_path = Path(pxe_os_path / iso_filename)

        # return (
        #     pxe_vmlinuz_path.exists()
        #     and pxe_initrd_path.exists()
        #     and pxe_iso_path.exists()
        # )

    def _mount_iso(self, iso_path: Path, mount_path: Path):
        if mount_path.exists():
            logger.info(f"Mount path {mount_path} already exists.")
            try:
                self._unmount_iso(mount_path=mount_path)
            except Exception as e:
                logger.warning(f"Failed to unmount existing mount at {mount_path}: {e}")
                mount_path.rmdir()
        mount_path.mkdir(parents=True, exist_ok=True)
        command = f"sudo mount -o loop {iso_path} {mount_path}"
        logger.info(f"Mounting ISO with command: {command}")
        result = os.system(command)
        if result != 0:
            raise Exception(f"Failed to mount ISO {iso_path} to {mount_path}")

    def _unmount_iso(self, mount_path: Path):
        command = f"sudo umount {mount_path}"
        logger.info(f"Unmounting ISO with command: {command}")
        result = os.system(command)
        if result != 0:
            raise Exception(f"Failed to unmount ISO from {mount_path}")

    def _add_operating_system_to_pxe(self, operating_system_slug: str):
        is_cached, cache_path = self.is_operating_system_cached(
            slug=operating_system_slug,
        )
        if not is_cached:
            raise Exception(
                f"Operating system {operating_system_slug} is not cached. Please download it first."
            )

        operating_system = self.get(slug=operating_system_slug)
        iso_filename = operating_system.get("isoFile").get("fileName")

        pxe_os_path = Path(
            f"/var/www/html/pxe/operating-systems/{operating_system_slug}/"
        )
        pxe_os_path.mkdir(parents=True, exist_ok=True)
        if pxe_os_path.exists():
            logger.info(f"PXE operating system path {pxe_os_path} already exists.")

        pxe_vmlinuz_path = Path(pxe_os_path / "vmlinuz")
        pxe_initrd_path = Path(pxe_os_path / "initrd")
        pxe_iso_path = Path(pxe_os_path / iso_filename)

        if operating_system_slug.startswith("rocky"):
            # specific for rocky linux
            pxe_initrd_path = Path(pxe_os_path / "initrd.img")

        if self.is_operating_system_cached_for_pxe(
            slug=operating_system_slug, iso_filename=iso_filename
        ):
            logger.info(
                f"Operating system {operating_system_slug} already configured for PXE."
            )
            logger.info("PXE Paths:")
            logger.info(pxe_iso_path)
            logger.info(pxe_initrd_path)
            logger.info(pxe_vmlinuz_path)
            return

        iso_path = Path(cache_path / "iso" / iso_filename)
        if not iso_path.exists():
            raise Exception(
                f"No ISO file found for operating system {operating_system_slug}"
            )

        mount_path = Path(f"/mnt/{operating_system_slug}")

        self._mount_iso(iso_path=iso_path, mount_path=mount_path)

        # this only works for ubuntu based isos for now
        if operating_system_slug.startswith("ubuntu"):
            source_vmlinuz_path = mount_path / "casper" / "vmlinuz"
            source_initrd_path = mount_path / "casper" / "initrd"
        elif operating_system_slug.startswith("rocky"):
            source_vmlinuz_path = mount_path / "images" / "pxeboot" / "vmlinuz"
            source_initrd_path = mount_path / "images" / "pxeboot" / "initrd.img"

        else:
            self._unmount_iso(mount_path=mount_path)
            raise Exception(
                f"Operating system {operating_system_slug} is not supported for PXE setup yet."
            )

        copy2(source_vmlinuz_path, pxe_vmlinuz_path)
        copy2(source_initrd_path, pxe_initrd_path)
        copy2(iso_path, pxe_iso_path)
        if operating_system_slug.startswith("rocky"):
            pxe_rocky_os_path = Path(pxe_os_path / "os")
            pxe_rocky_os_path.mkdir(parents=True, exist_ok=True)
            copytree(mount_path, pxe_rocky_os_path, dirs_exist_ok=True)

        self._unmount_iso(mount_path=mount_path)

        if (
            pxe_vmlinuz_path.exists()
            and pxe_initrd_path.exists()
            and pxe_iso_path.exists()
        ):
            logger.info(
                f"Successfully configured operating system {operating_system_slug} for PXE."
            )
        else:
            raise Exception(
                f"Failed to configure operating system {operating_system_slug} for PXE."
            )

        logger.info("PXE Paths:")
        logger.info(pxe_iso_path)
        logger.info(pxe_initrd_path)
        logger.info(pxe_vmlinuz_path)

    def _create_boot_script_for_operating_system(
        self,
        target_mac_address: str,
        file_server_hostname: str,
        operating_system_slug: str,
        iso_filename: str,
    ):
        pxe_os_path = Path(f"/var/www/html/pxe/hardware/{target_mac_address}")
        pxe_os_path.mkdir(parents=True, exist_ok=True)
        boot_script_path = Path(pxe_os_path / "boot.ipxe")
        if boot_script_path.exists():
            boot_script_path.unlink()

        if operating_system_slug.startswith("ubuntu"):
            boot_script_content = f"""#!ipxe
kernel http://{file_server_hostname}/pxe/operating-systems/{operating_system_slug}/vmlinuz
initrd http://{file_server_hostname}/pxe/operating-systems/{operating_system_slug}/initrd
imgargs vmlinuz initrd=initrd ip=dhcp BOOTIF=${{netX/mac}} cloud-config-url=/dev/null priority=critical DEBCONF_DEBUG=5 url=http://{file_server_hostname}/pxe/operating-systems/{operating_system_slug}/{iso_filename} autoinstall ds=nocloud-net;s=http://{file_server_hostname}/pxe/hardware/{target_mac_address}/autoinstall/
boot
"""
        elif operating_system_slug.startswith("rocky"):
            boot_script_content = f"""#!ipxe
kernel http://{file_server_hostname}/pxe/operating-systems/{operating_system_slug}/vmlinuz ip=dhcp BOOTIF=${{netX/mac}} inst.stage2=http://{file_server_hostname}/pxe/operating-systems/{operating_system_slug}/os/ inst.ks=http://{file_server_hostname}/pxe/kickstart/rocky10.ks
initrd http://{file_server_hostname}/pxe/operating-systems/{operating_system_slug}/initrd.img
boot
"""

        else:
            raise Exception(
                f"Operating system {operating_system_slug} is not supported for PXE setup yet."
            )

        with open(boot_script_path, "w") as boot_script_file:
            boot_script_file.write(boot_script_content)

        logger.info(f"Created PXE boot script at {boot_script_path}")

    def _create_autoinstall_config(
        self,
        file_server_hostname: str,
        target_mac_address: str,
        target_username: str,
        target_password: str,
        target_machine_name: str,
        target_auth_token: str,
    ):
        pxe_os_path = Path(f"/var/www/html/pxe/hardware/{target_mac_address}")
        autoinstall_path = Path(pxe_os_path / "autoinstall")
        autoinstall_path.mkdir(parents=True, exist_ok=True)

        meta_data_file = Path(autoinstall_path / "meta-data")

        if meta_data_file.exists():
            meta_data_file.unlink()
        with open(meta_data_file, "w") as meta_data:
            meta_data.write(
                f"instance-id: iid-local01\nlocal-hostname: {target_machine_name}\n"
            )
        logger.info(f"Created autoinstall meta-data at {meta_data_file}")

        user_data_file = Path(autoinstall_path / "user-data")
        if user_data_file.exists():
            user_data_file.unlink()

        hashed_password = (
            subprocess.check_output(["mkpasswd", "--method=SHA-512", target_password])
            .decode()
            .strip()
        )

        with open(user_data_file, "w") as user_data:
            user_data.write(f"""#cloud-config
autoinstall:
  version: 1
  locale: en_US.UTF-8
  keyboard:
    layout: us
  timezone: America/New_York
  user-data:
    locale: en_US.UTF-8
    disable_root: false
    users:
      - name: {target_username}
        shell: /bin/bash
        groups: [adm, sudo]
        sudo: ALL=(ALL) NOPASSWD:ALL
    runcmd:
      - curl -LsSf http://{file_server_hostname}/pxe/hardware/{target_mac_address}/autoinstall/user-data-script.sh | sh

  identity:
    hostname: {target_machine_name}
    username: {target_username}
    password: {hashed_password}

  apt:
    disable_suites: [updates, security]

  storage:
    swap:
      size: 0
    layout:
      name: direct
      match:
        size: smallest

  packages:
    - curl

  ssh:
    install-server: true
    allow-pw: true
""")

        user_data_script_file = Path(autoinstall_path / "user-data-script.sh")
        if user_data_script_file.exists():
            user_data_script_file.unlink()
        with open(user_data_script_file, "w") as user_data_script:
            user_data_script.write(f"""#! /bin/bash
# LOGS ARE LOCATED AT /var/log/cloud-init-output.log
ls -la
pwd
echo $USER
curl -LsSf https://astral.sh/uv/install.sh | sh
. /$USER/.local/bin/env
. /$USER/.bashrc
uv python install --default 3.14.0
uv venv --no-project /$USER/.venv/
. /$USER/.venv/bin/activate
uv pip install --no-cache primitive
primitive --host {self.primitive.host} config --auth-token {target_auth_token}
primitive --host {self.primitive.host} hardware register --issue-certificate
primitive --debug --host {self.primitive.host} daemons install
""")

    def _prepare_operating_system_for_pxe(
        self,
        organization_id: str,
        operating_system_slug: str,
        iso_filename: str,
        file_server_hostname: str,
        target_mac_address: str,
        target_username: str,
        target_password: str,
        target_machine_name: str,
        target_auth_token: str,
    ):
        if not target_mac_address:
            raise Exception("Target MAC Address is required for PXE setup.")

        self._create_autoinstall_config(
            file_server_hostname=file_server_hostname,
            target_mac_address=target_mac_address,
            target_username=target_username,
            target_password=target_password,
            target_machine_name=target_machine_name,
            target_auth_token=target_auth_token,
        )

        self._create_boot_script_for_operating_system(
            target_mac_address=target_mac_address,
            file_server_hostname=file_server_hostname,
            operating_system_slug=operating_system_slug,
            iso_filename=iso_filename,
        )

        if self.is_operating_system_cached_for_pxe(
            slug=operating_system_slug, iso_filename=iso_filename
        ):
            logger.info(
                f"Operating system {operating_system_slug} already configured for PXE."
            )
            return

        is_cached, cache_path = self.is_operating_system_cached(
            slug=operating_system_slug,
        )
        if not is_cached:
            self.download(organization_id=organization_id, slug=operating_system_slug)

        self._add_operating_system_to_pxe(operating_system_slug=operating_system_slug)
