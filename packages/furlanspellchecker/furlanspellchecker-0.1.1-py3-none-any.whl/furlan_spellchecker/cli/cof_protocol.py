"""
COF protocol handler for stdin/stdout automation compatibility.

This module implements the exact protocol used by the Perl COF CLI for
automation and testing purposes, ensuring 100% output compatibility.

Protocol Specification:
    Commands:
        c <word> [<word2> ...]  - Check spelling of word(s)
        s <word>                - Get suggestions for a word
        q                       - Quit

    Output Format:
        Check (c): "ok\n" if correct, "no\n" if incorrect
        Suggest (s): "ok\n" if correct, "no\t<sug1>,<sug2>,...\n" if incorrect
        Invalid: "err\n"

    Options:
        -c <encoding>   - Character encoding (default: utf8)
        -n <number>     - Maximum suggestions (default: 10)
        --debug         - Enable debug logging to STDERR

    Special Handling:
        - Words ending with '.' have the endpoint stripped before checking
        - Multiple words in 'c' command are processed sequentially
"""

import io
import sys
import time
from datetime import datetime
from typing import TextIO

from ..dictionary.dictionary import Dictionary
from ..spellchecker.spell_checker import FurlanSpellChecker
from ..spellchecker.text_processor import TextProcessor


class COFProtocol:
    """Handler for COF stdin/stdout protocol."""

    # Progress counter interval for debug logging
    PROGRESS_INTERVAL = 100

    def __init__(
        self,
        encoding: str = "utf8",
        max_suggestions: int = 10,
        input_stream: TextIO | None = None,
        output_stream: TextIO | None = None,
        debug: bool = False,
    ):
        """
        Initialize COF protocol handler.

        Args:
            encoding: Character encoding for I/O (default: utf8)
            max_suggestions: Maximum number of suggestions to return (default: 10)
            input_stream: Input stream (default: sys.stdin)
            output_stream: Output stream (default: sys.stdout)
            debug: Enable debug logging to STDERR (default: False)
        """
        self.encoding = encoding
        self.max_suggestions = max_suggestions
        self.debug = debug
        self.command_count = 0

        # Reconfigure stdin/stdout with the specified encoding
        self.input_stream: TextIO
        if input_stream is None:
            # Wrap stdin buffer with TextIOWrapper using the specified encoding
            self.input_stream = io.TextIOWrapper(
                sys.stdin.buffer, encoding=encoding, errors="replace", line_buffering=True
            )
        else:
            self.input_stream = input_stream

        self.output_stream: TextIO
        if output_stream is None:
            # Wrap stdout buffer with TextIOWrapper using the specified encoding
            self.output_stream = io.TextIOWrapper(
                sys.stdout.buffer, encoding=encoding, errors="replace", line_buffering=True
            )
        else:
            self.output_stream = output_stream

        self.spell_checker: FurlanSpellChecker | None = None

    def debug_log(self, tag: str, message: str) -> None:
        """
        Output a timestamped debug message to STDERR.

        Args:
            tag: Category tag (e.g., INIT, CMD, SUGGEST)
            message: Log message
        """
        if not self.debug:
            return
        timestamp = (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S.")
            + f"{datetime.now().microsecond // 1000:03d}"
        )
        sys.stderr.write(f"[{timestamp}] [{tag}] {message}\n")
        sys.stderr.flush()

    def elapsed_ms(self, start_time: float) -> str:
        """Calculate elapsed time in milliseconds."""
        return f"{(time.time() - start_time) * 1000:.1f}"

    def initialize(self) -> None:
        """Initialize the spell checker. Called once before processing commands."""
        self.debug_log("STARTUP", "cof_protocol.py (Python) starting...")
        startup_time = time.time()

        self.debug_log(
            "CONFIG", f"encoding={self.encoding}, max_suggestions={self.max_suggestions}"
        )

        self.debug_log("INIT", "Loading Dictionary...")
        dict_start = time.time()
        dictionary = Dictionary()
        self.debug_log("INIT", f"Dictionary loaded in {self.elapsed_ms(dict_start)}ms")

        self.debug_log("INIT", "Creating TextProcessor...")
        text_processor = TextProcessor()

        self.debug_log("INIT", "Creating FurlanSpellChecker...")
        speller_start = time.time()
        self.spell_checker = FurlanSpellChecker(dictionary, text_processor)
        self.debug_log("INIT", f"FurlanSpellChecker created in {self.elapsed_ms(speller_start)}ms")

        self.debug_log(
            "READY",
            f"Initialization complete in {self.elapsed_ms(startup_time)}ms. Waiting for commands...",
        )

    def process_check_command(self, words: list[str]) -> None:
        """
        Process check command for one or more words.

        Args:
            words: List of words to check
        """
        if not self.spell_checker:
            self.output_stream.write("err\n")
            self.output_stream.flush()
            return

        for word in words:
            if not word:
                continue

            # COF Perl Logic:
            # 1. Check word as-is.
            # 2. If incorrect AND ends with '.', check word without dot.

            has_endpoint = False
            stripped_word = word
            if len(word) > 1 and word.endswith("."):
                has_endpoint = True
                stripped_word = word[:-1]

            # Check word as-is
            is_correct = self.spell_checker.check_word_str_sync(word)

            # If incorrect and has endpoint, check stripped word
            if not is_correct and has_endpoint:
                is_correct = self.spell_checker.check_word_str_sync(stripped_word)

            result = "ok\n" if is_correct else "no\n"
            self.output_stream.write(result)
            self.output_stream.flush()

    def process_suggest_command(self, word: str) -> None:
        """
        Process suggest command for a single word.

        Args:
            word: Word to get suggestions for
        """
        suggest_start = time.time()

        if not self.spell_checker:
            self.output_stream.write("err\n")
            self.output_stream.flush()
            return

        # COF Perl Logic Compatibility:
        # 1. Check word as-is.
        # 2. If incorrect AND ends with '.', check word without dot.
        # 3. If correct (either way), print "ok".
        # 4. If incorrect, get suggestions for ORIGINAL word.
        # 5. If NO suggestions AND ends with '.', get suggestions for STRIPPED word.
        # 6. If suggestions found AND ends with '.', strip trailing dots from suggestions.

        original_word = word
        has_endpoint = False
        stripped_word = word

        if len(word) > 1 and word.endswith("."):
            has_endpoint = True
            stripped_word = word[:-1]

        if not word:
            self.output_stream.write("err\n")
            self.output_stream.flush()
            return

        # Check word (as-is first)
        is_correct = self.spell_checker.check_word_str_sync(word)

        # If incorrect and has endpoint, check stripped word
        if not is_correct and has_endpoint:
            is_correct = self.spell_checker.check_word_str_sync(stripped_word)

        if is_correct:
            self.output_stream.write("ok\n")
            self.debug_log(
                "SUGGEST",
                f"word='{original_word}' result=ok (correct) time={self.elapsed_ms(suggest_start)}ms",
            )
        else:
            # Get suggestions for ORIGINAL word
            suggestions = self.spell_checker.suggest(word, max_suggestions=self.max_suggestions)

            # If no suggestions and has endpoint, get suggestions for STRIPPED word
            if not suggestions and has_endpoint:
                suggestions = self.spell_checker.suggest(
                    stripped_word, max_suggestions=self.max_suggestions
                )

            # If suggestions found and has endpoint, strip trailing dots from suggestions
            if suggestions and has_endpoint:
                cleaned_suggestions = []
                for sug in suggestions:
                    if len(sug) > 1 and sug.endswith("."):
                        cleaned_suggestions.append(sug[:-1])
                    else:
                        cleaned_suggestions.append(sug)
                suggestions = cleaned_suggestions

            if suggestions:
                # Format: "no\t<sug1>,<sug2>,...\n"
                sugs_str = ",".join(suggestions)
                self.output_stream.write(f"no\t{sugs_str}\n")
            else:
                self.output_stream.write("no\t\n")
            num_suggestions = len(suggestions) if suggestions else 0
            self.debug_log(
                "SUGGEST",
                f"word='{original_word}' result=no suggestions={num_suggestions} time={self.elapsed_ms(suggest_start)}ms",
            )

        self.output_stream.flush()

    def run(self) -> None:
        """
        Run the COF protocol loop, reading commands from stdin until 'q' or EOF.

        This is the main entry point for the protocol handler.
        """
        self.initialize()

        try:
            for line in self.input_stream:
                line = line.strip()

                if not line:
                    continue

                parts = line.split()
                if not parts:
                    continue

                self.command_count += 1

                # Log progress every N commands
                if self.command_count % self.PROGRESS_INTERVAL == 0:
                    self.debug_log("PROGRESS", f"Processed {self.command_count} commands")

                command = parts[0].lower()

                if command == "q":
                    # Quit command
                    self.debug_log(
                        "CMD", f"Quit command received after {self.command_count} commands"
                    )
                    break
                elif command == "c":
                    # Check command: c <word> [<word2> ...]
                    if len(parts) < 2:
                        self.output_stream.write("err\n")
                        self.output_stream.flush()
                    else:
                        words = parts[1:]
                        self.process_check_command(words)
                elif command == "s":
                    # Suggest command: s <word>
                    if len(parts) != 2:
                        self.output_stream.write("err\n")
                        self.output_stream.flush()
                    else:
                        word = parts[1]
                        self.process_suggest_command(word)
                else:
                    # Unknown command
                    self.output_stream.write("err\n")
                    self.output_stream.flush()

        except (EOFError, KeyboardInterrupt):
            # Clean exit on EOF or Ctrl+C
            pass

        self.debug_log("SHUTDOWN", f"Exiting after processing {self.command_count} total commands")
