from rich.console import Console
from rich.table import Table


def render_files_table(file_list) -> None:
    console = Console()

    table = Table(show_header=True, header_style="bold #FFA800")
    table.add_column("File Name")
    table.add_column("File ID")
    table.add_column("File Size (bytes)", justify="right")

    for file in file_list:
        file_name = file.get("fileName")
        file_id = file.get("id")
        file_size = file.get("fileSize")

        table.add_row(
            file_name,
            file_id,
            file_size,
        )

    console.print(table)


def file_status_string(file) -> str:
    if file.get("isQuarantined"):
        return "Quarantined"
    if not file.get("isOnline"):
        return "Offline"
    if not file.get("isHealthy"):
        return "Not healthy"
    if not file.get("isAvailable"):
        return "Not available"
    else:
        return "Available"
