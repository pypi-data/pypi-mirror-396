import os
import subprocess
from typing import Optional

from gql import Client
from loguru import logger
from rich.logging import RichHandler
from rich.traceback import install

from primitive.messaging.actions import Messaging

from .agent.actions import Agent
from .auth.actions import Auth
from .daemons.actions import Daemons
from .exec.actions import Exec
from .files.actions import Files
from .git.actions import Git
from .hardware.actions import Hardware
from .jobs.actions import Jobs
from .monitor.actions import Monitor
from .network.actions import Network
from .operating_systems.actions import OperatingSystems
from .organizations.actions import Organizations
from .projects.actions import Projects
from .provisioning.actions import Provisioning
from .reservations.actions import Reservations
from .utils.config import read_config_file


class Primitive:
    def __init__(
        self,
        DEBUG: bool = False,
        JSON: bool = False,
        host: Optional[str] = None,
        token: Optional[str] = None,
        transport: Optional[str] = None,
    ) -> None:
        # if no host supplied by user, check the environment variables first
        if host is None:
            # if user didn't supply host and no PRIMITIVE_HOST environment variable
            # use the default production API host
            self.host = os.getenv("PRIMITIVE_HOST", "api.primitive.tech")
        else:
            self.host = host

        # if no host supplied by user, check the environment variables first
        if token is None:
            self.token = os.getenv("PRIMITIVE_TOKEN", None)
        else:
            self.token = token

        # if no host supplied by user, check the environment variables first
        if transport is None:
            self.transport = os.getenv("PRIMITIVE_TRANSPORT", None)
        else:
            self.transport = transport

        self.session: Optional[Client] = None
        self.DEBUG: bool = DEBUG
        self.JSON: bool = JSON

        # Enable tracebacks with local variables
        if self.DEBUG:
            install(show_locals=True)

        # Configure rich logging handler
        rich_handler = RichHandler(
            rich_tracebacks=self.DEBUG,  # Pretty tracebacks
            markup=True,  # Allow Rich markup tags
            show_time=self.DEBUG,  # Show timestamps
            show_level=self.DEBUG,  # Show log levels
            show_path=self.DEBUG,  # Hide source path (optional)
        )

        def formatter(record) -> str:
            match record["level"].name:
                case "ERROR":
                    return "[bold red]Error>[/bold red] {name}:{function}:{line} - {message}"
                case "CRITICAL":
                    return "[italic bold red]Critical>[/italic bold red] {name}:{function}:{line} - {message}"
                case "WARNING":
                    return "[bold yellow]Warning>[/bold yellow] {message}"
                case _:
                    return "[#666666]>[/#666666] {message}"

        logger.remove()
        logger.add(
            sink=rich_handler,
            format="{message}" if self.DEBUG else formatter,
            level="DEBUG" if self.DEBUG else "INFO",
            backtrace=self.DEBUG,
        )

        # Nothing will print here if DEBUG is false
        logger.debug("Debug mode enabled")

        # Generate full or partial host config
        if not token and not transport:
            # Attempt to build host config from file
            try:
                self.get_host_config()
            except KeyError:
                self.host_config = {}
        else:
            self.host_config = {"username": "", "token": token, "transport": transport}

        is_root_user = "uid=0" in subprocess.check_output(["id"]).strip().decode(
            "utf-8"
        )

        self.messaging: Messaging = Messaging(self)

        self.auth: Auth = Auth(self)
        self.organizations: Organizations = Organizations(self)
        self.projects: Projects = Projects(self)
        self.jobs: Jobs = Jobs(self)
        self.files: Files = Files(self)
        self.reservations: Reservations = Reservations(self)
        self.hardware: Hardware = Hardware(self)
        self.agent: Agent = Agent(self)
        self.git: Git = Git(self)
        self.daemons: Daemons = Daemons(self, root_user=is_root_user)
        self.exec: Exec = Exec(self)
        self.provisioning: Provisioning = Provisioning(self)
        self.monitor: Monitor = Monitor(self)
        self.network: Network = Network(self)
        self.operating_systems: OperatingSystems = OperatingSystems(self)

    def get_host_config(self):
        self.full_config = read_config_file()
        self.host_config = self.full_config.get(self.host)

        if not self.host_config:
            raise KeyError(f"Host {self.host} not found in config file.")
