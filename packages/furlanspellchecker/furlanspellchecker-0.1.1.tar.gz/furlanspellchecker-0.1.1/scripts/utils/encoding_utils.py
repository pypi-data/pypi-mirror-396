#!/usr/bin/env python3
"""
Encoding Utilities - FurlanSpellChecker CLI utility

Provides command-line interface for encoding diagnostics:
- Inspect UTF-8 encoding of words
- Display Unicode code points
- Show hex representation
- Process words from files or suggestions

Mirrors COF util/encoding_utils.pl functionality.
"""

import argparse
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


def display_encoding_info(
    words: list[str],
    show_hex: bool = True,
    show_unicode: bool = True,
    show_index: bool = True,
    list_only: bool = False,
) -> None:
    """Display encoding information for words."""
    if list_only:
        for word in words:
            print(word)
        return

    print("=== ENCODING DEBUG ===")
    print(f"Items: {len(words)}\n")

    for i, word in enumerate(words, 1):
        cols = []

        if show_index:
            cols.append(f"{i:2d}")

        cols.append(word)

        if show_hex:
            hex_str = word.encode("utf-8").hex()
            cols.append(f"UTF-8: {hex_str}")

        if show_unicode:
            unicode_str = " ".join(f"U+{ord(c):04X}" for c in word)
            cols.append(f"Unicode: {unicode_str}")

        print(" | ".join(cols))

    # Character summary for interesting characters
    interesting_chars = {"þ", "ç", "à", "è", "é", "ì", "î", "ò", "ù", "û", "ñ"}
    found_interesting = False

    for word in words:
        for ch in word:
            if ch in interesting_chars:
                if not found_interesting:
                    print("\n=== CHARACTER SUMMARY ===")
                    found_interesting = True
                hex_repr = ch.encode("utf-8").hex()
                print(f"Found in '{word}': {ch} (U+{ord(ch):04X}, UTF-8: {hex_repr})")


def process_word(word: str, **display_args) -> int:
    """Process a single word."""
    try:
        display_encoding_info([word], **display_args)
        return 0
    except Exception as e:
        print(f"Error processing word: {e}", file=sys.stderr)
        return 1


def process_file(file_path: Path, **display_args) -> int:
    """Process words from a file."""
    if not file_path.exists():
        print(f"Error: File '{file_path}' not found", file=sys.stderr)
        return 1

    try:
        with open(file_path, encoding="utf-8") as f:
            words = [line.strip() for line in f if line.strip()]

        if not words:
            # Empty file handling - COF exits 1 for encoding_utils.pl
            print("Error: No words found in file", file=sys.stderr)
            return 1

        display_encoding_info(words, **display_args)
        return 0
    except Exception as e:
        print(f"Error processing file: {e}", file=sys.stderr)
        return 1


def process_suggestions(word: str, **display_args) -> int:
    """Get suggestions for a word and display their encoding."""
    try:
        config = FurlanSpellCheckerConfig()
        dictionary = Dictionary()
        text_processor = TextProcessor()
        spellchecker = FurlanSpellChecker(
            dictionary=dictionary, text_processor=text_processor, config=config
        )

        suggestions = spellchecker.suggest(word)

        if not suggestions:
            print(f"No suggestions found for '{word}'")
            return 0

        display_encoding_info(suggestions, **display_args)
        return 0
    except Exception as e:
        print(f"Error getting suggestions: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Main entry point for encoding_utils CLI."""
    parser = argparse.ArgumentParser(
        description="FurlanSpellChecker encoding diagnostics utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --word cjàse
  %(prog)s --suggest cjupe
  %(prog)s --file wordlist.txt --nohex
  %(prog)s --word furlan --list
        """,
    )

    parser.add_argument("--word", "-w", help="Inspect encoding of a single word")
    parser.add_argument(
        "--suggest", "-s", help="Get suggestions for a word and show their encoding"
    )
    parser.add_argument("--file", "-f", type=Path, help="Process words from file (one per line)")
    parser.add_argument("--nohex", action="store_true", help="Do not show hex representation")
    parser.add_argument("--nounicode", action="store_true", help="Do not show Unicode code points")
    parser.add_argument("--noindex", action="store_true", help="Do not show line numbers")
    parser.add_argument("--list", action="store_true", help="Output words only (no encoding info)")

    args = parser.parse_args()

    # Validate that at least one input method is specified
    if not any([args.word, args.suggest, args.file]):
        parser.print_help()
        print("\nError: Specify --word, --suggest, or --file", file=sys.stderr)
        return 1

    # Prepare display arguments
    display_args = {
        "show_hex": not args.nohex,
        "show_unicode": not args.nounicode,
        "show_index": not args.noindex,
        "list_only": args.list,
    }

    # Process based on input method
    if args.word:
        return process_word(args.word, **display_args)
    elif args.suggest:
        return process_suggestions(args.suggest, **display_args)
    elif args.file:
        return process_file(args.file, **display_args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
