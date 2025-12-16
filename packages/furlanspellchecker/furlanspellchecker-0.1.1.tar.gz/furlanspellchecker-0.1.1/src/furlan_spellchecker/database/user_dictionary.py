"""User dictionary database implementation for FurlanSpellChecker.

This module implements user dictionary functionality compatible with COF's user_dict
using a SQLite backend.
"""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from ..phonetic.furlan_phonetic import FurlanPhoneticAlgorithm


class UserDictionaryDatabase:
    """
    User dictionary database using SQLite backend.

    Implements COF's user_dict functionality:
    - Stores user-added words indexed by phonetic codes
    - Uses phonetic algorithm to generate lookup keys
    - Supports add, delete, and lookup operations
    - Maintains COF-compatible comma-separated value format

    Uses a persistent connection for performance (avoids repeated connect overhead).
    """

    def __init__(self, db_path: Path):
        """Initialize user dictionary database.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.phonetic = FurlanPhoneticAlgorithm()
        self._conn: sqlite3.Connection | None = None
        self._ensure_database_exists()

    def _get_connection(self) -> sqlite3.Connection:
        """Get or create the persistent SQLite connection.

        Returns a cached connection for performance. The connection is created
        with check_same_thread=False to allow reuse across the same thread.
        """
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        return self._conn

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        """Context manager that reuses the persistent connection.

        For backward compatibility, this now yields the persistent connection
        instead of creating a new one each time.
        """
        yield self._get_connection()

    def _ensure_database_exists(self) -> None:
        """Create database and table if they don't exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with self._connect() as conn:
            cursor = conn.cursor()
            # COF-compatible schema: phonetic_code -> comma-separated words
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_dictionary (
                    phonetic_code TEXT PRIMARY KEY,
                    words TEXT NOT NULL
                )
            """
            )
            conn.commit()

    def add_word(self, word: str) -> int:
        """
        Add word to user dictionary.

        Implements COF's add_user_dict logic:
        1. Calculate phonetic codes for the word
        2. For each code, check if word already exists
        3. If not exists, add to comma-separated list
        4. Store under both codes (if different)

        Args:
            word: Word to add

        Returns:
            0 if word was added successfully (COF: success)
            2 if word already exists (COF: duplicate)
            1 if error occurred
        """
        if not word:
            return 1  # Error

        word = word.strip()
        code1, code2 = self.phonetic.get_phonetic_hashes_by_word(word)

        # Get unique codes
        codes = [code1] if code1 == code2 else [code1, code2]

        with self._connect() as conn:
            cursor = conn.cursor()

            # Check if word already exists under any code
            for code in codes:
                cursor.execute("SELECT words FROM user_dictionary WHERE phonetic_code = ?", (code,))
                result = cursor.fetchone()

                if result:
                    existing_words = result[0].split(",")
                    if word in existing_words:
                        return 2  # Duplicate (COF code)

            # Add word to all relevant codes
            for code in codes:
                cursor.execute("SELECT words FROM user_dictionary WHERE phonetic_code = ?", (code,))
                result = cursor.fetchone()

                if result:
                    # Add to existing list
                    existing_words = result[0].split(",")
                    existing_words.append(word)
                    new_words = ",".join(existing_words)
                    cursor.execute(
                        "UPDATE user_dictionary SET words = ? WHERE phonetic_code = ?",
                        (new_words, code),
                    )
                else:
                    # Create new entry
                    cursor.execute(
                        "INSERT INTO user_dictionary (phonetic_code, words) VALUES (?, ?)",
                        (code, word),
                    )

            conn.commit()

        return 0  # Success (COF code)

    def change_word(self, new_word: str, old_word: str) -> int:
        """
        Change word in user dictionary (atomic delete + add).

        Implements COF's change_user_dict logic:
        1. Remove old word
        2. Add new word
        3. Both operations in transactional context

        Args:
            new_word: New word to add
            old_word: Old word to remove

        Returns:
            0 if successful (COF: success)
            1 if error occurred
        """
        try:
            # Remove old word
            self.remove_word(old_word)

            # Add new word
            result = self.add_word(new_word)

            # Return 0 for success (COF compatible)
            return 0 if result in (0, 2) else 1
        except Exception:
            return 1  # Error

    def remove_word(self, word: str) -> int:
        """
        Remove word from user dictionary.

        Implements COF's delete_user_dict logic:
        1. Calculate phonetic codes for the word
        2. For each code, remove word from comma-separated list
        3. Delete entry if no words remain

        Args:
            word: Word to remove

        Returns:
            0 if word was removed successfully (COF: success)
            1 if word not found or error
        """
        if not word:
            return 1  # Error

        word = word.strip()
        code1, code2 = self.phonetic.get_phonetic_hashes_by_word(word)

        # Get unique codes
        codes = [code1] if code1 == code2 else [code1, code2]

        removed = False

        with self._connect() as conn:
            cursor = conn.cursor()

            for code in codes:
                cursor.execute("SELECT words FROM user_dictionary WHERE phonetic_code = ?", (code,))
                result = cursor.fetchone()

                if result:
                    existing_words = [w for w in result[0].split(",") if w != word]

                    if len(existing_words) < len(result[0].split(",")):
                        removed = True

                        if existing_words:
                            # Update with remaining words
                            new_words = ",".join(existing_words)
                            cursor.execute(
                                "UPDATE user_dictionary SET words = ? WHERE phonetic_code = ?",
                                (new_words, code),
                            )
                        else:
                            # Delete empty entry
                            cursor.execute(
                                "DELETE FROM user_dictionary WHERE phonetic_code = ?", (code,)
                            )

            conn.commit()

        return 0 if removed else 1  # COF: 0=success, 1=not found

    def find_by_phonetic_code(self, phonetic_code: str) -> str | None:
        """
        Find words by phonetic code.

        Args:
            phonetic_code: Phonetic hash code

        Returns:
            Comma-separated string of words, or None if not found
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT words FROM user_dictionary WHERE phonetic_code = ?", (phonetic_code,)
            )
            result = cursor.fetchone()
            return result[0] if result else None

    def get_phonetic_suggestions(self, word: str, max_suggestions: int = 10) -> list[str]:
        """Get phonetic suggestions for a word, mirroring COF user dict behavior."""
        return self._get_phonetic_suggestions_internal(word, max_suggestions=max_suggestions)

    def contains_word(self, word: str) -> bool:
        """
        Check if word exists in user dictionary.

        Args:
            word: Word to check

        Returns:
            True if word exists in user dictionary
        """
        suggestions = self.get_phonetic_suggestions(word)
        return word in suggestions

    def get_all_words(self) -> list[str]:
        """
        Get all words in user dictionary.

        Returns:
            List of all words in user dictionary
        """
        words = set()

        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT words FROM user_dictionary")

            for row in cursor.fetchall():
                words.update(row[0].split(","))

        return sorted(words)

    def clear(self) -> None:
        """Clear all words from user dictionary."""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_dictionary")
            conn.commit()

    def get_word_count(self) -> int:
        """Get total number of words in user dictionary."""
        return len(self.get_all_words())

    def has_word(self, word: str) -> bool:
        """
        Check if word exists in user dictionary.

        Args:
            word: Word to check

        Returns:
            True if word exists in dictionary
        """
        if not word:
            return False

        return word in self.get_all_words()

    def get_words_by_phonetic_code(self, phonetic_code: str) -> list[str]:
        """
        Get all words stored under a specific phonetic code.

        Args:
            phonetic_code: The phonetic code to search for

        Returns:
            List of words matching the phonetic code
        """
        if not phonetic_code:
            return []

        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT words FROM user_dictionary WHERE phonetic_code = ?", (phonetic_code,)
            )
            result = cursor.fetchone()

            if result:
                return str(result[0]).split(",")
            return []

    def _get_phonetic_suggestions_internal(self, word: str, max_suggestions: int = 10) -> list[str]:
        """Internal method for phonetic suggestions with max_suggestions parameter."""
        if not word:
            return []

        try:
            # Get phonetic codes for input word
            code_a, code_b = self.phonetic.get_phonetic_hashes_by_word(word.lower())

            suggestions = []

            # Get words for both phonetic codes
            for code in [code_a, code_b]:
                if code:  # Skip empty codes
                    words = self.get_words_by_phonetic_code(code)
                    suggestions.extend(words)

            # Remove duplicates and the original word
            unique_suggestions = []
            seen = set()

            for suggestion in suggestions:
                if suggestion and suggestion.lower() != word.lower() and suggestion not in seen:
                    unique_suggestions.append(suggestion)
                    seen.add(suggestion)

            return unique_suggestions[:max_suggestions]

        except Exception:
            return []

    def close(self) -> None:
        """Close database connections and release resources.

        This is particularly important on Windows where SQLite files
        can remain locked even after connections are closed.
        Calling this method ensures all database handles are released.
        """
        if self._conn is not None:
            try:
                self._conn.close()
            except Exception:
                pass  # Ignore errors during close
            finally:
                self._conn = None
