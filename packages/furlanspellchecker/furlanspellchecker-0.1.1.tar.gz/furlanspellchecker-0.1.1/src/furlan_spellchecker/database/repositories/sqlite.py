"""SQLite repository implementations with optimized read performance."""

import sqlite3
from pathlib import Path

from .base import (
    IElisionRepository,
    IErrorRepository,
    IFrequencyRepository,
    IPhoneticRepository,
)

# SQLite PRAGMA optimizations for read-heavy workloads
SQLITE_PRAGMAS = [
    "PRAGMA journal_mode=WAL",
    "PRAGMA synchronous=NORMAL",
    "PRAGMA mmap_size=268435456",  # 256MB memory-map
    "PRAGMA cache_size=-65536",  # 64MB cache
    "PRAGMA temp_store=MEMORY",
]


class SQLiteRepositoryBase:
    """Base class with SQLite connection management."""

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self._conn: sqlite3.Connection | None = None

    def _ensure_connection(self) -> sqlite3.Connection:
        if self._conn is None:
            if not self.db_path.exists():
                raise FileNotFoundError(f"Database not found: {self.db_path}")
            self._conn = sqlite3.connect(
                self.db_path, check_same_thread=False, isolation_level=None
            )
            for pragma in SQLITE_PRAGMAS:
                self._conn.execute(pragma)
        return self._conn

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None


class SQLitePhoneticRepository(SQLiteRepositoryBase, IPhoneticRepository):
    """
    SQLite phonetic repository.

    Schema: CREATE TABLE phonetic (hash TEXT PRIMARY KEY, words TEXT NOT NULL)
    """

    def get(self, phonetic_hash: str) -> str | None:
        if not phonetic_hash:
            return None
        conn = self._ensure_connection()
        cursor = conn.execute(
            "SELECT words FROM phonetic WHERE hash = ?",
            (phonetic_hash,),
        )
        row = cursor.fetchone()
        return row[0] if row else None

    def get_words_list(self, phonetic_hash: str) -> list[str]:
        result = self.get(phonetic_hash)
        return result.split(",") if result else []

    def get_batch(self, phonetic_hashes: list[str]) -> dict[str, str]:
        """Batch lookup for multiple phonetic hashes."""
        if not phonetic_hashes:
            return {}

        hashes = [h for h in phonetic_hashes if h]
        if not hashes:
            return {}

        conn = self._ensure_connection()
        placeholders = ",".join("?" for _ in hashes)
        cursor = conn.execute(
            f"SELECT hash, words FROM phonetic WHERE hash IN ({placeholders})",
            hashes,
        )
        return {row[0]: row[1] for row in cursor}

    def has(self, phonetic_hash: str) -> bool:
        return self.get(phonetic_hash) is not None

    # Alias methods for IPhoneticDatabase interface compatibility
    def find_by_phonetic_hash(self, phonetic_hash: str) -> str | None:
        """Alias for get() - IPhoneticDatabase compatibility."""
        return self.get(phonetic_hash)

    def get_words_by_phonetic_hash(self, phonetic_hash: str) -> list[str]:
        """Alias for get_words_list() - IPhoneticDatabase compatibility."""
        return self.get_words_list(phonetic_hash)

    def has_phonetic_hash(self, phonetic_hash: str) -> bool:
        """Alias for has() - IPhoneticDatabase compatibility."""
        return self.has(phonetic_hash)


