from dataclasses import dataclass


@dataclass
class P_CLI_200(Exception):
    """Operating System Already Exists"""

    codename: str = "P_CLI_200"
    message: str = "Operating System Already Exists"

    def __str__(self):
        return f"{self.codename}: {self.message}"


@dataclass
class P_CLI_201(Exception):
    """Operating System Not Found"""

    codename: str = "P_CLI_201"
    message: str = "Operating System Not Found"

    def __str__(self):
        return f"{self.codename}: {self.message}"
