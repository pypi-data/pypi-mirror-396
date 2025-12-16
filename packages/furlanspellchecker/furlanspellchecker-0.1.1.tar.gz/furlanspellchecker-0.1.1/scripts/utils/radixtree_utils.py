#!/usr/bin/env python3
"""
RadixTree Utilities - FurlanSpellChecker CLI utility

Provides command-line interface for RadixTree operations:
- Get edit-distance-1 suggestions for words
- Process words from files
- Output in various formats (list, array, json)

Mirrors COF util/radixtree_utils.pl functionality.
"""

import argparse
import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from furlan_spellchecker.config import FurlanSpellCheckerConfig
    from furlan_spellchecker.database.radix_tree import RadixTreeDatabase
except ImportError as e:
    print(f"Error importing RadixTreeDatabase: {e}", file=sys.stderr)
    sys.exit(1)


def create_radix_tree() -> RadixTreeDatabase | None:
    """Create and initialize RadixTreeDatabase instance."""
    try:
        config = FurlanSpellCheckerConfig()
        radix_tree_path = config.get_radix_tree_path()

        if not radix_tree_path.exists():
            print(f"Error: RadixTree database not found at '{radix_tree_path}'", file=sys.stderr)
            return None

        return RadixTreeDatabase(radix_tree_path)
    except Exception as e:
        print(f"Error initializing RadixTree: {e}", file=sys.stderr)
        return None


def process_word(radix_tree: RadixTreeDatabase, word: str, format_type: str = "list") -> int:
    """Process a single word and output edit-distance-1 suggestions."""
    try:
        suggestions = radix_tree.get_words_ed1(word)

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


def process_file(radix_tree: RadixTreeDatabase, file_path: Path, format_type: str = "list") -> int:
    """Process words from a file."""
    if not file_path.exists():
        print(f"Error: File '{file_path}' not found", file=sys.stderr)
        return 1

    try:
        with open(file_path, encoding="utf-8") as f:
            words = [line.strip() for line in f if line.strip()]

        if not words:
            # Empty file handling - COF exits 1 for radixtree_utils.pl
            print("Error: No words found in file", file=sys.stderr)
            return 1

        all_suggestions = []
        for word in words:
            suggestions = radix_tree.get_words_ed1(word)
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
    """Main entry point for radixtree_utils CLI."""
    parser = argparse.ArgumentParser(
        description="FurlanSpellChecker RadixTree CLI utility for edit-distance operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --word cjupe
  %(prog)s --file wordlist.txt
  %(prog)s --word cjase --format json
        """,
    )

    parser.add_argument("--word", "-w", help="Get edit-distance-1 suggestions for a word")
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
    if not any([args.word, args.file]):
        parser.print_help()
        print("\nError: Specify --word or --file", file=sys.stderr)
        return 1

    # Initialize RadixTree
    radix_tree = create_radix_tree()
    if radix_tree is None:
        return 1

    # Process based on input method
    if args.word:
        return process_word(radix_tree, args.word, args.format)
    elif args.file:
        return process_file(radix_tree, args.file, args.format)

    return 0


if __name__ == "__main__":
    sys.exit(main())
