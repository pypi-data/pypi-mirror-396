#!/usr/bin/env python3
"""
word_lookup.py - FurlanSpellChecker word lookup and metadata inspection utility

Utility for querying the FurlanSpellChecker database to check if specific words exist
and retrieve their associated metadata (frequency, phonetic code, suggestions, etc.).

Useful for:
- Debugging why specific words appear/don't appear in suggestions
- Comparing database content between COF and Python implementations
- Verifying word frequencies and phonetic codes
- Investigating ranking differences

Usage:
    python scripts/word_lookup.py --word WORD [options]
    python scripts/word_lookup.py --batch FILE [options]

Options:
    --help, -h          Show this help message
    --word, -w WORD     Look up a single word
    --batch, -b FILE    Look up words from file (one per line)
    --suggest, -s       Include suggestions for the word
    --phonetic, -p      Include phonetic code
    --similar, -m       Include similar words (within edit distance 1-2)
    --json              Output in JSON format
    --verbose, -v       Verbose output with all metadata

Examples:
    # Basic word lookup
    python scripts/word_lookup.py --word Cjas

    # Detailed lookup with suggestions and phonetic
    python scripts/word_lookup.py --word cjasa --suggest --phonetic

    # Check multiple words
    python scripts/word_lookup.py --batch words_to_check.txt

    # Full metadata with similar words
    python scripts/word_lookup.py --word furla --verbose --similar

    # JSON output for scripting
    python scripts/word_lookup.py --word cjase --json

Output:
For each word, displays:
- Existence in dictionary (radix tree)
- Frequency value (if exists)
- Phonetic code (if requested)
- Suggestions (if requested)
- Similar words (if requested)
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from furlan_spellchecker.config.schemas import FurlanSpellCheckerConfig
from furlan_spellchecker.dictionary.dictionary import Dictionary
from furlan_spellchecker.spellchecker.spell_checker import FurlanSpellChecker
from furlan_spellchecker.spellchecker.text_processor import TextProcessor


def create_spellchecker() -> FurlanSpellChecker:
    """Initialize the spell checker."""
    config = FurlanSpellCheckerConfig()
    dictionary = Dictionary()
    text_processor = TextProcessor()
    return FurlanSpellChecker(dictionary=dictionary, text_processor=text_processor, config=config)


def lookup_word_text(sc: FurlanSpellChecker, word: str, args: argparse.Namespace) -> None:
    """Display word lookup results in text format."""
    print("=" * 70)
    print(f"WORD LOOKUP: '{word}'")
    print("=" * 70)
    print()

    # Access database components
    db = sc._suggestion_engine.db

    # Check if word is correct by trying to find it in dictionary
    try:
        in_dict = db.radix_tree.find(word.lower()) is not None
        is_correct = in_dict
    except (AttributeError, KeyError):
        is_correct = False
    print(f"Correct spelling: {'YES [OK]' if is_correct else 'NO [X]'}")

    # Get frequency
    try:
        # Access frequency database through database manager
        if hasattr(db, "frequency_db"):
            frequency = db.frequency_db.get_frequency(word)
        elif hasattr(db, "word_frequencies"):
            frequency = db.word_frequencies.get_frequency(word)
        else:
            frequency = 0
    except (AttributeError, KeyError, Exception):
        frequency = 0
    print(f"Frequency: {frequency}")

    # Phonetic code
    if args.phonetic or args.verbose:
        try:
            if hasattr(db, "phonetic_db"):
                phonetic = db.phonetic_db.get_phonetic_code(word)
            else:
                phonetic = None
        except (AttributeError, KeyError, Exception):
            phonetic = None
        print(f"Phonetic code: {phonetic if phonetic else '(none)'}")

    # Get suggestions if requested
    if args.suggest or args.verbose:
        print("\nSuggestions:")
        try:
            suggestions = sc.suggest(word, max_suggestions=100 if args.verbose else 10)
            if not suggestions:
                print("  (none)")
            else:
                max_show = len(suggestions) if args.verbose else 10
                for i, sugg in enumerate(suggestions[:max_show], 1):
                    # Try to get frequency for each suggestion
                    try:
                        if hasattr(db, "frequency_db"):
                            sugg_freq = db.frequency_db.get_frequency(sugg)
                        elif hasattr(db, "word_frequencies"):
                            sugg_freq = db.word_frequencies.get_frequency(sugg)
                        else:
                            sugg_freq = 0
                    except Exception:
                        sugg_freq = 0
                    print(f"  {i:2d}. {sugg:20s} (frequency: {sugg_freq})")
                if len(suggestions) > max_show:
                    print(f"  ... and {len(suggestions) - max_show} more")
        except Exception as e:
            print(f"  Error getting suggestions: {e}")

    # Find similar words
    if args.similar or args.verbose:
        print("\nSimilar words in dictionary:")
        try:
            # Get suggestions as "similar words"
            suggestions = sc.suggest(word, max_suggestions=20)
            if not suggestions:
                print("  (none found)")
            else:
                for sugg in suggestions[:20]:
                    try:
                        if hasattr(db, "frequency_db"):
                            sugg_freq = db.frequency_db.get_frequency(sugg)
                        elif hasattr(db, "word_frequencies"):
                            sugg_freq = db.word_frequencies.get_frequency(sugg)
                        else:
                            sugg_freq = 0
                    except Exception:
                        sugg_freq = 0
                    print(f"  {sugg:20s} (frequency: {sugg_freq})")
                if len(suggestions) > 20:
                    print(f"  ... and {len(suggestions) - 20} more")
        except Exception as e:
            print(f"  Error finding similar words: {e}")

    print("=" * 70)


def lookup_word_json(sc: FurlanSpellChecker, word: str, args: argparse.Namespace) -> dict[str, Any]:
    """Return word lookup results as a dictionary for JSON output."""
    db = sc._suggestion_engine.db

    result: dict[str, Any] = {
        "word": word,
        "correct_spelling": False,
        "frequency": 0,
    }

    # Get frequency
    try:
        result["frequency"] = db.word_frequencies.get_frequency(word)
    except (AttributeError, KeyError):
        pass

    # Check correctness by finding in radix tree
    try:
        result["correct_spelling"] = db.radix_tree.find(word.lower()) is not None
    except Exception:
        pass

    # Phonetic code
    if args.phonetic or args.verbose:
        try:
            result["phonetic_code"] = db.phonetic_db.get_phonetic_code(word)
        except (AttributeError, KeyError):
            result["phonetic_code"] = None

    # Suggestions
    if args.suggest or args.verbose:
        try:
            result["suggestions"] = sc.suggest(word, max_suggestions=100 if args.verbose else 10)
        except Exception:
            result["suggestions"] = []

    # Similar words
    if args.similar or args.verbose:
        try:
            result["similar_words"] = sc.suggest(word, max_suggestions=20)
        except Exception:
            result["similar_words"] = []

    return result


def main():
    parser = argparse.ArgumentParser(
        description="FurlanSpellChecker word lookup and metadata inspection utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--word", "-w", help="Look up a single word")
    parser.add_argument("--batch", "-b", help="Look up words from file (one per line)")
    parser.add_argument("--suggest", "-s", action="store_true", help="Include suggestions")
    parser.add_argument("--phonetic", "-p", action="store_true", help="Include phonetic code")
    parser.add_argument("--similar", "-m", action="store_true", help="Include similar words")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output with all metadata"
    )

    args = parser.parse_args()

    # Require at least one word source
    if not args.word and not args.batch:
        parser.error("Must specify --word or --batch")

    # Collect words to check
    words_to_check: list[str] = []
    if args.word:
        words_to_check.append(args.word)
    if args.batch:
        try:
            with open(args.batch, encoding="utf-8") as f:
                for line in f:
                    word = line.strip()
                    if word:
                        words_to_check.append(word)
        except OSError as e:
            print(f"Error: Cannot open batch file '{args.batch}': {e}", file=sys.stderr)
            sys.exit(1)

    # Initialize spell checker
    try:
        sc = create_spellchecker()
    except Exception as e:
        print(f"Error: Cannot initialize FurlanSpellChecker: {e}", file=sys.stderr)
        sys.exit(1)

    # Process words
    if args.json:
        results = [lookup_word_json(sc, word, args) for word in words_to_check]
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        for word in words_to_check:
            lookup_word_text(sc, word, args)
            if len(words_to_check) > 1:
                print()


if __name__ == "__main__":
    main()
