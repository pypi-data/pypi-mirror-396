"""Database interfaces for Friulian spell checker.

This module defines interfaces for accessing different types of databases:
- Phonetic dictionary
- Databases for errors, frequencies, elisions
- Binary radix tree for fast word lookups

The factory pattern allows transparent access to different database formats
without changing consuming code or tests.
"""

# Import enums and interfaces from interfaces module
# Import downloader
from .downloader import DatabaseDownloader, download_database, get_downloader

# Import factory
from .factory import DatabaseFactory
from .interfaces import (
    AddExceptionResult,
    AddWordResult,
    DatabaseFormat,
    DictionaryType,
    IElisionDatabase,
    IErrorDatabase,
    IFrequencyDatabase,
    IKeyValueDatabase,
    IPhoneticDatabase,
    IRadixTree,
    RemoveWordResult,
)
from .manager import DatabaseManager
from .radix_tree import BinaryRadixTree, RadixTreeDatabase

# Import implementations
from .sqlite_database import SQLiteKeyValueDatabase

__all__ = [
    # Enums
    "DictionaryType",
    "AddWordResult",
    "RemoveWordResult",
    "AddExceptionResult",
    "DatabaseFormat",
    # Interfaces
    "IKeyValueDatabase",
    "IRadixTree",
    "IPhoneticDatabase",
    "IFrequencyDatabase",
    "IErrorDatabase",
    "IElisionDatabase",
    # Factory
    "DatabaseFactory",
    # Downloader
    "DatabaseDownloader",
    "get_downloader",
    "download_database",
    # Implementations
    "SQLiteKeyValueDatabase",
    "BinaryRadixTree",
    "RadixTreeDatabase",
    # Manager
    "DatabaseManager",
]
