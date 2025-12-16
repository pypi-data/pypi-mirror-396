"""Central Suggestion Engine for FurlanSpellChecker.

Phase 1 scope:
- Phonetic cluster retrieval (system dictionary only)
- System error corrections integration
- Frequency weighting
- Elision / apostrophe prefixed variants (l'/la, d'/di, un'/une)
- Case classification & normalization
- Hyphen handling (basic split & recombination)
- Ranking: weight constants / frequency > edit distance > Friulian sort

Deferred (placeholders):
- User dictionary integration
- User errors integration
- Radix tree edit-distance-1 suggestions

Design notes:
- Weight constants reflect an internal priority ladder; future tiers (user dict, radix) can be inserted without renumbering existing ones.
- Dependencies are injected (database manager, phonetic algorithm) to simplify testing.
- Returned list is already ranked and unique. By default, returns all suggestions (like COF).
  Applications can limit results by setting max_suggestions parameter.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

try:
    from rapidfuzz.distance import Levenshtein as _RFLevenshtein
except Exception:  # pragma: no cover - optional dependency
    _RFLevenshtein = None  # type: ignore

from ..database import DatabaseManager
from ..phonetic.furlan_phonetic import FurlanPhoneticAlgorithm

# -----------------------------
# Weight Constants
# -----------------------------
# Priority ladder (COF-compatible):
# 1. User exception (1000)      - User-defined corrections (highest priority)
# 2. Exact same lowercase (400) - Exact match from system dictionary
# 3. User dictionary (350)      - User-added words
# 4. System errors (300)        - System error corrections
# 5. Radix edit distance (freq) - Edit distance 1 suggestions
# 6. System phonetic (freq)     - Phonetic similarity suggestions
# Numeric values chosen to leave gaps for future insertion without rewrites.

F_USER_EXC = 1000  # User exceptions (highest priority)
F_SAME = 400  # Exact match from system dictionary
F_USER_DICT = 350  # User dictionary words
F_ERRS = 300  # System error corrections
# Radix suggestions will use frequency directly (0-255).

_VOWEL_TRANSLATION = str.maketrans(
    {
        "à": "a",
        "á": "a",
        "â": "a",
        "è": "e",
        "é": "e",
        "ê": "e",
        "ì": "i",
        "í": "i",
        "î": "i",
        "ò": "o",
        "ó": "o",
        "ô": "o",
        "ù": "u",
        "ú": "u",
        "û": "u",
        "j": "i",
    }
)


@dataclass
class Candidate:
    word: str
    base_weight: int
    distance: int
    original_freq: int


class CaseClass(Enum):
    LOWER = 1
    UCFIRST = 2
    UPPER = 3


class SuggestionEngine:
    def __init__(
        self,
        db_manager: DatabaseManager,
        phonetic: FurlanPhoneticAlgorithm | None = None,
        max_suggestions: int | None = None,
    ) -> None:
        self.db = db_manager
        self.phonetic = phonetic or FurlanPhoneticAlgorithm()
        self.max_suggestions = max_suggestions
        # Simple cache for frequency lookups
        self._freq_cache: dict[str, int] = {}

    # -------- Public API --------
    def suggest(self, word: str) -> list[str]:
        """
        Generate spelling suggestions following COF's exact algorithm.

        COF Priority Order (from SpellChecker.pm _basic_suggestions):
        5. Phonetic suggestions (system dict) + frequency
        4. Phonetic suggestions (user dict) + frequency
        3. RadixTree suggestions + frequency
        2. System error corrections (no frequency)
        1. User error corrections (no frequency)

        Special handling for apostrophes (d', un', l') and hyphens.
        """
        if not word:
            return []

        # NOTE: We do NOT strip punctuation here to maintain compatibility with COF Perl behavior.
        # COF Perl's suggest method takes the word as-is.
        # The stripping logic (if any) belongs in the CLI/Protocol layer.

        if not word:
            return []

        case_class = self._classify_case(word)
        lower_word = word.lower()

        # Build suggestions dictionary following COF logic
        suggestions = self._cof_basic_suggestions(word, lower_word, case_class)

        # Handle special cases like COF's _build_suggestions
        suggestions = self._cof_handle_apostrophes(word, lower_word, case_class, suggestions)
        suggestions = self._cof_handle_hyphens(word, suggestions)

        # Rank and return like COF's suggest method
        return self._cof_rank_suggestions(suggestions, case_class)

    # -------- COF Algorithm Implementation --------
    def _cof_basic_suggestions(
        self, word: str, lower_word: str, case_class: CaseClass
    ) -> dict[str, list[Any]]:
        """
        Implement COF's _basic_suggestions method exactly.

        Returns dictionary: {suggestion_word: [frequency_or_weight, distance]}
        """
        suggestions: dict[str, list[Any]] = {}
        temp_candidates = {}  # COF's %sugg hash

        # Get phonetic codes
        code_a, code_b = self.phonetic.get_phonetic_hashes_by_word(lower_word)

        # 1. Phonetic suggestions (system dict) - priority 5
        phonetic_sys: list[str] = []
        hashes_to_lookup: list[str] = [code_a] if code_a else []
        if code_b and code_b != code_a:
            hashes_to_lookup.append(code_b)

        batch_results: dict[str, str] = {}
        if hashes_to_lookup:
            try:
                batch_results = self.db.phonetic_db.get_batch(hashes_to_lookup)
            except AttributeError:
                batch_results = {}

        seen_sys: set[str] = set()
        for phon_hash in hashes_to_lookup:
            result = batch_results.get(phon_hash)
            if result is None:
                result = self.db.phonetic_db.find_by_phonetic_hash(phon_hash)
            if result:
                for word_candidate in result.split(","):
                    if word_candidate and word_candidate not in seen_sys:
                        seen_sys.add(word_candidate)
                        phonetic_sys.append(word_candidate)

        for word_candidate in phonetic_sys:
            temp_candidates[word_candidate] = 5

        # 2. Phonetic suggestions (user dict) - priority 4
        try:
            user_phonetic = self.db.sqlite_db.get_user_dictionary_suggestions(
                lower_word, max_suggestions=50
            )
            for word_candidate in user_phonetic:
                if word_candidate:
                    # Overwrite priority if found in user dict (better than system phonetic)
                    temp_candidates[word_candidate] = 4
        except Exception:
            pass

        # 3. RadixTree suggestions - priority 3
        # Use _add_radix_edit_distance_candidates which handles asterisk expansion
        try:
            # Create temporary dict for radix candidates
            radix_candidates_dict: dict[str, Any] = {}
            self._add_radix_edit_distance_candidates(lower_word, radix_candidates_dict)

            # Add to temp_candidates with priority 3
            for word_candidate in radix_candidates_dict.keys():
                if word_candidate:
                    # Overwrite priority if found in RadixTree (better than phonetic)
                    temp_candidates[word_candidate] = 3
        except Exception:
            pass

        # 4. System error corrections - priority 2
        try:
            error_correction = self.db.error_db.get_correction(word)
            if error_correction:
                temp_candidates[error_correction] = 2
        except (FileNotFoundError, AttributeError):
            # Fallback to old method
            error_corrections = self._get_error_corrections(word)
            for correction in error_corrections:
                temp_candidates[correction] = 2

        # 5. User error corrections - priority 1 (highest priority)
        try:
            user_correction = self.db.sqlite_db.find_in_user_errors_database(word)
            if user_correction:
                temp_candidates[user_correction] = 1
        except Exception:
            pass

        # Convert to COF's final format: {word: [frequency_or_weight, distance]}
        for candidate, priority in temp_candidates.items():
            fixed_candidate = self._apply_case(case_class, candidate)

            if fixed_candidate not in suggestions:
                candidate_lower = candidate.lower()

                # Calculate values like COF
                if lower_word == candidate_lower:
                    # Exact match gets F_SAME weight
                    vals = [F_SAME, 0]
                elif priority == 1:
                    # User exceptions
                    vals = [F_USER_EXC, 0]
                elif priority == 2:
                    # System errors
                    vals = [F_ERRS, 0]
                elif priority == 3:
                    # RadixTree - use frequency + edit distance 1
                    frequency = self._get_frequency(candidate)
                    vals = [frequency, 1]
                elif priority == 4:
                    # User dict - use F_USER_DICT + levenshtein
                    distance = self._levenshtein(lower_word, candidate_lower)
                    vals = [F_USER_DICT, distance]
                else:  # priority == 5
                    # System phonetic - use frequency + levenshtein
                    frequency = self._get_frequency(candidate)
                    distance = self._levenshtein(lower_word, candidate_lower)
                    vals = [frequency, distance]

                suggestions[fixed_candidate] = vals

        return suggestions

    def _cof_handle_apostrophes(
        self,
        word: str,
        lower_word: str,
        case_class: CaseClass,
        base_suggestions: dict[str, list[Any]],
    ) -> dict[str, list[Any]]:
        """
        Handle apostrophe contractions like COF's _build_suggestions.

        Handles d', un', l' patterns exactly like COF.
        """
        suggestions = base_suggestions.copy()

        # Handle d' prefix (pos=2)
        if len(lower_word) > 2 and lower_word.startswith("d'"):
            suffix_word = word[2:]
            suffix_lower = lower_word[2:]

            # Create answer object for suffix
            suffix_suggestions = self._cof_basic_suggestions(
                suffix_word, suffix_lower, self._classify_case(suffix_word)
            )

            # Determine case for 'di'
            if case_class == CaseClass.UPPER:
                prefix = "DI "
            elif case_class == CaseClass.UCFIRST or (len(word) > 0 and word[0].isupper()):
                prefix = "Di "
            else:
                prefix = "di "

            # Add combined suggestions
            for suffix_candidate, vals in suffix_suggestions.items():
                combined = prefix + suffix_candidate
                # Increment distance by 1 as per COF
                suggestions[combined] = [vals[0], vals[1] + 1]

        # Handle un' prefix (pos=3)
        elif len(lower_word) > 3 and lower_word.startswith("un'"):
            suffix_word = word[3:]
            suffix_lower = lower_word[3:]

            suffix_suggestions = self._cof_basic_suggestions(
                suffix_word, suffix_lower, self._classify_case(suffix_word)
            )

            # Determine case for 'une'
            if case_class == CaseClass.UPPER:
                prefix = "UNE "
            elif case_class == CaseClass.UCFIRST or (len(word) > 0 and word[0].isupper()):
                prefix = "Une "
            else:
                prefix = "une "

            for suffix_candidate, vals in suffix_suggestions.items():
                combined = prefix + suffix_candidate
                suggestions[combined] = [vals[0], vals[1] + 1]

        # Handle l' prefix (pos=2) - MOST COMPLEX CASE
        elif len(lower_word) > 2 and lower_word.startswith("l'"):
            suffix_word = word[2:]
            suffix_lower = lower_word[2:]

            suffix_suggestions = self._cof_basic_suggestions(
                suffix_word, suffix_lower, self._classify_case(suffix_word)
            )

            # Determine case for prefixes
            if case_class == CaseClass.UPPER:
                prefix_ap = "L'"  # l' apostrophe form
                prefix_no_ap = "LA "  # la non-apostrophe form
            elif case_class == CaseClass.UCFIRST or (len(word) > 0 and word[0].isupper()):
                prefix_ap = "L'"
                prefix_no_ap = "La "
            else:
                prefix_ap = "l'"
                prefix_no_ap = "la "

            # For each suffix candidate, decide l' vs la based on elision
            for suffix_candidate, vals in suffix_suggestions.items():
                frequency, distance = vals

                # Get the dictionary form for elision check (3rd element in COF)
                dict_form = suffix_candidate.lower()

                # Check if word supports elision using ElisionDatabase
                try:
                    has_elision = self.db.elision_db.has_elision(dict_form)
                except (FileNotFoundError, AttributeError):
                    # Fallback: assume no elision if database not available
                    has_elision = False

                # Choose prefix based on elision rule
                prefix = prefix_ap if has_elision else prefix_no_ap
                combined = prefix + suffix_candidate

                # Distance increases by 1 as per COF
                suggestions[combined] = [frequency, distance + 1]

        return suggestions

    def _get_case_words(self, word: str) -> list[str]:
        """Get all case variants of a word using phonetic dictionary.

        Matches COF::SpellChecker::get_case_words (SpellChecker.pm line 42-48).
        When radix tree returns asterisk-marked words (e.g., 'cjas*'), we need
        to expand to all case variants by querying the phonetic dict.

        Args:
            word: Input word (typically lowercase after asterisk strip)

        Returns:
            List of all case variants: ['cjas', 'Cjas']

        Example:
            >>> _get_case_words('cjas')
            ['cjas', 'Cjas']  # Common word + proper noun
        """
        lc_word = word.lower()

        # Get both phonetic codes for the word
        code_a, code_b = self.phonetic.get_phonetic_hashes_by_word(lc_word)

        # Query phonetic dict for all words with same codes (matching COF's phonetic hash lookup)
        all_words = []

        # Lookup codeA in phonetic database
        sys_a = self.db.phonetic_db.find_by_phonetic_hash(code_a)
        if sys_a:
            all_words.extend(sys_a.split(","))

        # Lookup codeB if different from codeA
        if code_b != code_a:
            sys_b = self.db.phonetic_db.find_by_phonetic_hash(code_b)
            if sys_b:
                all_words.extend(sys_b.split(","))

        # Filter to case-insensitive matches
        variants = [w for w in all_words if w and w.lower() == lc_word]

        # Remove duplicates while preserving order
        seen = set()
        unique_variants = []
        for w in variants:
            if w not in seen:
                seen.add(w)
                unique_variants.append(w)

        return unique_variants

    def _add_radix_edit_distance_candidates(
        self, lower_word: str, candidates: dict[str, Any]
    ) -> None:
        """Add edit-distance-1 suggestions using RadixTree, matching COF's get_rt_sugg method.

        Uses the binary RadixTree to find all words within edit distance 1 of the input word.
        This directly matches COF's RadixTree implementation for maximum compatibility.
        Matches COF::SpellChecker::get_rt_sugg (SpellChecker.pm line 49-60).
        When radix returns asterisk-marked words, expand to all case variants.

        Args:
            lower_word: The lowercase input word
            candidates: Dict to populate (Dict[str, Candidate] or simple Dict[str, Any])
        """
        if not lower_word:
            return

        try:
            # Get raw suggestions from RadixTree (includes asterisk markers)
            raw_suggestions = self.db.radix_tree.get_words_ed1(lower_word)

            for suggestion in raw_suggestions:
                if suggestion.endswith("*"):
                    # Asterisk marks uppercase variant - expand to all cases
                    base_word = suggestion.rstrip("*")
                    variants = self._get_case_words(base_word)

                    for variant in variants:
                        if variant not in candidates:
                            # Simple dict - just add the key (value will be set by caller)
                            candidates[variant] = None
                else:
                    # No asterisk - add as-is
                    if suggestion and suggestion not in candidates:
                        candidates[suggestion] = None

        except Exception:
            # If RadixTree fails, fall back gracefully
            pass

    # -------- Core Steps --------
    def _get_phonetic_candidates(self, lower_word: str) -> list[str]:
        """
        Get phonetic candidates exactly like COF's get_phonetic_sugg method.

        COF logic (SpellChecker.pm lines 18-40, 252-254):
        - Lookup codeA in phonetic hash (words.db) - priority 5
        - Lookup codeB in phonetic hash (words.db) - priority 5
        - Lookup codeA in user dictionary (phonetic) - priority 4
        - Lookup codeB in user dictionary (phonetic) - priority 4
        - Return union of both results (split by comma)
        - NO prefix matching, NO frequency database search

        Returns List to preserve phonetic dict order (lowercase before uppercase).
        This makes FurlanSpellChecker MORE deterministic than COF (which uses hash iteration).
        """
        h1, h2 = self.phonetic.get_phonetic_hashes_by_word(lower_word)
        words_list: list[str] = []
        seen: set[str] = set()

        # Exact lookup in system phonetic database (words.sqlite)
        # Matches COF: $hash->{$codeA} and $hash->{$codeB}
        hashes: list[str] = [h1] if h1 else []
        if h2 and h2 != h1:
            hashes.append(h2)

        batch_results: dict[str, str] = {}
        if hashes:
            try:
                batch_results = self.db.phonetic_db.get_batch(hashes)
            except AttributeError:
                batch_results = {}

        for phon_hash in hashes:
            sys_words = batch_results.get(phon_hash)
            if sys_words is None:
                sys_words = self.db.phonetic_db.find_by_phonetic_hash(phon_hash)
            if sys_words:
                for word in sys_words.split(","):
                    if word and word not in seen:
                        words_list.append(word)
                        seen.add(word)

        # Lookup in user dictionary phonetic index (COF line 254)
        # COF: $sugg{$_} = 4 for $self->get_phonetic_sugg( 'user', $codeA, $codeB );
        try:
            user_dict = self.db.sqlite_db._user_dictionary
            if user_dict:
                # Get words for h1
                user_words_h1 = user_dict.get_words_by_phonetic_code(h1)
                for word in user_words_h1:
                    if word and word not in seen:
                        words_list.append(word)
                        seen.add(word)

                # Get words for h2 (if different)
                if h2 != h1:
                    user_words_h2 = user_dict.get_words_by_phonetic_code(h2)
                    for word in user_words_h2:
                        if word and word not in seen:
                            words_list.append(word)
                            seen.add(word)
        except Exception:
            # Silently fail if user dictionary not available
            pass

        return words_list

    def _get_frequency_phonetic_candidates(self, lower_word: str, h1: str, h2: str) -> set[str]:
        """Find phonetically similar words in frequency database (COF-compatible behavior)."""
        words: set[str] = set()

        try:
            # Get all words from frequency database and check phonetic compatibility
            import sqlite3

            # Get frequency database path from database manager
            cache_dir = self.db._cache_dir
            freq_db_path = cache_dir / "frequencies" / "frequencies.sqlite"

            if not freq_db_path.exists():
                return words

            with sqlite3.connect(freq_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT Key FROM Data WHERE Value IS NOT NULL AND Key != ''")
                all_words = [row[0] for row in cursor.fetchall()]

            # Check each word for phonetic compatibility
            for word in all_words:
                if not word or len(word) < 2:
                    continue

                try:
                    word_h1, word_h2 = self.phonetic.get_phonetic_hashes_by_word(word)

                    # COF-style compatibility: exact match or prefix match
                    if (
                        h1 == word_h1
                        or h1 == word_h2
                        or h2 == word_h1
                        or h2 == word_h2
                        or
                        # Prefix compatibility (like fYl6 matches fYl65, fYl657, etc.)
                        (
                            len(h1) >= 3
                            and len(word_h1) >= 3
                            and (h1.startswith(word_h1) or word_h1.startswith(h1))
                        )
                        or (
                            len(h1) >= 3
                            and len(word_h2) >= 3
                            and (h1.startswith(word_h2) or word_h2.startswith(h1))
                        )
                        or (
                            len(h2) >= 3
                            and len(word_h1) >= 3
                            and (h2.startswith(word_h1) or word_h1.startswith(h2))
                        )
                        or (
                            len(h2) >= 3
                            and len(word_h2) >= 3
                            and (h2.startswith(word_h2) or word_h2.startswith(h2))
                        )
                    ):
                        words.add(word)

                except Exception:
                    continue

        except Exception:
            # If frequency database access fails, return empty set
            pass

        return words

    def _get_error_corrections(self, word: str) -> list[str]:
        """Get error corrections using the new ErrorDatabase."""
        results: list[str] = []
        try:
            # Use the new ErrorDatabase class for corrections
            correction = self.db.error_db.get_correction(word)
            if correction and correction != word:
                results.append(correction)
        except (FileNotFoundError, AttributeError):
            # Fall back to trying case variations
            variations = [word, word.lower(), word.capitalize(), word.upper()]
            seen = set()
            for v in variations:
                if v in seen:
                    continue
                seen.add(v)
                try:
                    cor = self.db.error_db.get_correction(v)
                    if cor:
                        results.append(cor)
                except Exception:
                    pass
        return results

    def _get_frequency(self, word: str) -> int:
        if word in self._freq_cache:
            return self._freq_cache[word]

        freq = 0
        if self.db.frequency_db:
            try:
                freq = self.db.frequency_db.get_frequency(word)
            except Exception:
                freq = 0

        self._freq_cache[word] = freq
        return freq

    # -------- Case Handling --------
    def _classify_case(self, word: str) -> CaseClass:
        if word.isupper():
            return CaseClass.UPPER
        if len(word) > 1 and word[0].isupper() and word[1:].islower():
            return CaseClass.UCFIRST
        return CaseClass.LOWER

    def _apply_case(self, case_class: CaseClass, word: str) -> str:
        # COF behavior: For lowercase input, preserve dictionary case
        # This allows proper nouns like "Cjassà" to keep their capitalization
        if case_class == CaseClass.LOWER:
            return word  # Preserve original dictionary case
        if case_class == CaseClass.UCFIRST:
            return word[:1].upper() + word[1:].lower()
        return word.upper()

    # -------- Apostrophes / Elisions --------
    def _expand_apostrophe_variants(
        self,
        original: str,
        case_class: CaseClass,
        candidates: dict[str, Candidate],
    ) -> None:
        lower_original = original.lower()
        # Patterns similar to COF: d' / un' / l'
        prefix_map = {
            "d'": "di ",
            "un'": "une ",
            "l'": "la ",
        }
        for ap, expanded in prefix_map.items():
            if lower_original.startswith(ap) and len(lower_original) > len(ap):
                suffix = lower_original[len(ap) :]
                # If suffix is a candidate base word, build two variants depending on elision rule
                # Check elision DB: if suffix is elidable keep l' variant else expanded form
                if ap == "l'":
                    try:
                        elidable = self.db.elision_db.has_elision(suffix)
                    except (FileNotFoundError, AttributeError):
                        # If elision database isn't available, assume not elidable
                        elidable = False
                    if elidable:
                        # ensure original elided form ranks properly (prefer elided if exists)
                        norm = lower_original
                        if norm not in candidates:
                            candidates[norm] = Candidate(
                                word=self._apply_case(case_class, lower_original),
                                base_weight=F_SAME,
                                distance=0,
                                original_freq=self._get_frequency(suffix),
                            )
                        # also add expanded variant (slightly lower base weight)
                        expanded_form = expanded + suffix
                        norm_exp = expanded_form.lower()
                        if norm_exp not in candidates:
                            candidates[norm_exp] = Candidate(
                                word=self._apply_case(case_class, expanded_form),
                                base_weight=0,
                                distance=1,
                                original_freq=self._get_frequency(suffix),
                            )
                    else:
                        # Only expanded form credible
                        expanded_form = expanded + suffix
                        norm_exp = expanded_form.lower()
                        if norm_exp not in candidates:
                            candidates[norm_exp] = Candidate(
                                word=self._apply_case(case_class, expanded_form),
                                base_weight=0,
                                distance=1,
                                original_freq=self._get_frequency(suffix),
                            )
                else:
                    expanded_form = expanded + suffix
                    norm_exp = expanded_form.lower()
                    if norm_exp not in candidates:
                        candidates[norm_exp] = Candidate(
                            word=self._apply_case(case_class, expanded_form),
                            base_weight=0,
                            distance=1,
                            original_freq=self._get_frequency(suffix),
                        )

    # -------- Hyphen Handling (basic) --------
    def _expand_hyphen_variants(self, original: str, candidates: dict[str, Candidate]) -> None:
        if "-" not in original:
            return
        parts = [p for p in original.split("-") if p]
        if len(parts) != 2:
            return  # basic phase only handles bi-part
        left, right = parts
        # Fetch phonetic candidates separately
        left_cands = self._get_phonetic_candidates(left.lower())
        right_cands = self._get_phonetic_candidates(right.lower())
        for lc in left_cands:
            for rc in right_cands:
                combo = f"{lc} {rc}"  # mimic COF space suggestion style
                norm = combo.lower()
                if norm not in candidates:
                    distance = self._levenshtein(
                        original.lower().replace("-", ""), norm.replace(" ", "")
                    )
                    candidates[norm] = Candidate(
                        word=combo,
                        base_weight=0,
                        distance=distance,
                        original_freq=min(self._get_frequency(lc), self._get_frequency(rc)),
                    )

    # -------- Ranking --------
    def _rank_candidates(
        self,
        lower_word: str,
        case_class: CaseClass,
        candidates: dict[str, Candidate],
    ) -> list[str]:
        # Adjust words to correct case
        adjusted: list[tuple[str, Candidate]] = []
        for norm, cand in candidates.items():
            adjusted.append((norm, cand))

        # Compose final score: base_weight primary, then original_freq, then negative distance
        # Sorting: base_weight desc, original_freq desc, distance asc, friulian sort
        def friulian_key(w: str) -> str:
            # Lightweight normalization similar to COF::sort_friulian
            trans_table = str.maketrans(
                {
                    "à": "a",
                    "á": "a",
                    "â": "a",
                    "è": "e",
                    "é": "e",
                    "ê": "e",
                    "ì": "i",
                    "í": "i",
                    "î": "i",
                    "ò": "o",
                    "ó": "o",
                    "ô": "o",
                    "ù": "u",
                    "ú": "u",
                    "û": "u",
                    "ç": "c",
                }
            )
            w2 = w.translate(trans_table)
            if w2.startswith("'s"):
                w2 = "s" + w2[2:]
            return w2

        # COF-compatible sorting:
        # - base_weight (error corrections) has absolute priority
        # - when base_weight is equal, distance has priority over frequency
        # - exact matches (distance=0) should come first regardless of frequency
        adjusted.sort(
            key=lambda kv: (
                -kv[1].base_weight,  # Error corrections first
                kv[1].distance,  # Then by edit distance (0 = exact match)
                -kv[1].original_freq,  # Then by frequency (higher first)
                friulian_key(kv[0]),  # Finally friulian alphabetical sort
            )
        )
        # Apply case after ordering
        out: list[str] = []
        seen_out = set()
        for _norm, cand in adjusted:
            cased = self._apply_case(case_class, cand.word)
            if cased not in seen_out:
                out.append(cased)
                seen_out.add(cased)
        return out

    # -------- Levenshtein (reuse phonetic component) --------
    @staticmethod
    def _normalize_vowels(text: str) -> str:
        return text.lower().translate(_VOWEL_TRANSLATION)

    def _levenshtein(self, a: str, b: str) -> int:
        # Rapid path using C-backed rapidfuzz when available; fallback keeps parity.
        if not a:
            return len(b) if b else 0
        if not b:
            return len(a)
        if _RFLevenshtein is not None:
            try:
                return int(
                    _RFLevenshtein.distance(
                        self._normalize_vowels(a),
                        self._normalize_vowels(b),
                    )
                )
            except Exception:
                pass
        return self.phonetic.levenshtein(a, b)

    # -------- Word validation --------
    def _is_valid_word(self, word: str) -> bool:
        """Check if a word exists in any of the databases."""
        if not word:
            return False

        # Check in system database via phonetic hash (fastest check)
        try:
            h1, h2 = self.phonetic.get_phonetic_hashes_by_word(word)
            sys_words = self.db.phonetic_db.find_by_phonetic_hash(h1)
            if sys_words and word in sys_words.split(","):
                return True
            if h2 != h1:
                sys_words = self.db.phonetic_db.find_by_phonetic_hash(h2)
                if sys_words and word in sys_words.split(","):
                    return True
        except Exception:
            pass

        # Check in frequency database (using new FrequencyDatabase)
        try:
            freq = self.db.frequency_db.get_frequency(word)
            if freq > 0:
                return True
        except (FileNotFoundError, AttributeError):
            # Fall back to old method
            try:
                legacy_freq = self.db.sqlite_db.find_in_frequencies_database(word)
                if legacy_freq is not None and legacy_freq > 0:
                    return True
            except Exception:
                pass

        return False

    # -------- Enhanced Database Methods (COF Integration) --------
    def _add_elision_candidates(self, word: str, candidates: dict[str, Candidate]) -> None:
        """Add elision-based candidates using ElisionDatabase.

        Adds variants like l'/la, d'/di, un'/une based on elision rules.
        Equivalent to COF's elision handling logic.
        """
        lower_word = word.lower()

        try:
            # Get elision candidates from the database
            # elision_candidates = self.db.elision_db.get_elision_candidates(lower_word)
            elision_candidates: list[str] = []

            for candidate in elision_candidates:
                if candidate and candidate not in candidates:
                    # Calculate edit distance
                    distance = self._levenshtein(lower_word, candidate.lower())

                    # Elision variants get moderate priority (between errors and phonetic)
                    base_weight = 250 if candidate.lower() != lower_word else F_SAME

                    candidates[candidate.lower()] = Candidate(
                        word=candidate,
                        base_weight=base_weight,
                        distance=distance,
                        original_freq=self._get_frequency(candidate),
                    )

        except (FileNotFoundError, AttributeError):
            # If ElisionDatabase not available, fall back to basic logic
            pass

    def _add_error_pattern_candidates(self, word: str, candidates: dict[str, Candidate]) -> None:
        """Add error pattern correction candidates using ErrorDatabase.

        Finds corrections for common Friulian spelling errors.
        Equivalent to COF's error pattern matching.
        """
        try:
            # Get error correction from the database
            correction = self.db.error_db.get_correction(word)

            if correction and correction != word:
                lower_correction = correction.lower()
                lower_word = word.lower()

                if lower_correction not in candidates:
                    distance = self._levenshtein(lower_word, lower_correction)

                    # Error corrections get high priority
                    base_weight = F_ERRS if lower_correction != lower_word else F_SAME

                    candidates[lower_correction] = Candidate(
                        word=correction,
                        base_weight=base_weight,
                        distance=distance,
                        original_freq=self._get_frequency(correction),
                    )

        except (FileNotFoundError, AttributeError):
            # If ErrorDatabase not available, fall back to existing logic
            pass

    def rank_suggestions_by_frequency(self, suggestions: list[str]) -> list[tuple[str, int]]:
        """Rank suggestions by frequency score using FrequencyDatabase.

        Args:
            suggestions: List of word suggestions

        Returns:
            List of (word, frequency) tuples sorted by frequency
        """
        # try:
        #     return self.db.frequency_db.rank_suggestions(suggestions)
        # except (FileNotFoundError, AttributeError):
        # Fall back to basic frequency lookup
        ranked = []
        for suggestion in suggestions:
            frequency = self._get_frequency(suggestion)
            ranked.append((suggestion, frequency))

        # Sort by frequency (descending) then alphabetically
        ranked.sort(key=lambda x: (-x[1], x[0]))
        return ranked

    def _cof_handle_hyphens(
        self, word: str, suggestions: dict[str, list[Any]]
    ) -> dict[str, list[Any]]:
        """
        Handle hyphenated words like COF's hyphen logic.
        """
        if "-" not in word:
            return suggestions

        # Split on first hyphen only
        parts = word.split("-", 1)
        if len(parts) != 2:
            return suggestions

        left_word, right_word = parts

        # Get suggestions for both parts
        left_lower = left_word.lower()
        right_lower = right_word.lower()

        left_suggestions = self._cof_basic_suggestions(
            left_word, left_lower, self._classify_case(left_word)
        )
        right_suggestions = self._cof_basic_suggestions(
            right_word, right_lower, self._classify_case(right_word)
        )

        # Combine all possibilities
        for left_candidate, left_vals in left_suggestions.items():
            for right_candidate, right_vals in right_suggestions.items():
                combined = f"{left_candidate} {right_candidate}"
                # Add frequencies and distances
                combined_vals = [
                    left_vals[0] + right_vals[0],  # frequency sum
                    left_vals[1] + right_vals[1],  # distance sum
                ]
                suggestions[combined] = combined_vals

        return suggestions

    def _cof_rank_suggestions(
        self, suggestions: dict[str, list[Any]], case_class: CaseClass
    ) -> list[str]:
        """
        Rank suggestions exactly like COF's suggest method.

        COF ranking (from SpellChecker.pm suggest/suggest_raw):
        1. Sort all words using Friulian sort
        2. Build peso structure: peso[frequency][distance] = [indices]
        3. Sort: frequency DESC, then distance ASC, then Friulian order (from step 1)
        """
        if not suggestions:
            return []

        # Convert to COF's format for sorting
        words_list = list(suggestions.keys())

        # Step 1: Sort using COF's friulian sort (like COF line 195)
        words_list = self._friulian_sort(words_list)

        # Step 2: Build COF's peso structure: peso[frequency][distance] = [indices]
        # COF uses: $parole_hamming{ $vals->[0] }{ $vals->[1] } (frequency first, distance second)
        peso: dict[int, dict[int, list[int]]] = {}

        for idx, word in enumerate(words_list):
            frequency, distance = suggestions[word]

            # COF structure: peso[frequency][distance]
            if frequency not in peso:
                peso[frequency] = {}
            if distance not in peso[frequency]:
                peso[frequency][distance] = []

            peso[frequency][distance].append(idx)

        # Step 3: Sort exactly like COF suggest method (lines 216-220):
        # for my $f ( sort { $b <=> $a } keys %$peso )           # frequency descending
        # { for my $d ( sort { $a <=> $b } keys %{ $peso->{$f} } )  # distance ascending
        ranked_words = []

        for freq in sorted(peso.keys(), reverse=True):  # frequency descending (like COF)
            for dist in sorted(peso[freq].keys()):  # distance ascending (like COF)
                for idx in peso[freq][dist]:
                    ranked_words.append(words_list[idx])

        # Return all suggestions if no limit, otherwise limit to max_suggestions
        if self.max_suggestions is None:
            result = ranked_words
        else:
            result = ranked_words[: self.max_suggestions]

        return result

    def _friulian_sort(self, words: list[str]) -> list[str]:
        """
        Sort words according to Friulian alphabetical order.
        Implements character transliteration matching COF::Data::sort_friulian.
        Maps special characters (ç→c, accented vowels→base) before sorting.
        """
        # Character transliteration map matching COF behavior
        transliteration_map = str.maketrans(
            {
                "ç": "c",
                "Ç": "C",
                "à": "a",
                "À": "A",
                "è": "e",
                "È": "E",
                "ì": "i",
                "Ì": "I",
                "ò": "o",
                "Ò": "O",
                "ù": "u",
                "Ù": "U",
                "â": "a",
                "Â": "A",
                "ê": "e",
                "Ê": "E",
                "î": "i",
                "Î": "I",
                "ô": "o",
                "Ô": "O",
                "û": "u",
                "Û": "U",
            }
        )

        def sort_key(word: str) -> tuple[str, str]:
            """Generate sort key with transliteration and 's handling."""
            lower_word = word.lower()
            transliterated = lower_word.translate(transliteration_map)
            # Handle 's prefix (if needed in future - COF has special handling)
            return (transliterated, lower_word)

        return sorted(words, key=sort_key)
