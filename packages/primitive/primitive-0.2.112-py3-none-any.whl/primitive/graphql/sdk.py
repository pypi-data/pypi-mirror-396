from typing import Dict, Optional

import requests
from gql import Client
from gql.transport.aiohttp import AIOHTTPTransport

from primitive.__about__ import __version__
from loguru import logger
from graphql import DocumentNode, ExecutionResult


def create_session(
    token: str,
    host: str = "api.primitive.tech",
    transport_protocol: str = "https",
    fingerprint: Optional[str] = None,
    fetch_schema_from_transport: bool = False,
):
    url = f"{transport_protocol}://{host}/"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "x-primitive-agent": f"primitive@{__version__}",
    }
    if token:
        headers["Authorization"] = f"Token {token}"

    if fingerprint:
        headers["x-primitive-fingerprint"] = fingerprint

    aio_transport = AIOHTTPTransport(url=url, headers=headers, ssl=True)
    session = Client(
        transport=aio_transport,
        fetch_schema_from_transport=fetch_schema_from_transport,
        execute_timeout=None,  # Prevents timeout errors on async transports
    )
    return session


def create_requests_session(
    host_config: Dict,
):
    token = host_config.get("token")

    headers = {
        # "Content-Type": "multipart/form-data", # DO NOT ADD THIS MIME TYPE IT BREAKS
        "Accept": "application/json",
        "x-primitive-agent": f"primitive@{__version__}",
    }
    if token:
        headers["Authorization"] = f"Token {token}"

    if fingerprint := host_config.get("fingerprint", None):
        headers["x-primitive-fingerprint"] = fingerprint

    session = requests.Session()
    session.headers.update(headers)
    return session


def handle_mutation_response(
    mutation: DocumentNode,
    result: Optional[ExecutionResult] = None,
    data_key: Optional[str] = None,
):
    if not result:
        raise Exception("No result returned from mutation.")

    if result.errors:
        message = " ".join([error.message for error in result.errors])
        logger.error(message)
        raise Exception(message)

    if not data_key:
        for definition in mutation.to_dict().get("definitions", []):
            if definition.get("kind") == "operation_definition":
                for selection in definition.get("selection_set", {}).get(
                    "selections", []
                ):
                    data_key = selection.get("name", {}).get("value")

    if not data_key:
        raise Exception("No data key found for mutation response handling.")

    if (
        result.data
        and result.data.get(data_key, {}).get("__typename") == "OperationInfo"
    ):
        error_message = f"{data_key}: "
        messages = result.data.get(data_key, {}).get("messages", [])

        for message in messages:
            if message.get("kind") in ["VALIDATION", "ERROR"]:
                logger.error(message.get("message"))
                error_message += message.get("message") + " "
                raise Exception(error_message)
            else:
                logger.info(message.get("message"))
