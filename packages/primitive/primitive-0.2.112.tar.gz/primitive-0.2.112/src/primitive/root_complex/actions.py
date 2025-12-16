from primitive.utils.actions import BaseAction
from subprocess import PIPE, Popen
from loguru import logger


class RootComplex(BaseAction):
    def __init__(self, primitive):
        super().__init__(primitive)
        self.latest_dmesg_timestamp = 0.0

    def parse_dmesg_page(self):
        with Popen(["dmesg"], stdout=PIPE) as process:
            for line in process.stdout.read().decode("utf-8").split("\n"):
                if line == "" or not line:
                    continue

                timestamp_str = line.split("]")[0].replace("[", "")
                try:
                    timestamp = float(timestamp_str)
                except ValueError:
                    continue
                if timestamp > self.latest_dmesg_timestamp:
                    self.latest_dmesg_timestamp = timestamp
                    # this is where do we do logic if we see the problem
                    logger.debug("New dmesg line: {}", line)
                    if "XID" in line:
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
