import enum
import json
import socket
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Literal, Optional
from uuid import uuid4

import pika
from loguru import logger
from pika import credentials

from primitive.__about__ import __version__
from primitive.utils.actions import BaseAction

from ..utils.x509 import (
    are_certificate_files_present,
    create_ssl_context,
    read_certificate_common_name,
)

if TYPE_CHECKING:
    import primitive.client

EXCHANGE = "hardware"
ROUTING_KEY = "hardware"
VIRTUAL_HOST = "primitive"
CELERY_TASK_NAME = "hardware.tasks.task_receive_hardware_message"


class MESSAGE_TYPES(enum.Enum):
    CHECK_IN = "CHECK_IN"
    SYSTEM_INFO = "SYSTEM_INFO"
    METRICS = "METRICS"
    SWITCH_AND_INTERFACES_INFO = "SWITCH_AND_INTERFACES_INFO"
    OWN_NETWORK_INTERFACES = "OWN_NETWORK_INTERFACES"
    EVENT = "EVENT"


@dataclass
class MC_Event:
    event_type: str
    severity: str
    timestamp: str

    source: Optional[str]
    correlation_id: Optional[str]
    summary: str

    message: str
    metadata: dict[str, Any]


class Messaging(BaseAction):
    def __init__(self, primitive: "primitive.client.Primitive") -> None:
        super().__init__(primitive=primitive)
        self.ready = False

        self.fingerprint = self.primitive.host_config.get("fingerprint", None)
        if not self.fingerprint:
            return
        self.token = self.primitive.host_config.get("token", None)
        if not self.token:
            return

        rabbitmq_host = "rabbitmq-cluster.primitive.tech"
        RABBITMQ_PORT = 443

        if primitive.host == "api.dev.primitive.tech":
            rabbitmq_host = "rabbitmq-cluster.dev.primitive.tech"
        elif primitive.host == "api.primitive.tech":
            rabbitmq_host = "rabbitmq-cluster.primitive.tech"
        elif primitive.host == "api.staging.primitive.tech":
            rabbitmq_host = "rabbitmq-cluster.staging.primitive.tech"
        elif primitive.host == "api.test.primitive.tech":
            rabbitmq_host = "rabbitmq-cluster.test.primitive.tech"
        elif primitive.host == "localhost:8000":
            rabbitmq_host = primitive.host.split(":")[0]
            RABBITMQ_PORT = 5671

        if not are_certificate_files_present():
            logger.warning(
                "Certificate files not present or incomplete. MessagingProvider not initialized."
            )
            return

        ssl_context = create_ssl_context()
        ssl_options = pika.SSLOptions(ssl_context)
        self.common_name = read_certificate_common_name()

        self.parameters = pika.ConnectionParameters(
            host=rabbitmq_host,
            port=RABBITMQ_PORT,
            virtual_host=VIRTUAL_HOST,
            ssl_options=ssl_options,
            credentials=credentials.ExternalCredentials(),
        )

        self.ready = True

    def send_message(self, message_type: MESSAGE_TYPES, message: dict[str, any]):  # type: ignore
        if not self.ready:
            logger.warning(
                "send_message: cannot send message. MessagingProvider not initialized."
            )
            return

        body = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message_type": message_type.value,
            "message": message,
        }

        full_body_for_celery = [
            [],
            body,
            {"callbacks": None, "errbacks": None, "chain": None, "chord": None},
        ]

        max_retries = 5
        conn = None
        for attempt in range(max_retries):
            try:
                conn = pika.BlockingConnection(parameters=self.parameters)
                break
            except socket.gaierror as exception:
                if (
                    getattr(exception, "errno", None)
                    == getattr(socket, "EAI_AGAIN", None)
                ) or ("Temporary failure in name resolution" in str(exception)):
                    logger.warning(
                        f"Temporary failure in name resolution. Retrying ({attempt + 1}/{max_retries})..."
                    )
                    time.sleep(min(2**attempt, 30))
                    continue
                raise

        if conn is None:
            raise RuntimeError(
                "Failed to establish connection after retries due to DNS resolution issues."
            )

        with conn:
            message_uuid = str(uuid4())
            channel = conn.channel()

            headers = {
                "fingerprint": self.fingerprint,
                "version": __version__,
                "token": self.token,
                "argsrepr": "()",
                "id": message_uuid,
                "ignore_result": False,
                "kwargsrepr": str(body),
                "lang": "py",
                "replaced_task_nesting": 0,
                "retries": 0,
                "root_id": message_uuid,
                "task": CELERY_TASK_NAME,
            }

            channel.basic_publish(
                exchange=EXCHANGE,
                routing_key=ROUTING_KEY,
                body=json.dumps(full_body_for_celery),
                properties=pika.BasicProperties(
                    user_id=self.common_name,
                    correlation_id=message_uuid,
                    priority=0,
                    delivery_mode=2,
                    headers=headers,
                    content_encoding="utf-8",
                    content_type="application/json",
                ),
            )

    def send_test_event(self):
        self.create_and_send_event(
            event_type="TEST_EVENT",
            severity="INFO",
            correlation_id="test-correlation-id",
            summary="This is a test event from primitive-cli",
            message="This is a detailed message for the test event.",
            metadata={"key": "value"},
        )

    def create_and_send_event(
        self,
        event_type: str,
        summary: str,
        message: str,
        metadata: dict,
        source: Optional[str] = "primitive-cli",
        severity: Literal["INFO", "WARNING", "ERROR"] = "INFO",
        correlation_id: Optional[str] = None,
    ):
        event = {
            "event_type": event_type,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat(),
            "source": source,
            "correlation_id": correlation_id,
            "summary": summary,
            "message": message,
            "metadata": metadata,
        }
        self.primitive.messaging.send_message(
            message_type=MESSAGE_TYPES.EVENT, message=event
        )
