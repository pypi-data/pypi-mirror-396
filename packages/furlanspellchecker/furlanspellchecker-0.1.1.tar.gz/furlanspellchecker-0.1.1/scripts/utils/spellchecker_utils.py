#!/usr/bin/env python3
"""
Spell Checker Utilities - FurlanSpellChecker CLI utility

Provides command-line interface for spell checking operations:
- Check individual words
- Get suggestions for misspelled words
- Process words from files
- Output in various formats (list, array, json)

Mirrors COF util/spellchecker_utils.pl functionality.
"""

import argparse
import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from furlan_spellchecker import FurlanSpellChecker
    from furlan_spellchecker.config import FurlanSpellCheckerConfig
    from furlan_spellchecker.dictionary import Dictionary
    from furlan_spellchecker.spellchecker.text_processor import TextProcessor
except ImportError as e:
    print(f"Error importing FurlanSpellChecker: {e}", file=sys.stderr)
    sys.exit(1)


def create_spellchecker() -> FurlanSpellChecker | None:
    """Create and initialize FurlanSpellChecker instance."""
    try:
        config = FurlanSpellCheckerConfig()
        dictionary = Dictionary()
        text_processor = TextProcessor()
        return FurlanSpellChecker(
            dictionary=dictionary, text_processor=text_processor, config=config
        )
    except Exception as e:
        print(f"Error initializing spellchecker: {e}", file=sys.stderr)
        return None


def process_word(spellchecker: FurlanSpellChecker, word: str, format_type: str = "list") -> int:
    """Process a single word and output results."""
    try:
        suggestions = spellchecker.suggest(word)

        if format_type == "json":
            result = {"word": word, "suggestions": suggestions}
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif format_type == "array":
            print(f"Array for test: [{', '.join(repr(s) for s in suggestions)}]")
            print(f"Count: {len(suggestions)}")
        else:  # list
            for suggestion in suggestions:
                print(suggestion)
            if not suggestions:
                print("No suggestions found.")

        return 0
    except Exception as e:
        print(f"Error processing word '{word}': {e}", file=sys.stderr)
        return 1


def process_file(
    spellchecker: FurlanSpellChecker, file_path: Path, format_type: str = "list"
) -> int:
    """Process words from a file."""
    if not file_path.exists():
        print(f"Error: File '{file_path}' not found", file=sys.stderr)
        return 1

    try:
        with open(file_path, encoding="utf-8") as f:
            words = [line.strip() for line in f if line.strip()]

        if not words:
            # Empty file handling - COF exits 0 for spellchecker_utils.pl
            return 0

        all_suggestions = []
        for word in words:
            suggestions = spellchecker.suggest(word)
            all_suggestions.append({"word": word, "suggestions": suggestions})

        if format_type == "json":
            print(json.dumps(all_suggestions, ensure_ascii=False, indent=2))
        elif format_type == "array":
            flat_suggestions = [s for item in all_suggestions for s in item["suggestions"]]
            print(f"Array for test: [{', '.join(repr(s) for s in flat_suggestions)}]")
            print(f"Count: {len(flat_suggestions)}")
        else:  # list
            for item in all_suggestions:
                for suggestion in item["suggestions"]:
                    print(suggestion)

        return 0
    except Exception as e:
        print(f"Error processing file '{file_path}': {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Main entry point for spellchecker_utils CLI."""
    parser = argparse.ArgumentParser(
        description="FurlanSpellChecker CLI utility for spell checking operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --word cjupe
  %(prog)s --suggest furla
  %(prog)s --file wordlist.txt
  %(prog)s --word cjase --format json
        """,
    )

    parser.add_argument("--word", "-w", help="Check spelling of a single word")
    parser.add_argument(
        "--suggest", "-s", help="Get suggestions for a misspelled word (alias for --word)"
    )
    parser.add_argument("--file", "-f", type=Path, help="Process words from file (one per line)")
    parser.add_argument(
        "--format",
        choices=["list", "array", "json"],
        default="list",
        help="Output format (default: list)",
    )
    parser.add_argument("--list", action="store_true", help="Output as list (default behavior)")

    args = parser.parse_args()

    # Validate that at least one input method is specified
    if not any([args.word, args.suggest, args.file]):
        parser.print_help()
        print("\nError: Specify --word, --suggest, or --file", file=sys.stderr)
        return 1

    # Initialize spellchecker
    spellchecker = create_spellchecker()
    if spellchecker is None:
        return 1

    # Process based on input method
    if args.word or args.suggest:
        word = args.word or args.suggest
        return process_word(spellchecker, word, args.format)
    elif args.file:
        return process_file(spellchecker, args.file, args.format)

    return 0


if __name__ == "__main__":
    sys.exit(main())
