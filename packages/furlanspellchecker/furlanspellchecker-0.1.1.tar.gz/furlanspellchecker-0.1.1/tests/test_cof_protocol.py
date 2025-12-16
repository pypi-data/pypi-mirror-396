"""
Tests for COF protocol compatibility.

This test suite verifies that the Python implementation of the COF protocol
produces exactly the same output as the Perl reference implementation.
"""

import subprocess
import sys
from io import StringIO

from furlan_spellchecker.cli.cof_protocol import COFProtocol


class TestCOFProtocolOutput:
    """Test that COF protocol produces correct output format."""

    def test_check_correct_word(self):
        """Test check command with a correct word."""
        input_stream = StringIO("c preon\nq\n")
        output_stream = StringIO()

        protocol = COFProtocol(input_stream=input_stream, output_stream=output_stream)
        protocol.run()

        output = output_stream.getvalue()
        assert output == "ok\n", f"Expected 'ok\\n', got {repr(output)}"

    def test_check_incorrect_word(self):
        """Test check command with an incorrect word."""
        input_stream = StringIO("c xyzabc\nq\n")
        output_stream = StringIO()

        protocol = COFProtocol(input_stream=input_stream, output_stream=output_stream)
        protocol.run()

        output = output_stream.getvalue()
        assert output == "no\n", f"Expected 'no\\n', got {repr(output)}"

    def test_check_multiple_words(self):
        """Test check command with multiple words."""
        input_stream = StringIO("c preon lenghe xyzabc\nq\n")
        output_stream = StringIO()

        protocol = COFProtocol(input_stream=input_stream, output_stream=output_stream)
        protocol.run()

        output = output_stream.getvalue()
        # Should output one line per word
        lines = output.strip().split("\n")
        assert len(lines) == 3, f"Expected 3 lines, got {len(lines)}"
        assert lines[0] == "ok", f"Expected 'ok', got {repr(lines[0])}"
        assert lines[1] == "ok", f"Expected 'ok', got {repr(lines[1])}"
        assert lines[2] == "no", f"Expected 'no', got {repr(lines[2])}"

    def test_suggest_correct_word(self):
        """Test suggest command with a correct word."""
        input_stream = StringIO("s preon\nq\n")
        output_stream = StringIO()

        protocol = COFProtocol(input_stream=input_stream, output_stream=output_stream)
        protocol.run()

        output = output_stream.getvalue()
        assert output == "ok\n", f"Expected 'ok\\n', got {repr(output)}"

    def test_suggest_incorrect_word_with_suggestions(self):
        """Test suggest command with an incorrect word that has suggestions."""
        input_stream = StringIO("s preo\nq\n")
        output_stream = StringIO()

        protocol = COFProtocol(input_stream=input_stream, output_stream=output_stream)
        protocol.run()

        output = output_stream.getvalue()
        # Should be "no\t<suggestions>\n"
        assert output.startswith(
            "no\t"
        ), f"Expected output to start with 'no\\t', got {repr(output)}"
        assert output.endswith("\n"), f"Expected output to end with newline, got {repr(output)}"

        # Verify format: "no\t<word1>,<word2>,...\n"
        parts = output.split("\t")
        assert len(parts) == 2, f"Expected 2 parts separated by tab, got {len(parts)}"
        assert parts[0] == "no", f"Expected 'no', got {repr(parts[0])}"

        suggestions_part = parts[1].strip()
        if suggestions_part:  # If there are suggestions
            # Verify comma-separated format
            suggestions = suggestions_part.split(",")
            assert len(suggestions) > 0, "Expected at least one suggestion"

    def test_suggest_incorrect_word_no_suggestions(self):
        """Test suggest command with an incorrect word that has no suggestions."""
        input_stream = StringIO("s xyzabcdefgh\nq\n")
        output_stream = StringIO()

        protocol = COFProtocol(input_stream=input_stream, output_stream=output_stream)
        protocol.run()

        output = output_stream.getvalue()
        # Should be "no\t\n" (no suggestions)
        assert output == "no\t\n", f"Expected 'no\\t\\n', got {repr(output)}"

    def test_endpoint_stripping_check(self):
        """Test that words ending with '.' are processed with the period stripped."""
        input_stream = StringIO("c preon.\nq\n")
        output_stream = StringIO()

        protocol = COFProtocol(input_stream=input_stream, output_stream=output_stream)
        protocol.run()

        output = output_stream.getvalue()
        assert output == "ok\n", f"Expected 'ok\\n' (period stripped), got {repr(output)}"

    def test_endpoint_stripping_suggest(self):
        """Test that words ending with '.' are processed with the period stripped in suggest."""
        input_stream = StringIO("s preon.\nq\n")
        output_stream = StringIO()

        protocol = COFProtocol(input_stream=input_stream, output_stream=output_stream)
        protocol.run()

        output = output_stream.getvalue()
        assert output == "ok\n", f"Expected 'ok\\n' (period stripped), got {repr(output)}"

    def test_empty_command(self):
        """Test that empty lines are ignored."""
        input_stream = StringIO("\n\nc preon\nq\n")
        output_stream = StringIO()

        protocol = COFProtocol(input_stream=input_stream, output_stream=output_stream)
        protocol.run()

        output = output_stream.getvalue()
        assert output == "ok\n", f"Expected only 'ok\\n', got {repr(output)}"

    def test_invalid_check_command(self):
        """Test check command without words returns error."""
        input_stream = StringIO("c\nq\n")
        output_stream = StringIO()

        protocol = COFProtocol(input_stream=input_stream, output_stream=output_stream)
        protocol.run()

        output = output_stream.getvalue()
        assert output == "err\n", f"Expected 'err\\n', got {repr(output)}"

    def test_invalid_suggest_command(self):
        """Test suggest command with wrong number of args returns error."""
        input_stream = StringIO("s\nq\n")
        output_stream = StringIO()

        protocol = COFProtocol(input_stream=input_stream, output_stream=output_stream)
        protocol.run()

        output = output_stream.getvalue()
        assert output == "err\n", f"Expected 'err\\n', got {repr(output)}"

    def test_unknown_command(self):
        """Test unknown command returns error."""
        input_stream = StringIO("x test\nq\n")
        output_stream = StringIO()

        protocol = COFProtocol(input_stream=input_stream, output_stream=output_stream)
        protocol.run()

        output = output_stream.getvalue()
        assert output == "err\n", f"Expected 'err\\n', got {repr(output)}"

    def test_case_insensitive_commands(self):
        """Test that commands are case-insensitive."""
        input_stream = StringIO("C preon\nS preon\nQ\n")
        output_stream = StringIO()

        protocol = COFProtocol(input_stream=input_stream, output_stream=output_stream)
        protocol.run()

        output = output_stream.getvalue()
        lines = output.strip().split("\n")
        assert len(lines) == 2, f"Expected 2 lines, got {len(lines)}"
        assert lines[0] == "ok", f"Expected 'ok', got {repr(lines[0])}"
        assert lines[1] == "ok", f"Expected 'ok', got {repr(lines[1])}"

    def test_max_suggestions_parameter(self):
        """Test that max_suggestions parameter limits the number of suggestions."""
        input_stream = StringIO("s preo\nq\n")
        output_stream = StringIO()

        protocol = COFProtocol(
            max_suggestions=3, input_stream=input_stream, output_stream=output_stream
        )
        protocol.run()

        output = output_stream.getvalue()
        if output.startswith("no\t"):
            parts = output.split("\t")
            suggestions_part = parts[1].strip()
            if suggestions_part:
                suggestions = suggestions_part.split(",")
                assert len(suggestions) <= 3, f"Expected max 3 suggestions, got {len(suggestions)}"


