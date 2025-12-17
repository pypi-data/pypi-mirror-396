import json
import typer
from rich.json import JSON
from rich.console import Console
from oko.service.service_endpoint import add_endpoint, run_endpoint, list_endpoints
from oko.ui.formatters import format_http_method, format_status_code
from oko.ui.prints import (
    print_section,
    print_success,
    print_error,
    print_header,
    print_table,
    print_info_panel,
)
from oko.ui.theme import custom_theme

app = typer.Typer(help="Manage endpoints")

console = Console(theme=custom_theme)


@app.command("add")
def add_endpoint_cmd(
    collection: str = typer.Argument(..., help="Collection name"),
    alias: str = typer.Argument(..., help="Endpoint alias"),
    url: str = typer.Argument(..., help="Endpoint URL"),
    method: str = typer.Option("GET", "--method", "-m", help="HTTP method"),
):
    """
    Add a new endpoint to a collection
    """
    try:
        add_endpoint(collection, alias, url, method)

        formatted_method = format_http_method(method)

        success_message = (
            f"Endpoint added successfully\n\n"
            f"[bold]Collection:[/bold] [primary]{collection}[/primary]\n"
            f"[bold]Alias:[/bold] [primary]{alias}[/primary]\n"
            f"[bold]Method:[/bold] {formatted_method}\n"
            f"[bold]URL:[/bold] [primary]{url}[/primary]"
        )

        print_success(success_message, title="Endpoint Created")

    except Exception as e:
        print_error(str(e), title="Error")


def list_endpoints_cmd(collection: str = typer.Argument(..., help="Collection name")):
    """
    List endpoints in a collection.
    """
    try:
        endpoints = list_endpoints(collection)

        print_header(f"Endpoints · {collection}")

        if not endpoints:
            print_info_panel(
                "No endpoints found in this collection.\n"
                "Use [secondary]oko endpoint add[/secondary] to create one.",
                title="Empty",
            )
            return

        rows = [[ep["alias"], ep["method"], ep["url"]] for ep in endpoints]

        print_table(
            title="Defined Endpoints",
            columns=["Alias", "Method", "URL"],
            rows=rows,
        )

    except Exception as e:
        print_error(str(e), title="Endpoint Error")


def _parse_kv(items: list[str]) -> dict:
    """
    Parse key=value pairs from CLI.
    """
    parsed = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"Invalid format '{item}'. Expected key=value")
        key, value = item.split("=", 1)
        parsed[key] = value
    return parsed


def endpoint_run_cmd(
    collection: str = typer.Argument(..., help="Collection name"),
    alias: str = typer.Argument(..., help="Endpoint alias"),
    params: list[str] = typer.Option(
        None, "--param", "-p", help="Query parameters (key=value)"
    ),
    headers: list[str] = typer.Option(
        None, "--header", "-H", help="Headers (key=value)"
    ),
    json_body: str = typer.Option(None, "--json", help="JSON body as string"),
):
    """
    Run an endpoint.
    """
    try:
        print_header("Details Endpoint")

        with console.status(
            "[secondary]Sending request...[/secondary]", spinner="dots"
        ):
            response = run_endpoint(
                collection=collection,
                alias=alias,
                params=_parse_kv(params) if params else None,
                headers=_parse_kv(headers) if headers else None,
                json_body=json.loads(json_body) if json_body else None,
            )

        # ── Metadata ───────────────────────────────
        status = format_status_code(response.status_code)
        method = format_http_method(response.request.method)
        print_section(
            "Response Metadata",
            (
                f"[label]Status:[/label] {status}\n"
                f"[label]Method:[/label] {method}\n"
                f"[label]URL:[/label] [value]{response.request.url}[/value]"
            ),
        )

        # ── Body ───────────────────────────────
        content_type = response.headers.get("content-type", "")

        if "application/json" in content_type:
            console.print(JSON.from_data(response.json()))
        else:
            console.print(response.text)

    except Exception as e:
        print_error(str(e), title="Error")
