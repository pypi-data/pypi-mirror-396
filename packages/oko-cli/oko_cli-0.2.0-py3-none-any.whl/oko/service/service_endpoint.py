import re
import httpx
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any, List

from oko.service.service_config import load_config
from oko.service.service_variable import load_variables

SUPPORTED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}

_VARIABLE_PATTERN = re.compile(r"\{\{\s*([a-zA-Z0-9_.]+)\s*\}\}")


def add_endpoint(
    collection_name: str,
    alias: str,
    url: str,
    method: str = "GET",
) -> Path:
    config = load_config()
    root = Path(config["root_path"])

    method = method.upper()

    if method not in SUPPORTED_METHODS:
        raise ValueError(
            f"Unsupported HTTP method '{method}'. "
            f"Supported methods: {', '.join(SUPPORTED_METHODS)}"
        )

    collection_path = root / "collections" / collection_name
    if not collection_path.exists():
        raise FileNotFoundError(f"Collection '{collection_name}' does not exist")

    endpoints_file = collection_path / "endpoints.json"

    if endpoints_file.exists():
        data = json.loads(endpoints_file.read_text())
    else:
        data = {"endpoints": {}}

    if alias in data["endpoints"]:
        raise ValueError(
            f"Endpoint '{alias}' already exists in collection '{collection_name}'"
        )

    data["endpoints"][alias] = {
        "url": url,
        "method": method,
        "created_at": datetime.now().isoformat(),
    }

    endpoints_file.write_text(json.dumps(data, indent=2))
    return endpoints_file


def list_endpoints(collection_name: str) -> List[Dict[str, str]]:
    """
    Lists endpoints for a given collection.

    Returns:
        [
            {
                "alias": "login",
                "method": "POST",
                "url": "https://..."
            }
        ]
    """
    config = load_config()
    root = Path(config["root_path"])

    collection_path = root / "collections" / collection_name
    if not collection_path.exists():
        raise FileNotFoundError(f"Collection '{collection_name}' does not exist")

    endpoints_file = collection_path / "endpoints.json"
    if not endpoints_file.exists():
        return []

    data = json.loads(endpoints_file.read_text())
    endpoints = data.get("endpoints", {})

    results = []
    for alias, meta in endpoints.items():
        results.append(
            {
                "alias": alias,
                "method": meta.get("method", ""),
                "url": meta.get("url", ""),
            }
        )

    return results


def run_endpoint(
    collection: str,
    alias: str,
    params: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None,
    json_body: Optional[Dict] = None,
    timeout: int = 10,
) -> httpx.Response:
    # 1. Load config
    config = load_config()
    root = Path(config["root_path"])

    # 2. Validate collection
    collection_path = root / "collections" / collection
    if not collection_path.exists():
        raise FileNotFoundError(f"Collection '{collection}' does not exist")

    # 3. Load endpoints
    endpoints_file = collection_path / "endpoints.json"
    if not endpoints_file.exists():
        raise FileNotFoundError(f"No endpoints defined for collection '{collection}'")

    data = json.loads(endpoints_file.read_text())

    if alias not in data.get("endpoints", {}):
        raise ValueError(f"Endpoint '{alias}' not found in collection '{collection}'")

    endpoint = data["endpoints"][alias]

    # 4. Load variables
    variables = load_variables()

    # 5. Resolve variables
    url = resolve_variables(endpoint["url"], variables)
    params = resolve_variables(params, variables) if params else None
    headers = resolve_variables(headers, variables) if headers else None
    json_body = resolve_variables(json_body, variables) if json_body else None

    # 6. Execute request
    response = httpx.request(
        method=endpoint["method"],
        url=url,
        params=params,
        headers=headers,
        json=json_body,
        timeout=timeout,
    )

    return response


def resolve_variables(value: Any, variables: dict) -> Any:
    """
    Recursively resolves variables in strings, dicts, and lists.

    Supported syntax:
        {{var}}
        {{user.id}}

    Args:
        value: Any value (str, dict, list, etc.)
        variables: Dict of available variables

    Returns:
        Value with resolved variables
    """

    if isinstance(value, str):
        return _resolve_string(value, variables)

    if isinstance(value, dict):
        return {key: resolve_variables(val, variables) for key, val in value.items()}

    if isinstance(value, list):
        return [resolve_variables(item, variables) for item in value]

    # Any other type (int, float, bool, None)
    return value


def _resolve_string(text: str, variables: dict) -> str:
    def replacer(match):
        path = match.group(1)
        resolved = _get_variable_value(path, variables)

        # If variable not found → keep original {{var}}
        return str(resolved) if resolved is not None else match.group(0)

    return _VARIABLE_PATTERN.sub(replacer, text)


def _get_variable_value(path: str, variables: dict) -> Any:
    """
    Resolves dotted variable paths like:
        token
        user.id
        user.profile.email
    """
    parts = path.split(".")
    current = variables

    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None

    return current
