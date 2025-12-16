"""Main spell checker implementation."""

from __future__ import annotations

import re

from ..config.schemas import FurlanSpellCheckerConfig
from ..core.interfaces import IDictionary, ISpellChecker, ITextProcessor
from ..database import DatabaseManager
from ..entities.processed_element import IProcessedElement, ProcessedWord
from ..phonetic.furlan_phonetic import FurlanPhoneticAlgorithm
from .suggestion_engine import SuggestionEngine

_RE_DIGIT = re.compile(r"\d")


class FurlanSpellChecker(ISpellChecker):
    """Main implementation of Friulian spell checker."""

    def __init__(
        self,
        dictionary: IDictionary,
        text_processor: ITextProcessor,
        config: FurlanSpellCheckerConfig | None = None,
    ) -> None:
        """Initialize the spell checker."""
        self._dictionary = dictionary
        self._text_processor = text_processor
        self._processed_elements: list[IProcessedElement] = []
        self._config = config or FurlanSpellCheckerConfig()
        self._db_manager = DatabaseManager(self._config)
        self._phonetic_algo = FurlanPhoneticAlgorithm()
        # Central suggestion engine encapsulates ranking, phonetic clusters, error corrections
        self._suggestion_engine = SuggestionEngine(
            db_manager=self._db_manager,
            phonetic=self._phonetic_algo,
            max_suggestions=(config.dictionary.max_suggestions if config else 10),
        )

    @property
    def processed_elements(self) -> list[IProcessedElement]:
        """Get immutable collection of all processed elements."""
        return self._processed_elements.copy()

    @property
    def processed_words(self) -> list[IProcessedElement]:
        """Get immutable collection containing only processed words."""
        return [elem for elem in self._processed_elements if isinstance(elem, ProcessedWord)]

    def execute_spell_check(self, text: str) -> None:
        """Execute spell check on the given text."""
        # TODO: Implement spell checking logic
        self._processed_elements = self._text_processor.process_text(text)

        # Check each word
        for element in self._processed_elements:
            if isinstance(element, ProcessedWord):
                # TODO: Implement async word checking
                pass

    def clean_spell_checker(self) -> None:
        """Clean the spell checker state."""
        self._processed_elements.clear()

    def _check_word_core(self, word: ProcessedWord) -> bool:
        """
        Core implementation for checking if a word is correct.

        Shared by both async and sync frontends to avoid event loop overhead when
        not required (e.g., CLI usage).
        """
        word_str = word.current

        def _lookup_phonetic_words(hash_primary: str, hash_secondary: str) -> list[str]:
            """Batch phonetic lookup to minimize SQLite round-trips."""
            hashes: list[str] = []
            if hash_primary:
                hashes.append(hash_primary)
            if hash_secondary and hash_secondary != hash_primary:
                hashes.append(hash_secondary)

            results: list[str] = []
            batch: dict[str, str] | None = None
            if hashes:
                try:
                    batch = self._db_manager.phonetic_db.get_batch(hashes)
                except AttributeError:
                    batch = None

            for phon_hash in hashes:
                value = batch.get(phon_hash) if batch else None
                if value is None:
                    value = self._db_manager.phonetic_db.find_by_phonetic_hash(phon_hash)
                if value:
                    results.extend(value.split(","))

            return results

        # Rule 1: COF compatibility - Numbers and non-letter sequences are always correct
        # Matches Perl: if ( $word =~ /\d|(^[^$WORD_LETTERS]+$)/o ) { $answer->{ok} = 1; }
        if _RE_DIGIT.search(word_str):  # Contains any digit
            word.checked = True
            word.correct = True
            return True

        # Rule 2: COF case validation - Reject mixed case words
        # COF Perl: calc_case sets case=1 for mixed case, then _find() returns 0 (reject)
        # Valid cases: lowercase, Title case, ALL CAPS
        # Invalid case: Mixed case like FlAGJEL, FuRlAn
        is_valid_case, normalized_word = self._validate_word_case(word_str)
        if not is_valid_case:
            # Mixed case (not lowercase, not Title, not ALL CAPS) → INVALID
            word.checked = True
            word.correct = False
            return False

        # Rule 3: Check user exceptions first (highest priority - F_USER_EXC=1000)
        # Exception words should be marked as INCORRECT (they have corrections)
        user_exception = self._db_manager.sqlite_db.find_in_user_errors_database(normalized_word)
        if user_exception:
            word.checked = True
            word.correct = False  # Exception word is INCORRECT
            return False

        # Rule 4: COF compatibility - Handle Friulian elisions (l' prefix)
        # Matches Perl: elsif ( length($lc_word) > 2 && ( substr( $lc_word, 0, 2 ) eq "l'" ) )
        # The word after l' must BOTH exist in dictionary AND be in elision database
        lc_word = normalized_word
        if len(lc_word) > 2 and lc_word.startswith("l'"):
            # Extract the part after "l'"
            word_without_elision = word_str[2:]  # Preserve original case for validation
            lc_word[2:]

            # Validate case of word_without_elision
            is_valid_case_suffix, normalized_suffix = self._validate_word_case(word_without_elision)
            if not is_valid_case_suffix:
                # Mixed case in suffix → INVALID
                word.checked = True
                word.correct = False
                return False

            # Check if word without elision exists in system dictionary
            hash_a, hash_b = self._phonetic_algo.get_phonetic_hashes_by_word(normalized_suffix)
            suffix_cluster_words = _lookup_phonetic_words(hash_a, hash_b)
            word_in_dict = normalized_suffix in suffix_cluster_words

            # COF Rule: Word must be in dictionary AND in elision database
            # Perl: return !$apostrof || $self->data->word_has_elision($_);
            if word_in_dict:
                try:
                    # Check if word is in elision database
                    if self._db_manager.elision_db.has_elision(normalized_suffix):
                        word.checked = True
                        word.correct = True
                        return True
                except (FileNotFoundError, AttributeError):
                    # Elision database not available, don't mark as correct
                    pass

        # Rule 5: Check system dictionary using phonetic hashes
        # COF Perl logic (_find function):
        # 1. First check EXACT match (original case)
        # 2. If case==1 (lowercase or mixed): return 0 (reject) - already handled above
        # 3. If case==2 (Title): also check lowercase version
        # 4. If case==3 (ALL CAPS): also check lowercase and Title versions
        hash_a, hash_b = self._phonetic_algo.get_phonetic_hashes_by_word(normalized_word)

        all_cluster_words = _lookup_phonetic_words(hash_a, hash_b)

        # Step 1: Check EXACT match (original case) - Perl line 98-102
        if word_str in all_cluster_words:
            word.checked = True
            word.correct = True
            return True

        # Step 2-4: Check based on case type
        lc_word = normalized_word  # lowercase version

        # Determine case type (matching Perl calc_case)
        if word_str == lc_word:
            # case == 1: lowercase - no exact match found above, so reject
            # (This shouldn't happen since we already validated case)
            pass
        elif len(word_str) > 0 and word_str == (
            lc_word[0].upper() + lc_word[1:] if len(lc_word) > 1 else lc_word.upper()
        ):
            # case == 2: Title case - also check lowercase version
            if lc_word in all_cluster_words:
                word.checked = True
                word.correct = True
                return True
        elif word_str == lc_word.upper():
            # case == 3: ALL CAPS - check lowercase and Title versions
            ucf_word = lc_word[0].upper() + lc_word[1:] if len(lc_word) > 1 else lc_word.upper()
            if lc_word in all_cluster_words or ucf_word in all_cluster_words:
                word.checked = True
                word.correct = True
                return True

        # Rule 6: Check user dictionary (same logic as system dictionary - check EXACT word)
        user_result_a = self._db_manager.sqlite_db.find_in_user_database(hash_a)
        user_result_b = (
            self._db_manager.sqlite_db.find_in_user_database(hash_b) if hash_a != hash_b else None
        )

        # Collect user dictionary words for this phonetic hash
        user_cluster_words = []
        if user_result_a:
            user_cluster_words.extend(user_result_a.split(","))
        if user_result_b:
            user_cluster_words.extend(user_result_b.split(","))

        # Check EXACT match in user dictionary (same as system dictionary)
        if word_str in user_cluster_words or lc_word in user_cluster_words:
            word.checked = True
            word.correct = True
            return True

        # Rule 6: Fallback to in-memory dictionary (sample tests scenario)
        # NOTE: This is for tests only - real COF uses phonetic clusters exclusively
        if self._dictionary.contains_word(word_str):
            word.checked = True
            word.correct = True
            return True

        # NOTE: Radix tree is NOT used for word validation in COF Perl.
        # Perl COF uses only phonetic hash clusters (system/user dictionaries).
        # The radix tree is used for suggestion generation, not validation.
        # Removing this check ensures compatibility with Perl COF behavior.

        # Check for corrections in error databases
        system_correction = self._db_manager.error_db.get_correction(word_str)
        if system_correction:
            word.checked = True
            word.correct = False
            return False

        # Word not found in any database
        word.checked = True
        word.correct = False
        return False

    async def check_word(self, word: ProcessedWord) -> bool:
        """Async compatibility wrapper for the core word-check logic."""
        return self._check_word_core(word)

    def check_word_sync(self, word: ProcessedWord) -> bool:
        """Synchronous entrypoint for word validation (avoids event loop overhead)."""
        return self._check_word_core(word)

    async def get_word_suggestions(self, word: ProcessedWord) -> list[str]:
        """Get suggestions for the given word using the central SuggestionEngine."""
        if word.correct:
            return []
        # Delegate to suggestion engine (synchronous); keep async signature for interface parity
        return self._suggestion_engine.suggest(word.current)

    def swap_word_with_suggested(self, original_word: ProcessedWord, suggested_word: str) -> None:
        """Replace the original word with the suggested one."""
        # TODO: Implement case preservation logic
        original_word.current = suggested_word

    def ignore_word(self, word: ProcessedWord) -> None:
        """Ignore the given word during spell checking."""
        word.correct = True
        word.checked = True

    def add_word(self, word: ProcessedWord) -> None:
        """Add the given word to the dictionary."""
        # Add to user database
        self._db_manager.sqlite_db.add_to_user_database(word.current)

        # Also add to in-memory dictionary if available
        self._dictionary.add_word(word.current)

        word.correct = True
        word.checked = True

    def get_processed_text(self) -> str:
        """Return the corrected text."""
        # TODO: Implement text reconstruction logic
        return "".join(elem.current for elem in self._processed_elements)

    def get_all_incorrect_words(self) -> list[ProcessedWord]:
        """Retrieve all incorrect words."""
        incorrect_words = []
        for element in self._processed_elements:
            if isinstance(element, ProcessedWord) and element.checked and not element.correct:
                incorrect_words.append(element)
        return incorrect_words

    def suggest(self, word: str, max_suggestions: int | None = None) -> list[str]:
        """Return ranked suggestions for a raw input word (CLI/API parity)."""
        if not word:
            return []

        suggestions = self._suggestion_engine.suggest(word)
        if max_suggestions is not None:
            return suggestions[:max_suggestions]
        return suggestions

    async def check_word_str(self, word_str: str) -> bool:
        """
        Check if a raw string word is correct (async helper for backwards compatibility).

        Args:
            word_str: Word string to check

        Returns:
            True if word is correct, False otherwise
        """
        return self.check_word_str_sync(word_str)

    def check_word_str_sync(self, word_str: str) -> bool:
        """
        Synchronous helper to check a raw string word.

        Avoids creating an event loop for hot paths (CLI/COF protocol).
        """
        from ..entities.processed_element import ProcessedWord

        word = ProcessedWord(word_str)
        return self._check_word_core(word)

    async def suggest_str(self, word_str: str, max_suggestions: int | None = None) -> list[str]:
        """
        Get suggestions for a raw string word (test helper).

        Args:
            word_str: Word string to check
            max_suggestions: Maximum number of suggestions to return

        Returns:
            List of suggestion strings
        """
        return self.suggest(word_str, max_suggestions)

    def _validate_word_case(self, word_str: str) -> tuple[bool, str]:
        """
        Validate word case following COF Perl rules.

        COF case rules (from COF::SpellChecker::Answer::calc_case):
        - lowercase → valid, use as-is (case=1 in Perl, but passes exact match)
        - Title case (Furlan) → valid, normalize to lowercase (case=2 in Perl)
        - ALL CAPS (FURLAN) → valid, normalize to lowercase (case=3 in Perl)
        - Mixed case (FlAGJEL) → INVALID, reject immediately (case=1 in Perl, returns 0)

        The Perl logic:
        1. First checks exact case-sensitive match (line 98-102)
        2. If no exact match, calls calc_case
        3. calc_case returns:
           - case=1: lowercase OR mixed case
           - case=2: Title case (first upper, rest lower)
           - case=3: ALL CAPS
        4. In _find():
           - case=1 with NO exact match → return 0 (reject)
           - case=2 → check lowercase version in suggestions
           - case=3 → check lowercase or Title version in suggestions

        Returns:
            (is_valid, normalized_word)
            - is_valid: True for lowercase/Title/ALL CAPS, False for mixed case
            - normalized_word: lowercase version for dictionary lookup
        """
        lc_word = word_str.lower()

        # Check if lowercase (valid)
        if word_str == lc_word:
            return (True, lc_word)

        # Check if Title case (first upper, rest lower) - valid
        if len(word_str) > 0:
            ucf_word = lc_word[0].upper() + lc_word[1:] if len(lc_word) > 1 else lc_word.upper()
            if word_str == ucf_word:
                return (True, lc_word)

        # Check if ALL CAPS - valid
        if word_str == lc_word.upper():
            return (True, lc_word)

        # Mixed case (not lowercase, not Title, not ALL CAPS) → INVALID
        # Examples: FlAGJEL, FuRlAn, pArTiCoLâr
        return (False, lc_word)
