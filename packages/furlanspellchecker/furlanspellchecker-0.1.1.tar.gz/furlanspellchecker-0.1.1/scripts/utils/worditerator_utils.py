#!/usr/bin/env python3
"""
WordIterator Utilities - FurlanSpellChecker CLI utility

Provides command-line interface for word iteration debugging:
- Tokenize text and display tokens
- Show position information for each token
- Process text from files
- Limit output for large texts

Mirrors COF util/worditerator_utils.pl functionality.
"""

import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from furlan_spellchecker.spellchecker.text_processor import TextProcessor
except ImportError as e:
    print(f"Error importing TextProcessor: {e}", file=sys.stderr)
    sys.exit(1)


def process_text(text: str, limit: int = 25, raw: bool = False) -> int:
    """Process text and display word iteration results."""
    try:
        word_iterator = TextProcessor.WordIterator(text)

        print("# WordIterator Debug")
        print(f"# Limit: {limit}")
        print(f"# Raw mode: {'on' if raw else 'off'}")

        count = 0
        tokens = []

        for token in word_iterator:
            if count >= limit:
                break

            count += 1

            # Extract word from token
            if isinstance(token, dict):
                word = token.get("word", "<undef>")
                start = token.get("start")
                end = token.get("end")
            else:
                word = token if token else "<undef>"
                start = None
                end = None

            if raw:
                # Raw mode: show full token structure
                print(f"[{count:02d}] {repr(token)}")
            else:
                # Normal mode: show word and position
                pos_info = f" ({start},{end})" if start is not None and end is not None else ""
                print(f"[{count:02d}] {word}{pos_info}")

            tokens.append(token)

        # Test reset and ahead functionality (matching COF behavior)
        word_iterator = TextProcessor.WordIterator(text)
        peek_token = None
        try:
            # Get first token to test ahead
            for i, token in enumerate(word_iterator):
                if i == 0:
                    peek_token = token
                    break
        except Exception:
            pass

        if peek_token:
            if isinstance(peek_token, dict):
                peek_word = peek_token.get("word", "<none>")
            else:
                peek_word = peek_token if peek_token else "<none>"
            print(f"# After reset ahead(): {peek_word}")
        else:
            print("# After reset ahead(): <none>")

        return 0
    except Exception as e:
        print(f"Error processing text: {e}", file=sys.stderr)
        return 1


def process_file(file_path: Path, limit: int = 25, raw: bool = False) -> int:
    """Process text from a file."""
    if not file_path.exists():
        print(f"Error: File '{file_path}' not found", file=sys.stderr)
        return 1

    try:
        with open(file_path, encoding="utf-8") as f:
            text = f.read()

        if not text.strip():
            print("# WordIterator Debug")
            print(f"# Limit: {limit}")
            print(f"# Raw mode: {'on' if raw else 'off'}")
            print("# No tokens (empty file)")
            return 0

        return process_text(text, limit, raw)
    except Exception as e:
        print(f"Error processing file: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Main entry point for worditerator_utils CLI."""
    parser = argparse.ArgumentParser(
        description="FurlanSpellChecker WordIterator debugging utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --text "l'aghe e il cjât"
  %(prog)s --file sample.txt
  %(prog)s --text "Cjale il libri" --limit 10
  %(prog)s --text "Test" --raw
        """,
    )

    parser.add_argument("--text", "-t", help="Text to tokenize and analyze")
    parser.add_argument("--file", "-f", type=Path, help="File containing text to process (UTF-8)")
    parser.add_argument(
        "--limit",
        "-l",
        type=int,
        default=25,
        help="Maximum number of tokens to display (default: 25)",
    )
    parser.add_argument(
        "--raw", action="store_true", help="Show raw token structure instead of just word"
    )

    args = parser.parse_args()

    # Validate that at least one input method is specified
    if not any([args.text, args.file]):
        parser.print_help()
        print("\nError: Provide --text or --file", file=sys.stderr)
        return 1

    # Process based on input method
    if args.text:
        return process_text(args.text, args.limit, args.raw)
    elif args.file:
        return process_file(args.file, args.limit, args.raw)

    return 0


if __name__ == "__main__":
    sys.exit(main())
