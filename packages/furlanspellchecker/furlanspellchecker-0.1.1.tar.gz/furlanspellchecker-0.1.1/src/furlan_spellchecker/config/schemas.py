"""Configuration schemas and dataclasses for FurlanSpellChecker."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DictionaryConfig:
    """Configuration for dictionary settings."""

    main_dictionary_path: str | None = None
    user_dictionary_path: str | None = None
    cache_directory: str | None = None
    auto_load_user_dict: bool = True
    max_suggestions: int = 10
    use_phonetic_suggestions: bool = True


@dataclass
class SpellCheckerConfig:
    """Configuration for spell checker behavior."""

    ignore_capitalized: bool = False
    ignore_all_caps: bool = False
    ignore_numbers: bool = True
    ignore_mixed_case: bool = False
    min_word_length: int = 2
    auto_correct: bool = False


@dataclass
class TextProcessingConfig:
    """Configuration for text processing."""

    preserve_formatting: bool = True
    split_contractions: bool = True
    handle_abbreviations: bool = True
    custom_tokenization_rules: dict[str, str] | None = None

    def __post_init__(self) -> None:
        """Post-init processing."""
        if self.custom_tokenization_rules is None:
            self.custom_tokenization_rules = {}


@dataclass
class PhoneticConfig:
    """Configuration for phonetic algorithm."""

    algorithm_variant: str = "standard"
    similarity_threshold: float = 0.8
    enable_dialect_variants: bool = True
    custom_rules: dict[str, str] | None = None

    def __post_init__(self) -> None:
        """Post-init processing."""
        if self.custom_rules is None:
            self.custom_rules = {}


@dataclass
class FurlanSpellCheckerConfig:
    """Main configuration class for FurlanSpellChecker."""

    dictionary: DictionaryConfig = field(default_factory=DictionaryConfig)
    spell_checker: SpellCheckerConfig = field(default_factory=SpellCheckerConfig)
    text_processing: TextProcessingConfig = field(default_factory=TextProcessingConfig)
    phonetic: PhoneticConfig = field(default_factory=PhoneticConfig)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FurlanSpellCheckerConfig:
        """Create configuration from dictionary."""
        dictionary_data = data.get("dictionary", {})
        spell_checker_data = data.get("spell_checker", {})
        text_processing_data = data.get("text_processing", {})
        phonetic_data = data.get("phonetic", {})

        return cls(
            dictionary=DictionaryConfig(**dictionary_data),
            spell_checker=SpellCheckerConfig(**spell_checker_data),
            text_processing=TextProcessingConfig(**text_processing_data),
            phonetic=PhoneticConfig(**phonetic_data),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "dictionary": {
                "main_dictionary_path": self.dictionary.main_dictionary_path,
                "user_dictionary_path": self.dictionary.user_dictionary_path,
                "cache_directory": self.dictionary.cache_directory,
                "auto_load_user_dict": self.dictionary.auto_load_user_dict,
                "max_suggestions": self.dictionary.max_suggestions,
                "use_phonetic_suggestions": self.dictionary.use_phonetic_suggestions,
            },
            "spell_checker": {
                "ignore_capitalized": self.spell_checker.ignore_capitalized,
                "ignore_all_caps": self.spell_checker.ignore_all_caps,
                "ignore_numbers": self.spell_checker.ignore_numbers,
                "ignore_mixed_case": self.spell_checker.ignore_mixed_case,
                "min_word_length": self.spell_checker.min_word_length,
                "auto_correct": self.spell_checker.auto_correct,
            },
            "text_processing": {
                "preserve_formatting": self.text_processing.preserve_formatting,
                "split_contractions": self.text_processing.split_contractions,
                "handle_abbreviations": self.text_processing.handle_abbreviations,
                "custom_tokenization_rules": self.text_processing.custom_tokenization_rules,
            },
            "phonetic": {
                "algorithm_variant": self.phonetic.algorithm_variant,
                "similarity_threshold": self.phonetic.similarity_threshold,
                "enable_dialect_variants": self.phonetic.enable_dialect_variants,
                "custom_rules": self.phonetic.custom_rules,
            },
        }
