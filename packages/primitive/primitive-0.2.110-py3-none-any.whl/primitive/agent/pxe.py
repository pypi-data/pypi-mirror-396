from loguru import logger

from primitive.network.redfish import RedfishClient
from primitive.utils.ssh import test_ssh_connection, run_command


def pxe_boot_via_redfish(bmc_hostname: str, bmc_username: str, bmc_password: str):
    redfish = RedfishClient(
        host=bmc_hostname, username=bmc_username, password=bmc_password
    )
    redfish.update_boot_options(
        system_id="1",
        boot_source_override_target="Pxe",
        boot_source_override_enabled="Once",
        boot_source_override_mode="UEFI",
    )
    redfish.compute_system_reset(system_id="1", reset_type="ForceRestart")


def pxe_boot_via_efibootmgr(hostname: str, username: str, password: str):
    run_command(
        hostname=hostname,
        username=username,
        password=password,
        command="sudo efibootmgr -n $(efibootmgr | awk '/PXE IPV4/ {print substr($1,5,4)}' | head -n1 || efibootmgr | awk '/ubuntu/ {print substr($1,5,4)}' | head -n1) && sudo reboot",
        port=22,
    )


def pxe_boot(
    target_hardware_secret: dict, bmc_hostname: str | None, target_hostname: str | None
) -> bool:
    redfish_available = False
    ssh_available = False

    if bmc_hostname:
        redfish_available = True
    else:
        logger.info(
            "No BMC hostname found, skipping Redfish PXE boot method. Checking SSH connectivity."
        )
        ssh_available = test_ssh_connection(
            hostname=target_hostname,
            username=target_hardware_secret.get("username"),
            password=target_hardware_secret.get("password"),
            port=22,
        )

    if redfish_available and bmc_hostname:
        pxe_boot_via_redfish(
            bmc_hostname=bmc_hostname,
            bmc_username=target_hardware_secret.get("bmcUsername"),
            bmc_password=target_hardware_secret.get("bmcPassword"),
        )
        return True
    elif ssh_available:
        pxe_boot_via_efibootmgr(
            hostname=target_hostname,
            username=target_hardware_secret.get("username"),
            password=target_hardware_secret.get("password"),
        )
        return True
    else:
        logger.error(
            "No available method to PXE boot target hardware. Missing BMC credentials and SSH is not available."
        )
    return False
