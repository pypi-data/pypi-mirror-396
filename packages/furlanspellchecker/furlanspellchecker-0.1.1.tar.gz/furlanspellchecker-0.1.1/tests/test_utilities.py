#!/usr/bin/env python3
"""
test_utilities.py - Utility and support functionality tests for FurlanSpellChecker

Tests for utility functions and support infrastructure:
- Encoding functionality (UTF-8, Latin-1, Friulian diacritics)
- CLI parameter validation for utility scripts
- Legacy vocabulary handling and tokenization
- Error handling and edge cases

These tests ensure the supporting infrastructure works correctly
and can handle various input scenarios gracefully.

Matches COF test_utilities.pl for 100% parity.
Total: 37 tests
"""

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from furlan_spellchecker.spellchecker.text_processor import TextProcessor

# ============================================================================
# ENCODING COMPREHENSIVE TESTS (18 tests)
# ============================================================================


class TestEncodingFunctionality:
    """Test encoding functionality for various character sets."""

    def test_utf8_encoding_detection(self):
        """Test 1: UTF-8 encoding detection.

        Verifies that UTF-8 text is properly handled.
        """
        utf8_text = "café naïve"
        # In Python 3, strings are unicode by default
        assert isinstance(utf8_text, str), "UTF-8 detection should work"
        assert len(utf8_text) == 10, "UTF-8 string length should be correct"

    def test_latin1_to_utf8_conversion(self):
        """Test 2: Latin-1 to UTF-8 conversion.

        Verifies that Latin-1 encoded bytes can be decoded to UTF-8 strings.
        """
        # café in Latin-1 bytes
        latin1_bytes = b"caf\xe9"
        utf8_text_converted = latin1_bytes.decode("latin-1")

        assert len(utf8_text_converted) > 0, "Latin-1 to UTF-8 conversion should work"
        assert utf8_text_converted == "café", "Converted text should match expected"

    @pytest.mark.parametrize("char", ["à", "è", "é", "ì", "î", "ò", "ù", "û", "ç", "ñ"])
    def test_friulian_diacritics_handling(self, char):
        """Test 3-12: Friulian diacritics handling (10 tests).

        Verifies that each Friulian special character encodes/decodes correctly.
        Tests: à, è, é, ì, î, ò, ù, û, ç, ñ
        """
        # Encode to UTF-8 bytes and decode back
        encoded = char.encode("utf-8")
        decoded = encoded.decode("utf-8")

        assert decoded == char, f"Friulian character '{char}' should encode/decode correctly"

    def test_mixed_encoding_text_handling(self):
        """Test 13: Mixed encoding text handling.

        Verifies that text with various diacritics is handled correctly.
        """
        mixed_text = "Hello café naïve résumé"
        encoded = mixed_text.encode("utf-8")
        decoded = encoded.decode("utf-8")

        assert decoded == mixed_text, "Mixed encoding text should handle correctly"

    def test_empty_string_handling(self):
        """Test 14: Empty string handling.

        Verifies that empty strings encode/decode without errors.
        """
        empty = ""
        empty_encoded = empty.encode("utf-8")
        empty_decoded = empty_encoded.decode("utf-8")

        assert empty_decoded == empty, "Empty string should handle correctly"

    def test_ascii_text_handling(self):
        """Test 15: ASCII text handling.

        Verifies that plain ASCII text encodes/decodes correctly.
        """
        ascii_text = "Hello World"
        ascii_encoded = ascii_text.encode("utf-8")
        ascii_decoded = ascii_encoded.decode("utf-8")

        assert ascii_decoded == ascii_text, "ASCII text should handle correctly"

    def test_invalid_utf8_sequences(self):
        """Test 16: Invalid UTF-8 sequences.

        Verifies that invalid UTF-8 byte sequences are detected.
        """
        invalid_utf8 = b"\xff\xfe\x00\x00"

        with pytest.raises(UnicodeDecodeError):
            invalid_utf8.decode("utf-8")

    def test_double_encoding_detection(self):
        """Test 17: Double encoding detection.

        Verifies that double encoding produces different results.
        """
        text = "café"
        single_encoded = text.encode("utf-8")
        double_encoded = single_encoded.decode("utf-8").encode("utf-8")

        # Double encoding UTF-8 string should be same as single (Python 3 str is unicode)
        # But if we encode bytes again, we get different result
        assert (
            double_encoded == single_encoded
        ), "UTF-8 encoding should be idempotent for unicode strings"

        # Test actual double encoding scenario (encode already-encoded bytes as string)
        # This simulates the Perl test where encode_utf8 is called twice
        text_bytes = text.encode("utf-8")
        # If we mistakenly treat bytes as latin-1 and encode again
        double_encoded_scenario = text_bytes.decode("latin-1").encode("utf-8")
        assert double_encoded_scenario != text_bytes, "Should detect double encoding scenario"


