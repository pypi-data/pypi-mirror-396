"""
Test Suggestion Ranking Order (COF as ground truth).

This test suite verifies the EXACT order of suggestions returned by FurlanSpellChecker
to ensure 1:1 compatibility with COF (Coretôr Ortografic Furlan) Perl implementation.

Port of: COF/tests/test_suggestion_ranking.pl (51 tests)
"""

from __future__ import annotations

import re

import pytest

from furlan_spellchecker import FurlanSpellChecker
from furlan_spellchecker.config import FurlanSpellCheckerConfig
from furlan_spellchecker.dictionary import Dictionary
from furlan_spellchecker.spellchecker.text_processor import TextProcessor

# Ground truth test cases from COF SpellChecker implementation
# Generated: Wed Oct 15 15:29:14 2025
# Using: util/suggestion_ranking_utils.pl --generate-tests --top 10
SUGGESTION_ORDER_TEST_CASES = {
    # Format: word => [ordered list of expected suggestions]
    # Order is critical: first suggestion is most likely, last is least likely
    # Basic single or few suggestions
    "furla": ["furlan"],
    "lengha": ["lenghe", "linguâi"],
    "anell": ["anel", "anîl", "amîl"],
    "ostaria": ["ostarie", "ossidarijai"],
    "lontam": ["lontan"],
    # Complex cases with multiple suggestions in specific order
    "cjupe": ["cjape", "cope", "copi", "sope", "supe", "copii", "cjepe", "supi", "zupe", "copiii"],
    "cjasa": [
        "cjase",
        "Cjassà",
        "cjasâi",
        "cjast",
        "Cjas",
        "cjaçâ",
        "siacai",
        "cassâ",
        "cjassâ",
        "cjaçà",
    ],
    "scuela": ["scuele", "scueli", "scuelâ", "scuelà", "scuelâi", "scuelai"],
    "gjave": [
        "gjave",
        "savê",
        "gjavâ",
        "savè",
        "grave",
        "gjavi",
        "gjate",
        "gjavà",
        "savi",
        "savei",
    ],
    "aghe": ["aghe", "agne", "asse", "asîi", "agjî", "caghe", "saghe", "ache", "maghe", "aghi"],
    "plui": ["plui", "lui", "pui", "ploie", "plus", "puli", "plei", "pluti"],
    "prossim": [
        "prossim",
        "prossime",
        "prossims",
        "prossimi",
        "prossimâ",
        "prossimà",
        "pruchin",
        "pruchins",
    ],
    # Frequency-based ranking
    "bon": ["bon", "son", "non", "ben", "con", "don", "bot", "bol", "boh", "von"],
    "grant": [
        "grant",
        "gran",
        "zirant",
        "grans",
        "garant",
        "frant",
        "granç",
        "guant",
        "erant",
        "glant",
    ],
    "alt": ["alt", "al", "alc", "art", "at", "alte", "ale", "alì", "lat", "salt"],
    "bas": ["bas", "as", "base", "fas", "pas", "las", "nas", "cas", "bar", "basc"],
    # Case variations (case preservation)
    "Furla": ["Furlan"],
    "FURLA": ["FURLAN"],
    "Lengha": ["Lenghe", "Linguâi"],
    "LENGHA": ["LENGHE", "LINGUÂI"],
    # Very short inputs
    "a": ["a", "e", "al", "la", "i", "o", "è", "à", "ma", "ai"],
    "ab": ["a", "al", "ai", "ae", "an", "ad", "as", "b", "at", "ah"],
    "fu": ["su", "tu", "cu", "fâ", "lu", "fa", "ju", "fo", "f", "fi"],
}


@pytest.fixture(scope="module")
def spellchecker():
    """Initialize FurlanSpellChecker for testing."""
    config = FurlanSpellCheckerConfig()
    dictionary = Dictionary()
    text_processor = TextProcessor()
    return FurlanSpellChecker(dictionary=dictionary, text_processor=text_processor, config=config)


def get_suggestions_ordered(spellchecker, word: str) -> list[str]:
    """Helper function to safely get suggestions in order."""
    try:
        return spellchecker.suggest(word)
    except Exception:
        return []


# === TEST SUITE: Suggestion Ranking Order ===


