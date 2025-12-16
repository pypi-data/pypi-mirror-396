"""FurlanSpellChecker public API."""

from __future__ import annotations

from .__about__ import __version__
from .config import (
    DictionaryConfig,
    FurlanSpellCheckerConfig,
    PhoneticConfig,
    SpellCheckerConfig,
    TextProcessingConfig,
)
from .core.interfaces import (
    IDictionary,
    IPhoneticAlgorithm,
    ISpellChecker,
    ITextProcessor,
)
from .database import (
    AddWordResult,
    BinaryRadixTree,
    DatabaseManager,
    DictionaryType,
    RadixTreeDatabase,
    SQLiteKeyValueDatabase,
)
from .dictionary import Dictionary
from .entities import IProcessedElement, ProcessedPunctuation, ProcessedWord
from .phonetic import FurlanPhoneticAlgorithm
from .services import IOService, SpellCheckPipeline
from .services.dictionary_manager import DictionaryManager
from .spellchecker import FurlanSpellChecker, TextProcessor

version = __version__

__all__ = [
    "version",
    # Core interfaces
    "ISpellChecker",
    "IDictionary",
    "IPhoneticAlgorithm",
    "ITextProcessor",
    # Main implementations
    "FurlanSpellChecker",
    "TextProcessor",
    "Dictionary",
    "FurlanPhoneticAlgorithm",
    # Entities
    "IProcessedElement",
    "ProcessedWord",
    "ProcessedPunctuation",
    # Services
    "SpellCheckPipeline",
    "IOService",
    "DictionaryManager",
    # Database
    "DatabaseManager",
    "SQLiteKeyValueDatabase",
    "BinaryRadixTree",
    "RadixTreeDatabase",
    "DictionaryType",
    "AddWordResult",
    # Configuration
    "FurlanSpellCheckerConfig",
    "DictionaryConfig",
    "SpellCheckerConfig",
    "TextProcessingConfig",
    "PhoneticConfig",
]
