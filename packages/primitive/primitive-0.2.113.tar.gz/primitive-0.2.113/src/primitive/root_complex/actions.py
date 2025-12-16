import platform
from primitive.utils.actions import BaseAction
from subprocess import PIPE, Popen
from loguru import logger
from datetime import datetime, timedelta
from primitive.utils.shell import does_executable_exist


class RootComplex(BaseAction):
    def __init__(self, primitive):
        super().__init__(primitive)
        self.can_parse_journalctl = (
            platform.system() == "Linux" and does_executable_exist("journalctl")
        )
        self.latest_journalctl_timestamp = datetime.now() - timedelta(minutes=60)

    def parse_journalctl(self):
        if not self.can_parse_journalctl:
            logger.warning("Cannot parse journalctl on this system.")
            return

        with Popen(
            [
                "journalctl",
                "--boot=0",
                "--dmesg",
                "--since="
                + str(self.latest_journalctl_timestamp.strftime("%b %d %H:%M:%S")),
            ],
            stdout=PIPE,
        ) as process:
            for line in process.stdout.read().decode("utf-8").split("\n"):
                if line == "" or not line:
                    continue

                try:
                    ts_part = " ".join(line.split()[:3])  # e.g. "Dec 09 18:31:22"
                    line_timestamp = datetime.strptime(
                        ts_part, "%b %d %H:%M:%S"
                    ).replace(year=datetime.now().year)
                except Exception as exception:
                    logger.error(
                        "Error parsing timestamp from line: {}: {}", line, exception
                    )
                    continue

                self.latest_journalctl_timestamp = line_timestamp
                # this is where do we do logic if we see the problem
                logger.debug("New dmesg line: {}", line)
                if "XID" in line:
                    logger.warning("Found actionable dmesg line: {}", line)
                    self.primitive.messaging.create_and_send_event(
                        event_type="TEST_EVENT",
                        severity="INFO",
                        correlation_id="test-correlation-id",
                        summary="we found a message from dmesg with XID",
                        message="Found XID message in dmesg: {}".format(line),
                        metadata={"key": "value"},
                    )
                else:
                    continue
