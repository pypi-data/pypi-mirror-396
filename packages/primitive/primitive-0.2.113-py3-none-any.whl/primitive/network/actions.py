import json
import re
from pathlib import Path
from subprocess import PIPE, Popen
from typing import TypedDict

import requests
import serial
from loguru import logger
from paramiko import SSHClient

from primitive.hardware.actions import does_executable_exist
from primitive.messaging.actions import MESSAGE_TYPES
from primitive.utils.actions import BaseAction

# 0. see if this controller node hardware has a switch connected to it
# see if there is any information about the switch from the database
# 1. check if the switch is reachable by an IP
# 2. if reachable, check if the API is enabled
# 3. if API is enabled, return True
# 4. if API is not enabled
# - check if we can do ssh connection
# - if ssh connection is possible, enable the API, return True
# - if ssh connection is not possible, check for serial connection
# - if serial connection is possible, enable the API, return True
# - if serial connection is not possible, return False
# 5. if switch is not reachable by IP, SSH or Serial, return False
# 6. if the switch is reachable, ask for the switch information
# 7. json form that switch information and send it over rabbitmq


def mac_address_manufacturer_style_to_ieee(mac: str) -> str:
    """
    Convert Arista-style MAC (xxxx.xxxx.xxxx) into IEEE style (xx:xx:xx:xx:xx:xx).
    Example: '54b2.0319.7692' -> '54:b2:03:19:76:92'
    """
    # Remove dots
    mac = mac.replace(".", "")
    # Ensure correct length
    if len(mac) != 12:
        raise ValueError("Invalid Arista MAC format")
    # Split into pairs
    return ":".join(mac[i : i + 2] for i in range(0, 12, 2))


def natural_interface_key(s):
    # extract numbers after "Ethernet" or subports
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", s)]


class SwitchConnectionInfo(TypedDict):
    vendor: str
    hostname: str
    username: str
    password: str


class MacAddressEntry(TypedDict):
    ip_address: str | None
    mac_address: str
    vlan: str


