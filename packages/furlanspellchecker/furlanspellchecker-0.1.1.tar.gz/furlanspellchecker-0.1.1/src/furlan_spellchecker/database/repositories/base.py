"""Repository pattern base classes for database access."""

from abc import ABC, abstractmethod
from typing import Literal

from ..interfaces import (
    IElisionDatabase,
    IErrorDatabase,
    IFrequencyDatabase,
    IPhoneticDatabase,
)


class BaseRepository(ABC):
    """Abstract base class for all repositories."""

    @abstractmethod
    def get(self, key: str) -> str | None:
        """Get value by key."""
        pass

    @abstractmethod
    def has(self, key: str) -> bool:
        """Check if key exists."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Release resources."""
        pass

    def __enter__(self) -> "BaseRepository":
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> Literal[False]:
        self.close()
        return False


class IPhoneticRepository(BaseRepository, IPhoneticDatabase):
    """Repository for phonetic hash -> words mapping."""

    @abstractmethod
    def get_words_list(self, phonetic_hash: str) -> list[str]:
        """Get words as list instead of comma-separated string."""
        pass

    @abstractmethod
    def get_batch(self, phonetic_hashes: list[str]) -> dict[str, str]:
        """Retrieve multiple phonetic hashes in a single call."""
        pass


class IFrequencyRepository(BaseRepository, IFrequencyDatabase):
    """Repository for word -> frequency mapping."""

    @abstractmethod
    def get_frequency(self, word: str) -> int:
        """Get frequency score (0 if not found)."""
        pass


class IErrorRepository(BaseRepository, IErrorDatabase):
    """Repository for error -> correction mapping."""

    @abstractmethod
    def get_correction(self, error_word: str) -> str | None:
        """Get correction for error word."""
        pass


class IElisionRepository(BaseRepository, IElisionDatabase):
    """Repository for elision word checking."""

    @abstractmethod
    def has_elision(self, word: str) -> bool:
        """Check if word is valid elision."""
        pass
