"""
Database factory for creating database instances based on file format.

This module provides a format-agnostic way to instantiate databases,
allowing the implementation to change without modifying consuming code or tests.
"""

import logging
from pathlib import Path

from .downloader import download_database
from .interfaces import (
    DatabaseFormat,
    IElisionDatabase,
    IErrorDatabase,
    IFrequencyDatabase,
    IPhoneticDatabase,
)
from .repositories import (
    CachedErrorRepository,
    CachedFrequencyRepository,
    CachedPhoneticRepository,
    IErrorRepository,
    IFrequencyRepository,
    InMemoryElisionRepository,
    IPhoneticRepository,
    SQLiteErrorRepository,
    SQLiteFrequencyRepository,
    SQLitePhoneticRepository,
)

logger = logging.getLogger(__name__)


# Path to packaged databases bundled with the package
_PACKAGE_DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "databases"


class DatabaseFactory:
    """
    Factory for creating database instances based on file extension.

    This allows transparent migration between database formats without
    changing consuming code. Automatically downloads databases from
    GitHub Releases if not found locally.

    Search order:
    1. Absolute or relative path (if exists)
    2. Packaged data directory (data/databases/)
    3. Auto-download from GitHub Releases (if enabled)

    Example:
        >>> factory = DatabaseFactory()
        >>> freq_db = factory.create_frequency_database("frequencies.sqlite")
        >>> # Same interface, different implementation!
    """

    @staticmethod
    def _resolve_database_path(db_path: str | Path, auto_download: bool = True) -> Path:
        """
        Resolve database path, downloading from GitHub Releases if necessary.

        Args:
            db_path: Path to database file (can be just filename)
            auto_download: Whether to auto-download if file not found locally

        Returns:
            Resolved Path to database file

        Raises:
            FileNotFoundError: If file not found and auto_download is False
        """
        path = Path(db_path)

        # If absolute path exists, use it
        if path.is_absolute() and path.exists():
            return path

        # If relative path exists, use it
        if path.exists():
            return path.resolve()

        # Check packaged data directory (data/databases/)
        packaged_path = _PACKAGE_DATA_DIR / path.name
        if packaged_path.exists():
            logger.debug(f"Found database in package data: {packaged_path}")
            return packaged_path

        # Try auto-download if enabled
        if auto_download:
            filename = path.name
            logger.info(f"Database '{filename}' not found locally, attempting download...")
            try:
                return download_database(filename)
            except Exception as e:
                logger.error(f"Failed to download database '{filename}': {e}")
                raise FileNotFoundError(
                    f"Database '{filename}' not found locally and download failed: {e}"
                ) from e

        raise FileNotFoundError(f"Database file not found: {db_path}")

    @staticmethod
    def detect_format(file_path: Path) -> DatabaseFormat:
        """
        Detect database format from file extension.

        Args:
            file_path: Path to database file

        Returns:
            DatabaseFormat enum value

        Raises:
            ValueError: If format cannot be determined
        """
        suffix = file_path.suffix.lower()

        if suffix == ".sqlite":
            return DatabaseFormat.SQLITE
        elif suffix == ".rt":
            return DatabaseFormat.BINARY
        else:
            raise ValueError(f"Unknown database format: {suffix}")

    @classmethod
    def create_phonetic_database(
        cls,
        db_path: str | Path = "words.sqlite",
        auto_download: bool = True,
        cache_size: int = 50000,
    ) -> IPhoneticDatabase:
        """
        Create phonetic database instance based on file format.

        Args:
            db_path: Path to database file
            auto_download: Whether to auto-download if file not found locally

        Returns:
            IPhoneticDatabase implementation

        Raises:
            ValueError: If format is unsupported
            FileNotFoundError: If file not found and auto_download is False
        """
        path = cls._resolve_database_path(db_path, auto_download)
        fmt = cls.detect_format(path)

        if fmt == DatabaseFormat.SQLITE:
            repo: IPhoneticRepository = SQLitePhoneticRepository(path)
            if cache_size > 0:
                repo = CachedPhoneticRepository(repo, cache_size)
            return repo
        raise ValueError(f"Unsupported phonetic database format: {fmt}")

    @classmethod
    def create_frequency_database(
        cls,
        db_path: str | Path = "frequencies.sqlite",
        auto_download: bool = True,
        cache_size: int = 20000,
    ) -> IFrequencyDatabase:
        """
        Create frequency database instance based on file format.

        Args:
            db_path: Path to database file
            auto_download: Whether to auto-download if file not found locally

        Returns:
            IFrequencyDatabase implementation

        Raises:
            ValueError: If format is unsupported
            FileNotFoundError: If file not found and auto_download is False
        """
        path = cls._resolve_database_path(db_path, auto_download)
        fmt = cls.detect_format(path)

        if fmt == DatabaseFormat.SQLITE:
            repo: IFrequencyRepository = SQLiteFrequencyRepository(path)
            if cache_size > 0:
                repo = CachedFrequencyRepository(repo, cache_size)
            return repo
        raise ValueError(f"Unsupported frequency database format: {fmt}")

    @classmethod
    def create_error_database(
        cls,
        db_path: str | Path = "errors.sqlite",
        auto_download: bool = True,
        cache_size: int = 1000,
    ) -> IErrorDatabase:
        """
        Create error database instance based on file format.

        Args:
            db_path: Path to database file
            auto_download: Whether to auto-download if file not found locally

        Returns:
            IErrorDatabase implementation

        Raises:
            ValueError: If format is unsupported
            FileNotFoundError: If file not found and auto_download is False
        """
        path = cls._resolve_database_path(db_path, auto_download)
        fmt = cls.detect_format(path)

        if fmt == DatabaseFormat.SQLITE:
            repo: IErrorRepository = SQLiteErrorRepository(path)
            if cache_size > 0:
                repo = CachedErrorRepository(repo, cache_size)
            return repo
        raise ValueError(f"Unsupported error database format: {fmt}")

    @classmethod
    def create_elision_database(
        cls,
        db_path: str | Path = "elisions.sqlite",
        auto_download: bool = True,
        cache_size: int = 5000,
    ) -> IElisionDatabase:
        """
        Create elision database instance based on file format.

        Args:
            db_path: Path to database file
            auto_download: Whether to auto-download if file not found locally

        Returns:
            IElisionDatabase implementation

        Raises:
            ValueError: If format is unsupported
            FileNotFoundError: If file not found and auto_download is False
        """
        path = cls._resolve_database_path(db_path, auto_download)
        fmt = cls.detect_format(path)

        if fmt == DatabaseFormat.SQLITE:
            # Load entire elision table into memory for O(1) lookups
            repo: IElisionDatabase = InMemoryElisionRepository(path)
            return repo
        raise ValueError(f"Unsupported elision database format: {fmt}")
