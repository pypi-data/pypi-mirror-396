from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.box import ROUNDED
from .theme import custom_theme

console = Console(theme=custom_theme)


def print_header(title: str):
    """Prints a section header using secondary color."""
    console.rule(f"[title]{title}[/title]", style="title")
    console.print()


def print_section(title: str, content: str):
    """Prints content inside a pretty styled panel."""
    console.print(
        Panel(
            f"[output]{content}[/output]",
            title=f"[accent]{title}[/accent]",
            border_style="secondary",
            padding=1,
        )
    )


def print_kv(key: str, value: str):
    """Consistent key-value printing."""
    console.print(f"[label]{key}: [/label][value]{value}[/value]")


def print_success(message: str, title: str = "Success"):
    console.print(
        Panel(
            f"[success]{message}[/success]",
            title=f"[success]{title}[/success]",
            border_style="success",
            expand=False,
            padding=1,
        )
    )


def print_error(message: str, title: str = "Error"):
    console.print(
        Panel(
            f"[error]{message}[/error]",
            title=f"[error]{title}[/error]",
            border_style="error",
            expand=False,
            padding=1,
        )
    )


def print_warning(message: str, title: str = "Warning"):
    console.print(
        Panel(
            f"[warning]{message}[/warning]",
            title=f"[warning]{title}[/warning]",
            border_style="warning",
            expand=False,
            padding=1,
        )
    )


def print_info_panel(message: str, title: str = "Info"):
    console.print(
        Panel(
            f"[info]{message}[/info]",
            title=f"[info]{title}[/info]",
            border_style="info",
            expand=False,
            padding=1,
        )
    )


def print_table(
    title: str,
    columns: list[str],
    rows: list[list[str]],
):
    table = Table(
        title=title,
        box=ROUNDED,
        show_header=True,
        header_style="title",
        style="primary",
    )

    for col in columns:
        table.add_column(col, style="white", no_wrap=True)

    for row in rows:
        table.add_row(*row)

    console.print(table)
