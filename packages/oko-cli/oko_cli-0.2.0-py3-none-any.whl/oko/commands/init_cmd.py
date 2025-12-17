from rich.prompt import Prompt
from oko.ui.prints import (
    print_error,
    print_header,
    print_section,
    print_kv,
    print_success,
    print_warning,
)
from oko.ui.theme import custom_theme
from oko.ui.logo import print_logo
from oko.service.service_config import (
    check_existing_oko,
    create_config_file,
    create_oko_folder,
)
from rich.console import Console

console = Console(theme=custom_theme)


def init_project():
    print_logo()
    print_header("Welcome to OKO - CLI")

    # 1. Check existing configuration
    existing = check_existing_oko()

    if existing["exists"]:
        warning_message = (
            f"[label]Configuration already exists at:[/label] [value]{existing['path']}[/value]\n"
            f"[label]Type:[/label] [value]{existing['type']}[/value]"
        )
        print_warning(warning_message, title="Configuration Detected")

        confirm = Prompt.ask(
            "[label]Do you want to reinitialize the project?[/label]",
            choices=["y", "n"],
            default="n",
        )

        if confirm == "n":
            print_error("Operation cancelled", title="Status")
            return

    # 2. Display options
    options = [
        {"key": "project", "label": "In this project (.oko/)", "path": ".oko/"},
        {"key": "global", "label": "In your home folder (~/.oko/)", "path": "~/.oko/"},
        {"key": "custom", "label": "Specify a custom path", "path": None},
    ]

    options_message = (
        "[prompt]Where would you like to save this project?[/prompt]\n\n"
        "[bold]Options:[/bold]\n"
        + "\n".join(
            f"  • [info]{idx}[/info]. {opt['label']}"
            for idx, opt in enumerate(options, 1)
        )
    )

    print_section("Location", options_message)

    # 3. User selection
    choice = Prompt.ask(
        "[label]\nSelect an option[/label]", choices=["1", "2", "3"], default="2"
    )

    selected = options[int(choice) - 1]

    print_kv("Selected", selected["label"])

    # 4. Handle custom path
    if selected["key"] == "custom":
        custom_path = Prompt.ask("[prompt]\nEnter the custom path[/prompt]")
        selected["path"] = custom_path
        location = create_oko_folder("custom", selected["path"])
    else:
        location = create_oko_folder(selected["key"])

    # 5. Create config.json
    create_config_file(oko_root=location, install_type=selected["key"])

    # 6. Final success message
    success_message = (
        f"Configuration saved at: [info]{location}[/info]\n\n"
        "[bold]Next steps:[/bold]\n"
        "  • Add a collection: [secondary]oko collection add <alias>[/secondary]\n"
        "  • Add an endpoint: [secondary]oko endpoint add <alias> <url>[/secondary]\n"
        "  • Run an endpoint: [secondary]oko run <alias>[/secondary]"
    )

    print_success(success_message, title="OKO Initialization Successfully")
