"""Command-line interface for FurlanSpellChecker."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any

import click

from ..config.manager import ConfigManager
from ..config.schemas import FurlanSpellCheckerConfig
from ..database import DatabaseManager, DictionaryType
from ..dictionary import Dictionary
from ..services import IOService, SpellCheckPipeline
from ..services.dictionary_manager import DictionaryManager
from ..spellchecker.spell_checker import FurlanSpellChecker
from ..spellchecker.text_processor import TextProcessor
from .ascii_logo import print_logo, print_title
from .cof_protocol import COFProtocol
from .colors import Color, init_colors, is_color_available, write_colored
from .localization import Language, Localization


@click.group()
@click.version_option()
@click.pass_context
def main(ctx: click.Context) -> None:
    """Friulian Spell Checker - A spell checker for the Friulian language."""
    ctx.ensure_object(dict)


@main.command()
@click.argument("text", type=str)
@click.option("--dictionary", "-d", type=click.Path(exists=True), help="Path to dictionary file")
@click.option("--output", "-o", type=click.Path(), help="Output file for results")
@click.option(
    "--format", "-f", type=click.Choice(["text", "json"]), default="text", help="Output format"
)
def check(text: str, dictionary: str | None, output: str | None, format: str) -> None:
    """Check spelling of the given text."""
    # Initialize pipeline
    dict_obj = Dictionary()
    if dictionary:
        dict_obj.load_dictionary(dictionary)

    pipeline = SpellCheckPipeline(dictionary=dict_obj)

    # Check text
    result = pipeline.check_text(text)

    # Format output
    if format == "json":
        import json

        output_content = json.dumps(result, ensure_ascii=False, indent=2)
    else:
        output_content = _format_text_result(result)

    # Write output
    if output:
        IOService.write_text_file(output, output_content)
        click.echo(f"Results written to: {output}")
    else:
        click.echo(output_content)


@main.command("download-dicts")
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    default=False,
    help="Automatically accept download prompts",
)
@click.option(
    "--cache-dir",
    type=click.Path(),
    default=None,
    help="Override default cache directory to store dictionaries",
)
def download_dicts(yes: bool, cache_dir: str | None) -> None:
    """Download required dictionary artifacts using DictionaryManager."""
    cfg = ConfigManager.load()
    # allow CLI override
    cache_path = cache_dir or cfg.get("dictionary_cache_dir")
    cache_path_obj = Path(cache_path) if cache_path else None

    manager = DictionaryManager(cache_dir=cache_path_obj)

    # simple prompt
    if not yes:
        click.echo("Dictionaries are required but not present. This will download ~100+ MB.")
        ok = click.confirm("Do you want to download now?", default=True)
        if not ok:
            click.echo("Aborted by user.")
            return

    try:
        manager.install_from_manifest()
        click.echo("Dictionaries installed successfully.")
        # persist chosen cache dir
        if cache_path:
            cfg["dictionary_cache_dir"] = str(cache_path)
            ConfigManager.save(cfg)
    except Exception as e:
        click.echo(f"Failed to install dictionaries: {e}", err=True)
        raise


@main.command("db-status")
@click.option(
    "--cache-dir",
    type=click.Path(),
    default=None,
    help="Override default cache directory to check",
)
def db_status(cache_dir: str | None) -> None:
    """Check status of database files."""
    # Load config and override cache dir if provided
    cfg = ConfigManager.load()
    config = FurlanSpellCheckerConfig()

    if cache_dir:
        config.dictionary.cache_directory = cache_dir
    elif cfg.get("dictionary_cache_dir"):
        config.dictionary.cache_directory = cfg["dictionary_cache_dir"]

    db_manager = DatabaseManager(config)

    # Check availability
    availability = db_manager.ensure_databases_available()
    missing = db_manager.get_missing_databases()

    click.echo("Database Status:")
    click.echo("=" * 50)
    click.echo(f"Cache directory: {db_manager._cache_dir}")

    for db_type in DictionaryType:
        is_available = availability.get(db_type, False)
        status = "✓ Available" if is_available else "✗ Missing"
        click.echo(f"{db_type.value:20} {status}")

        if db_type in missing:
            click.echo(f"  Expected at: {missing[db_type]}")

    click.echo()
    if missing:
        click.echo(f"Missing {len(missing)} required databases.")
        click.echo("Run 'furlan-spellchecker download-dicts' to install them.")
    else:
        click.echo("All required databases are available!")


@main.command("extract-dicts")
@click.option(
    "--cache-dir",
    type=click.Path(),
    default=None,
    help="Override default cache directory",
)
def extract_dicts(cache_dir: str | None) -> None:
    """Extract dictionary ZIP files from data/databases/ to cache directory."""
    cfg = ConfigManager.load()
    cache_path = cache_dir or cfg.get("dictionary_cache_dir")
    cache_path_obj = Path(cache_path) if cache_path else None

    manager = DictionaryManager(cache_dir=cache_path_obj)

    click.echo("Checking for ZIP files in data/databases/...")

    # Check for local ZIP files
    repo_data_dir = Path.cwd() / "data" / "databases"
    if not repo_data_dir.exists():
        click.echo(f"Directory not found: {repo_data_dir}")
        click.echo("Make sure you're running from the repository root.")
        return

    zip_files = list(repo_data_dir.glob("*.zip"))
    if not zip_files:
        click.echo("No ZIP files found in data/databases/")
        return

    click.echo(f"Found {len(zip_files)} ZIP files:")
    for zip_file in zip_files:
        click.echo(f"  - {zip_file.name}")

    # Create manifest for local files
    import hashlib

    artifacts = []

    for zip_file in zip_files:
        name = zip_file.stem  # Remove .zip extension
        sha256 = hashlib.sha256(zip_file.read_bytes()).hexdigest()
        url = zip_file.as_uri()  # file:// URL

        artifacts.append({"name": name, "url": url, "sha256": sha256, "split": False})

    manifest = {"artifacts": artifacts}

    click.echo("\nExtracting ZIP files...")
    try:
        installed = manager.install_from_manifest(manifest)
        click.echo(f"Successfully extracted {len(installed)} archives:")
        for path in installed:
            click.echo(f"  - {path}")

        # Update config
        if cache_path:
            cfg["dictionary_cache_dir"] = str(cache_path)
            ConfigManager.save(cfg)

        # Check database status after extraction
        click.echo("\nChecking database status...")
        config = FurlanSpellCheckerConfig()
        config.dictionary.cache_directory = cache_path or config.dictionary.cache_directory

        db_manager = DatabaseManager(config)
        availability = db_manager.ensure_databases_available()

        available_count = sum(1 for available in availability.values() if available)
        total_count = len(availability)

        click.echo(f"Databases available: {available_count}/{total_count}")

    except Exception as e:
        click.echo(f"Error extracting dictionaries: {e}", err=True)
        raise


@main.command()
@click.argument("word", type=str)
@click.option("--dictionary", "-d", type=click.Path(exists=True), help="Path to dictionary file")
@click.option(
    "--max-suggestions", "-n", type=int, default=10, help="Maximum number of suggestions to show"
)
def suggest(word: str, dictionary: str | None, max_suggestions: int) -> None:
    """Get spelling suggestions for a word."""
    # Initialize pipeline
    dict_obj = Dictionary()
    if dictionary:
        dict_obj.load_dictionary(dictionary)

    pipeline = SpellCheckPipeline(dictionary=dict_obj)

    # Get suggestions
    try:
        suggestions = asyncio.run(pipeline.get_suggestions(word, max_suggestions))

        if suggestions:
            click.echo(f"Suggestions for '{word}':")
            for i, suggestion in enumerate(suggestions, 1):
                click.echo(f"  {i}. {suggestion}")
        else:
            click.echo(f"No suggestions found for '{word}'")

    except Exception as e:
        click.echo(f"Error getting suggestions: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("word", type=str)
@click.option("--dictionary", "-d", type=click.Path(exists=True), help="Path to dictionary file")
def lookup(word: str, dictionary: str | None) -> None:
    """Check if a word is in the dictionary."""
    # Load config and initialize database-integrated spell checker
    ConfigManager.load()
    config = FurlanSpellCheckerConfig()

    if dictionary:
        config.dictionary.main_dictionary_path = dictionary

    # Check word
    try:
        from ..entities import ProcessedWord
        from ..spellchecker import FurlanSpellChecker

        text_processor = TextProcessor()
        dictionary_obj = Dictionary()
        if dictionary:
            dictionary_obj.load_dictionary(dictionary)

        spell_checker = FurlanSpellChecker(dictionary_obj, text_processor, config)
        processed_word = ProcessedWord(word)

        asyncio.run(spell_checker.check_word(processed_word))

        if processed_word.correct:
            click.echo(f"✓ '{word}' is correct")
        else:
            click.echo(f"✗ '{word}' is not found in dictionary")

            # TODO: Add suggestion functionality when implemented

    except Exception as e:
        click.echo(f"Error checking word: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file for corrected text")
@click.option("--dictionary", "-d", type=click.Path(exists=True), help="Path to dictionary file")
def file(input_file: str, output: str | None, dictionary: str | None) -> None:
    """Check spelling of text from a file."""
    try:
        # Read input file
        text = IOService.read_text_file(input_file)

        # Initialize pipeline
        dict_obj = Dictionary()
        if dictionary:
            dict_obj.load_dictionary(dictionary)

        pipeline = SpellCheckPipeline(dictionary=dict_obj)

        # Check text
        result = pipeline.check_text(text)

        # Write output
        if output:
            IOService.write_text_file(output, result["processed_text"])
            click.echo(f"Corrected text written to: {output}")
        else:
            click.echo("Corrected text:")
            click.echo(result["processed_text"])

        # Show summary
        click.echo("\nSummary:")
        click.echo(f"  Total words: {result['total_words']}")
        click.echo(f"  Incorrect words: {result['incorrect_count']}")

        if result["incorrect_words"]:
            click.echo("  Incorrect words found:")
            for word_info in result["incorrect_words"]:
                click.echo(f"    - {word_info['original']}")

    except Exception as e:
        click.echo(f"Error processing file: {e}", err=True)
        sys.exit(1)


def _format_text_result(result: dict[str, Any]) -> str:
    """Format spell check result as text."""
    lines = [
        f"Original text: {result['original_text']}",
        f"Processed text: {result['processed_text']}",
        f"Total words: {result['total_words']}",
        f"Incorrect words: {result['incorrect_count']}",
    ]

    if result["incorrect_words"]:
        lines.append("\nIncorrect words:")
        for word_info in result["incorrect_words"]:
            lines.append(f"  - {word_info['original']} (case: {word_info['case']})")
            if word_info["suggestions"]:
                lines.append(f"    Suggestions: {', '.join(word_info['suggestions'])}")

    return "\n".join(lines)


@main.command()
@click.option(
    "--language",
    "-l",
    type=click.Choice(["en", "fur", "it"]),
    help="Interface language (en=English, fur=Friulian, it=Italian)",
)
@click.option("--no-color", is_flag=True, help="Disable colored output")
def interactive(language: str | None, no_color: bool) -> None:
    """
    Start interactive REPL mode with colored output and i18n support.

    This mode provides a user-friendly interface with:
    - ASCII art logo
    - Colored console output
    - Multilingual support (English, Friulian, Italian)
    - Interactive command loop

    Commands:
        C <words>...  - Check spelling of one or more words
        S <word>      - Get suggestions for a misspelled word
        Q             - Quit the application
    """
    # Initialize colors if not disabled
    if not no_color and is_color_available():
        init_colors()
        use_colors = True
    else:
        use_colors = False

    # Display logo
    if use_colors:
        write_colored("", Color.CYAN)  # Set color context
    print_logo()
    print_title()

    # Language selection
    if language:
        lang_map = {"en": Language.ENGLISH, "fur": Language.FRIULIAN, "it": Language.ITALIAN}
        selected_language = lang_map[language]
    else:
        selected_language = Localization.select_language()

    Localization.load_strings(selected_language)

    # Initialize spell checker
    try:
        dictionary = Dictionary()
        text_processor = TextProcessor()
        spell_checker = FurlanSpellChecker(dictionary, text_processor)
    except Exception as e:
        error_msg = f"Error initializing spell checker: {e}"
        if use_colors:
            write_colored(error_msg, Color.RED)
        else:
            click.echo(error_msg, err=True)
        sys.exit(1)

    # Display instructions
    if use_colors:
        write_colored(f"\n{Localization.get('Instructions')}", Color.YELLOW)
        write_colored("-" * 70, Color.DARK_GRAY)
    else:
        click.echo(f"\n{Localization.get('Instructions')}")
        click.echo("-" * 70)

    # Main REPL loop
    try:
        while True:
            try:
                # Read command
                user_input = input("\n> ").strip()

                if not user_input:
                    continue

                parts = user_input.split()
                command = parts[0].upper()

                if command == "Q":
                    # Quit command
                    if use_colors:
                        write_colored(f"\n{Localization.get('Closing')}", Color.CYAN)
                    else:
                        click.echo(f"\n{Localization.get('Closing')}")
                    break

                elif command == "C":
                    # Check command: C <words>...
                    if len(parts) < 2:
                        error_msg = Localization.get("NoWordsProvided")
                        if use_colors:
                            write_colored(error_msg, Color.RED)
                        else:
                            click.echo(error_msg)
                        continue

                    words = parts[1:]
                    for word in words:
                        # Strip trailing period
                        if word.endswith("."):
                            word = word[:-1]

                        if not word:
                            continue

                        # Use asyncio.run for async check
                        is_correct = asyncio.run(spell_checker.check_word_str(word))
                        status = (
                            Localization.get("Correct")
                            if is_correct
                            else Localization.get("Incorrect")
                        )

                        if use_colors:
                            write_colored(f"{word} ", Color.WHITE, newline=False)
                            write_colored(Localization.get("Is"), Color.DARK_GRAY, newline=False)
                            write_colored(f" {status}", Color.GREEN if is_correct else Color.RED)
                        else:
                            click.echo(f"{word} {Localization.get('Is')} {status}")

                elif command == "S":
                    # Suggest command: S <word>
                    if len(parts) != 2:
                        error_msg = Localization.get("ProvideCommandAndWord")
                        if use_colors:
                            write_colored(error_msg, Color.RED)
                        else:
                            click.echo(error_msg)
                        continue

                    word = parts[1]
                    # Strip trailing period
                    if word.endswith("."):
                        word = word[:-1]

                    if not word:
                        continue

                    # Use asyncio.run for async check
                    is_correct = asyncio.run(spell_checker.check_word_str(word))

                    if is_correct:
                        if use_colors:
                            write_colored(f"{word} ", Color.WHITE, newline=False)
                            write_colored(Localization.get("Is"), Color.DARK_GRAY, newline=False)
                            write_colored(f" {Localization.get('Correct')}", Color.GREEN)
                        else:
                            click.echo(
                                f"{word} {Localization.get('Is')} {Localization.get('Correct')}"
                            )
                    else:
                        suggestions = spell_checker.suggest(word, max_suggestions=10)

                        if use_colors:
                            write_colored(f"{word} ", Color.WHITE, newline=False)
                            write_colored(Localization.get("Is"), Color.DARK_GRAY, newline=False)
                            write_colored(f" {Localization.get('Incorrect')}", Color.RED)
                        else:
                            click.echo(
                                f"{word} {Localization.get('Is')} {Localization.get('Incorrect')}"
                            )

                        if suggestions:
                            sugs_text = (
                                f"{Localization.get('SuggestionsAre')}: {', '.join(suggestions)}"
                            )
                            if use_colors:
                                write_colored(sugs_text, Color.CYAN)
                            else:
                                click.echo(sugs_text)
                        else:
                            no_sugs = Localization.get("NoSuggestions")
                            if use_colors:
                                write_colored(no_sugs, Color.DARK_YELLOW)
                            else:
                                click.echo(no_sugs)

                else:
                    # Unknown command
                    error_msg = Localization.get("UnknownCommandFormat")
                    if use_colors:
                        write_colored(error_msg, Color.RED)
                    else:
                        click.echo(error_msg)

            except EOFError:
                # Handle Ctrl+D
                if use_colors:
                    write_colored(f"\n{Localization.get('Closing')}", Color.CYAN)
                else:
                    click.echo(f"\n{Localization.get('Closing')}")
                break

    except KeyboardInterrupt:
        # Handle Ctrl+C
        if use_colors:
            write_colored(f"\n{Localization.get('Closing')}", Color.CYAN)
        else:
            click.echo(f"\n{Localization.get('Closing')}")


@main.command("cof-cli")
@click.option("--encoding", "-c", default="utf8", help="Character encoding (default: utf8)")
@click.option(
    "--max-suggestions",
    "-n",
    default=10,
    type=int,
    help="Maximum number of suggestions (default: 10)",
)
@click.option(
    "--debug",
    "-d",
    is_flag=True,
    default=False,
    help="Enable debug logging to STDERR with timestamps",
)
def cof_cli(encoding: str, max_suggestions: int, debug: bool) -> None:
    """
    COF protocol mode for automation and testing compatibility.

    This mode implements the exact stdin/stdout protocol used by the Perl COF CLI,
    ensuring 100% output format compatibility for automation and testing.

    Protocol:
        Commands (from stdin):
            c <word> [<word2> ...]  - Check spelling
            s <word>                - Get suggestions
            q                       - Quit

        Output (to stdout):
            Check: "ok\\n" (correct) or "no\\n" (incorrect)
            Suggest: "ok\\n" (correct) or "no\\t<sug1>,<sug2>,...\\n" (incorrect)
            Error: "err\\n"

    Debug mode (-d, --debug):
        Outputs timestamped diagnostic logs to STDERR for debugging.
        Format: [TIMESTAMP] [TAG] message

    Special handling:
        - Words ending with '.' are processed with the period stripped
        - Multiple words in check command are processed sequentially

    Example:
        \b
        $ echo -e "c preon\\ns sbaliât\\nq" | furlan-spellchecker cof-cli
        ok
        no\tsbaliât,sbaliâ,sbaliàt

        \b
        $ echo -e "s test\\nq" | furlan-spellchecker cof-cli --debug
        [2025-11-28 10:15:30.123] [INIT] Loading Dictionary...
        ...
    """
    protocol = COFProtocol(encoding=encoding, max_suggestions=max_suggestions, debug=debug)
    protocol.run()


if __name__ == "__main__":
    main()
