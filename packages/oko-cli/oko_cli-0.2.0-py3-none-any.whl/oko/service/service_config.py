import json
from datetime import datetime
from pathlib import Path


def create_oko_folder(mode: str, custom_path: str | None = None) -> Path:
    """
    Crea la carpeta .oko según el modo seleccionado.

    mode:
        - "project": crea .oko en el directorio actual
        - "global": crea ~/.oko/
        - "custom": crea .oko dentro de custom_path

    custom_path:
        Solo se usa si mode = "custom".
    """

    if mode not in ("project", "global", "custom"):
        raise ValueError("mode must be 'project', 'global', or 'custom'")

    # 1. Modo proyecto → carpeta actual
    if mode == "project":
        base = Path.cwd() / ".oko"

    # 2. Modo global → home
    elif mode == "global":
        base = Path("~/.oko").expanduser()

    # 3. Modo custom → dentro del path que te den
    else:  # custom
        if not custom_path:
            raise ValueError("custom_path is required when mode='custom'")
        base = Path(custom_path).expanduser() / ".oko"

    # Crear carpeta
    base.mkdir(parents=True, exist_ok=True)

    return base


def create_config_file(
    oko_root: Path,
    install_type: str,
    project_name: str | None = None,
) -> Path:
    config_path = oko_root / "config.json"

    if project_name is None:
        project_name = oko_root.parent.name

    config = {
        "schema_version": "1.0",
        "install_type": install_type,
        "project_name": project_name,
        "root_path": str(oko_root.resolve()),
        "created_at": datetime.now().isoformat(),
    }

    config_path.write_text(json.dumps(config, indent=2))
    return config_path


def check_existing_oko():
    """
    Checks if a .oko directory exists in either:
    - the current working directory
    - the user's home directory (~/.oko)

    Returns a dict:
    {
        "exists": bool,
        "path": str or None,
        "type": "project" | "global" | None
    }
    """
    # 1. Check project folder (current directory)
    project_path = Path.cwd() / ".oko"
    if project_path.exists() and project_path.is_dir():
        return {"exists": True, "path": str(project_path.resolve()), "type": "project"}

    # 2. Check global folder (~/.oko)
    global_path = Path.home() / ".oko"
    if global_path.exists() and global_path.is_dir():
        return {
            "exists": True,
            "path": str(global_path.expanduser().resolve()),
            "type": "global",
        }

    # 3. No existing configuration
    return {"exists": False, "path": None, "type": None}


def load_config() -> dict:
    """
    Loads OKO configuration.

    Search order:
    1. Project config: .oko/config.json
    2. Global config: ~/.oko/config.json

    Returns:
        dict: config content

    Raises:
        FileNotFoundError: if no config is found
        ValueError: if config is invalid JSON
    """
    # 1. Project config
    project_config = Path.cwd() / ".oko" / "config.json"
    if project_config.exists():
        return _read_config(project_config)

    # 2. Global config
    global_config = Path.home() / ".oko" / "config.json"
    if global_config.exists():
        return _read_config(global_config)

    raise FileNotFoundError("No OKO configuration found. Run 'oko init' first.")


def _read_config(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid config file at {path}") from e
