from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Union

STAMP_FILENAME = "directory_stemp.json"


@dataclass(frozen=True)
class StampData:
    hash: str
    date: str


def _iter_relative_paths(directory_path: Path) -> list[str]:
    """
    Collect all relative paths (files + directories) in a deterministic order.
    The stamp file in the directory root is excluded.
    """
    paths: list[str] = []

    root_str = str(directory_path)

    for root, dirs, files in os.walk(root_str):
        dirs.sort()
        files.sort()

        for name in dirs + files:
            # Ignore stamp file only if it is in the root directory
            if Path(root) == directory_path and name == STAMP_FILENAME:
                continue

            abs_path = Path(root) / name
            rel_path = abs_path.relative_to(directory_path).as_posix()
            paths.append(rel_path)

    paths.sort()
    return paths


def generate_directory_hash(directory_path: Union[str, Path]) -> str | int:
    """
    Generate a SHA-256 hash based on the directory's structure (relative paths).
    Returns:
      - hex digest string on success
      - -1 if directory does not exist
    """
    directory = Path(directory_path)

    if not directory.exists():
        print("Directory does not exist.")
        return -1

    sha_hash = hashlib.sha256()

    for rel_path in _iter_relative_paths(directory):
        sha_hash.update(rel_path.encode("utf-8"))

    print(f"Generated hash for directory: {directory}")
    return sha_hash.hexdigest()


def create_stamp_file(directory_path: Union[str, Path]) -> None:
    """
    Create the stamp file in the directory root.
    Exits with code 2 if the stamp file already exists.
    Exits with code 3 if the target is missing or not a directory.
    """
    directory = Path(directory_path)

    if not directory.is_dir():
        print("Directory does not exist or is not a directory.")
        raise SystemExit(3)

    stamp_path = directory / STAMP_FILENAME

    if stamp_path.exists():
        print("Error: Stamp file already exists.")
        raise SystemExit(2)

    hash_value = generate_directory_hash(directory)
    if hash_value == -1:
        # Defensive: never write a broken stamp
        raise SystemExit(3)

    data = StampData(hash=str(hash_value), date=datetime.now().isoformat())

    stamp_path.write_text(json.dumps({"hash": data.hash, "date": data.date}))
    print("Stamp file created.")


def validate(directory_path: Union[str, Path]) -> None:
    """
    Validate the directory stamp.
    Exits with:
      - 0 if valid
      - 1 if invalid
      - 3 if directory is missing/not a directory, or stamp file not found
    """
    directory = Path(directory_path)

    if not directory.is_dir():
        print("Directory does not exist or is not a directory.")
        raise SystemExit(3)

    stamp_path = directory / STAMP_FILENAME

    if not stamp_path.exists():
        print("Stamp file not found.")
        raise SystemExit(3)

    stemp_data = json.loads(stamp_path.read_text())
    current_hash = generate_directory_hash(directory)

    if current_hash == stemp_data.get("hash"):
        print("Validation successful. The hash value matches.")
        raise SystemExit(0)

    print("Validation failed. The hash value does not match.")
    raise SystemExit(1)
