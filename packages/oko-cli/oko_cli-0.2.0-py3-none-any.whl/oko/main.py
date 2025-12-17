import typer
from oko.commands.endpoint_cmd import (
    add_endpoint_cmd,
    endpoint_run_cmd,
    list_endpoints_cmd,
)
from oko.commands.init_cmd import init_project
from oko.commands.collection_cmd import add_collection, list_collections_cmd
from oko.commands.variable_cmd import variable_add, variable_delete, variable_list

app = typer.Typer(help="OKO - API testing made simple", no_args_is_help=True)
add_app = typer.Typer(help="Add resources to OKO")

collection_app = typer.Typer(help="Manage Collections")
endpoint_app = typer.Typer(help="Manage Endpoints")
variable_app = typer.Typer(help="Manage Variables")

# ── Root commands ────────────────────────────────


@app.command("init")
def init():
    """Initialize a new project"""
    init_project()


# ── Collection commands ───────────────────────────────
@collection_app.command("add")
def collection_add(name: str = typer.Argument(None)):
    """Add a new collection"""
    add_collection(name)


@collection_app.command("list")
def collection_list():
    """List all collections"""
    list_collections_cmd()


# ── Endpoints commands ───────────────────────────────
endpoint_app.command("add")(add_endpoint_cmd)
endpoint_app.command("run")(endpoint_run_cmd)
endpoint_app.command("list")(list_endpoints_cmd)

# ── Variable commands ─────────────────────────────────
variable_app.command("add")(variable_add)
variable_app.command("list")(variable_list)
variable_app.command("delete")(variable_delete)

app.add_typer(collection_app, name="collection")
app.add_typer(endpoint_app, name="endpoint")
app.add_typer(variable_app, name="variable")


if __name__ == "__main__":
    app()
