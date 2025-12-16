from rich.console import Console
from rich.table import Table


def render_ports_table(ports_dict: dict = {}) -> None:
    console = Console()

    table = Table(show_header=True, header_style="bold #FFA800")
    table.add_column("Port")
    table.add_column("Status")
    table.add_column("MAC Address | IP | VLAN")

    for k, v in ports_dict.items():
        table.add_row(
            k,
            v.get("link_status"),
            "\n".join(
                [
                    f"{key} | {values.get('ip_address')} | VLAN {values.get('vlan')}"
                    for key, values in v.get("mac_addresses", {}).items()
                ]
            ),
        )

    console.print(table)
