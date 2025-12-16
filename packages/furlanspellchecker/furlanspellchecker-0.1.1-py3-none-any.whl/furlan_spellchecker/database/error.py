"""
Error patterns database for common Friulian spelling corrections.

This module implements error pattern database functionality from COF,
which contains ~300 entries for spacing and apostrophe corrections
(NOT phonetic corrections - those are handled by phonetic algorithm + RadixTree).

Uses SQLite format exclusively.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from .interfaces import IErrorDatabase

# ============================================================================
# SQLite Implementation
# ============================================================================


class ErrorDatabaseSQLite(IErrorDatabase):
    """SQLite-based error patterns database."""

    def __init__(self, db_path: str | Path) -> None:
        """
        Initialize error patterns database.

        Args:
            db_path: Path to SQLite database containing error patterns
        """
        self.db_path = Path(db_path) if isinstance(db_path, str) else db_path
        self._connection: sqlite3.Connection | None = None
        self._error_cache: dict[str, str] = {}

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection (lazy initialization)."""
        if self._connection is None:
            if not self.db_path.exists():
                raise FileNotFoundError(f"Error database not found: {self.db_path}")

            self._connection = sqlite3.connect(str(self.db_path))
            self._connection.row_factory = sqlite3.Row

        return self._connection

    def get_correction(self, error_word: str) -> str | None:
        """
        Get error correction for word if it exists.

        Equivalent to COF's errors database lookup in _find_in_exc().

        Args:
            error_word: Potentially incorrect word

        Returns:
            Corrected word if pattern exists, None otherwise

        Examples:
            >>> db.get_correction("un'")
            "une"
            >>> db.get_correction("bench├®")
            "ben che"
            >>> db.get_correction("furla")  # phonetic, not in errors.db
            None
        """
        if not error_word:
            return None

        # Check cache first
        if error_word in self._error_cache:
            correction = self._error_cache[error_word]
            return correction if correction else None

        conn = self._get_connection()

        # Try exact match first
        cursor = conn.execute("SELECT Value FROM Data WHERE Key = ? LIMIT 1", (error_word,))
        result = cursor.fetchone()

        if result and result["Value"]:
            correction = result["Value"]
            self._error_cache[error_word] = correction
            return str(correction)

        # Cache negative result
        self._error_cache[error_word] = ""
        return None

    def has_error(self, error_word: str) -> bool:
        """Check if error has a correction entry."""
        return self.get_correction(error_word) is not None

    def close(self) -> None:
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
        self._error_cache.clear()