class TestCOFProtocolCLI:
    """Test COF protocol via CLI command."""

    def test_cof_cli_command_check(self):
        """Test cof-cli command with check operation."""
        # Run the CLI command
        result = subprocess.run(
            [sys.executable, "-m", "furlan_spellchecker.cli", "cof-cli"],
            input="c preon\nq\n",
            capture_output=True,
            text=True,
            errors="replace",
        )

        assert result.returncode == 0, f"Command failed with return code {result.returncode}"
        assert result.stdout == "ok\n", f"Expected 'ok\\n', got {repr(result.stdout)}"

    def test_cof_cli_command_suggest(self):
        """Test cof-cli command with suggest operation."""
        result = subprocess.run(
            [sys.executable, "-m", "furlan_spellchecker.cli", "cof-cli"],
            input="s preo\nq\n",
            capture_output=True,
            text=True,
            errors="replace",
        )

        assert result.returncode == 0, f"Command failed with return code {result.returncode}"
        assert result.stdout.startswith(
            "no\t"
        ), f"Expected output to start with 'no\\t', got {repr(result.stdout)}"

    def test_cof_cli_encoding_option(self):
        """Test cof-cli command with encoding option."""
        result = subprocess.run(
            [sys.executable, "-m", "furlan_spellchecker.cli", "cof-cli", "-c", "utf8"],
            input="c preon\nq\n",
            capture_output=True,
            text=True,
            errors="replace",
        )

        assert result.returncode == 0, f"Command failed with return code {result.returncode}"
        assert result.stdout == "ok\n", f"Expected 'ok\\n', got {repr(result.stdout)}"

    def test_cof_cli_max_suggestions_option(self):
        """Test cof-cli command with max-suggestions option."""
        result = subprocess.run(
            [sys.executable, "-m", "furlan_spellchecker.cli", "cof-cli", "-n", "5"],
            input="s preo\nq\n",
            capture_output=True,
            text=True,
            errors="replace",
        )

        assert result.returncode == 0, f"Command failed with return code {result.returncode}"

        if result.stdout.startswith("no\t"):
            parts = result.stdout.split("\t")
            suggestions_part = parts[1].strip()
            if suggestions_part:
                suggestions = suggestions_part.split(",")
                assert len(suggestions) <= 5, f"Expected max 5 suggestions, got {len(suggestions)}"