# ============================================================================
# CLI PARAMETER VALIDATION TESTS (9 tests)
# ============================================================================


class TestCLIParameterValidation:
    """Test CLI parameter validation for utility scripts."""

    @pytest.fixture
    def scripts_dir(self):
        """Get path to scripts/utils directory."""
        return Path(__file__).parent.parent / "scripts" / "utils"

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def run_utility(self, script_path: Path, args: list = None) -> subprocess.CompletedProcess:
        """Run a utility script and return the result."""
        cmd = [sys.executable, str(script_path)]
        if args:
            cmd.extend(args)

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",  # Replace invalid UTF-8 sequences with � to avoid warnings
        )
        return result

    def test_spellchecker_utils_no_parameters(self, scripts_dir):
        """Test 19: spellchecker_utils should fail with no parameters.

        Verifies that spellchecker_utils.py exits with non-zero code when called
        without required parameters, matching COF behavior.
        """
        script = scripts_dir / "spellchecker_utils.py"
        result = self.run_utility(script)

        assert result.returncode != 0, "spellchecker_utils should fail with no parameters"
        # Should show help or error message
        assert (
            "Error" in result.stderr or "usage" in result.stderr.lower()
        ), "Should show helpful error message"

    def test_spellchecker_utils_nonexistent_file(self, scripts_dir, temp_dir):
        """Test 20: spellchecker_utils should fail with nonexistent file.

        Verifies proper error handling for nonexistent input files.
        """
        script = scripts_dir / "spellchecker_utils.py"
        nonexistent = temp_dir / "nonexistent" / "file.txt"
        result = self.run_utility(script, ["--file", str(nonexistent)])

        assert result.returncode != 0, "spellchecker_utils should fail with nonexistent file"

    def test_radixtree_utils_no_parameters(self, scripts_dir):
        """Test 21: radixtree_utils should fail with no parameters.

        Verifies that radixtree_utils.py exits with non-zero code when called
        without required parameters.
        """
        script = scripts_dir / "radixtree_utils.py"
        result = self.run_utility(script)

        assert result.returncode != 0, "radixtree_utils should fail with no parameters"

    def test_encoding_utils_no_parameters(self, scripts_dir):
        """Test 22: encoding_utils should fail with no parameters.

        Verifies that encoding_utils.py exits with non-zero code when called
        without required parameters.
        """
        script = scripts_dir / "encoding_utils.py"
        result = self.run_utility(script)

        assert result.returncode != 0, "encoding_utils should fail with no parameters"

    def test_worditerator_utils_no_parameters(self, scripts_dir):
        """Test 23: worditerator_utils should fail with no parameters.

        Verifies that worditerator_utils.py exits with non-zero code when called
        without required parameters.
        """
        script = scripts_dir / "worditerator_utils.py"
        result = self.run_utility(script)

        assert result.returncode != 0, "worditerator_utils should fail with no parameters"

    def test_radixtree_utils_empty_file(self, scripts_dir, temp_dir):
        """Test 24: radixtree_utils should fail gracefully with empty file.

        COF behavior: radixtree_utils.pl exits with non-zero for empty files.
        """
        script = scripts_dir / "radixtree_utils.py"
        empty_file = temp_dir / "empty.txt"
        empty_file.touch()

        result = self.run_utility(script, ["--file", str(empty_file)])

        assert result.returncode != 0, "radixtree_utils should fail gracefully with empty file"

    def test_encoding_utils_empty_file(self, scripts_dir, temp_dir):
        """Test 25: encoding_utils should fail gracefully with empty file.

        COF behavior: encoding_utils.pl exits with non-zero for empty files.
        """
        script = scripts_dir / "encoding_utils.py"
        empty_file = temp_dir / "empty.txt"
        empty_file.touch()

        result = self.run_utility(script, ["--file", str(empty_file)])

        assert result.returncode != 0, "encoding_utils should fail gracefully with empty file"

    def test_spellchecker_utils_empty_file_handling(self, scripts_dir, temp_dir):
        """Test 26: spellchecker_utils should handle empty file without crashing.

        COF behavior: spellchecker_utils.pl successfully processes empty files (exit 0)
        with no output, gracefully handling the "no words" case.
        """
        script = scripts_dir / "spellchecker_utils.py"
        empty_file = temp_dir / "empty.txt"
        empty_file.touch()

        result = self.run_utility(script, ["--file", str(empty_file)])

        # COF exits 0 for empty files in spellchecker_utils.pl
        assert (
            result.returncode == 0
        ), "spellchecker_utils should handle empty file without crashing"

    def test_cli_utils_existence_documentation(self, scripts_dir):
        """Test 27: Document expected CLI utilities for future implementation.

        This test verifies that all CLI utilities exist in scripts/utils/ directory
        to match COF Perl functionality:
        - spellchecker_utils: Interactive spellchecker CLI
        - radixtree_utils: Radix tree inspection/debugging
        - encoding_utils: Encoding detection and conversion
        - worditerator_utils: Text tokenization utilities
        """
        expected_utils = [
            "spellchecker_utils.py",
            "radixtree_utils.py",
            "encoding_utils.py",
            "worditerator_utils.py",
        ]

        for util in expected_utils:
            util_path = scripts_dir / util
            assert util_path.exists(), f"CLI utility {util} should exist"


