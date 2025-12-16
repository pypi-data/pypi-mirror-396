"""
Localization support for CLI interface.

This module provides internationalization (i18n) support for the FurlanSpellChecker CLI,
allowing users to interact with the application in their preferred language.
"""

import json
from enum import Enum
from pathlib import Path


class Language(Enum):
    """Supported languages for the CLI interface."""

    ENGLISH = "en"
    FRIULIAN = "fur"
    ITALIAN = "it"


class Localization:
    """Manages localization strings for the CLI interface."""

    _strings: dict[str, str] = {}
    _current_language: Language = Language.ENGLISH

    @classmethod
    def load_strings(cls, language: Language) -> None:
        """
        Load localization strings for the specified language.

        Args:
            language: The language to load strings for

        Raises:
            FileNotFoundError: If the localization file doesn't exist
            json.JSONDecodeError: If the localization file is invalid
        """
        localization_dir = Path(__file__).parent / "localization"
        file_path = localization_dir / f"{language.value}.json"

        if not file_path.exists():
            raise FileNotFoundError(f"Localization file not found: {file_path}")

        with open(file_path, encoding="utf-8") as f:
            cls._strings = json.load(f)

        cls._current_language = language

    @classmethod
    def get(cls, key: str, default: str = "") -> str:
        """
        Get a localized string by key.

        Args:
            key: The string key to retrieve
            default: Default value if key not found

        Returns:
            The localized string, or default if not found
        """
        return cls._strings.get(key, default)

    @classmethod
    def select_language(cls) -> Language:
        """
        Prompt the user to select their preferred language.

        Returns:
            The selected language
        """
        print("\nSelect language / Sielç lenghe / Seleziona lingua:")
        print("1. English")
        print("2. Furlan")
        print("3. Italiano")

        while True:
            try:
                choice = input("\nYour choice / La tô sielte / La tua scelta (1-3): ").strip()

                if choice == "1":
                    return Language.ENGLISH
                elif choice == "2":
                    return Language.FRIULIAN
                elif choice == "3":
                    return Language.ITALIAN
                else:
                    print("Invalid choice. Please enter 1, 2, or 3.")
                    print("Sielte no valide. Scrîf 1, 2 o 3.")
                    print("Scelta non valida. Inserisci 1, 2 o 3.")
            except (EOFError, KeyboardInterrupt):
                print("\nDefaulting to English / Par impostazion Inglês / Predefinito Inglese")
                return Language.ENGLISH

    @classmethod
    def get_current_language(cls) -> Language:
        """
        Get the currently selected language.

        Returns:
            The current language
        """
        return cls._current_language


# Initialize with English by default
Localization.load_strings(Language.ENGLISH)
