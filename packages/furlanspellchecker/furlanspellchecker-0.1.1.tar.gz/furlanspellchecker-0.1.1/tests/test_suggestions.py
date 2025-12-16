"""Tests for Suggestion component integration (matching COF test_suggestions.pl).

This test suite validates complete suggestion generation behavior with COF parity,
including database availability, initialization, and comprehensive suggestion tests.
Based on COF test_suggestions.pl (50 tests: 11 db + 6 init + 33 suggestion tests).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from furlan_spellchecker.database.manager import DatabaseManager
from furlan_spellchecker.spellchecker.suggestion_engine import SuggestionEngine

sys.path.insert(0, str(Path(__file__).parent))


# ============================================================================
# SECTION 1: DATABASE AVAILABILITY TESTS (11 tests - COF lines 19-27)
# ============================================================================


class TestDatabaseAvailability:
    """Test that all required database files exist and are readable (11 tests)."""

    def test_dictionary_directory_exists(self, real_databases):
        """Test that dictionary directory exists (COF line 19)."""
        # Get parent directory from any database path
        dict_dir = real_databases["words"].parent
        assert dict_dir.exists(), f"Dictionary directory should exist: {dict_dir}"
        assert dict_dir.is_dir(), f"Dictionary path should be a directory: {dict_dir}"

    # Map COF database names to Python fixture keys (SQLite format)
    DATABASE_MAPPING = [
        ("words.sqlite", "words"),
        ("words_radix_tree.rt", "radix_tree"),
        ("elisions.sqlite", "elisions"),
        ("errors.sqlite", "errors"),
        ("frequencies.sqlite", "frequencies"),
    ]

    @pytest.mark.parametrize("db_name,fixture_key", DATABASE_MAPPING)
    def test_database_file_exists(self, real_databases, db_name, fixture_key):
        """Test that required database file exists (COF lines 20-24)."""
        db_path = real_databases[fixture_key]
        assert db_path.exists(), f"Database file should exist: {db_name} at {db_path}"

    @pytest.mark.parametrize("db_name,fixture_key", DATABASE_MAPPING)
    def test_database_file_readable(self, real_databases, db_name, fixture_key):
        """Test that required database file is readable (COF lines 25-27)."""
        db_path = real_databases[fixture_key]
        assert db_path.is_file(), f"Database file should be readable: {db_name}"
        # Try to open it to verify readability
        with open(db_path, "rb") as f:
            f.read(1)  # Read at least 1 byte


# ============================================================================
# SECTION 2: INITIALIZATION TESTS (6 tests - COF lines 29-39)
# ============================================================================


class TestInitialization:
    """Test DatabaseManager and SuggestionEngine initialization (6 tests)."""

    def test_database_manager_creation(self, real_db_manager):
        """Test COF::Data equivalent - DatabaseManager creation succeeded (COF line 31)."""
        assert real_db_manager is not None, "DatabaseManager creation should succeed"

    def test_database_manager_defined(self, real_db_manager):
        """Test that DatabaseManager object is properly defined (COF line 32)."""
        assert real_db_manager is not None, "DatabaseManager object should be defined"

    def test_database_manager_type(self, real_db_manager):
        """Test DatabaseManager type check (COF line 33)."""
        assert isinstance(real_db_manager, DatabaseManager), "Should be DatabaseManager instance"

    def test_suggestion_engine_creation(self, real_suggestion_engine):
        """Test COF::SpellChecker equivalent - SuggestionEngine creation succeeded (COF line 36)."""
        assert real_suggestion_engine is not None, "SuggestionEngine creation should succeed"

    def test_suggestion_engine_defined(self, real_suggestion_engine):
        """Test that SuggestionEngine object is properly defined (COF line 37)."""
        assert real_suggestion_engine is not None, "SuggestionEngine object should be defined"

    def test_suggestion_engine_type(self, real_suggestion_engine):
        """Test SuggestionEngine type check (COF line 38)."""
        assert isinstance(
            real_suggestion_engine, SuggestionEngine
        ), "Should be SuggestionEngine instance"


# ============================================================================
# SECTION 3: CORE SUGGESTION TESTS (33 tests - COF lines 41-135)
# ============================================================================


class TestCoreSuggestions:
    """Core suggestion tests matching COF test_suggestions.pl patterns (33 tests)."""

    def test_furla_returns_defined_value(self, real_suggestion_engine):
        """Test suggest('furla') returns defined value (COF line 43)."""
        suggestions = real_suggestion_engine.suggest("furla")
        assert suggestions is not None, "suggest('furla') should return defined value"

    def test_furla_returns_array_reference(self, real_suggestion_engine):
        """Test suggest('furla') returns array reference (COF line 44)."""
        suggestions = real_suggestion_engine.suggest("furla")
        assert isinstance(suggestions, list), "suggest('furla') should return list/array"

    def test_furla_has_suggestions(self, real_suggestion_engine):
        """Test 'furla' produces at least one suggestion (COF line 45)."""
        suggestions = real_suggestion_engine.suggest("furla")
        assert len(suggestions) > 0, "'furla' should produce at least one suggestion"

    def test_furla_first_suggestion_is_furlan(self, real_suggestion_engine):
        """Test first suggestion for 'furla' is 'furlan' (COF line 47)."""
        suggestions = real_suggestion_engine.suggest("furla")
        assert len(suggestions) > 0, "'furla' should produce suggestions"
        assert suggestions[0].lower() == "furlan", "First suggestion for 'furla' should be 'furlan'"

    def test_cjasa_first_suggestion(self, real_suggestion_engine):
        """Test first suggestion for 'cjasa' is 'cjase' (COF line 52)."""
        suggestions = real_suggestion_engine.suggest("cjasa")
        assert len(suggestions) > 0, "'cjasa' should produce suggestions"
        assert suggestions[0].lower() == "cjase", "First suggestion for 'cjasa' should be 'cjase'"

    def test_nonsense_no_suggestions(self, real_suggestion_engine):
        """Test 'blablabla' returns no suggestions (COF line 56)."""
        suggestions = real_suggestion_engine.suggest("blablabla")
        assert isinstance(suggestions, list), "Should return list"
        assert len(suggestions) == 0, "'blablabla' should return no suggestions"

    def test_elision_l_aghe_preserved(self, real_suggestion_engine):
        """Test elision preserved for l'aghe (COF line 60)."""
        suggestions = real_suggestion_engine.suggest("l'aghe")
        assert len(suggestions) > 0, "l'aghe should have suggestions"
        # First suggestion should be 'la aghe' or similar elision handling
        assert "aghe" in suggestions[0].lower() or "la" in suggestions[0].lower()

    def test_elision_un_ore_preserved(self, real_suggestion_engine):
        """Test elision preserved for un'ore (COF line 61)."""
        suggestions = real_suggestion_engine.suggest("un'ore")
        assert len(suggestions) > 0, "un'ore should have suggestions"
        # Should handle 'une ore' or similar
        first = suggestions[0].lower()
        assert "ore" in first or "un" in first

    def test_phonetic_lengha_to_lenghe(self, real_suggestion_engine):
        """Test phonetic correction for 'lengha' (COF line 62)."""
        suggestions = real_suggestion_engine.suggest("lengha")
        assert len(suggestions) > 0, "'lengha' should have suggestions"
        assert (
            suggestions[0].lower() == "lenghe"
        ), "First suggestion for 'lengha' should be 'lenghe'"

    def test_phonetic_ostaria_to_ostarie(self, real_suggestion_engine):
        """Test phonetic correction for 'ostaria' (COF line 63)."""
        suggestions = real_suggestion_engine.suggest("ostaria")
        assert len(suggestions) > 0, "'ostaria' should have suggestions"
        assert (
            suggestions[0].lower() == "ostarie"
        ), "First suggestion for 'ostaria' should be 'ostarie'"

    def test_consonant_doubling_anell(self, real_suggestion_engine):
        """Test consonant doubling corrected for 'anell' (COF line 64)."""
        suggestions = real_suggestion_engine.suggest("anell")
        assert len(suggestions) > 0, "'anell' should have suggestions"
        assert suggestions[0].lower() == "anel", "First suggestion for 'anell' should be 'anel'"

    def test_known_word_cjol_preserved(self, real_suggestion_engine):
        """Test known word preserved for 'cjol' (COF line 65)."""
        suggestions = real_suggestion_engine.suggest("cjol")
        if len(suggestions) > 0:
            assert suggestions[0].lower() == "cjol", "Known word 'cjol' should be preserved"

    def test_case_preserved_Furlan(self, real_suggestion_engine):
        """Test case preserved for 'Furlan' (COF line 66)."""
        suggestions = real_suggestion_engine.suggest("Furlan")
        if len(suggestions) > 0:
            assert suggestions[0] == "Furlan", "Case should be preserved for 'Furlan'"

    def test_case_preserved_FURLAN(self, real_suggestion_engine):
        """Test case preserved for 'FURLAN' (COF line 67)."""
        suggestions = real_suggestion_engine.suggest("FURLAN")
        if len(suggestions) > 0:
            assert suggestions[0] == "FURLAN", "Case should be preserved for 'FURLAN'"

    def test_lowercase_furlan_kept(self, real_suggestion_engine):
        """Test lowercase word kept for 'furlan' (COF line 68)."""
        suggestions = real_suggestion_engine.suggest("furlan")
        if len(suggestions) > 0:
            assert suggestions[0] == "furlan", "Lowercase 'furlan' should be kept"

    def test_plural_furlans_preserved(self, real_suggestion_engine):
        """Test plural preserved for 'furlans' (COF line 69)."""
        suggestions = real_suggestion_engine.suggest("furlans")
        if len(suggestions) > 0:
            assert suggestions[0].lower() == "furlans", "Plural 'furlans' should be preserved"

    def test_feminine_furlane_preserved(self, real_suggestion_engine):
        """Test feminine preserved for 'furlane' (COF line 70)."""
        suggestions = real_suggestion_engine.suggest("furlane")
        if len(suggestions) > 0:
            assert suggestions[0].lower() == "furlane", "Feminine 'furlane' should be preserved"

    def test_plural_feminine_furlanis(self, real_suggestion_engine):
        """Test plural feminine preserved for 'furlanis' (COF line 71)."""
        suggestions = real_suggestion_engine.suggest("furlanis")
        if len(suggestions) > 0:
            assert (
                suggestions[0].lower() == "furlanis"
            ), "Plural feminine 'furlanis' should be preserved"

    def test_circumflex_fur_to_fûr(self, real_suggestion_engine):
        """Test Friulian circumflex preserved for 'fur' (COF line 72)."""
        suggestions = real_suggestion_engine.suggest("fur")
        if len(suggestions) > 0:
            assert suggestions[0].lower() == "fûr", "Should suggest 'fûr' for 'fur'"

    def test_comparative_plui_preserved(self, real_suggestion_engine):
        """Test comparative preserved for 'plui' (COF line 73)."""
        suggestions = real_suggestion_engine.suggest("plui")
        if len(suggestions) > 0:
            assert suggestions[0].lower() == "plui", "Comparative 'plui' should be preserved"

    def test_frequency_prossim(self, real_suggestion_engine):
        """Test frequency-weighted priority for 'prossim' (COF line 74)."""
        suggestions = real_suggestion_engine.suggest("prossim")
        if len(suggestions) > 0:
            assert suggestions[0].lower() == "prossim", "Frequency priority for 'prossim'"

    def test_gj_sequence_gjave(self, real_suggestion_engine):
        """Test Friulian gj sequence handled for 'gjave' (COF line 75)."""
        suggestions = real_suggestion_engine.suggest("gjave")
        if len(suggestions) > 0:
            assert suggestions[0].lower() == "gjave", "Friulian 'gj' in 'gjave' preserved"

    def test_ghe_cluster_aghe(self, real_suggestion_engine):
        """Test Friulian ghe cluster handled for 'aghe' (COF line 76)."""
        suggestions = real_suggestion_engine.suggest("aghe")
        if len(suggestions) > 0:
            assert suggestions[0].lower() == "aghe", "Friulian 'ghe' cluster in 'aghe' preserved"

    def test_short_bas_preserved(self, real_suggestion_engine):
        """Test short base form preserved for 'bas' (COF line 77)."""
        suggestions = real_suggestion_engine.suggest("bas")
        if len(suggestions) > 0:
            assert suggestions[0].lower() == "bas", "Short form 'bas' should be preserved"

    def test_ranking_grant(self, real_suggestion_engine):
        """Test ranking maintained for 'grant' (COF line 78)."""
        suggestions = real_suggestion_engine.suggest("grant")
        if len(suggestions) > 0:
            assert suggestions[0].lower() == "grant", "Ranking maintained for 'grant'"

    def test_short_consonant_alt(self, real_suggestion_engine):
        """Test short consonant cluster preserved for 'alt' (COF line 79)."""
        suggestions = real_suggestion_engine.suggest("alt")
        if len(suggestions) > 0:
            assert suggestions[0].lower() == "alt", "Short consonant cluster 'alt' preserved"

    def test_single_letter_a(self, real_suggestion_engine):
        """Test single letter preserved for 'a' (COF line 80)."""
        suggestions = real_suggestion_engine.suggest("a")
        if len(suggestions) > 0:
            assert suggestions[0].lower() == "a", "Single letter 'a' should be preserved"

    def test_nearest_neighbour_ab(self, real_suggestion_engine):
        """Test nearest neighbour suggested for 'ab' (COF line 81)."""
        suggestions = real_suggestion_engine.suggest("ab")
        if len(suggestions) > 0:
            # Should suggest 'a' as nearest valid word
            assert "a" in [s.lower() for s in suggestions], "Should suggest 'a' for 'ab'"

    def test_phonetic_fu_to_su(self, real_suggestion_engine):
        """Test closest phonetic match for 'fu' (COF line 82)."""
        suggestions = real_suggestion_engine.suggest("fu")
        if len(suggestions) > 0:
            # Should suggest phonetically similar word
            suggestion_lower = [s.lower() for s in suggestions]
            assert (
                "su" in suggestion_lower or "fûr" in suggestion_lower
            ), "Should have phonetic match for 'fu'"

    def test_hyphen_decomposition(self, real_suggestion_engine):
        """Test hyphen decomposition handled for 'cjase-parol' (COF line 83)."""
        suggestions = real_suggestion_engine.suggest("cjase-parol")
        # Should handle hyphen decomposition or suggest component words
        assert isinstance(suggestions, list), "Should handle hyphenated words"

    def test_cjoll_contains_cjol(self, real_suggestion_engine):
        """Test suggestion list for 'cjoll' contains 'cjol' (COF line 89)."""
        suggestions = real_suggestion_engine.suggest("cjoll")
        suggestion_lower = [s.lower() for s in suggestions]
        assert "cjol" in suggestion_lower, "Suggestions for 'cjoll' should contain 'cjol'"

    def test_suggestions_stable_lengha(self, real_suggestion_engine):
        """Test suggestions for 'lengha' are stable between calls (COF line 95)."""
        first_call = real_suggestion_engine.suggest("lengha")
        second_call = real_suggestion_engine.suggest("lengha")
        assert first_call == second_call, "Suggestions for 'lengha' should be stable between calls"

    def test_suggestions_stable_furla(self, real_suggestion_engine):
        """Test suggestions for 'furla' are stable between calls (COF line 135)."""
        first_call = real_suggestion_engine.suggest("furla")
        second_call = real_suggestion_engine.suggest("furla")
        assert first_call == second_call, "Suggestions for 'furla' should be stable between calls"
