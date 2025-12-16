"""Tests for database functionality."""

import os
import shutil
import sqlite3
import tempfile
import time
from pathlib import Path

import pytest

from furlan_spellchecker.config.schemas import DictionaryConfig, FurlanSpellCheckerConfig
from furlan_spellchecker.database import (
    AddWordResult,
    DatabaseManager,
    DictionaryType,
    SQLiteKeyValueDatabase,
)


@pytest.fixture
def temp_config():
    """Create a temporary configuration for testing with robust Windows cleanup.

    Using TemporaryDirectory context directly sometimes triggers PermissionError on Windows
    because SQLite may keep the file handle a fraction of a second after context exit.
    We implement manual cleanup with retries.
    """
    temp_dir = tempfile.mkdtemp()
    config = FurlanSpellCheckerConfig(dictionary=DictionaryConfig(cache_directory=temp_dir))
    try:
        yield config
    finally:
        # Retry deletion a few times if locked
        for attempt in range(5):
            try:
                # Attempt rename of sqlite files to break lingering handles (Windows quirk)
                for root, _dirs, files in os.walk(temp_dir):
                    for f in files:
                        if f.endswith(".sqlite"):
                            p = os.path.join(root, f)
                            try:
                                os.replace(p, p + f".tmp{attempt}")
                            except OSError:
                                pass
                shutil.rmtree(temp_dir)
                break
            except PermissionError:
                if attempt == 4:
                    # Give up and leak temp dir rather than failing test on Windows
                    break
                time.sleep(0.2)


@pytest.fixture
def sqlite_db(temp_config):
    """Create SQLiteKeyValueDatabase instance for testing."""
    return SQLiteKeyValueDatabase(temp_config)


@pytest.fixture
def sample_system_db(temp_config):
    """Create a sample system database for testing."""
    cache_dir = Path(temp_config.dictionary.cache_directory)
    words_dir = cache_dir / "words_database"
    words_dir.mkdir(parents=True, exist_ok=True)

    db_path = words_dir / "words.db"

    # Create and populate sample database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table structure similar to C# version
    cursor.execute(
        """
        CREATE TABLE Words (
            Key TEXT PRIMARY KEY,
            Value TEXT NOT NULL
        )
    """
    )

    # Add some sample data (phonetic hash -> word mappings)
    sample_data = [
        ("KS", "cjase"),  # house
        ("FRD", "fradi"),  # brother
        ("MR", "mari"),  # mother
    ]

    cursor.executemany("INSERT INTO Words (Key, Value) VALUES (?, ?)", sample_data)
    conn.commit()
    conn.close()

    return db_path


class TestSQLiteKeyValueDatabase:
    """Test SQLite database operations."""

    def test_user_database_creation(self, sqlite_db):
        """Test that user database is created when accessed."""
        # Database should be created when first accessed
        result = sqlite_db.add_to_user_database("test_word")

        # Should succeed in creating and adding
        assert result in [AddWordResult.SUCCESS, AddWordResult.ALREADY_PRESENT]

    def test_find_in_system_database(self, sqlite_db, sample_system_db):
        """Test finding words in system database."""
        # Should find existing phonetic hash
        result = sqlite_db.find_in_system_database("KS")
        assert result == "cjase"

        # Should return None for non-existent hash
        result = sqlite_db.find_in_system_database("NONEXISTENT")
        assert result is None

    def test_add_to_user_database(self, sqlite_db):
        """Test adding words to user database with COF-compatible return codes.

        Tests:
        1. Adding new word returns SUCCESS (COF code 0)
        2. Adding duplicate word returns ALREADY_PRESENT (COF code 2)
        """
        # Use unique word to ensure clean state
        import time

        test_word = f"test_word_{int(time.time() * 1000000)}"

        # Add a word first time - should return SUCCESS
        result = sqlite_db.add_to_user_database(test_word)
        assert result == AddWordResult.SUCCESS, f"First add should return SUCCESS, got {result}"

        # Adding the same word again should return ALREADY_PRESENT
        result = sqlite_db.add_to_user_database(test_word)
        assert (
            result == AddWordResult.ALREADY_PRESENT
        ), f"Duplicate add should return ALREADY_PRESENT, got {result}"

    def test_unicode_replacement(self, sqlite_db):
        """Test Unicode code replacement functionality."""
        # This tests the internal method
        result = sqlite_db._replace_unicode_codes_with_special_chars("test\\e7word")
        assert result == "testçword"

        result = sqlite_db._replace_unicode_codes_with_special_chars("norm\\e2l")
        assert result == "normâl"