class Network(BaseAction):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.switch_tty_name = None

        self.switch_connection_info: SwitchConnectionInfo | None = None
        self.remote_switch = None
        self.local_switch = None

        # session info
        # if it is set to None it has not been checked yet
        self.switch_api_available: bool | None = None
        self.switch_ssh_available: bool | None = None

    def is_switch_api_enabled(self) -> bool:
        if self.switch_api_available is not None:
            return self.switch_api_available

        self.switch_api_available = False
        if (
            self.switch_connection_info
            and self.switch_connection_info["vendor"] == "arista"
        ):
            if not self.switch_connection_info["hostname"]:
                logger.error(
                    "Switch hostname is not set, it is not set in the hardware list"
                )
                return False

            try:
                response = requests.get(
                    f"http://{self.switch_connection_info['hostname']}/eapi"
                )
                if response.ok:
                    self.switch_api_available = True
            except requests.exceptions.ConnectionError as exception:
                logger.error(f"Switch API connection error: {exception}")
                self.switch_api_available = False
        return self.switch_api_available

    def is_switch_ssh_enabled(self) -> bool:
        if self.switch_ssh_available is not None:
            return self.switch_ssh_available

        self.switch_ssh_available = False
        if self.switch_connection_info:
            ssh_client = SSHClient()
            ssh_client.load_system_host_keys()

            ssh_hostname = self.switch_connection_info.get("hostname", None)
            ssh_username = self.switch_connection_info.get("username", None)
            ssh_password = self.switch_connection_info.get("password", None)
            if ssh_hostname and ssh_username and ssh_password:
                try:
                    ssh_client.connect(
                        hostname=ssh_hostname,
                        username=ssh_username,
                        password=ssh_password,
                        timeout=5,
                    )
                    self.switch_ssh_available = True
                except Exception as exception:
                    logger.error(f"Error connecting to switch via SSH: {exception}")
        return self.switch_ssh_available

    def arista_eapi_request_handler(self, command):
        # example commands "show version" "show interfaces status"
        if not self.switch_connection_info:
            return None

        url = f"http://{self.switch_connection_info['hostname']}/command-api"
        with requests.Session() as session:
            session.auth = (
                self.switch_connection_info["username"],
                self.switch_connection_info["password"],
            )
            session.headers.update({"Content-type": "application/json-rpc"})
            payload = {
                "jsonrpc": "2.0",
                "method": "runCmds",
                "params": {
                    "version": "latest",
                    "format": "json",
                    "cmds": [command],
                },
                "id": 1,
            }
            with session:
                response = session.post(
                    url=url,
                    json=payload,
                )
                if response.ok:
                    return response.json()
                else:
                    logger.error(
                        f"Error connecting to eAPI: {response.status_code} {response.text}"
                    )
                return None

    def get_switch_info(self):
        if self.switch_connection_info is None:
            self.primitive.hardware.get_and_set_switch_info()
        if self.is_switch_api_enabled():
            switch_info = self.get_switch_info_via_api()
            if switch_info:
                return switch_info

        return None

    def get_interfaces_info(self) -> dict:
        if self.switch_connection_info is None:
            self.primitive.hardware.get_and_set_switch_info()
        if self.is_switch_api_enabled():
            interfaces_info = self.get_interfaces_via_api()
            mac_address_info = self.get_mac_address_info_via_api()

            ip_arp_table_info = self.get_ip_arp_table_via_api()
            controllers_neighbors = self.get_ip_arp_table_via_ip_command()

            if interfaces_info and mac_address_info and ip_arp_table_info:
                for interface, mac_info in mac_address_info.items():
                    if interface in interfaces_info:
                        mac_addresses: dict[str, MacAddressEntry] = {}
                        for entry in mac_info:
                            mac_addresses[entry.get("macAddress", "")] = {
                                "mac_address": entry.get("macAddress", ""),
                                "ip_address": None,
                                "vlan": entry.get("vlanId", ""),
                            }

                        for neighbor in controllers_neighbors:
                            neighbor_state = neighbor.get("state", [])
                            if "FAILED" in neighbor_state:
                                continue

                            # if there is an existing MAC address, update its IP address only if the ip address is empty AND the state is REACHABLE
                            lladdr = neighbor.get(
                                "lladdr", None
                            )  # this is the mac address
                            dst = neighbor.get("dst", None)  # this is the IP address
                            if lladdr in mac_addresses and dst:
                                if (
                                    mac_addresses[lladdr]["ip_address"]
                                    and "REACHABLE" in neighbor_state
                                ):
                                    # if there is a populated ip address, overwrite if REACHABLE
                                    mac_addresses[lladdr]["ip_address"] = dst
                                elif mac_addresses[lladdr]["ip_address"] is None:
                                    # if there is no populated ip address, set it, even if the state is STALE
                                    mac_addresses[lladdr]["ip_address"] = dst

                        interfaces_info[interface]["mac_addresses"] = mac_addresses

                        if interface in ip_arp_table_info:
                            for ip_arp in ip_arp_table_info[interface]:
                                for mac_address_entry in interfaces_info[interface][
                                    "mac_addresses"
                                ].values():
                                    if (
                                        ip_arp.get("mac_address", "")
                                        in mac_address_entry["mac_address"]
                                    ):
                                        mac_address_entry["ip_address"] = ip_arp.get(
                                            "ip_address", None
                                        )

                return interfaces_info

        return {}

    def get_mac_address_info(self):
        if self.is_switch_api_enabled():
            mac_address_info = self.get_mac_address_info_via_api()
            if mac_address_info:
                return mac_address_info

        return None

    def get_switch_info_via_api(self):
        formatted_switch_info = None
        if (
            self.switch_connection_info
            and self.switch_connection_info["vendor"] == "arista"
        ):
            if response := self.arista_eapi_request_handler("show version"):
                arista_version_info = response.get("result", [])[0]
                # example output:
                # {
                #     "imageFormatVersion": "3.0",
                #     "uptime": 6038503.06,
                #     "modelName": "DCS-7050TX-64-R",
                #     "internalVersion": "4.28.5.1M-30127723.42851M",
                #     "memTotal": 3982512,
                #     "mfgName": "Arista",
                #     "serialNumber": "JPE16121065",
                #     "systemMacAddress": "44:4c:a8:a3:61:77",
                #     "bootupTimestamp": 1753302953.365648,
                #     "memFree": 2546096,
                #     "version": "4.28.5.1M",
                #     "configMacAddress": "00:00:00:00:00:00",
                #     "isIntlVersion": false,
                #     "imageOptimization": "Strata-4GB",
                #     "internalBuildId": "9adca383-a3bd-4507-b53b-d99ca7d61291",
                #     "hardwareRevision": "01.11",
                #     "hwMacAddress": "44:4c:a8:a3:61:77",
                #     "architecture": "i686"
                # },
                formatted_switch_info = {
                    "vendor": arista_version_info.get("mfgName", ""),
                    "model": arista_version_info.get("modelName", ""),
                    "serial_number": arista_version_info.get("serialNumber", ""),
                    "mac_address": arista_version_info.get("systemMacAddress", ""),
                    # "raw_output": arista_version_info,
                }
        return formatted_switch_info

    def get_interfaces_via_api(self):
        formatted_interfaces_info = None
        if (
            self.switch_connection_info
            and self.switch_connection_info["vendor"] == "arista"
        ):
            if response := self.arista_eapi_request_handler("show interfaces status"):
                # example output:
                # {
                #     "interfaceStatuses": {
                #         "Ethernet10": {
                #             "vlanInformation": {
                #                 "interfaceMode": "bridged",
                #                 "vlanId": 1,
                #                 "interfaceForwardingModel": "bridged"
                #             },
                #             "bandwidth": 0,
                #             "interfaceType": "10GBASE-T",
                #             "description": "george-michael-oob",
                #             "autoNegotiateActive": true,
                #             "duplex": "duplexUnknown",
                #             "autoNegotigateActive": true,
                #             "linkStatus": "notconnect",
                #             "lineProtocolStatus": "down"
                #         },
                #     }
                # }
                arista_interfaces_info = response.get("result", [])[0]
                formatted_interfaces_info = {
                    k: {
                        "interface_name": k,
                        "interface_type": v.get("interfaceType", ""),
                        "link_status": v.get("linkStatus", ""),
                        "line_protocol_status": v.get("lineProtocolStatus", ""),
                        "mac_addresses": {},
                    }
                    for k, v in dict(
                        sorted(
                            arista_interfaces_info.get("interfaceStatuses", {}).items()
                        )
                    ).items()
                }
        if formatted_interfaces_info:
            formatted_interfaces_info = {
                k: formatted_interfaces_info[k]
                for k in sorted(
                    formatted_interfaces_info.keys(), key=natural_interface_key
                )
            }

        return formatted_interfaces_info

    def get_mac_address_info_via_api(self):
        interface_to_mac_address_info = None
        if (
            self.switch_connection_info
            and self.switch_connection_info["vendor"] == "arista"
        ):
            if response := self.arista_eapi_request_handler("show mac address-table"):
                # {
                #     "multicastTable": {"tableEntries": []},
                #     "unicastTable": {
                #         "tableEntries": [
                #             {
                #                 "macAddress": "20:37:f0:6b:d6:8c",
                #                 "lastMove": 1759519474.903184,
                #                 "interface": "Ethernet46",
                #                 "moves": 1,
                #                 "entryType": "dynamic",
                #                 "vlanId": 1,
                #             },
                #         ]
                #     },
                #     "disabledMacLearningVlans": [],
                # }

                interface_to_mac_address_info = {}
                table_entries = (
                    response.get("result", [])[0]
                    .get("unicastTable", [])
                    .get("tableEntries", [])
                )
                table_entries.sort(key=lambda x: x["lastMove"])

                for entry in table_entries:
                    if entry.get("interface") not in interface_to_mac_address_info:
                        interface_to_mac_address_info[entry.get("interface")] = [entry]
                    else:
                        interface_to_mac_address_info[entry.get("interface")].append(
                            entry
                        )

        return interface_to_mac_address_info

    def get_ip_arp_table_via_api(self):
        ip_to_mac_address_info = {}
        if (
            self.switch_connection_info
            and self.switch_connection_info["vendor"] == "arista"
        ):
            if response := self.arista_eapi_request_handler("show ip arp"):
                table_entries = response.get("result", [])[0].get("ipV4Neighbors", [])
                for entry in table_entries:
                    interface = entry["interface"].split(", ")[
                        1
                    ]  # 'Vlan1, Ethernet46',
                    mac_address = mac_address_manufacturer_style_to_ieee(
                        entry["hwAddress"]
                    )
                    if interface not in ip_to_mac_address_info:
                        ip_to_mac_address_info[interface] = []
                    ip_to_mac_address_info[interface].append(
                        {
                            "ip_address": entry["address"],
                            "mac_address": mac_address,
                            "age": entry["age"],
                        }
                    )
        return ip_to_mac_address_info

    def get_ip_arp_table_via_ip_command(self):
        if does_executable_exist("ip") is False:
            return []

        command = "ip --json neigh show"
        ip_result = None
        with Popen(command.split(" "), stdout=PIPE) as process:
            ip_result = json.loads(process.stdout.read().decode("utf-8"))
        return ip_result

    def get_ip_address_to_mac_address_dict(self):
        arp_table = self.get_ip_arp_table_via_ip_command()
        dest_to_lladdr = {e["dst"]: e.get("lladdr") for e in arp_table if "lladdr" in e}
        return dest_to_lladdr

    def serial_connect(self):
        self.ser = serial.Serial()
        self.ser.port = self.switch_tty_name
        self.ser.baudrate = 9600
        self.ser.open()

    def serial_disconnect(self):
        if self.ser.is_open:
            self.ser.close()

    def send_serial_command(self, command):
        if not self.ser.is_open:
            self.serial_connect()
        self.ser.write(command.encode("utf-8") + b"\n")
        response = self.ser.read_all().decode("utf-8")
        return response

    def get_tty_devices(self):
        tty_devices = list(Path("/dev").glob("tty.*"))
        return [str(device) for device in tty_devices]

    def get_switch_tty_device_name(self):
        if self.switch_tty_name is not None:
            return self.switch_tty_name

        tty_devices = self.get_tty_devices()
        for device in tty_devices:
            if "usbserial" in device or "usbmodem" in device:
                self.switch_tty_name = device
                break
            if "ttyUSB0" in device:
                self.switch_tty_name = device
                break
        return self.switch_tty_name

    def arista_enable_api_via_ssh(self):
        # TODO: implement this function
        return True

    def arista_enable_api_via_tty(self):
        # TODO: implement this function
        return True
        # configure terminal
        # management api http-commands
        # protocol http
        # no protocol https
        # exit
        # write memory

    def enable_switch_api_via_ssh(self):
        if (
            self.switch_connection_info
            and self.switch_connection_info["vendor"] == "arista"
        ):
            return self.arista_enable_api_via_ssh()
        return False

    def enable_switch_api_via_tty(self):
        if (
            self.switch_connection_info
            and self.switch_connection_info["vendor"] == "arista"
        ):
            return self.arista_enable_api_via_tty()
        return False

    def enable_switch_api(self):
        if self.is_switch_ssh_enabled():
            result = self.enable_switch_api_via_ssh()
            return result

        elif self.switch_tty_name or self.get_switch_tty_device_name():
            self.switch_tty_name = (
                self.switch_tty_name or self.get_switch_tty_device_name()
            )
            result = self.enable_switch_api_via_tty()
            return result

        return False

    def push_switch_and_interfaces_info(self, interfaces_info: dict | None = None):
        logger.debug("Pushing switch and interfaces info")
        if self.primitive.messaging.ready and self.switch_connection_info is not None:
            switch_info = self.get_switch_info()
            interfaces_info = interfaces_info or self.get_interfaces_info()

            message = {"switch_info": {}, "interfaces_info": {}}
            if switch_info:
                message["switch_info"] = switch_info
            if interfaces_info:
                message["interfaces_info"] = interfaces_info

            if message:
                self.primitive.messaging.send_message(
                    message_type=MESSAGE_TYPES.SWITCH_AND_INTERFACES_INFO,
                    message=message,
                )
                logger.debug("Switch and interfaces info pushed")