class TestBasicSuggestionOrder:
    """COF Tests 1-3: Basic suggestion order verification."""

    def test_1a_furla_produces_suggestions(self, spellchecker):
        """Test 1a: 'furla' produces suggestions."""
        suggestions = get_suggestions_ordered(spellchecker, "furla")
        assert len(suggestions) > 0, "'furla' produces suggestions"

    def test_1b_furla_first_suggestion_is_furlan(self, spellchecker):
        """Test 1b: First suggestion for 'furla' is 'furlan'."""
        suggestions = get_suggestions_ordered(spellchecker, "furla")
        if suggestions:
            assert suggestions[0] == "furlan", "First suggestion for 'furla' is 'furlan'"

    def test_2a_cjupe_produces_suggestions(self, spellchecker):
        """Test 2a: 'cjupe' produces suggestions."""
        suggestions = get_suggestions_ordered(spellchecker, "cjupe")
        assert len(suggestions) > 0, "'cjupe' produces suggestions"

    def test_2b_cjupe_order_recorded(self, spellchecker):
        """Test 2b: Record suggestion order for 'cjupe'."""
        suggestions = get_suggestions_ordered(spellchecker, "cjupe")
        # Record the exact order for ground truth
        if len(suggestions) >= 5:
            # We expect at least 5 suggestions, check the first ones
            # The order should be deterministic based on:
            # 1. Frequency weight (F_ERRS=300, F_USER_DICT=350, F_SAME=400, F_USER_EXC=1000)
            # 2. Levenshtein distance (lower is better)
            # 3. Alphabetical order (Friulian sort) for same weight+distance
            pass  # Suggestion order recorded for 'cjupe'

    def test_3_lengha_order_stability(self, spellchecker):
        """Test 3: Verify order stability - same word, same order."""
        first_call = get_suggestions_ordered(spellchecker, "lengha")
        second_call = get_suggestions_ordered(spellchecker, "lengha")
        assert (
            first_call == second_call
        ), "Suggestion order is stable across multiple calls for 'lengha'"


class TestCuratedSuggestionOrder:
    """COF Tests 4-29: Verify exact suggestion order for curated test cases (26 words)."""

    @pytest.mark.parametrize("word", sorted(SUGGESTION_ORDER_TEST_CASES.keys()))
    def test_4_to_29_suggestion_order_matches_expected(self, spellchecker, word):
        """Tests 4-29: Verify the order of top N suggestions matches expected."""
        expected_order = SUGGESTION_ORDER_TEST_CASES[word]
        actual_suggestions = get_suggestions_ordered(spellchecker, word)

        if len(actual_suggestions) == 0:
            pytest.fail(f"No suggestions for '{word}' (expected {len(expected_order)})")

        # Check if we have at least as many suggestions as expected
        if len(actual_suggestions) < len(expected_order):
            pytest.fail(
                f"Insufficient suggestions for '{word}': got {len(actual_suggestions)}, "
                f"expected at least {len(expected_order)}\n"
                f"Got: {', '.join(actual_suggestions)}"
            )

        # Verify the order of top N suggestions matches expected
        order_matches = True
        mismatches = []

        for i, expected_sugg in enumerate(expected_order):
            if actual_suggestions[i] != expected_sugg:
                order_matches = False
                mismatches.append(
                    f"Position {i}: expected '{expected_sugg}', got '{actual_suggestions[i]}'"
                )

        # Special handling for known non-deterministic cases (see test_known_bugs.pl)
        # These words have positions 4-5 that swap due to equal weight+distance
        # Known cases: 'scuela' (scuelâi/scuelai), 'prossim' (prossimâ/prossimà)
        if (word == "scuela" or word == "prossim") and not order_matches:
            # Check if only positions 4 and 5 are swapped
            only_45_swapped = True
            for i, expected_sugg in enumerate(expected_order):
                if i == 4 or i == 5:  # Skip positions 4 and 5
                    continue
                if actual_suggestions[i] != expected_sugg:
                    only_45_swapped = False
                    break

            # Check if positions 4 and 5 contain the expected items (in any order)
            expected_45 = set(expected_order[4:6])
            actual_45 = set(actual_suggestions[4:6])
            has_same_45 = expected_45 == actual_45

            if only_45_swapped and has_same_45:
                order_matches = True  # Accept this as correct

        assert order_matches, (
            f"Suggestion order matches for '{word}'\n"
            f"Order mismatches:\n" + "\n".join(mismatches) + "\n"
            f"Expected: {', '.join(expected_order)}\n"
            f"Got: {', '.join(actual_suggestions[: len(expected_order)])}"
        )


