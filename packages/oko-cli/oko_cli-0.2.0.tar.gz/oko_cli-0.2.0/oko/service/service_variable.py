from pathlib import Path
import json

from oko.service.service_config import load_config


def _save_config(config: dict) -> None:
    """
    Persists the updated config.json to disk.
    """
    config_path = Path(config["root_path"]) / "config.json"
    config_path.write_text(json.dumps(config, indent=2))


def add_variable(key: str, value: str) -> None:
    """
    Adds or updates a variable in config.json.
    """
    if not key:
        raise ValueError("Variable key cannot be empty")

    config = load_config()

    variables = config.get("variables", {})
    variables[key] = value

    config["variables"] = variables
    _save_config(config)


def delete_variable(key: str) -> None:
    """
    Deletes a variable from config.json.
    """
    config = load_config()
    variables = config.get("variables", {})

    if key not in variables:
        raise KeyError(f"Variable '{key}' does not exist")

    del variables[key]
    config["variables"] = variables
    _save_config(config)


def load_variables() -> dict:
    """
    Returns all variables from config.json.
    """
    config = load_config()
    return config.get("variables", {})
