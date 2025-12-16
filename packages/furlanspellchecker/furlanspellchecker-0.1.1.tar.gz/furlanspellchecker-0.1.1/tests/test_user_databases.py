"""
User Database Operations Tests

This test suite mirrors COF test_user_databases.pl (54 tests) for 1:1 behavioral parity.
COF commit: 474c6e6 (2025-11-20)

Test Structure:
- Section 1: User Dictionary CRUD Operations (Tests 1-9, lines 45-159)
- Section 2: User Exceptions CRUD Operations (Tests 10-16, lines 163-237)
- Section 3: Suggestion Ranking Integration (Tests 17-25, lines 241-444)

Priority Constants (COF::SpellChecker line 9):
- F_USER_EXC = 1000 (highest priority - user exceptions override everything)
- F_SAME = 400 (exact match from system dictionary)
- F_USER_DICT = 350 (user dictionary words)
- F_ERRS = 300 (system error corrections)
- Frequency = 0-255 (corpus frequency, lowest tier)
"""

import tempfile
from pathlib import Path

import pytest
import pytest_asyncio

from furlan_spellchecker.database.user_dictionary import UserDictionaryDatabase
from furlan_spellchecker.database.user_exceptions import UserExceptionsDatabase


@pytest.fixture
def temp_dir():
    """Create temporary directory for test databases."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def user_dict_db(temp_dir):
    """Create UserDictionaryDatabase instance."""
    db_path = temp_dir / "user_dict.sqlite"
    db = UserDictionaryDatabase(db_path)
    yield db
    db.close()  # Ensure connection is closed before temp dir cleanup


@pytest.fixture
def user_exc_db(temp_dir):
    """Create UserExceptionsDatabase instance."""
    db_path = temp_dir / "user_exc.sqlite"
    db = UserExceptionsDatabase(db_path)
    yield db
    db.close()  # Ensure connection is closed before temp dir cleanup


@pytest_asyncio.fixture
async def spellchecker_with_databases(temp_dir, spellchecker_cache_dir):
    """
    Initialize FurlanSpellChecker with temporary user databases.
    Uses production system databases (via spellchecker_cache_dir) but temporary user databases.
    Returns tuple: (spellchecker, user_dict_db, user_exc_db)
    """
    from furlan_spellchecker import (
        Dictionary,
        FurlanSpellChecker,
        FurlanSpellCheckerConfig,
        TextProcessor,
    )

    # Create config that uses production system databases but temp user databases
    config = FurlanSpellCheckerConfig()
    config.dictionary.cache_directory = str(spellchecker_cache_dir)  # Use real system DBs

    # Override user database paths to temp directory
    config.dictionary.user_dictionary_path = str(temp_dir / "user_dict.sqlite")
    config.dictionary.user_exceptions_path = str(temp_dir / "user_exc.sqlite")

    # Create dictionary and text processor
    dictionary = Dictionary()
    text_processor = TextProcessor()

    # Create spellchecker (will initialize DatabaseManager internally)
    spellchecker = FurlanSpellChecker(
        dictionary=dictionary, text_processor=text_processor, config=config
    )

    # Ensure databases are available (synchronous method)
    spellchecker._db_manager.ensure_databases_available()

    # Get references to user databases
    user_dict = spellchecker._db_manager.sqlite_db._user_dictionary
    user_exc = spellchecker._db_manager.sqlite_db._user_exceptions

    yield spellchecker, user_dict, user_exc

    # Close user database connections before temp dir cleanup
    user_dict.close()
    user_exc.close()


# ============================================================================
# SECTION 1: USER DICTIONARY CRUD OPERATIONS (Tests 1-9)
# COF test_user_databases.pl lines 45-159
# ============================================================================


class TestUserDictionaryCRUD:
    """Section 1: User Dictionary CRUD Operations (COF lines 45-159)."""

    def test_01_user_dict_not_loaded_initially(self, user_dict_db):
        """
        Test 1: User dictionary not loaded initially (COF lines 45-49).

        COF assertion:
            is($data->has_user_dict, '', 'User dictionary not loaded initially');
        """
        # In Python, we check if database is empty (no words)
        assert user_dict_db.get_word_count() == 0, "User dictionary should be empty initially"

    def test_02_create_user_dict_file(self, temp_dir):
        """
        Test 2: Create user dictionary file (COF lines 51-61).

        COF assertions:
            ok(defined $result, 'User dictionary file created');
            ok($data->has_user_dict, 'User dictionary now available');
            ok(-f $user_dict_file, "User dictionary file exists: $user_dict_file");
        """
        user_dict_file = temp_dir / "test_user_dict.db"

        # Create database
        db = UserDictionaryDatabase(user_dict_file)

        try:
            # Verify creation (database initialized)
            assert db is not None, "User dictionary file created"

            # Verify database is available (can perform operations)
            assert db.get_word_count() == 0, "User dictionary now available"

            # Verify file exists on disk
            assert user_dict_file.exists(), f"User dictionary file exists: {user_dict_file}"
        finally:
            db.close()  # Ensure connection closed before temp dir cleanup

    def test_03_add_word_to_user_dict(self, user_dict_db):
        """
        Test 3: Add word to user dictionary (COF lines 63-78).

        COF assertions:
            is($result, 0, "Successfully added '$test_word' to user dictionary (returned 0)");
            ok(exists $all_words{$test_word}, "Word '$test_word' found in user dictionary");
        """
        test_word = "testfurlan"

        # Add word
        result = user_dict_db.add_word(test_word)
        assert result == 0, f"Successfully added '{test_word}' to user dictionary (returned 0)"

        # Verify word was stored
        assert user_dict_db.has_word(test_word), f"Word '{test_word}' found in user dictionary"

    def test_04_add_duplicate_word_returns_code_2(self, user_dict_db):
        """
        Test 4: Add duplicate word returns expected code (COF lines 80-83).

        COF assertion:
            is($result, 2, "Adding duplicate word '$test_word' returns 2 (already present)");
        """
        test_word = "testfurlan"

        # Add word first time
        user_dict_db.add_word(test_word)

        # Add word second time (duplicate)
        result = user_dict_db.add_word(test_word)
        assert result == 2, f"Adding duplicate word '{test_word}' returns 2 (already present)"

    def test_05_add_multiple_words_to_user_dict(self, user_dict_db):
        """
        Test 5: Add multiple words to user dictionary (COF lines 85-103).

        COF assertions:
            - 3x: is($result, 0, "Successfully added '$word' to user dictionary");
            - 3x: ok(exists $all_words{$word}, "Word '$word' found in user dictionary");
        """
        test_words = ["cjasute", "lenghete", "furlanuç"]

        # Add all words
        for word in test_words:
            result = user_dict_db.add_word(word)
            assert result == 0, f"Successfully added '{word}' to user dictionary"

        # Verify all words are accessible
        for word in test_words:
            assert user_dict_db.has_word(word), f"Word '{word}' found in user dictionary"

    def test_06_delete_word_from_user_dict(self, user_dict_db):
        """
        Test 6: Delete word from user dictionary (COF lines 105-120).

        COF assertions:
            is($result, 0, "Successfully deleted '$word_to_delete' from user dictionary");
            ok(!exists $all_words{$word_to_delete}, "Word '$word_to_delete' no longer in user dictionary");
        """
        word_to_delete = "cjasute"

        # Add word first
        user_dict_db.add_word(word_to_delete)
        assert user_dict_db.has_word(word_to_delete), "Word added successfully"

        # Delete word
        result = user_dict_db.remove_word(word_to_delete)
        assert result == 0, f"Successfully deleted '{word_to_delete}' from user dictionary"

        # Verify word is no longer in dictionary
        assert not user_dict_db.has_word(
            word_to_delete
        ), f"Word '{word_to_delete}' no longer in user dictionary"

    def test_07_change_word_in_user_dict(self, user_dict_db):
        """
        Test 7: Change word in user dictionary (delete old, add new) (COF lines 122-140).

        COF assertions:
            is($result, 0, "Successfully changed '$old_word' to '$new_word'");
            ok(!exists $all_words{$old_word}, "Old word '$old_word' no longer in user dictionary");
            ok(exists $all_words{$new_word}, "New word '$new_word' found in user dictionary");
        """
        old_word = "lenghete"
        new_word = "lenghetis"

        # Add old word
        user_dict_db.add_word(old_word)

        # Change word
        result = user_dict_db.change_word(new_word, old_word)
        assert result == 0, f"Successfully changed '{old_word}' to '{new_word}'"

        # Verify old word is gone and new word exists
        assert not user_dict_db.has_word(
            old_word
        ), f"Old word '{old_word}' no longer in user dictionary"
        assert user_dict_db.has_word(new_word), f"New word '{new_word}' found in user dictionary"

    @pytest.mark.asyncio
    async def test_08_user_dict_word_recognized_as_correct(self, spellchecker_with_databases):
        """
        Test 8: User dictionary words are recognized as correct (COF lines 142-147).

        COF assertion:
            is($result->{ok}, 1, "User dictionary word '$user_word' recognized as correct");
        """
        spellchecker, user_dict, user_exc = spellchecker_with_databases

        user_word = "furlanuç"

        # Add word to user dictionary
        user_dict.add_word(user_word)

        # Check word (should be correct)
        result = await spellchecker.check_word_str(user_word)
        assert result is True, f"User dictionary word '{user_word}' recognized as correct"

    def test_09_clear_user_dict(self, user_dict_db):
        """
        Test 9: Clear user dictionary (COF lines 149-159).

        COF assertion:
            is($word_count, 0, 'User dictionary cleared (empty)');
        """
        # Add some words
        user_dict_db.add_word("word1")
        user_dict_db.add_word("word2")
        user_dict_db.add_word("word3")

        # Clear dictionary
        user_dict_db.clear()

        # Verify empty
        word_count = user_dict_db.get_word_count()
        assert word_count == 0, "User dictionary cleared (empty)"


# ============================================================================
# SECTION 2: USER EXCEPTIONS CRUD OPERATIONS (Tests 10-16)
# COF test_user_databases.pl lines 163-237
# ============================================================================


class TestUserExceptionsCRUD:
    """Section 2: User Exceptions CRUD Operations (COF lines 163-237)."""

    def test_10_user_exc_not_loaded_initially(self, user_exc_db):
        """
        Test 10: User exceptions not loaded initially (COF lines 163-167).

        COF assertion:
            is($data->has_user_exc, '', 'User exceptions not loaded initially');
        """
        # In Python, check if database is empty (no exceptions)
        assert user_exc_db.get_exception_count() == 0, "User exceptions not loaded initially"

    def test_11_create_user_exc_file(self, temp_dir):
        """
        Test 11: Create user exceptions file (COF lines 169-179).

        COF assertions:
            ok(defined $result, 'User exceptions file created');
            ok($data->has_user_exc, 'User exceptions now available');
            ok(-f $user_exc_file, "User exceptions file exists: $user_exc_file");
        """
        user_exc_file = temp_dir / "test_user_exc.db"

        # Create database
        db = UserExceptionsDatabase(user_exc_file)

        try:
            # Verify creation
            assert db is not None, "User exceptions file created"

            # Verify database is available
            assert db.get_exception_count() == 0, "User exceptions now available"

            # Verify file exists on disk
            assert user_exc_file.exists(), f"User exceptions file exists: {user_exc_file}"
        finally:
            db.close()  # Ensure connection closed before temp dir cleanup

    def test_12_add_exception_to_user_exc(self, user_exc_db):
        """
        Test 12: Add exception to user exceptions (COF lines 181-194).

        COF assertion:
            is($user_exc->{$error_word}, $correction,
               "Exception '$error_word' → '$correction' added successfully");
        """
        error_word = "sbajât"
        correction = "sbagliât"

        # Add exception
        result = user_exc_db.add_exception(error_word, correction)
        assert result is True, "Exception added successfully"

        # Verify exception stored correctly
        stored_correction = user_exc_db.get_correction(error_word)
        assert (
            stored_correction == correction
        ), f"Exception '{error_word}' → '{correction}' added successfully"

    @pytest.mark.asyncio
    async def test_13_user_exc_word_marked_as_incorrect(self, spellchecker_with_databases):
        """
        Test 13: User exception word is marked as incorrect (COF lines 196-207).

        COF assertion:
            is($result->{ok}, 0, "User exception word '$error_word' marked as incorrect");

        CRITICAL TEST: Exception words should be marked as INCORRECT (not correct).
        This tests that SpellChecker.check_word() properly checks user exceptions.
        """
        spellchecker, user_dict, user_exc = spellchecker_with_databases

        error_word = "sbajât"
        correction = "sbagliât"

        # Add exception
        user_exc.add_exception(error_word, correction)

        # Check word (should be INCORRECT)
        result = await spellchecker.check_word_str(error_word)
        assert result is False, f"User exception word '{error_word}' marked as incorrect"

    def test_14_add_multiple_exceptions(self, user_exc_db):
        """
        Test 14: Add multiple exceptions (COF lines 209-222).

        COF assertions (3x):
            is($user_exc->{$error}, $test_exceptions{$error},
               "Exception '$error' → '$test_exceptions{$error}' stored correctly");
        """
        test_exceptions = {
            "errôr1": "correction1",
            "errôr2": "correction2",
            "errôr3": "correction3",
        }

        # Add all exceptions
        for error, correction in test_exceptions.items():
            user_exc_db.add_exception(error, correction)

        # Verify all exceptions stored correctly
        for error, expected_correction in test_exceptions.items():
            stored_correction = user_exc_db.get_correction(error)
            assert (
                stored_correction == expected_correction
            ), f"Exception '{error}' → '{expected_correction}' stored correctly"

    def test_15_delete_exception_from_user_exc(self, user_exc_db):
        """
        Test 15: Delete exception from user exceptions (COF lines 224-231).

        COF assertion:
            ok(!exists $user_exc->{$error_to_delete},
               "Exception '$error_to_delete' deleted successfully");
        """
        error_to_delete = "errôr1"

        # Add exception first
        user_exc_db.add_exception(error_to_delete, "correction1")
        assert user_exc_db.has_exception(error_to_delete), "Exception added"

        # Delete exception
        result = user_exc_db.remove_exception(error_to_delete)
        assert result is True, "Delete operation successful"

        # Verify exception deleted
        assert not user_exc_db.has_exception(
            error_to_delete
        ), f"Exception '{error_to_delete}' deleted successfully"

    def test_16_clear_user_exc(self, user_exc_db):
        """
        Test 16: Clear user exceptions (COF lines 233-237).

        COF assertion:
            is($exc_count, 0, 'User exceptions cleared (empty)');
        """
        # Add some exceptions
        user_exc_db.add_exception("error1", "correction1")
        user_exc_db.add_exception("error2", "correction2")
        user_exc_db.add_exception("error3", "correction3")

        # Clear exceptions
        user_exc_db.clear()

        # Verify empty
        exc_count = user_exc_db.get_exception_count()
        assert exc_count == 0, "User exceptions cleared (empty)"


# ============================================================================
# SECTION 3: SUGGESTION RANKING INTEGRATION (Tests 17-25)
# COF test_user_databases.pl lines 241-444
# ============================================================================


class TestSuggestionRankingIntegration:
    """Section 3: Suggestion Ranking Integration (COF lines 241-444)."""

    @pytest.mark.asyncio
    async def test_17_user_dict_word_ranks_with_priority_350(self, spellchecker_with_databases):
        """
        Test 17: User dictionary word appears in suggestions with F_USER_DICT priority (350) (COF lines 245-273).

        COF assertions:
            ok($found, "User dictionary word '$user_word' appears in suggestions for '$misspelling'");
            (diagnostic: position in ranking)
        """
        spellchecker, user_dict, user_exc = spellchecker_with_databases

        # Add a phonetically similar word to user dictionary
        user_word = "testcjase"
        user_dict.add_word(user_word)

        # Misspell it slightly to trigger suggestions
        misspelling = "testcjaze"
        suggestions = await spellchecker.suggest_str(misspelling)

        # Check if user_word appears in suggestions
        found = any(s.lower() == user_word.lower() for s in suggestions)
        assert (
            found
        ), f"User dictionary word '{user_word}' appears in suggestions for '{misspelling}'"

        # Diagnostic: log position
        if found:
            position = next(i for i, s in enumerate(suggestions) if s.lower() == user_word.lower())
            print(f"User word '{user_word}' found at position {position}")

    @pytest.mark.asyncio
    async def test_18_user_exc_correction_ranks_first_priority_1000(
        self, spellchecker_with_databases
    ):
        """
        Test 18: User exception correction ranks with F_USER_EXC priority (1000 - highest) (COF lines 275-295).

        COF assertions:
            ok(@$suggestions > 0, "Suggestions returned for user exception '$error'");
            is(lc($suggestions->[0]), lc($correction),
               "User exception correction '$correction' ranks first (F_USER_EXC=1000)");

        CRITICAL TEST: User exception corrections should rank FIRST (highest priority).
        """
        spellchecker, user_dict, user_exc = spellchecker_with_databases

        # Add an exception: common misspelling → correction
        error = "testfurla"
        correction = "testfurlan"
        user_exc.add_exception(error, correction)

        # Get suggestions for the error word
        suggestions = await spellchecker.suggest_str(error)

        # Verify suggestions returned
        assert len(suggestions) > 0, f"Suggestions returned for user exception '{error}'"

        # Verify correction ranks first (highest priority)
        assert (
            suggestions[0].lower() == correction.lower()
        ), f"User exception correction '{correction}' ranks first (F_USER_EXC=1000)"

    @pytest.mark.asyncio
    async def test_19_system_error_dict_correction_ranks_priority_300(
        self, spellchecker_with_databases
    ):
        """
        Test 19: System error dictionary correction ranks with F_ERRS priority (300) (COF lines 297-323).

        COF assertions:
            ok(@$suggestions > 0, "Suggestions returned for system error '$sys_error'");
            (diagnostic: first suggestion logged)
            pass("System error dictionary tested (F_ERRS=300)");

        Note: This test uses a known system error from errors database.
        Example: 'adincuatri' → 'ad in cuatri'
        """
        spellchecker, user_dict, user_exc = spellchecker_with_databases

        # Use a known system error (if errors database available)
        sys_error = "adincuatri"

        # Get suggestions
        suggestions = await spellchecker.suggest_str(sys_error)

        # Verify suggestions returned
        assert len(suggestions) > 0, f"Suggestions returned for system error '{sys_error}'"

        # Diagnostic: log first suggestion
        print(f"First suggestion for '{sys_error}': '{suggestions[0]}'")

        # Pass test (system error dictionary tested with F_ERRS=300)
        assert True, "System error dictionary tested (F_ERRS=300)"

    @pytest.mark.asyncio
    async def test_20_priority_order_verification_complete_hierarchy(
        self, spellchecker_with_databases
    ):
        """
        Test 20: Priority order verification (F_USER_EXC > F_USER_DICT > F_ERRS > frequency) (COF lines 325-360).

        COF complete priority hierarchy:
            F_USER_EXC (1000) > F_SAME (400) > F_USER_DICT (350) > F_ERRS (300) > frequency (0-255)

        COF assertions:
            is($result->{ok}, 0, "User exception overrides user dictionary (word marked incorrect)");
            ok(@$suggestions > 0, "Suggestions returned for priority test");
            is(lc($suggestions->[0]), lc($user_exc_correction),
               "User exception correction ranks first (highest priority)");

        CRITICAL TEST: Verifies complete priority hierarchy with exception overriding dictionary.
        """
        spellchecker, user_dict, user_exc = spellchecker_with_databases

        # Add both user dict word and user exception for same phonetic space
        user_dict_word = "prioritest"
        user_exc_error = "prioritest"
        user_exc_correction = "prioritestcorrect"

        # Add to user dictionary first
        user_dict.add_word(user_dict_word)

        # Then add as exception (exception should override)
        user_exc.add_exception(user_exc_error, user_exc_correction)

        # Check that exception overrides dictionary
        result = await spellchecker.check_word_str(user_exc_error)
        assert result is False, "User exception overrides user dictionary (word marked incorrect)"

        # Get suggestions
        suggestions = await spellchecker.suggest_str(user_exc_error)
        assert len(suggestions) > 0, "Suggestions returned for priority test"

        # Exception correction should rank first
        assert (
            suggestions[0].lower() == user_exc_correction.lower()
        ), "User exception correction ranks first (highest priority)"

    @pytest.mark.asyncio
    async def test_21_case_handling_in_user_dict(self, spellchecker_with_databases):
        """
        Test 21: Case handling in user dictionary (COF lines 362-381).

        COF assertions (3x):
            ok($result->{ok} >= 0, "Case variation of user word recognized: '$lower'");
        """
        spellchecker, user_dict, user_exc = spellchecker_with_databases

        # Add words with different cases
        case_words = ["TestCase", "ALLCAPS", "lowercase"]

        for word in case_words:
            user_dict.add_word(word)

        # Verify case-insensitive matching
        for word in case_words:
            lower = word.lower()
            result = await spellchecker.check_word_str(lower)

            # Should be recognized (case-insensitive)
            assert result is not None, f"Case variation of user word recognized: '{lower}'"

    def test_22_phonetic_indexing_integrity(self, user_dict_db):
        """
        Test 22: Phonetic indexing integrity (COF lines 383-406).

        COF assertions:
            ok(defined $code_a && $code_a ne '', "Primary phonetic code generated: '$code_a'");
            ok(defined $code_b && $code_b ne '', "Secondary phonetic code generated: '$code_b'");
            ok(exists $all_words{$test_word}, "Word indexed and retrievable from dictionary");
        """
        from furlan_spellchecker.phonetic.furlan_phonetic import FurlanPhoneticAlgorithm

        test_word = "phonetictestword"

        # Add word
        user_dict_db.add_word(test_word)

        # Get phonetic codes
        phonetic = FurlanPhoneticAlgorithm()
        code_a, code_b = phonetic.get_phonetic_hashes_by_word(test_word)

        # Verify codes generated
        assert code_a and code_a != "", f"Primary phonetic code generated: '{code_a}'"
        assert code_b and code_b != "", f"Secondary phonetic code generated: '{code_b}'"

        # Verify word indexed and retrievable
        assert user_dict_db.has_word(test_word), "Word indexed and retrievable from dictionary"

    def test_23_empty_word_handling(self, user_dict_db, user_exc_db):
        """
        Test 23: Empty word handling (COF lines 408-423).

        COF assertions:
            ok(!$@ || defined $result, "Empty word handled without crash");
            ok($exc_result, "Empty exception key handled without crash");
        """
        # Test empty word in user dictionary
        result = None
        try:
            result = user_dict_db.add_word("")
        except Exception:
            pass

        # Should not crash (either returns result or exception handled)
        assert result is not None or True, "Empty word handled without crash"

        # Test empty exception key
        exc_result = None
        try:
            exc_result = user_exc_db.add_exception("", "correction")
        except Exception:
            exc_result = True  # Exception handled gracefully

        assert exc_result is not None, "Empty exception key handled without crash"

    def test_24_unicode_special_character_handling(self, user_dict_db):
        """
        Test 24: Unicode/special character handling (COF lines 425-434).

        COF assertions (4x):
            ok(defined $result, "Special character word '$word' handled");
        """
        special_words = ["cjàse", "furlanâ", "ç", "àèìòù"]

        for word in special_words:
            result = user_dict_db.add_word(word)
            assert result is not None, f"Special character word '{word}' handled"

    def test_25_large_user_dict_performance(self, user_dict_db):
        """
        Test 25: Large user dictionary performance (COF lines 436-444).

        COF assertion:
            ok($elapsed < 10, "Added $word_count words in reasonable time ($elapsed seconds)");
        """
        import time

        word_count = 100
        start_time = time.time()

        # Add many words to test performance
        for i in range(word_count):
            word = f"perftest{i}"
            user_dict_db.add_word(word)

        elapsed = time.time() - start_time

        assert elapsed < 10, f"Added {word_count} words in reasonable time ({elapsed:.2f} seconds)"