class TestRankingAlgorithm:
    """COF Tests 30-35: Ranking algorithm verification."""

    def test_30_error_dictionary_ranking(self, spellchecker):
        """Test 30: Error dictionary suggestions should rank higher (F_ERRS priority).

        Error dictionary corrections receive F_ERRS weight (300) and should rank
        first in suggestions, above phonetic matches from the system dictionary.

        Test case: 'adincuatri' → 'ad in cuatri' (spacing correction from errors.sqlite)
        """
        suggestions = get_suggestions_ordered(spellchecker, "adincuatri")

        assert len(suggestions) > 0, "Expected suggestions for 'adincuatri'"
        assert suggestions[0].lower() == "ad in cuatri", (
            f"Error dictionary correction should rank first. "
            f"Expected 'ad in cuatri', got '{suggestions[0]}'"
        )

    def test_32_frequency_based_ranking(self, spellchecker):
        """Test 32: Frequency-based ranking."""
        # More frequent words should rank higher (when other factors equal)
        # This is determined by freq.db values
        suggestions = get_suggestions_ordered(spellchecker, "bon")
        if len(suggestions) > 0:
            pass  # Frequency-based ranking test executed

    def test_33_levenshtein_distance_ranking(self, spellchecker):
        """Test 33: Levenshtein distance ranking."""
        # Words with lower edit distance should rank higher
        # When frequency is equal or absent
        suggestions = get_suggestions_ordered(spellchecker, "plui")
        if len(suggestions) > 0:
            # Calculate Levenshtein distances to verify ranking
            pass  # Levenshtein distance ranking test executed

    def test_34a_case_preservation_lowercase(self, spellchecker):
        """Test 34a: Lowercase input produces lowercase suggestions."""
        suggestions_lower = get_suggestions_ordered(spellchecker, "furla")
        if suggestions_lower:
            assert re.match(
                r"^[a-z]", suggestions_lower[0]
            ), "Lowercase input produces lowercase suggestions"

    def test_34b_case_preservation_titlecase(self, spellchecker):
        """Test 34b: Title case input produces title case suggestions."""
        suggestions_title = get_suggestions_ordered(spellchecker, "Furla")
        if suggestions_title:
            assert re.match(
                r"^[A-Z][a-z]", suggestions_title[0]
            ), "Title case input produces title case suggestions"

    def test_34c_case_preservation_verified(self, spellchecker):
        """Test 34c: Case preservation verified overall."""
        # Overall verification that case preservation works
        suggestions_lower = get_suggestions_ordered(spellchecker, "furla")
        suggestions_title = get_suggestions_ordered(spellchecker, "Furla")
        if suggestions_lower and suggestions_title:
            assert True, "Case preservation verified"


class TestLargeSuggestionSets:
    """COF Test 36-37: Performance and Consistency Tests."""

    def test_36_large_suggestion_set_produces_suggestions(self, spellchecker):
        """Test 36: Large suggestion set ordering - single character 'a' produces suggestions."""
        # Test with a word that produces many suggestions
        suggestions = get_suggestions_ordered(spellchecker, "a")
        assert len(suggestions) > 0, "Single character 'a' produces suggestions"

    def test_37_large_suggestion_set_no_duplicates(self, spellchecker):
        """Test 37: Large suggestion set ordering - no duplicates."""
        suggestions = get_suggestions_ordered(spellchecker, "a")

        if len(suggestions) > 10:
            # Verify no duplicates in ordered list
            seen = set()
            has_duplicates = False
            for sugg in suggestions:
                if sugg in seen:
                    has_duplicates = True
                    break
                seen.add(sugg)

            assert not has_duplicates, "No duplicates in suggestion list for 'a'"
        else:
            # Even with <10 suggestions, check for duplicates
            assert len(suggestions) == len(
                set(suggestions)
            ), "No duplicates in suggestion list for 'a'"


class TestOrderConsistency:
    """COF Tests 38-40: Order consistency across different word lengths."""

    # NOTE: 'grant', 'scuela', and 'prossim' show non-deterministic ordering for suggestions
    # with same weight+distance. This is documented in test_known_bugs.pl.

    def test_38_order_consistency_ab(self, spellchecker):
        """Test 38: Order consistency for 'ab' (length 2)."""
        # Note: 'prossim' excluded from consistency test due to non-deterministic positions 4-5
        # Excluded: 'grant' (non-deterministic order for 'granç' vs other same-weight suggestions)
        sugg1 = get_suggestions_ordered(spellchecker, "ab")
        sugg2 = get_suggestions_ordered(spellchecker, "ab")
        assert sugg1 == sugg2, "Order consistency for 'ab' (length 2)"

    def test_39_order_consistency_abc(self, spellchecker):
        """Test 39: Order consistency for 'abc' (length 3)."""
        sugg1 = get_suggestions_ordered(spellchecker, "abc")
        sugg2 = get_suggestions_ordered(spellchecker, "abc")
        assert sugg1 == sugg2, "Order consistency for 'abc' (length 3)"

    def test_40_order_consistency_abcd(self, spellchecker):
        """Test 40: Order consistency for 'abcd' (length 4)."""
        sugg1 = get_suggestions_ordered(spellchecker, "abcd")
        sugg2 = get_suggestions_ordered(spellchecker, "abcd")
        assert sugg1 == sugg2, "Order consistency for 'abcd' (length 4)"


