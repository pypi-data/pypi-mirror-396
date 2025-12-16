"""Repository pattern implementations for database access."""

from .base import (
    BaseRepository,
    IElisionRepository,
    IErrorRepository,
    IFrequencyRepository,
    IPhoneticRepository,
)
from .cached import (
    CachedElisionRepository,
    CachedErrorRepository,
    CachedFrequencyRepository,
    CachedPhoneticRepository,
    CachedRepository,
    LRUCache,
)
from .sqlite import (
    InMemoryElisionRepository,
    SQLiteElisionRepository,
    SQLiteErrorRepository,
    SQLiteFrequencyRepository,
    SQLitePhoneticRepository,
)

__all__ = [
    # Base
    "BaseRepository",
    "IPhoneticRepository",
    "IFrequencyRepository",
    "IErrorRepository",
    "IElisionRepository",
    # SQLite
    "SQLitePhoneticRepository",
    "SQLiteFrequencyRepository",
    "SQLiteErrorRepository",
    "SQLiteElisionRepository",
    "InMemoryElisionRepository",
    # Cached
    "LRUCache",
    "CachedRepository",
    "CachedPhoneticRepository",
    "CachedFrequencyRepository",
    "CachedErrorRepository",
    "CachedElisionRepository",
]
