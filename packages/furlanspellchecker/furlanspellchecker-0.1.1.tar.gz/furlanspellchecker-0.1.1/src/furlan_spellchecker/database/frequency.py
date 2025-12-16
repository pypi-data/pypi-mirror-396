"""
Frequency database for Friulian word frequency-based suggestion ranking.

This module implements frequency database functionality from COF,
which contains ~69,000 word frequency entries for prioritizing
spelling suggestions based on word usage frequency.

Uses SQLite format exclusively.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from .interfaces import IFrequencyDatabase

# ============================================================================
# SQLite Implementation
# ============================================================================


class FrequencyDatabaseSQLite(IFrequencyDatabase):
    """SQLite-based frequency database with in-memory caching."""

    def __init__(self, db_path: str | Path) -> None:
        """
        Initialize frequency database.

        Args:
            db_path: Path to SQLite database containing frequency data
        """
        self.db_path = Path(db_path) if isinstance(db_path, str) else db_path
        self._connection: sqlite3.Connection | None = None
        # Lazy-loaded full frequency cache (~2MB for 69K entries)
        self._freq_cache: dict[str, int] | None = None
        self._loaded = False

    def _ensure_loaded(self) -> None:
        """Load entire frequency table into memory on first access."""
        if self._loaded:
            return

        if not self.db_path.exists():
            raise FileNotFoundError(f"Frequency database not found: {self.db_path}")

        conn = sqlite3.connect(str(self.db_path))
        try:
            cursor = conn.execute("SELECT Key, Value FROM Data")
            self._freq_cache = {}
            for key, value in cursor:
                if key and value is not None:
                    self._freq_cache[key] = int(value)
        finally:
            conn.close()

        self._loaded = True

    def get_frequency(self, word: str) -> int:
        """
        Get frequency score for word.

        Equivalent to COF's $self->data->get_freq->{$word} || 0

        Args:
            word: Friulian word to lookup

        Returns:
            Frequency score (0 if word not found)
            Higher numbers = more frequent words

        Examples:
            >>> db.get_frequency("di")     # Most common word
            255
            >>> db.get_frequency("furlan") # Common word
            192
            >>> db.get_frequency("blablabla") # Unknown
            0
        """
        if not word:
            return 0

        self._ensure_loaded()
        return self._freq_cache.get(word, 0) if self._freq_cache is not None else 0

    def rank_suggestions(self, suggestions: list[str]) -> list[tuple[str, int]]:
        """Rank suggestions by frequency score."""
        ranked = []
        for suggestion in suggestions:
            frequency = self.get_frequency(suggestion)
            ranked.append((suggestion, frequency))

        ranked.sort(key=lambda x: (-x[1], x[0]))
        return ranked

    def has_word(self, word: str) -> bool:
        """Check if word has a frequency entry (even if NULL)."""
        if not word:
            return False

        self._ensure_loaded()
        return self._freq_cache is not None and word in self._freq_cache

    def close(self) -> None:
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
        if self._freq_cache is not None:
            self._freq_cache.clear()
        self._loaded = False