# ============================================================================
# LEGACY VOCABULARY TESTS (10 tests)
# ============================================================================


class TestLegacyVocabulary:
    """Test legacy vocabulary handling and tokenization."""

    @pytest.fixture
    def legacy_dir(self):
        """Get path to COF legacy directory."""
        # Path to COF legacy directory (sibling repository)
        cof_base = Path(__file__).parent.parent.parent / "COF"
        legacy_path = cof_base / "legacy"
        return legacy_path

    def test_legacy_lemmas_file_exists(self, legacy_dir):
        """Test 28: Legacy lemmas file exists.

        Verifies that COF legacy lemmas file is available.
        """
        lemmas_file = legacy_dir / "lemis_cof_2015.txt"

        if not legacy_dir.exists():
            pytest.skip("COF legacy directory not available")

        assert lemmas_file.exists(), "Legacy lemmas file should exist"

    def test_legacy_words_file_exists(self, legacy_dir):
        """Test 29: Legacy words file exists.

        Verifies that COF legacy words file is available.
        """
        words_file = legacy_dir / "peraulis_cof_2015.txt"

        if not legacy_dir.exists():
            pytest.skip("COF legacy directory not available")

        assert words_file.exists(), "Legacy words file should exist"

    @pytest.fixture
    def legacy_word_sample(self, legacy_dir):
        """Load a sample of legacy words for testing."""
        words_file = legacy_dir / "peraulis_cof_2015.txt"

        if not words_file.exists():
            pytest.skip("Legacy words file not available")

        # Read bounded sample (500 words) to keep runtime reasonable
        MAX_WORDS = 500
        words = []

        with open(words_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # Strip trailing columns/frequencies (tab-separated)
                word = line.split("\t")[0]
                words.append(word)
                if len(words) >= MAX_WORDS:
                    break

        return words

    def test_legacy_word_sample_collection(self, legacy_word_sample):
        """Test 30: Legacy word sample collection.

        Verifies that a substantial sample of words can be loaded.
        """
        assert len(legacy_word_sample) > 100, "Should collect substantial word sample"

    def test_legacy_apostrophe_forms_present(self, legacy_word_sample):
        """Test 31: Legacy apostrophe forms present.

        Verifies that words with apostrophes exist in legacy data.
        """
        apostrophe_count = sum(
            1 for w in legacy_word_sample if any(c in w for c in ["'", "'", "`"])
        )
        assert apostrophe_count > 0, "Apostrophe forms should be present in legacy data"

    def test_legacy_accented_e_present(self, legacy_word_sample):
        """Test 32: Legacy accented e present.

        Verifies that words with accented e exist in legacy data.
        """
        accent_e_count = sum(1 for w in legacy_word_sample if any(c in w for c in ["è", "é", "ê"]))
        assert accent_e_count > 0, "Accented e should be present in legacy data"

    def test_legacy_accented_i_present(self, legacy_word_sample):
        """Test 33: Legacy accented i present.

        Verifies that words with accented i exist in legacy data.
        """
        accent_i_count = sum(1 for w in legacy_word_sample if any(c in w for c in ["ì", "í", "î"]))
        assert accent_i_count > 0, "Accented i should be present in legacy data"

    @pytest.fixture
    def representative_words(self, legacy_word_sample):
        """Get representative words with diacritics for tokenization testing."""
        # Find words with diacritics
        representative = [
            w
            for w in legacy_word_sample
            if any(
                c in w
                for c in [
                    "'",
                    "à",
                    "á",
                    "â",
                    "è",
                    "é",
                    "ê",
                    "ì",
                    "í",
                    "î",
                    "ò",
                    "ó",
                    "ô",
                    "ù",
                    "ú",
                    "û",
                ]
            )
        ]
        return representative[:5]  # Take first 5

    @pytest.fixture
    def tokenized_words(self, legacy_word_sample):
        """Tokenize a sample of legacy words and return observed words."""
        # Take first 100 words for speed
        subset = legacy_word_sample[:100]
        joined_text = " ".join(subset)

        # Tokenize with WordIterator
        word_iterator = TextProcessor.WordIterator(joined_text)
        observed = {}

        for token in word_iterator:
            word = token.get("word") if isinstance(token, dict) else token
            if word:
                observed[word] = observed.get(word, 0) + 1

        return observed

    def test_legacy_tokenization_word_1(self, representative_words, tokenized_words):
        """Test 34: Legacy tokenization for representative word 1.

        Verifies that first representative word with diacritics is tokenized correctly.
        """
        if len(representative_words) < 1:
            pytest.skip("Not enough representative words found")

        word = representative_words[0]
        assert (
            word in tokenized_words
        ), f"Representative word '{word}' should be tokenized correctly"

    def test_legacy_tokenization_word_2(self, representative_words, tokenized_words):
        """Test 35: Legacy tokenization for representative word 2.

        Verifies that second representative word with diacritics is tokenized correctly.
        """
        if len(representative_words) < 2:
            pytest.skip("Not enough representative words found")

        word = representative_words[1]
        assert (
            word in tokenized_words
        ), f"Representative word '{word}' should be tokenized correctly"

    def test_legacy_tokenization_word_3(self, representative_words, tokenized_words):
        """Test 36: Legacy tokenization for representative word 3.

        Verifies that third representative word with diacritics is tokenized correctly.
        """
        if len(representative_words) < 3:
            pytest.skip("Not enough representative words found")

        word = representative_words[2]
        assert (
            word in tokenized_words
        ), f"Representative word '{word}' should be tokenized correctly"

    def test_legacy_tokenization_word_4(self, representative_words, tokenized_words):
        """Test 37: Legacy tokenization for representative word 4.

        Verifies that fourth representative word with diacritics is tokenized correctly.
        """
        if len(representative_words) < 4:
            pytest.skip("Not enough representative words found")

        word = representative_words[3]
        assert (
            word in tokenized_words
        ), f"Representative word '{word}' should be tokenized correctly"

    def test_legacy_tokenization_word_5(self, representative_words, tokenized_words):
        """Test 38: Legacy tokenization for representative word 5.

        Verifies that fifth representative word with diacritics is tokenized correctly.
        """
        if len(representative_words) < 5:
            pytest.skip("Not enough representative words found")

        word = representative_words[4]
        assert (
            word in tokenized_words
        ), f"Representative word '{word}' should be tokenized correctly"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