class SQLiteFrequencyRepository(SQLiteRepositoryBase, IFrequencyRepository):
    """
    SQLite frequency repository.

    Schema: CREATE TABLE frequencies (word TEXT PRIMARY KEY, frequency INTEGER NOT NULL)
    """

    def get(self, word: str) -> str | None:
        freq = self.get_frequency(word)
        return str(freq) if freq > 0 else None

    def get_frequency(self, word: str) -> int:
        if not word:
            return 0
        conn = self._ensure_connection()
        cursor = conn.execute(
            "SELECT frequency FROM frequencies WHERE word = ?",
            (word,),
        )
        row = cursor.fetchone()
        return row[0] if row else 0

    def rank_suggestions(self, suggestions: list[str]) -> list[tuple[str, int]]:
        """Rank suggestions by descending frequency, then alphabetically."""
        ranked = []
        for suggestion in suggestions:
            ranked.append((suggestion, self.get_frequency(suggestion)))

        ranked.sort(key=lambda item: (-item[1], item[0]))
        return ranked

    def has(self, word: str) -> bool:
        return self.get_frequency(word) > 0

    # Alias methods for IFrequencyDatabase interface compatibility
    def has_word(self, word: str) -> bool:
        """Alias for has() - IFrequencyDatabase compatibility."""
        return self.has(word)


class SQLiteErrorRepository(SQLiteRepositoryBase, IErrorRepository):
    """
    SQLite error corrections repository.

    Schema: CREATE TABLE errors (error TEXT PRIMARY KEY, correction TEXT NOT NULL)
    """

    def get(self, error_word: str) -> str | None:
        return self.get_correction(error_word)

    def get_correction(self, error_word: str) -> str | None:
        if not error_word:
            return None
        conn = self._ensure_connection()
        # Try exact match first
        cursor = conn.execute(
            "SELECT correction FROM errors WHERE error = ?",
            (error_word,),
        )
        row = cursor.fetchone()
        if row:
            return str(row[0])
        # Try lowercase version for case-insensitive match
        cursor = conn.execute(
            "SELECT correction FROM errors WHERE error = ?",
            (error_word.lower(),),
        )
        row = cursor.fetchone()
        return row[0] if row else None

    def has(self, error_word: str) -> bool:
        return self.get_correction(error_word) is not None

    # Alias methods for IErrorDatabase interface compatibility
    def has_error(self, error_word: str) -> bool:
        """Alias for has() - IErrorDatabase compatibility."""
        return self.has(error_word)


class SQLiteElisionRepository(SQLiteRepositoryBase, IElisionRepository):
    """
    SQLite elision repository.

    Schema: CREATE TABLE elisions (word TEXT PRIMARY KEY)
    """

    def get(self, word: str) -> str | None:
        return word if self.has_elision(word) else None

    def has_elision(self, word: str) -> bool:
        if not word:
            return False
        conn = self._ensure_connection()
        # Try exact match first
        cursor = conn.execute(
            "SELECT 1 FROM elisions WHERE word = ?",
            (word,),
        )
        if cursor.fetchone() is not None:
            return True
        # Try lowercase version for case-insensitive match
        cursor = conn.execute(
            "SELECT 1 FROM elisions WHERE word = ?",
            (word.lower(),),
        )
        return cursor.fetchone() is not None

    def has(self, word: str) -> bool:
        return self.has_elision(word)


class InMemoryElisionRepository(IElisionRepository):
    """In-memory elision repository for O(1) lookups."""

    def __init__(self, db_path: str | Path):
        self._db_path = Path(db_path)
        self._elisions: frozenset[str] | None = None

    def _ensure_loaded(self) -> frozenset[str]:
        if self._elisions is None:
            if not self._db_path.exists():
                raise FileNotFoundError(f"Elisions database not found: {self._db_path}")

            conn = sqlite3.connect(str(self._db_path))
            try:
                cursor = conn.execute("SELECT word FROM elisions")
                self._elisions = frozenset(row[0].lower() for row in cursor if row and row[0])
            finally:
                conn.close()
        return self._elisions

    def get(self, word: str) -> str | None:
        return word if self.has_elision(word) else None

    def has_elision(self, word: str) -> bool:
        if not word:
            return False
        return word.lower() in self._ensure_loaded()

    def has(self, word: str) -> bool:
        return self.has_elision(word)

    def close(self) -> None:
        # Nothing to close for in-memory data
        pass
