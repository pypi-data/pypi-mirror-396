from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich import box
from typing import Dict, Any
from pypipackagestats.core.metadata import get_project_metadata
from pypipackagestats.output.utils import normalize_os_name
from pypipackagestats.output.utils import humanize_number
from pypipackagestats.output.utils import humanize_date
from nestedutils import get_path


console = Console()


def format_package_info(data: Dict[str, Any]) -> None:
    pkg = get_path(data, "package")

    console.print(f"\n[bold cyan]{get_path(pkg, 'name')}[/bold cyan]")
    console.print(f"{get_path(pkg, 'description')}")
    console.print(f"Version     : {get_path(pkg, 'version', default='Unknown')}")
    console.print(f"Upload time : {humanize_date(get_path(pkg, 'upload_time')) or 'Unknown'}")
    console.print(f"Author      : {get_path(pkg, 'author', default='Unknown')}")
    console.print(f"License     : {get_path(pkg, 'license', default='Unknown')}")
    console.print(f"Home page   : {get_path(pkg, 'home_page', default='Unknown')}")
    console.print(f"PyPI        : {get_path(pkg, 'pypi_url', default='Unknown')}\n")


def format_download_stats(data: Dict[str, Any]) -> None:
    dl = get_path(data, "downloads")

    table = Table(title="Downloads (excluding mirrors)", box=box.ROUNDED)
    table.add_column("Period", style="cyan")
    table.add_column("Downloads", style="green", justify="right")

    table.add_row("Last day", humanize_number(get_path(dl, "last_day", default=0)))
    table.add_row("Last week", humanize_number(get_path(dl, "last_week", default=0)))
    table.add_row("Last month", humanize_number(get_path(dl, "last_month", default=0)))
    table.add_row("Last 180 days", humanize_number(get_path(dl, "last_180d", default=0)))

    console.print(table)
    console.print()


def format_python_versions(data: Dict[str, Any]) -> None:
    versions = get_path(data, "python_versions")

    if not versions:
        console.print("[yellow]No Python version data available for last 30 days.[/yellow]\n")
        return

    table = Table(title="Top Python versions (last 30 days)", box=box.ROUNDED)
    table.add_column("Version", style="cyan")
    table.add_column("Share", style="yellow", justify="right")
    table.add_column("Downloads", style="green", justify="right")

    for item in versions:
        version = get_path(item, "version") if get_path(item, "version") != "null" else "Unknown"
        table.add_row(
            version,
            f"{get_path(item, 'percentage', default=0):.1f}%",
            humanize_number(get_path(item, "downloads", default=0))
        )

    console.print(table)
    console.print()


def format_os_distribution(data: Dict[str, Any]) -> None:
    systems = get_path(data, "operating_systems")

    if not systems:
        console.print("[yellow]No OS distribution data available for last 30 days.[/yellow]")
        return

    table = Table(title="Top operating systems (last 30 days)", box=box.ROUNDED)
    table.add_column("OS", style="cyan")
    table.add_column("Share", style="yellow", justify="right")
    table.add_column("Downloads", style="green", justify="right")

    for item in systems:
        table.add_row(
            normalize_os_name(get_path(item, "os")),
            f"{get_path(item, 'percentage', default=0):.1f}%",
            humanize_number(get_path(item, "downloads", default=0))
        )

    console.print(table)


def print_project_banner():
    banner_text = Text()
    project_metadata = get_project_metadata()
    
    # ASCII art for "PYPI STATS"
    banner_text.append("\n  _____       _____ _____   _____           _                       _____ _        _       ", style="bold blue")
    banner_text.append("\n |  __ \\     |  __ \\_   _| |  __ \\         | |                     / ____| |      | |      ", style="bold blue")
    banner_text.append("\n | |__) |   _| |__) || |   | |__) |_ _  ___| | ____ _  __ _  ___  | (___ | |_ __ _| |_ ___ ", style="bold blue")
    banner_text.append("\n |  ___/ | | |  ___/ | |   |  ___/ _` |/ __| |/ / _` |/ _` |/ _ \\  \\___ \\| __/ _` | __/ __|", style="bold blue")
    banner_text.append("\n | |   | |_| | |    _| |_  | |  | (_| | (__|   < (_| | (_| |  __/  ____) | || (_| | |_\\__ \\", style="bold blue")
    banner_text.append("\n |_|    \\__, |_|   |_____| |_|   \\__,_|\\___|_|\\_\\__,_|\\__, |\\___| |_____/ \\__\\__,_|\\__|___/", style="bold blue")
    banner_text.append("\n         __/ |                                         __/ |                               ", style="bold blue")
    banner_text.append("\n        |___/                                         |___/                                \n", style="bold blue")
    
    banner_text.append(f"Version : {project_metadata.version}\n", style="bold blue")
    banner_text.append(f"Author  : {project_metadata.author} ({project_metadata.author_url})\n", style="magenta")
    banner_text.append(f"Repo    : {project_metadata.repository_url}\n", style="green")
    
    console.print(Panel(banner_text, expand=False, border_style="blue", title="Welcome", title_align="left"))