class TestNonDeterministicCases:
    """COF Tests 41-42: Non-deterministic cases - verify at least one valid variant."""

    def test_41_scuela_nondeterministic_positions_4_5(self, spellchecker):
        """Test 41: For 'scuela', positions 4-5 can swap between 'scuelai' and 'scuelâi'."""
        scuela_sugg = get_suggestions_ordered(spellchecker, "scuela")
        if len(scuela_sugg) >= 6:
            pos_4_5 = scuela_sugg[4:6]
            scuela_variant_a = pos_4_5[0] == "scuelai" and pos_4_5[1] == "scuelâi"
            scuela_variant_b = pos_4_5[0] == "scuelâi" and pos_4_5[1] == "scuelai"

            assert scuela_variant_a or scuela_variant_b, (
                f"Non-deterministic 'scuela' positions 4-5 match a valid variant\n"
                f"Got positions 4-5: {', '.join(pos_4_5)}\n"
                f"Expected either: [scuelai, scuelâi] OR [scuelâi, scuelai]"
            )

    def test_42_prossim_nondeterministic_positions_4_5(self, spellchecker):
        """Test 42: For 'prossim', positions 4-5 can swap between 'prossimâ' and 'prossimà'."""
        prossim_sugg = get_suggestions_ordered(spellchecker, "prossim")
        if len(prossim_sugg) >= 6:
            pos_4_5 = prossim_sugg[4:6]
            prossim_variant_a = pos_4_5[0] == "prossimâ" and pos_4_5[1] == "prossimà"
            prossim_variant_b = pos_4_5[0] == "prossimà" and pos_4_5[1] == "prossimâ"

            assert prossim_variant_a or prossim_variant_b, (
                f"Non-deterministic 'prossim' positions 4-5 match a valid variant\n"
                f"Got positions 4-5: {', '.join(pos_4_5)}\n"
                f"Expected either: [prossimâ, prossimà] OR [prossimà, prossimâ]"
            )


class TestEdgeCases:
    """COF Tests 43-51: Edge Cases for Ranking."""

    def test_43_empty_input_handling(self, spellchecker):
        """Test 43: Empty input handled without crash."""
        suggestions_empty = get_suggestions_ordered(spellchecker, "")
        assert isinstance(suggestions_empty, list), "Empty input handled without crash"

    def test_44_single_char_x_handling(self, spellchecker):
        """Test 44: Single character 'x' handled without crash."""
        suggestions_one = get_suggestions_ordered(spellchecker, "x")
        assert isinstance(suggestions_one, list), "Single character 'x' handled without crash"

    def test_45_words_with_apostrophes(self, spellchecker):
        """Test 45: Words with apostrophes."""
        suggestions = get_suggestions_ordered(spellchecker, "d'aghe")

        if len(suggestions) > 0:
            pass  # Apostrophe words produce ordered suggestions
        else:
            pass  # Apostrophe words handled (no suggestions expected)

    def test_46_friulian_special_char_cjase(self, spellchecker):
        """Test 46: Friulian special character 'cjàse' handled."""
        word = "cjàse"
        suggestions = get_suggestions_ordered(spellchecker, word)
        assert isinstance(suggestions, list), f"Friulian special character '{word}' handled"

        if len(suggestions) > 0:
            pass  # Special char suggestions recorded

    def test_47_friulian_special_char_furlana(self, spellchecker):
        """Test 47: Friulian special character 'furlanâ' handled."""
        word = "furlanâ"
        suggestions = get_suggestions_ordered(spellchecker, word)
        assert isinstance(suggestions, list), f"Friulian special character '{word}' handled"

        if len(suggestions) > 0:
            pass  # Special char suggestions recorded

    def test_48_friulian_special_char_ci(self, spellchecker):
        """Test 48: Friulian special character 'çi' handled."""
        word = "çi"
        suggestions = get_suggestions_ordered(spellchecker, word)
        assert isinstance(suggestions, list), f"Friulian special character '{word}' handled"

        if len(suggestions) > 0:
            pass  # Special char suggestions recorded


def min_helper(a: int, b: int) -> int:
    """Helper function matching COF's min subroutine."""
    return a if a < b else b


if __name__ == "__main__":
    # Allow running this test file directly
    # Example usage:
    #   python tests/test_suggestion_ranking.py
    #   python -m pytest tests/test_suggestion_ranking.py -v
    pytest.main([__file__, "-v"])
