import platform
import typing
from pathlib import Path
from typing import Dict, List, Optional, TypedDict

if typing.TYPE_CHECKING:
    from ..client import Primitive

from ..utils.daemons import Daemon
from .launch_agents import LaunchAgent
from .launch_service import LaunchService

HOME_DIRECTORY = Path.home()


class DaemonInfo(TypedDict):
    default: bool
    daemon: Daemon


class Daemons:
    def __init__(self, primitive, root_user: bool = False) -> None:
        self.primitive: Primitive = primitive
        command_flags = ""

        if primitive.host != "api.primitive.tech":
            command_flags += f"--host {primitive.host} "
        if primitive.DEBUG:
            command_flags += "--debug "
        self.os_family = platform.system()

        match self.os_family:
            case "Darwin":
                self.daemons: Dict[str, DaemonInfo] = {
                    "agent": {
                        "default": True,
                        "daemon": LaunchAgent(
                            label="tech.primitive.agent",
                            command=f"{command_flags} agent",
                        ),
                    },
                    "monitor": {
                        "default": True,
                        "daemon": LaunchAgent(
                            label="tech.primitive.monitor",
                            command=f"{command_flags} monitor",
                        ),
                    },
                }
            case "Linux":
                self.daemons: Dict[str, DaemonInfo] = {
                    "agent": {
                        "default": True,
                        "daemon": LaunchService(
                            label="tech.primitive.agent",
                            command=f"{command_flags} agent",
                            root_user=root_user,
                        ),
                    },
                    "monitor": {
                        "default": True,
                        "daemon": LaunchService(
                            label="tech.primitive.monitor",
                            command=f"{command_flags} monitor",
                            root_user=root_user,
                        ),
                    },
                    "webserver": {
                        "default": False,
                        "daemon": LaunchService(
                            label="tech.primitive.webserver",
                            command=f"{command_flags} webserver",
                            root_user=root_user,
                        ),
                    },
                }
            case _:
                raise NotImplementedError(f"{self.os_family} is not supported.")

    def install(self, name: Optional[str]) -> bool:
        if name:
            return self.daemons[name]["daemon"].install()
        else:
            return all(
                [
                    daemon["daemon"].install() if daemon["default"] else True
                    for daemon in self.daemons.values()
                ]
            )

    def uninstall(self, name: Optional[str]) -> bool:
        if name:
            return self.daemons[name]["daemon"].uninstall()
        else:
            return all(
                [daemon["daemon"].uninstall() for daemon in self.daemons.values()]
            )

    def stop(self, name: Optional[str]) -> bool:
        if name:
            return self.daemons[name]["daemon"].stop()
        else:
            return all([daemon["daemon"].stop() for daemon in self.daemons.values()])

    def start(self, name: Optional[str]) -> bool:
        if name:
            return self.daemons[name]["daemon"].start()
        else:
            return all([daemon["daemon"].start() for daemon in self.daemons.values()])

    def list(self) -> List[Daemon]:
        """List all daemons"""
        return list(daemon["daemon"] for daemon in self.daemons.values())

    def logs(self, name: str) -> None:
        self.daemons[name]["daemon"].view_logs()
