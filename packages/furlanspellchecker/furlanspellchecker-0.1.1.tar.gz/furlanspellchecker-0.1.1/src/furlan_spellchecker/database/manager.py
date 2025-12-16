"""Database management for Friulian spell checker."""

import platform
from pathlib import Path

from ..config.schemas import FurlanSpellCheckerConfig
from .factory import DatabaseFactory
from .interfaces import (
    DictionaryType,
    IElisionDatabase,
    IErrorDatabase,
    IFrequencyDatabase,
    IPhoneticDatabase,
)
from .radix_tree import RadixTreeDatabase
from .sqlite_database import SQLiteKeyValueDatabase


class DatabaseManager:
    """Manages all database connections and operations."""

    def __init__(self, config: FurlanSpellCheckerConfig | None = None):
        """Initialize database manager with configuration."""
        self.config = config or FurlanSpellCheckerConfig()
        self._sqlite_db: SQLiteKeyValueDatabase | None = None
        self._radix_tree: RadixTreeDatabase | None = None
        self._elision_db: IElisionDatabase | None = None
        self._error_db: IErrorDatabase | None = None
        self._frequency_db: IFrequencyDatabase | None = None
        self._phonetic_db: IPhoneticDatabase | None = None
        self._cache_dir = self._get_cache_directory()
        self._data_dir = Path(__file__).resolve().parents[3] / "data" / "databases"

    def _get_cache_directory(self) -> Path:
        """Get cache directory, using default if not specified."""
        if self.config.dictionary.cache_directory:
            return Path(self.config.dictionary.cache_directory)

        # Default cache directory based on platform
        system = platform.system()
        if system == "Windows":
            cache_dir = Path.home() / "AppData" / "Local" / "FurlanSpellChecker"
        elif system == "Darwin":  # macOS
            cache_dir = Path.home() / "Library" / "Caches" / "FurlanSpellChecker"
        else:  # Linux and other Unix-like
            cache_dir = Path.home() / ".cache" / "FurlanSpellChecker"

        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir

    @property
    def sqlite_db(self) -> SQLiteKeyValueDatabase:
        """Get SQLite database instance."""
        if self._sqlite_db is None:
            self._sqlite_db = SQLiteKeyValueDatabase(self.config)
        return self._sqlite_db

    @property
    def radix_tree(self) -> RadixTreeDatabase:
        """Get radix tree database instance using packaged data."""
        if self._radix_tree is None:
            radix_tree_path = self._data_dir / "words_radix_tree.rt"
            if not radix_tree_path.exists():
                raise FileNotFoundError(f"Radix tree file not found at '{radix_tree_path}'")
            self._radix_tree = RadixTreeDatabase(radix_tree_path)
        return self._radix_tree

    @property
    def elision_db(self) -> IElisionDatabase:
        """Get elision database instance (SQLite format with auto-download)."""
        if self._elision_db is None:
            self._elision_db = DatabaseFactory.create_elision_database(auto_download=True)
        return self._elision_db

    @property
    def error_db(self) -> IErrorDatabase:
        """Get error database instance (SQLite format with auto-download)."""
        if self._error_db is None:
            self._error_db = DatabaseFactory.create_error_database(auto_download=True)
        return self._error_db

    @property
    def frequency_db(self) -> IFrequencyDatabase:
        """Get frequency database instance (SQLite format with auto-download)."""
        if self._frequency_db is None:
            self._frequency_db = DatabaseFactory.create_frequency_database(auto_download=True)
        return self._frequency_db

    @property
    def phonetic_db(self) -> IPhoneticDatabase:
        """Get phonetic database instance (SQLite format with auto-download).

        This is the main dictionary database containing phonetic hash -> words mapping.
        Replaces the deprecated sqlite_db.find_in_system_database() method.
        """
        if self._phonetic_db is None:
            self._phonetic_db = DatabaseFactory.create_phonetic_database(auto_download=True)
        return self._phonetic_db

    def ensure_databases_available(self) -> dict[DictionaryType, bool]:
        """Check which databases are available or can be auto-downloaded."""
        availability = {}

        # System databases (SQLite format with auto-download)
        # These will be automatically downloaded if missing, so mark as available
        availability[DictionaryType.SYSTEM_DICTIONARY] = True  # words.sqlite (auto-download)
        availability[DictionaryType.SYSTEM_ERRORS] = True  # errors.sqlite (auto-download)
        availability[DictionaryType.FREQUENCIES] = True  # frequencies.sqlite (auto-download)
        availability[DictionaryType.ELISIONS] = True  # elisions.sqlite (auto-download)
        availability[DictionaryType.RADIX_TREE] = (self._data_dir / "words_radix_tree.rt").exists()

        # User databases (these can be created on demand)
        self._cache_dir / "UserDictionary" / "user_dictionary.sqlite"
        user_errors_path = self._cache_dir / "UserErrors" / "user_errors.sqlite"
        availability[DictionaryType.USER_DICTIONARY] = True  # Can be created
        availability[DictionaryType.USER_ERRORS] = user_errors_path.exists()

        return availability

    def get_missing_databases(self) -> dict[DictionaryType, Path]:
        """Get list of missing required databases and their expected paths.

        Note: All databases now use auto-download from GitHub Releases.
        This method returns paths for databases that haven't been downloaded yet.
        """
        from .downloader import DatabaseDownloader

        availability = self.ensure_databases_available()
        missing: dict[DictionaryType, Path] = {}

        required_databases = [
            DictionaryType.SYSTEM_DICTIONARY,
            DictionaryType.SYSTEM_ERRORS,
            DictionaryType.FREQUENCIES,
            DictionaryType.ELISIONS,
        ]

        downloader = DatabaseDownloader()

        for db_type in required_databases:
            if not availability.get(db_type, False):
                if db_type == DictionaryType.SYSTEM_DICTIONARY:
                    missing[db_type] = downloader.get_database_path("words.sqlite")
                elif db_type == DictionaryType.SYSTEM_ERRORS:
                    missing[db_type] = downloader.get_database_path("errors.sqlite")
                elif db_type == DictionaryType.FREQUENCIES:
                    missing[db_type] = downloader.get_database_path("frequencies.sqlite")
                elif db_type == DictionaryType.ELISIONS:
                    missing[db_type] = downloader.get_database_path("elisions.sqlite")

        radix_tree_path = self._data_dir / "words_radix_tree.rt"
        if not availability.get(DictionaryType.RADIX_TREE, False):
            missing[DictionaryType.RADIX_TREE] = radix_tree_path

        return missing
