from rich.console import Console
from rich.table import Table
from rich import box
from typing import Dict, Any

from pypipackagestats.output.utils import humanize_number

console = Console()


def format_package_info(data: Dict[str, Any]) -> None:
    pkg = data["package"]

    console.print(f"\n[bold cyan]{pkg['name']} {pkg['version']}[/bold cyan] [dim]({pkg['upload_time']})[/dim]")
    console.print(f"Description : {pkg['description'] or '(none)'}")
    console.print(f"Author      : {pkg['author'] or '(unknown)'}")
    console.print(f"License     : {pkg['license'] or '(not specified)'}")
    console.print(f"Home page   : {pkg['home_page'] or '(none)'}")
    console.print(f"PyPI        : {pkg['pypi_url']}\n")


def format_download_stats(data: Dict[str, Any]) -> None:
    dl = data["downloads"]

    table = Table(title="Downloads (excluding mirrors)", box=box.ROUNDED)
    table.add_column("Period", style="cyan")
    table.add_column("Downloads", style="green", justify="right")

    table.add_row("Last day", humanize_number(dl["last_day"]))
    table.add_row("Last week", humanize_number(dl["last_week"]))
    table.add_row("Last month", humanize_number(dl["last_month"]))
    table.add_row("Last 180d", humanize_number(dl["last_180d"]))

    console.print(table)
    console.print()


def format_python_versions(data: Dict[str, Any]) -> None:
    versions = data["python_versions"]

    if not versions:
        console.print("[yellow]No Python version data available for last 30 days.[/yellow]\n")
        return

    table = Table(title="Top Python versions (last 30 days)", box=box.ROUNDED)
    table.add_column("Version", style="cyan")
    table.add_column("%", style="yellow", justify="right")
    table.add_column("Downloads", style="green", justify="right")

    for item in versions:
        table.add_row(
            item["version"],
            f"{item['percentage']:.1f}%",
            humanize_number(item["downloads"])
        )

    console.print(table)
    console.print()


def format_os_distribution(data: Dict[str, Any]) -> None:
    systems = data["operating_systems"]

    if not systems:
        console.print("[yellow]No OS distribution data available for last 30 days.[/yellow]")
        return

    table = Table(title="Top operating systems (last 30 days)", box=box.ROUNDED)
    table.add_column("OS", style="cyan")
    table.add_column("%", style="yellow", justify="right")
    table.add_column("Downloads", style="green", justify="right")

    for item in systems:
        table.add_row(
            item["os"],
            f"{item['percentage']:.1f}%",
            humanize_number(item["downloads"])
        )

    console.print(table)
