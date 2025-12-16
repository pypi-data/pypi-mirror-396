"""Test suite for Friulian phonetic algorithm - exact compatibility with COF Perl implementation"""

import pytest

from furlan_spellchecker.phonetic import FurlanPhoneticAlgorithm


class TestFurlanPhoneticAlgorithm:
    """Test the Friulian phonetic algorithm for exact compatibility with COF Perl implementation"""

    @pytest.fixture
    def algorithm(self):
        """Create a phonetic algorithm instance"""
        return FurlanPhoneticAlgorithm()

    # === INDIVIDUALIZED TESTS FOR 1:1 COF PARITY ===
    # Each word gets its own test methods to match COF's 209 individual tests
    # This creates true 1:1 parity with COF test structure

    # Core phonetic test cases from COF - All 98 words from test_phonetic_algorithm.pl
    PHONETIC_TEST_CASES = [
        # Existing regression tests from COF
        ("furlan", "fYl65", "fYl65"),
        ("cjase", "A6A7", "c76E7"),
        ("lenghe", "X7", "X7"),
        ("scuele", "AA87l7", "Ec87l7"),
        ("mandrie", "5659r77", "5659r77"),
        ("barcon", "b2A85", "b2c85"),
        ("nade", "5697", "5697"),
        ("nuie", "5877", "5877"),
        ("specifiche", "Ap7Af7A7", "Ep7c7f7c7"),
        # From test_phonetic_perl.pl (consolidated duplications)
        ("çavatis", "A6v6AA", "ç6v697E"),
        ("cjatâ", "A696", "c7696"),
        ("diretamentri", "I7r79O", "Er79O"),
        ("sdrumâ", "A9r856", "E9r856"),
        ("aghe", "6g7", "6E7"),
        ("çucjar", "A8A2", "ç8c72"),
        ("çai", "A6", "ç6"),
        ("cafè", "A6f7", "c6f7"),
        ("cjanditi", "A6597A", "c765E97"),
        ("gjobat", "g78b69", "E8b69"),
        ("glama", "gl656", "El656"),
        ("gnûf", "g584", "E584"),
        ("savetât", "A6v7969", "E6v7969"),
        ("parol", "p28l", "p28l"),
        ("frut", "fr89", "fr89"),
        ("femine", "f75757", "f75757"),
        # Single character tests
        ("a", "6", "6"),
        ("e", "7", "7"),
        ("i", "7", "7"),
        ("o", "8", "8"),
        ("u", "8", "8"),
        # Short words (1-2 syllables)
        ("me", "57", "57"),
        ("no", "58", "58"),
        ("sì", "A", "E7"),
        ("là", "l6", "l6"),
        # Basic words and common patterns
        ("mote", "5897", "5897"),
        # Words with 'ç' consonant
        ("çarve", "A2v7", "ç2v7"),
        ("braç", "br6A", "br6ç"),
        ("piçul", "p7A8l", "p7ç8l"),
        ("çûç", "A8A", "ç8ç"),
        ("çucule", "A8A8l7", "ç8c8l7"),
        ("çuple", "A8pl7", "ç8pl7"),
        ("çurì", "AY7", "çY7"),
        ("çuse", "A8A7", "ç8E7"),
        ("çusse", "A8A7", "ç8E7"),
        # Words with 'gj' digraphs
        ("gjat", "g769", "E69"),
        ("bragje", "br6g77", "br6E7"),
        ("gjaldi", "g76l97", "E6l97"),
        ("gjalde", "g76l97", "E6l97"),
        ("gjenar", "g7752", "E752"),
        ("gjessis", "g77AA", "E7E7E"),
        ("gjetâ", "g7796", "E796"),
        ("gjoc", "g78A", "E80"),
        # Words with 'cj' digraphs
        ("cjalç", "A6lA", "c76lç"),
        ("ancje", "65A7", "65c77"),
        ("vecje", "v7A7", "v7c77"),
        ("cjandùs", "A6598A", "c76598E"),
        # Words with 'h' letter combinations
        ("ghe", "g7", "E7"),
        ("ghi", "g7", "E"),
        ("chê", "A", "c7"),
        ("schei", "AA7", "Ec7"),
        # Consonant clusters and complex sequences
        ("struc", "A9r8A", "E9r80"),
        ("spès", "Ap7A", "Ep7E"),
        ("blanc", "bl65A", "bl650"),
        ("spirt", "Ap7r9", "Ep7r9"),
        ("sdrume", "A9r857", "E9r857"),
        ("strucâ", "A9r8A6", "E9r8c6"),
        ("blave", "bl6v7", "bl6v7"),
        ("cnît", "A579", "c579"),
        # Words with apostrophes (common in Friulian)
        ("l'aghe", "l6g7", "l6E7"),
        ("d'àcue", "I6A87", "I6c87"),
        ("n'omp", "5853", "5853"),
        # Words with accented vowels
        ("gòs", "g8A", "E8E"),
        ("pôc", "p8A", "p80"),
        ("crês", "Ar7A", "cr7E"),
        ("fûc", "f8A", "f80"),
        ("nobèl", "58b7l", "58b7l"),
        ("babèl", "b6b7l", "b6b7l"),
        ("bertòs", "b298A", "b298E"),
        ("corfù", "AYf8", "cYf8"),
        ("epicûr", "7p7AY", "7p7cY"),
        ("maiôr", "56Y", "56Y"),
        ("nîf", "574", "574"),
        ("nîl", "57l", "57l"),
        ("nît", "579", "579"),
        ("mûf", "584", "584"),
        ("mûr", "5Y", "5Y"),
        ("mûs", "58A", "58E"),
        # Double consonants
        ("mame", "5657", "5657"),
        ("sasse", "A6A7", "E6E7"),
        ("puarte", "pY97", "pY97"),
        ("nissun", "57A85", "57E85"),
        # Words with specific endings
        ("prins", "pr1", "pr1"),
        ("gjenç", "g775A", "E75ç"),
        ("mont", "5859", "5859"),
        ("viert", "v729", "v729"),
        # Complex and longer words
        ("diretament", "I7r7965759", "Er7965759"),
        ("incjamarade", "75A652697", "75c7652697"),
        ("straçonarie", "A9r6A85277", "E9r6ç85277"),
    ]

    PHONETIC_SIMILARITY_CASES = [
        ("cjase", "cjase", True),  # identical words
        ("cjase", "kjase", False),  # different hashes (A6A7/c76E7 vs A76A7/k76E7)
        ("furlan", "forlan", True),  # vowel variation still matches
        ("xyz", "abc", False),  # clearly distinct
    ]

    FRIULIAN_SORTING_CASES = [
        ("a", "b", 1),  # phonetic hash '6' > '3' in ordering
        ("furla", "furlan", -1),  # hash 'fYl6' < 'fYl65'
        ("xyz", "abc", 1),  # xyz sorts after abc
    ]

    @pytest.mark.parametrize("word,expected_primo,expected_secondo", PHONETIC_TEST_CASES)
    def test_phonetic_word_first_hash(self, algorithm, word, expected_primo, expected_secondo):
        """Test first phonetic hash for specific word - matches COF structure"""
        primo, secondo = algorithm.get_phonetic_hashes_by_word(word)
        assert (
            primo == expected_primo
        ), f"First hash for '{word}': expected '{expected_primo}', got '{primo}'"

    @pytest.mark.parametrize("word,expected_primo,expected_secondo", PHONETIC_TEST_CASES)
    def test_phonetic_word_second_hash(self, algorithm, word, expected_primo, expected_secondo):
        """Test second phonetic hash for specific word - matches COF structure"""
        primo, secondo = algorithm.get_phonetic_hashes_by_word(word)
        assert (
            secondo == expected_secondo
        ), f"Second hash for '{word}': expected '{expected_secondo}', got '{secondo}'"

    def test_core_phonetic_hashes_bulk_verification(self, algorithm):
        """Bulk verification test to ensure all test cases pass - for regression checking"""

        # Bulk test for verification - this is now secondary to individual tests
        for word, expected_primo, expected_secondo in self.PHONETIC_TEST_CASES:
            primo, secondo = algorithm.get_phonetic_hashes_by_word(word)
            assert (
                primo == expected_primo
            ), f"Bulk test - First hash for '{word}': expected '{expected_primo}', got '{primo}'"
            assert (
                secondo == expected_secondo
            ), f"Bulk test - Second hash for '{word}': expected '{expected_secondo}', got '{secondo}'"

    @pytest.mark.parametrize(
        ("accented", "unaccented"),
        [
            ("cjatâ", "cjata"),  # â -> a normalization
            ("àèìòù", "aeiou"),  # multiple accents
        ],
    )
    def test_accent_normalization(self, algorithm, accented, unaccented):
        """Test that accented and unaccented versions produce same hashes (COF parity)"""
        acc_first, acc_second = algorithm.get_phonetic_hashes_by_word(accented)
        un_first, un_second = algorithm.get_phonetic_hashes_by_word(unaccented)

        assert (
            acc_first == un_first
        ), f"Accented '{accented}' vs unaccented '{unaccented}': first hashes differ"
        assert (
            acc_second == un_second
        ), f"Accented '{accented}' vs unaccented '{unaccented}': second hashes differ"

    def test_consistency(self, algorithm):
        """Test that the algorithm produces consistent results"""

        test_words = ["cjase", "furlan", "lenghe", "aghe", "parol"]

        for word in test_words:
            # Multiple calls should return identical results
            first1, second1 = algorithm.get_phonetic_hashes_by_word(word)
            first2, second2 = algorithm.get_phonetic_hashes_by_word(word)

            assert first1 == first2, f"Inconsistent first hash for '{word}'"
            assert second1 == second2, f"Inconsistent second hash for '{word}'"

    def test_empty_and_edge_cases(self, algorithm):
        """Test edge cases like empty strings and None inputs"""

        # Empty string
        first, second = algorithm.get_phonetic_hashes_by_word("")
        assert first == "", "Empty string should return empty first hash"
        assert second == "", "Empty string should return empty second hash"

        # None input
        first, second = algorithm.get_phonetic_hashes_by_word(None)
        assert first == "", "None input should return empty first hash"
        assert second == "", "None input should return empty second hash"

    def test_backwards_compatibility(self, algorithm):
        """Test backwards compatibility method"""

        # get_phonetic_code should return first hash only
        first_only = algorithm.get_phonetic_code("cjase")
        first, _ = algorithm.get_phonetic_hashes_by_word("cjase")

        assert first_only == first, "get_phonetic_code should return first hash"

    def test_phonetic_similarity(self, algorithm):
        """Test phonetic similarity detection"""

        # Same word should be similar
        assert algorithm.are_phonetically_similar("cjase", "cjase")

        # Different words with same hashes should be similar
        # (We'd need to find actual examples from the dictionary)

        # Completely different words should not be similar
        word1_first, word1_second = algorithm.get_phonetic_hashes_by_word("cjase")
        word2_first, word2_second = algorithm.get_phonetic_hashes_by_word("parol")

        # If none of the hashes match, they should not be similar
        if (
            word1_first != word2_first
            and word1_first != word2_second
            and word1_second != word2_first
            and word1_second != word2_second
        ):
            assert not algorithm.are_phonetically_similar("cjase", "parol")

    def test_levenshtein_friulian(self, algorithm):
        """Test Friulian-aware Levenshtein distance"""

        # Identical words
        assert algorithm.levenshtein("cjase", "cjase") == 0

        # Friulian vowel equivalences should have distance 0
        assert algorithm.levenshtein("à", "a") == 0
        assert algorithm.levenshtein("è", "e") == 0
        assert algorithm.levenshtein("café", "cafe") == 0

        # Different letters should have distance > 0
        assert algorithm.levenshtein("a", "b") == 1
        assert algorithm.levenshtein("cjase", "gjase") == 1

        # Empty strings
        assert algorithm.levenshtein("", "") == 0
        assert algorithm.levenshtein("a", "") == 1
        assert algorithm.levenshtein("", "a") == 1

    def test_friulian_sorting(self, algorithm):
        """Test Friulian-specific sorting"""

        # Basic sorting test
        words = ["zeta", "beta", "alfa", "gamma"]
        sorted_words = algorithm.sort_friulian(words)

        # Should preserve all words
        assert len(sorted_words) == len(words)
        assert set(sorted_words) == set(words)

        # Should be in alphabetical order (basic check)
        assert sorted_words[0] == "alfa"  # alfa should come first

        # Test with Friulian characters
        friulian_words = ["çà", "ca", "cè"]
        sorted_friulian = algorithm.sort_friulian(friulian_words)
        assert len(sorted_friulian) == len(friulian_words)

    def test_error_handling(self, algorithm):
        """Test error handling for invalid inputs"""

        # None input should be handled gracefully
        first, second = algorithm.get_phonetic_hashes_by_word(None)
        assert first == ""
        assert second == ""

        # Very long strings should not crash
        long_word = "a" * 1000
        first, second = algorithm.get_phonetic_hashes_by_word(long_word)
        assert isinstance(first, str)
        assert isinstance(second, str)

    # === ADDITIONAL ROBUSTNESS TESTS FOR FULL COF PARITY ===

    def test_defined_hashes_for_valid_words(self, algorithm):
        """Test that both hashes are defined for valid words"""
        primo, secondo = algorithm.get_phonetic_hashes_by_word("test")
        assert primo is not None and secondo is not None, "Valid word should return defined hashes"
        assert isinstance(primo, str) and isinstance(secondo, str), "Hashes should be strings"

    def test_non_empty_hashes_for_non_empty_input(self, algorithm):
        """Test non-empty hashes for non-empty input"""
        primo, secondo = algorithm.get_phonetic_hashes_by_word("nonempty")
        assert len(primo) > 0 and len(secondo) > 0, "Non-empty word should produce non-empty hashes"

    def test_accented_characters_robustness(self, algorithm):
        """Test accented characters handled properly"""
        primo, secondo = algorithm.get_phonetic_hashes_by_word("àèìòù")
        assert primo is not None and secondo is not None, "Accented characters should be handled"
        assert isinstance(primo, str) and isinstance(
            secondo, str
        ), "Accented char hashes should be strings"

    def test_apostrophe_handling_robustness(self, algorithm):
        """Test apostrophes (common in Friulian) handled properly"""
        primo, secondo = algorithm.get_phonetic_hashes_by_word("l'om")
        assert primo is not None and secondo is not None, "Apostrophes should be handled"
        assert isinstance(primo, str) and isinstance(
            secondo, str
        ), "Apostrophe hashes should be strings"

    def test_whitespace_only_string(self, algorithm):
        """Test whitespace-only string returns empty hashes"""
        primo, secondo = algorithm.get_phonetic_hashes_by_word("   ")
        assert primo == "", "Whitespace-only string should return empty first hash"
        assert secondo == "", "Whitespace-only string should return empty second hash"

    def test_case_insensitivity_uppercase_lowercase(self, algorithm):
        """Test case insensitivity - uppercase and lowercase produce same hashes"""
        upper_primo, upper_secondo = algorithm.get_phonetic_hashes_by_word("FURLAN")
        lower_primo, lower_secondo = algorithm.get_phonetic_hashes_by_word("furlan")

        assert upper_primo == lower_primo, "Uppercase and lowercase should produce same first hash"
        assert (
            upper_secondo == lower_secondo
        ), "Uppercase and lowercase should produce same second hash"

    # === EXTENDED BACKWARDS COMPATIBILITY TESTS ===

    def test_backwards_compatibility_fur(self, algorithm):
        """Backwards compatibility: 'fur' specific test case"""
        primo, secondo = algorithm.get_phonetic_hashes_by_word("fur")
        assert (
            primo == "fY"
        ), f"Backwards compatibility 'fur' first hash: expected 'fY', got '{primo}'"
        assert (
            secondo == "fY"
        ), f"Backwards compatibility 'fur' second hash: expected 'fY', got '{secondo}'"

    def test_backwards_compatibility_lan(self, algorithm):
        """Backwards compatibility: 'lan' specific test case"""
        primo, secondo = algorithm.get_phonetic_hashes_by_word("lan")
        assert (
            primo == "l65"
        ), f"Backwards compatibility 'lan' first hash: expected 'l65', got '{primo}'"
        assert (
            secondo == "l65"
        ), f"Backwards compatibility 'lan' second hash: expected 'l65', got '{secondo}'"

    def test_backwards_compatibility_cja(self, algorithm):
        """Backwards compatibility: 'cja' specific test case"""
        primo, secondo = algorithm.get_phonetic_hashes_by_word("cja")
        assert (
            primo == "A6"
        ), f"Backwards compatibility 'cja' first hash: expected 'A6', got '{primo}'"
        assert (
            secondo == "c76"
        ), f"Backwards compatibility 'cja' second hash: expected 'c76', got '{secondo}'"

    def test_backwards_compatibility_gjo(self, algorithm):
        """Backwards compatibility: 'gjo' specific test case"""
        primo, secondo = algorithm.get_phonetic_hashes_by_word("gjo")
        assert (
            primo == "g78"
        ), f"Backwards compatibility 'gjo' first hash: expected 'g78', got '{primo}'"
        assert (
            secondo == "E8"
        ), f"Backwards compatibility 'gjo' second hash: expected 'E8', got '{secondo}'"

    # === PHONETIC SIMILARITY DETECTION TESTS ===

    @pytest.mark.parametrize("word1,word2,expected_similar", PHONETIC_SIMILARITY_CASES)
    def test_phonetic_similarity_parity(self, algorithm, word1, word2, expected_similar):
        """Assert phonetic similarity matches COF expectations for each pair"""
        first_a, second_a = algorithm.get_phonetic_hashes_by_word(word1)
        first_b, second_b = algorithm.get_phonetic_hashes_by_word(word2)
        is_similar = (first_a == first_b) or (second_a == second_b)
        assert (
            is_similar == expected_similar
        ), f"Similarity for '{word1}' vs '{word2}' expected {expected_similar} (got {is_similar})"

    # === LEVENSHTEIN DISTANCE WITH FRIULIAN CHARACTERS ===

    def test_levenshtein_distance_furlan_furla(self, algorithm):
        """Levenshtein distance: 'furlan' vs 'furla' (edit distance 1)"""
        distance = algorithm.levenshtein("furlan", "furla")
        assert (
            distance == 1
        ), f"Levenshtein distance 'furlan' vs 'furla': expected 1, got {distance}"

    def test_levenshtein_distance_cjase_identical(self, algorithm):
        """Levenshtein distance: 'cjase' vs 'cjase' (identical, distance 0)"""
        distance = algorithm.levenshtein("cjase", "cjase")
        assert distance == 0, f"Levenshtein distance 'cjase' vs 'cjase': expected 0, got {distance}"

    def test_levenshtein_distance_lenghe_lengha(self, algorithm):
        """Levenshtein distance: 'lenghe' vs 'lengha' (edit distance 1)"""
        distance = algorithm.levenshtein("lenghe", "lengha")
        assert (
            distance == 1
        ), f"Levenshtein distance 'lenghe' vs 'lengha': expected 1, got {distance}"

    def test_levenshtein_distance_cucjar_çucjar(self, algorithm):
        """Levenshtein distance: 'çucjar' vs 'cucjar' (ç vs c, edit distance 1)"""
        distance = algorithm.levenshtein("çucjar", "cucjar")
        assert (
            distance == 1
        ), f"Levenshtein distance 'çucjar' vs 'cucjar': expected 1, got {distance}"

    # === FRIULIAN SORTING TESTS ===

    @pytest.mark.parametrize("word1,word2,expected_relation", FRIULIAN_SORTING_CASES)
    def test_friulian_sorting_parity(self, algorithm, word1, word2, expected_relation):
        """Assert Friulian phonetic sorting order matches COF expectations"""
        first_a, _ = algorithm.get_phonetic_hashes_by_word(word1)
        first_b, _ = algorithm.get_phonetic_hashes_by_word(word2)
        relation = -1 if first_a < first_b else (1 if first_a > first_b else 0)
        assert (
            relation == expected_relation
        ), f"Sorting relation for '{word1}' vs '{word2}' expected {expected_relation} (got {relation})"

    # === ERROR HANDLING EXTENDED TESTS ===

    def test_error_handling_empty_string(self, algorithm):
        """Error handling: empty string processed without crashing"""
        try:
            primo, secondo = algorithm.get_phonetic_hashes_by_word("")
            # Should return empty hashes
            assert primo == "" and secondo == "", "Empty string should return empty hashes"
        except Exception as e:
            pytest.fail(f"Error handling empty string failed: {e}")

    def test_error_handling_whitespace_only(self, algorithm):
        """Error handling: whitespace-only string processed without crashing"""
        try:
            primo, secondo = algorithm.get_phonetic_hashes_by_word("   ")
            # Should return empty hashes
            assert primo == "" and secondo == "", "Whitespace-only should return empty hashes"
        except Exception as e:
            pytest.fail(f"Error handling whitespace-only failed: {e}")

    def test_error_handling_special_characters(self, algorithm):
        """Error handling: special characters processed without crashing"""
        try:
            primo, secondo = algorithm.get_phonetic_hashes_by_word("123!@#")
            # Should handle gracefully without crashing
            assert isinstance(primo, str) and isinstance(
                secondo, str
            ), "Special chars should return string hashes"
        except Exception as e:
            pytest.fail(f"Error handling special characters failed: {e}")
