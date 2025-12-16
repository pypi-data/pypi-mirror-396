import concurrent
import hashlib
import sys
import threading
from pathlib import Path
from typing import Dict, Optional

import requests
from gql import gql
from loguru import logger

from primitive.graphql.sdk import create_requests_session
from primitive.utils.actions import BaseAction
from ..graphql.utility_fragments import operation_info_fragment

from ..utils.auth import create_new_session, guard
from ..utils.chunk_size import calculate_optimal_chunk_size, get_upload_speed_mb
from ..utils.memory_size import MemorySize
from .graphql.mutations import (
    file_update_mutation,
    pending_file_create_mutation,
    update_parts_details,
)
from .graphql.queries import files_list


# this class can be used in multithreaded S3 client uploader
# this requires getting an S3 access token to this machine however
# we are using presigned urls instead at this time Oct 29th, 2024
class ProgressPercentage(object):
    def __init__(self, filepath: Path) -> None:
        self._filename = filepath.name
        self._size = float(filepath.stat().st_size)
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)"
                % (self._filename, self._seen_so_far, self._size, percentage)
            )
            sys.stdout.flush()


class Files(BaseAction):
    def __init__(self, primitive):
        super().__init__(primitive)
        self.num_workers = 4
        self.upload_speed_mbps = None
        self.upload_speed_mbps = "100"

    def _pending_file_create(
        self,
        file_name: str,
        file_size: int,
        file_checksum: str,
        file_path: str,
        key_prefix: str,
        chunk_size: int,
        number_of_parts: int,
        is_public: bool = False,
        organization_id: Optional[str] = None,
        is_global: Optional[bool] = False,
    ):
        mutation = gql(pending_file_create_mutation)
        input = {
            "filePath": file_path,
            "fileName": file_name,
            "fileSize": file_size,
            "fileChecksum": file_checksum,
            "keyPrefix": key_prefix,
            "isPublic": is_public,
            "chunkSize": chunk_size,
            "numberOfParts": number_of_parts,
            "isGlobal": is_global,
        }
        if organization_id:
            input["organizationId"] = organization_id
        variables = {"input": input}
        result = self.primitive.session.execute(
            mutation, variable_values=variables, get_execution_result=True
        )
        data = result.data.get("pendingFileCreate")

        messages = data.get("messages")
        if messages:
            raise Exception("\n".join([message.get("message") for message in messages]))

        return data

    def _update_file_status(
        self,
        file_id: str,
        is_uploading: Optional[bool] = None,
        is_complete: Optional[bool] = None,
    ):
        mutation = gql(file_update_mutation)
        input: Dict[str, str | bool] = {
            "id": file_id,
        }
        if is_uploading is not None:
            input["isUploading"] = is_uploading
        if is_complete is not None:
            input["isComplete"] = is_complete

        variables = {"input": input}
        result = self.primitive.session.execute(
            mutation, variable_values=variables, get_execution_result=True
        )
        return result

    def _update_parts_details(
        self,
        file_id: str,
        part_number: int,
        etag: str,
    ):
        mutation = gql(update_parts_details)
        input = {
            "fileId": file_id,
            "partNumber": part_number,
            "etag": etag,
        }
        variables = {"input": input}

        # since this is called in a multithreaded environment,
        # we need to create a new session for each thread.
        session = create_new_session(self.primitive)
        result = session.execute(
            mutation, variable_values=variables, get_execution_result=True
        )
        return result

    @guard
    def files(
        self,
        file_id: Optional[str] = None,
        file_name: Optional[str] = None,
        organization_id: Optional[str] = None,
        organization_slug: Optional[str] = None,
        global_files: Optional[bool] = None,
    ):
        query = gql(files_list)

        filters = {}
        if not organization_id and not organization_slug and not global_files:
            whoami_result = self.primitive.auth.whoami()
            default_organization = whoami_result.data["whoami"]["defaultOrganization"]
            organization_id = default_organization["id"]
            logger.info(
                f"Using default organization ID: {default_organization.get('slug')} ({organization_id})"
            )
        if organization_slug and not organization_id:
            organization = self.primitive.organizations.get_organization(
                slug=organization_slug
            )
            organization_id = organization.get("id")

        if organization_id:
            filters["organization"] = {"id": organization_id}
        if file_id:
            filters["id"] = file_id
        if file_name:
            filters["fileName"] = {"exact": file_name}
        if global_files:
            filters["isGlobal"] = {"exact": True}

        variables = {
            "first": 25,
            "filters": filters,
        }
        result = self.primitive.session.execute(
            query, variable_values=variables, get_execution_result=True
        )
        return result

    def _upload_part(
        self,
        file_id: str,
        file_path: Path,
        part_number: int,
        presigned_url: str,
        start_byte: int,
        end_byte: int,
    ):
        part_data = None
        with open(file_path, "rb") as file:
            file.seek(start_byte)
            part_data = file.read(end_byte - start_byte)
            assert len(part_data) > 0
            file.seek(0)
        logger.debug(
            f"Part {part_number}. Start: {start_byte}. End: {end_byte}. Size: {len(part_data)}"
        )

        md5_hexdigest = hashlib.md5(part_data).hexdigest()  # Get raw MD5 bytes

        logger.debug(f"Uploading part {part_number}...")
        # Upload the part using the pre-signed URL
        response = requests.put(
            presigned_url,
            data=part_data,
        )
        # cleanup memory
        part_data = None

        logger.debug(f"Part {part_number} ETag: {response.headers.get('ETag')}")
        if response.ok:
            # Extract the ETag for the part from the response headers
            etag = response.headers.get("ETag").replace('"', "")
            if not etag:
                logger.error("Failed to retrieve ETag from response headers")
        else:
            logger.error(response.text)
            response.raise_for_status()

        if etag != md5_hexdigest:
            message = f"Part {part_number} ETag does not match MD5 checksum: {etag} != {md5_hexdigest}"
            logger.error(message)
            raise Exception(message)

        if etag:
            return self._update_parts_details(
                file_id, part_number=part_number, etag=etag
            )
        else:
            logger.error(f"Failed to upload part {part_number}")
            return None

    @guard
    def upload_file_direct(
        self,
        path: Path,
        is_public: bool = False,
        key_prefix: str = "",
        file_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        is_global: Optional[bool] = False,
    ):
        if path.exists() is False:
            raise Exception(f"File {path} does not exist.")

        file_size = path.stat().st_size
        if file_size == 0:
            raise Exception(f"{path} is empty.")

        file_checksum = hashlib.md5(path.read_bytes()).hexdigest()

        parts_details = None

        if not self.upload_speed_mbps:
            logger.info("Calculating upload speed...")
            self.upload_speed_mbps = get_upload_speed_mb()
            logger.info(f"Upload speed: {self.upload_speed_mbps} MB/s")

        if not file_id:
            chunk_size, number_of_parts = calculate_optimal_chunk_size(
                upload_speed_mb=self.upload_speed_mbps,
                file_size_bytes=file_size,
                num_workers=self.num_workers,
                optimal_time_seconds=5,
            )
            chunk_size_ms = MemorySize(chunk_size, "B")
            chunk_size_ms.convert_to("MB")
            logger.info(
                f"Creating Pending File for {path}. File Size: {MemorySize(file_size, 'B').get_human_readable()} ({file_size}). Chunk size: {chunk_size_ms} at Number of parts: {number_of_parts}"
            )

            pending_file_create = self._pending_file_create(
                file_name=path.name,
                file_size=path.stat().st_size,
                file_checksum=file_checksum,
                file_path=str(path),
                key_prefix=key_prefix,
                is_public=is_public,
                chunk_size=chunk_size,
                number_of_parts=number_of_parts,
                organization_id=organization_id,
                is_global=is_global,
            )
            file_id = pending_file_create.get("id")
            parts_details = pending_file_create.get("partsDetails")
        else:
            file_result = self.files(file_id=file_id)
            parts_details = (
                file_result.data.get("files")
                .get("edges")[0]
                .get("node")
                .get("partsDetails")
            )

        if not file_id:
            raise Exception("No file_id found or provided.")
        if not parts_details:
            raise Exception(f"No parts_details returned for File ID: {file_id}.")

        self._update_file_status(file_id, is_uploading=True)

        # now create a multithreaded uploader based on the number of cores available
        # each thread will read from its starting and ending byte range provided by parts_details
        # and upload that part to the presigned url
        # an ETag will be returned for each part uploaded and will need to stored in the parts_details
        # on the server side by updating the File object

        is_complete = True

        # Upload parts in parallel
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.num_workers
        ) as executor:
            future_to_part = {
                executor.submit(
                    self._upload_part,
                    file_id=file_id,
                    file_path=path,
                    part_number=part_details.get("PartNumber"),
                    presigned_url=part_details.get("presigned_url"),
                    start_byte=part_details.get("start_byte"),
                    end_byte=part_details.get("end_byte"),
                ): part_details
                for _key, part_details in parts_details.items()
            }
            for future in concurrent.futures.as_completed(future_to_part):
                part_detail = future_to_part[future]
                try:
                    future.result()
                    logger.debug(
                        f"Part {part_detail.get('PartNumber')} uploaded successfully."
                    )
                except Exception as exception:
                    logger.error(
                        f"Part {part_detail.get('PartNumber')} generated an exception: {exception}"
                    )
                    is_complete = False

        # when all parts have ETags (updated), send an update that
        if is_complete:
            update_file_status_result = self._update_file_status(
                file_id, is_uploading=False, is_complete=True
            )
            logger.info(f"File {path} marked is_complete.")
            return update_file_status_result

    @guard
    def upload_file_via_api(
        self,
        path: Path,
        is_public: bool = False,
        key_prefix: str = "",
        organization_id: Optional[str] = None,
        is_global: bool = False,
    ):
        """
        This method uploads a file via the Primitive API.
        This does NOT upload the file straight to S3
        """
        file_path = str(path.resolve())
        if path.exists() is False:
            raise FileNotFoundError(f"File not found at {file_path}")

        if is_public:
            operations = (
                """{ "query":\""""
                + operation_info_fragment.replace("\n", " ")
                + """mutation fileUpload($input: FileUploadInput!) { fileUpload(input: $input) { ... on File { id }, ...OperationInfoFragment } }", "variables": { "input": { "fileObject": null, "isPublic": true, "filePath": \""""
                + file_path
                + """\", "keyPrefix": \""""
                + key_prefix
                + """\", "isGlobal": """
                + ("true" if is_global else "false")
                + (
                    f', "organizationId": "{organization_id}"'
                    if organization_id
                    else ""
                )
                + """ } } }"""
            )  # noqa

        else:
            operations = (
                """{ "query":\""""
                + operation_info_fragment.replace("\n", " ")
                + """mutation fileUpload($input: FileUploadInput!) { fileUpload(input: $input) { ... on File { id }, ...OperationInfoFragment } }", "variables": { "input": { "fileObject": null, "isPublic": false, "filePath": \""""
                + file_path
                + """\", "keyPrefix": \""""
                + key_prefix
                + """\", "isGlobal": """
                + ("true" if is_global else "false")
                + (
                    f', "organizationId": "{organization_id}"'
                    if organization_id
                    else ""
                )
                + """ } } }"""
            )  # noqa
        body = {
            "operations": ("", operations),
            "map": ("", '{"fileObject": ["variables.input.fileObject"]}'),
            "fileObject": (path.name, open(path, "rb")),
        }

        session = create_requests_session(host_config=self.primitive.host_config)
        transport = self.primitive.host_config.get("transport")
        url = f"{transport}://{self.primitive.host}/"
        response = session.post(url, files=body)

        if response.ok:
            messages = (
                response.json()
                .get("data", {})
                .get("fileUpload", {})
                .get("messages", [])
            )
            if messages:
                raise Exception(
                    "\n".join([message.get("message") for message in messages])
                )

        return response

    def get_presigned_url(self, file_pk: str) -> str:
        transport = self.primitive.host_config.get("transport")
        host = self.primitive.host_config.get("host")
        file_access_url = f"{transport}://{host}/files/{file_pk}/presigned-url/"
        return file_access_url

    def download_file(
        self,
        file_name: str = "",
        file_id: str = "",
        organization_id: str = "",
        organization_slug: str = "",
        output_path: Path = Path().cwd(),
        global_file: Optional[bool] = False,
    ) -> Path:
        file_pk = None
        file_size = None

        files_result = self.primitive.files.files(
            file_id=file_id,
            file_name=file_name,
            organization_id=organization_id,
            organization_slug=organization_slug,
            global_files=global_file,
        )
        if files_data := files_result.data:
            file = files_data["files"]["edges"][0]["node"]
            file_pk = file["pk"]
            file_name = file["fileName"]
            file_size = int(file["fileSize"])

        if not file_pk:
            raise Exception(
                "File not found on remote server. Please check file name or file id"
            )

        session = create_requests_session(host_config=self.primitive.host_config)
        transport = self.primitive.host_config.get("transport")

        if file_size and file_size < 5 * 1024 * 1024:
            url = f"{transport}://{self.primitive.host}/files/{file_pk}/stream/"
        else:
            url = f"{transport}://{self.primitive.host}/files/{file_pk}/presigned-url/"

        downloaded_file = output_path / file_name

        with session.get(url, stream=True) as response:
            response.raise_for_status()
            with open(downloaded_file, "wb") as partial_downloaded_file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        partial_downloaded_file.write(chunk)
                        partial_downloaded_file.flush()

        return downloaded_file
