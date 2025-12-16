"""Database utilities for testing with real Friulian databases.

Uses SQLite databases from data/databases/ directory.
"""

import sqlite3
from pathlib import Path


def get_database_paths():
    """Get paths to SQLite database files."""
    base_dir = Path(__file__).parent.parent / "data" / "databases"
    return {
        "words": base_dir / "words.sqlite",
        "frequencies": base_dir / "frequencies.sqlite",
        "errors": base_dir / "errors.sqlite",
        "elisions": base_dir / "elisions.sqlite",
        "radix_tree": base_dir / "words_radix_tree.rt",
    }


def ensure_databases_extracted():
    """Return path to bundled databases."""
    return Path(__file__).parent.parent / "data" / "databases"


def _validate_sqlite(path: Path) -> bool:
    """Validate that a SQLite database file is readable."""
    try:
        with sqlite3.connect(path) as conn:
            conn.execute("SELECT name FROM sqlite_master LIMIT 1")
        return True
    except Exception as exc:
        print(f"Invalid sqlite database {path}: {exc}")
        return False


def verify_database_files():
    """Verify all database files are present and accessible."""
    paths = get_database_paths()

    for _, path in paths.items():
        if not path.exists():
            print(f"Missing database file: {path}")
            return False

        if path.suffix == ".sqlite":
            if not _validate_sqlite(path):
                return False
        elif path.suffix == ".rt":
            try:
                with path.open("rb") as f:
                    header = f.read(10)
                    if len(header) < 10:
                        print(f"Radix tree file too small: {path}")
                        return False
            except Exception as exc:
                print(f"Invalid radix tree file {path}: {exc}")
                return False

    return True
