from pathlib import Path

from rich.prompt import Prompt

from oko.service.service_config import load_config
from oko.service.service_collection import (
    create_collection,
    list_collections,
)
from oko.ui.prints import (
    print_success,
    print_error,
    print_info_panel,
    print_kv,
    print_header,
    print_table,
)


def add_collection(name: str | None = None):
    """
    Adds a new collection to OKO.
    """
    try:
        config = load_config()
        oko_root = Path(config["root_path"])

        if not name:
            name = Prompt.ask("[prompt]Collection name[/prompt]")

        path = create_collection(oko_root, name)

        print_success(
            f"Collection [highlight]{name}[/highlight] created at:\n"
            f"[info]{path}[/info]",
            title="Collection Added",
        )

    except Exception as e:
        print_error(str(e), title="Collection Error")


def list_collections_cmd():
    """
    Lists existing collections.
    """
    try:
        config = load_config()
        oko_root = Path(config["root_path"])

        collections = list_collections(oko_root)

        print_header("Collections")

        if not collections:
            print_info_panel(
                "No collections found.\n"
                "Use [secondary]oko add collection <name>[/secondary] to create one.",
                title="Empty",
            )
            return

        rows = [[col["name"], col["path"]] for col in collections]

        print_table(
            title="List of Collections",
            columns=["Alias", "Path"],
            rows=rows,
        )

    except Exception as e:
        print_error(str(e), title="Collection Error")