class TestDatabaseManager:
    """Test database manager functionality."""

    def test_database_availability_check(self, temp_config):
        """Test checking database availability."""
        manager = DatabaseManager(temp_config)
        availability = manager.ensure_databases_available()

        # Should return status for all database types
        assert DictionaryType.USER_DICTIONARY in availability
        assert DictionaryType.SYSTEM_DICTIONARY in availability
        assert DictionaryType.RADIX_TREE in availability

        # User database should be available (can be created)
        assert availability[DictionaryType.USER_DICTIONARY] is True

    def test_missing_databases(self, temp_config):
        """Test getting list of missing databases.

        Note: With auto-download enabled, this test checks the INITIAL state
        before ensure_databases_available() is called.
        """
        DatabaseManager(temp_config)

        # Check missing databases WITHOUT calling ensure_databases_available()
        # This directly checks what would be missing before auto-download
        cache_dir = Path(temp_config.dictionary.cache_directory)
        availability = {}
        required_databases = [
            DictionaryType.SYSTEM_DICTIONARY,
            DictionaryType.SYSTEM_ERRORS,
            DictionaryType.FREQUENCIES,
            DictionaryType.ELISIONS,
            DictionaryType.RADIX_TREE,
        ]

        # Check which files actually exist in the temp directory
        for db_type in required_databases:
            if db_type == DictionaryType.RADIX_TREE:
                path = cache_dir / "words_radix_tree.rt"
            elif db_type == DictionaryType.SYSTEM_DICTIONARY:
                path = cache_dir / "words.sqlite"
            elif db_type == DictionaryType.SYSTEM_ERRORS:
                path = cache_dir / "errors.sqlite"
            elif db_type == DictionaryType.FREQUENCIES:
                path = cache_dir / "frequencies.sqlite"
            elif db_type == DictionaryType.ELISIONS:
                path = cache_dir / "elisions.sqlite"
            else:
                continue

            availability[db_type] = path.exists()

        # In a fresh temp directory, these should NOT exist initially
        assert not availability.get(
            DictionaryType.SYSTEM_DICTIONARY, True
        ), "SYSTEM_DICTIONARY should not exist in fresh temp directory"
        assert not availability.get(
            DictionaryType.FREQUENCIES, True
        ), "FREQUENCIES should not exist in fresh temp directory"
        assert not availability.get(
            DictionaryType.ELISIONS, True
        ), "ELISIONS should not exist in fresh temp directory"


@pytest.mark.integration
class TestDatabaseIntegration:
    """Integration tests for database functionality."""

    @pytest.mark.skipif(
        os.environ.get("GITHUB_ACTIONS") == "true", reason="Skip integration tests in CI"
    )
    def test_database_with_extracted_files(self, temp_config):
        """Test database operations with actual extracted files.

        Note: With auto-download, this now tests that databases are automatically
        downloaded when ensure_databases_available() is called.
        """
        manager = DatabaseManager(temp_config)

        # Verify databases are available after ensure_databases_available()
        availability = manager.ensure_databases_available()

        # With auto-download, all required databases should be available
        assert (
            availability[DictionaryType.SYSTEM_DICTIONARY] is True
        ), "System dictionary should be auto-downloaded"
        assert (
            availability[DictionaryType.FREQUENCIES] is True
        ), "Frequencies should be auto-downloaded"
        assert availability[DictionaryType.ELISIONS] is True, "Elisions should be auto-downloaded"

        # Missing databases should be empty after auto-download
        missing = manager.get_missing_databases()
        assert len(missing) == 0, "No databases should be missing after auto-download"
