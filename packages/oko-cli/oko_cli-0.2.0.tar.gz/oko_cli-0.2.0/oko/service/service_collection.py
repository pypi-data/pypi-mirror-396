import json
from datetime import datetime, timezone
from pathlib import Path

# TODO:
# rename -> Renombrar carpeta
# delete -> Eliminar carpeta
# Implementar cuando endpoints tenga funcionando ->  add, list, y run este listo


def create_collection(oko_root: Path, name: str) -> Path:
    """
    Creates a collection structure:

    .oko/
      collections/
        <name>/
          collection.json
    """

    if not name or not name.strip():
        raise ValueError("Collection name cannot be empty")

    collections_dir = oko_root / "collections"
    collection_dir = collections_dir / name

    if collection_dir.exists():
        raise FileExistsError(f"Collection '{name}' already exists")

    # create directories
    collection_dir.mkdir(parents=True)

    # collection.json (metadata only)
    collection_meta = {
        "name": name,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    (collection_dir / "collection.json").write_text(
        json.dumps(collection_meta, indent=2),
        encoding="utf-8",
    )

    return collection_dir


def list_collections(oko_root: Path) -> list[dict]:
    """
    Lists all collections in the OKO project.

    Returns:
        [
            {
                "name": str,
                "path": str
            }
        ]
    """
    collections_dir = oko_root / "collections"

    if not collections_dir.exists():
        return []

    collections = []

    for item in collections_dir.iterdir():
        if not item.is_dir():
            continue

        collection_file = item / "collection.json"
        if not collection_file.exists():
            continue  # ignore invalid collections

        try:
            data = json.loads(collection_file.read_text(encoding="utf-8"))
            collections.append(
                {
                    "name": data.get("name", item.name),
                    "path": str(item.resolve()),
                }
            )
        except Exception:
            continue  # ignore broken collections

    return collections
