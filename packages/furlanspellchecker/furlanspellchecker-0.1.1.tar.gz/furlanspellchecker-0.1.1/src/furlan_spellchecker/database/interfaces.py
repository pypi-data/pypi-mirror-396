"""Separate interfaces module to avoid circular imports."""

from abc import ABC, abstractmethod
from enum import Enum


class DictionaryType(Enum):
    """Types of dictionaries available."""

    SYSTEM_DICTIONARY = "system_dictionary"
    USER_DICTIONARY = "user_dictionary"
    SYSTEM_ERRORS = "system_errors"
    USER_ERRORS = "user_errors"
    FREQUENCIES = "frequencies"
    ELISIONS = "elisions"
    RADIX_TREE = "radix_tree"


class DatabaseFormat(Enum):
    """Supported database formats."""

    SQLITE = "sqlite"  # .sqlite files
    BINARY = "binary"  # .rt files (RadixTree custom format)


class AddWordResult(Enum):
    """Results of adding a word to user dictionary."""

    SUCCESS = "success"
    ALREADY_PRESENT = "already_present"
    DATABASE_NOT_EXISTS = "database_not_exists"
    ERROR = "error"


class RemoveWordResult(Enum):
    """Results of removing a word from user dictionary."""

    SUCCESS = "success"
    NOT_FOUND = "not_found"
    DATABASE_NOT_EXISTS = "database_not_exists"
    ERROR = "error"


class AddExceptionResult(Enum):
    """Results of adding an exception."""

    SUCCESS = "success"
    UPDATED = "updated"
    INVALID_INPUT = "invalid_input"
    DATABASE_NOT_EXISTS = "database_not_exists"
    ERROR = "error"


class IKeyValueDatabase(ABC):
    """Interface for key-value database operations."""

    @abstractmethod
    def find_in_user_database(self, phonetic_hash: str) -> str | None:
        """Find value in user dictionary by phonetic hash."""
        pass

    @abstractmethod
    def find_in_user_errors_database(self, word: str) -> str | None:
        """Find correction in user errors database."""
        pass

    @abstractmethod
    def find_in_system_database(self, phonetic_hash: str) -> str | None:
        """Find value in system dictionary by phonetic hash."""
        pass

    @abstractmethod
    def find_in_system_errors_database(self, word: str) -> str | None:
        """Find correction in system errors database."""
        pass

    @abstractmethod
    def find_in_frequencies_database(self, word: str) -> int | None:
        """Find frequency value for a word."""
        pass

    @abstractmethod
    def has_elisions(self, word: str) -> bool:
        """Check if word exists in elisions database."""
        pass

    @abstractmethod
    def add_to_user_database(self, word: str) -> AddWordResult:
        """Add word to user dictionary."""
        pass

    @abstractmethod
    def remove_from_user_database(self, word: str) -> RemoveWordResult:
        """Remove word from user dictionary."""
        pass

    @abstractmethod
    def add_user_exception(self, error_word: str, correction: str) -> AddExceptionResult:
        """Add error -> correction pair to user exceptions."""
        pass

    @abstractmethod
    def remove_user_exception(self, error_word: str) -> RemoveWordResult:
        """Remove exception from user exceptions."""
        pass

    @abstractmethod
    def get_user_dictionary_suggestions(self, word: str, max_suggestions: int = 10) -> list[str]:
        """Get phonetic suggestions from user dictionary."""
        pass


class IRadixTree(ABC):
    """Interface for radix tree operations."""

    @abstractmethod
    def contains(self, word: str) -> bool:
        """Check if word exists in radix tree."""
        pass

    @abstractmethod
    def find_suggestions(self, word: str, max_suggestions: int = 10) -> list[str]:
        """Find spelling suggestions for a word."""
        pass

    @abstractmethod
    def get_words_with_prefix(self, prefix: str, max_results: int = 100) -> list[str]:
        """Get words starting with given prefix."""
        pass


# ============================================================================
# Granular Database Interfaces (Format-Agnostic)
# ============================================================================


class IPhoneticDatabase(ABC):
    """
    Interface for phonetic hash → words mapping database.

    This abstracts the storage format.
    """

    @abstractmethod
    def find_by_phonetic_hash(self, phonetic_hash: str) -> str | None:
        """
        Find words matching a phonetic hash.

        Args:
            phonetic_hash: The phonetic hash to look up

        Returns:
            Comma-separated string of matching words, or None if not found

        Example:
            >>> db.find_by_phonetic_hash("fjr")
            "fiere,fier,fjere"
        """
        pass

    @abstractmethod
    def get_words_by_phonetic_hash(self, phonetic_hash: str) -> list[str]:
        """
        Find words matching a phonetic hash, returned as a list.

        Args:
            phonetic_hash: The phonetic hash to look up

        Returns:
            List of matching words, or empty list if not found
        """
        pass

    @abstractmethod
    def has_phonetic_hash(self, phonetic_hash: str) -> bool:
        """Check if a phonetic hash exists in the database."""
        pass

    @abstractmethod
    def get_batch(self, phonetic_hashes: list[str]) -> dict[str, str]:
        """Batch lookup for multiple phonetic hashes."""
        pass


class IFrequencyDatabase(ABC):
    """
    Interface for word → frequency mapping database.

    This abstracts the storage format.
    """

    @abstractmethod
    def get_frequency(self, word: str) -> int:
        """
        Get frequency score for word.

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
        pass

    @abstractmethod
    def has_word(self, word: str) -> bool:
        """Check if word has a frequency entry."""
        pass


class IErrorDatabase(ABC):
    """
    Interface for error → correction mapping database.

    This abstracts the storage format.
    """

    @abstractmethod
    def get_correction(self, error_word: str) -> str | None:
        """
        Get correction for a known error.

        Args:
            error_word: The misspelled word

        Returns:
            Correct word, or None if not found

        Example:
            >>> db.get_correction("perchè")
            "parcè"
        """
        pass

    @abstractmethod
    def has_error(self, error_word: str) -> bool:
        """Check if error has a correction entry."""
        pass


class IElisionDatabase(ABC):
    """
    Interface for elision checking database.

    This abstracts the storage format.
    """

    @abstractmethod
    def has_elision(self, word: str) -> bool:
        """
        Check if word is a valid elision.

        Args:
            word: The word to check

        Returns:
            True if word is a valid elision, False otherwise

        Example:
            >>> db.has_elision("l")
            True
        """
        pass
