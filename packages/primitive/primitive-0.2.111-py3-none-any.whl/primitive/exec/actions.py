import typing

import paramiko

from primitive.exec.interactive import interactive_shell

if typing.TYPE_CHECKING:
    pass


from loguru import logger
from paramiko import SSHClient

from primitive.utils.actions import BaseAction


class Exec(BaseAction):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def execute_command(self, hardware_identifier: str, command: str) -> None:
        child_hardware = None
        if "." in hardware_identifier:
            hardware_slugs = hardware_identifier.split(".")
            hardware_identifier = hardware_slugs[0]
            child_hardware_identifier = hardware_slugs[-1]
            child_hardware = self.primitive.hardware.get_hardware_from_slug_or_id(
                hardware_identifier=child_hardware_identifier
            )

        hardware = self.primitive.hardware.get_hardware_from_slug_or_id(
            hardware_identifier=hardware_identifier
        )

        if not hardware:
            logger.error(
                f"Could not find hardware with identifier {hardware_identifier}"
            )
            return

        # since we found hardware, we need to check that the user:
        # - has a valid reservation on it
        # - OR if the device is free we can reserve it

        # if we create a reservation on behalf of the user, we need to release it after
        created_reservation_on_behalf_of_user = False

        if active_reservation := hardware["activeReservation"]:
            active_reservation_id = active_reservation["id"]
            reservation_result = self.primitive.reservations.get_reservation(
                reservation_id=active_reservation_id
            )
            reservation = reservation_result.data["reservation"]
        else:
            reservation_result = self.primitive.reservations.create_reservation(
                requested_hardware_ids=[hardware["id"]],
                reason="Executing command from Primitive CLI",
                wait=False,
            )
            reservation = reservation_result.data["reservationCreate"]
            created_reservation_on_behalf_of_user = True

        reservation_result = self.primitive.reservations.wait_for_reservation_status(
            reservation_id=reservation["id"], desired_status="in_progress"
        )

        reservation = reservation_result.data["reservation"]
        if reservation.get("status") != "in_progress":
            logger.info(
                f"Reservation {reservation.get('id')} is in status {reservation.get('status')}, cannot execute command at this time."
            )
            return

        hardware_secrets = self.primitive.hardware.get_hardware_secret(
            hardware_id=hardware["id"]
        )

        ssh_hostname = hardware.get("defaultIpv4Address", None)
        ssh_username = hardware_secrets["username"]

        ssh_client = SSHClient()
        ssh_client.load_system_host_keys()

        # if a failure case happens where the server is only accepting passwords
        # ensure that `PubkeyAuthentication yes` is set in your ssh config
        # this file is typically located at `/etc/ssh/sshd_config`

        try:
            ssh_client.connect(
                hostname=ssh_hostname,
                username=ssh_username,
            )
        except paramiko.AuthenticationException:
            logger.error(
                f"Authentication failed when connecting to {ssh_hostname} with username {ssh_username}."
            )
            ssh_password = hardware_secrets["password"]
            ssh_client.connect(
                hostname=ssh_hostname,
                username=ssh_username,
                password=ssh_password,
            )

        if command:
            if child_hardware:
                # if the child hardware has ssh credentials, format the proxy command
                if child_hardware.get("systemInfo").get("os_family"):
                    formatted_command = (
                        f"adb -s {child_hardware.get('slug')} shell {command}"
                    )
            else:
                # happy path!
                formatted_command = " ".join(command)

            stdin, stdout, stderr = ssh_client.exec_command(formatted_command)

            stdout_string = stdout.read().decode("utf-8").rstrip("\n")
            stderr_string = stderr.read().decode("utf-8").rstrip("\n")
            if stdout_string != b"":
                print(stdout_string)
            if stderr.read() != b"":
                print(stderr_string)

            ssh_client.close()
        else:
            # if the child hardware has ssh credentials, format the proxy jump

            channel = ssh_client.get_transport().open_session()
            channel.get_pty()
            channel.invoke_shell()
            interactive_shell(channel)
            ssh_client.close()

        if created_reservation_on_behalf_of_user:
            print("Cleaning up reservation.")
            self.primitive.reservations.release_reservation(
                reservation_or_hardware_identifier=reservation["id"]
            )
