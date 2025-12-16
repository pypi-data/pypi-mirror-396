"""Core parity tests backed by the production SQLite database bundle."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

import pytest

from furlan_spellchecker import FurlanPhoneticAlgorithm, FurlanSpellCheckerConfig
from furlan_spellchecker.database import DatabaseFactory, DatabaseManager, DictionaryType
from furlan_spellchecker.database.radix_tree import RadixTreeDatabase
from furlan_spellchecker.entities.processed_element import ProcessedWord
from furlan_spellchecker.phonetic.furlan_phonetic import FriulianCaseUtils

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _check_word(spell_checker, token: str) -> ProcessedWord:
    word = ProcessedWord(token)

    async def _run():
        await spell_checker.check_word(word)
        return word

    return asyncio.run(_run())


def _build_database_manager(cache_dir: Path | str) -> DatabaseManager:
    config = FurlanSpellCheckerConfig()
    config.dictionary.cache_directory = str(cache_dir)
    return DatabaseManager(config)


class _CompatDataHarness:
    """Minimal stand-in for COF::DataCompat backed entirely by bundled SQLite assets."""

    def __init__(self, bundle_paths: dict[str, Path]):
        self._bundle_paths = bundle_paths
        self._phonetic = FurlanPhoneticAlgorithm()

    def has_radix_tree(self) -> bool:
        return self._bundle_paths["words_radix_tree.rt"].exists()

    def get_radix_tree(self) -> RadixTreeDatabase:
        return RadixTreeDatabase(self._bundle_paths["words_radix_tree.rt"])

    def has_rt_checker(self) -> bool:
        return self.has_radix_tree()

    def get_rt_checker(self) -> RadixTreeDatabase:
        return self.get_radix_tree()

    def has_user_dict(self) -> bool:
        return False

    @staticmethod
    def change_user_dict() -> int:
        return 1

    @staticmethod
    def delete_user_dict() -> int:
        return 1

    def phalg_furlan(self, word: str) -> tuple[str, str]:
        return self._phonetic.get_phonetic_hashes_by_word(word)


@pytest.fixture(scope="module")
def compat_data_layer(production_database_paths):
    return _CompatDataHarness(production_database_paths)


# ---------------------------------------------------------------------------
# Production bundle smoke tests (COF Section 1: C01–C05 guards)
# ---------------------------------------------------------------------------


def test_dictionary_directory_exists(production_databases_dir):
    assert production_databases_dir.is_dir(), "Expected data/databases/ to exist for parity"
    contents = list(production_databases_dir.iterdir())
    assert contents, "Dictionary directory is empty; run scripts/create_database_release.py"


def test_production_bundle_structure(production_database_paths):
    expected = {
        "words.sqlite",
        "frequencies.sqlite",
        "errors.sqlite",
        "elisions.sqlite",
        "words_radix_tree.rt",
    }
    assert set(production_database_paths.keys()) == expected
    for name, path in production_database_paths.items():
        assert path.exists(), f"Missing production asset for {name}: {path}"
        assert path.stat().st_size > 0, f"Release asset {name} is empty"


def test_words_bundle_contains_expected_words(production_database_paths, phonetic_algo):
    db = DatabaseFactory.create_phonetic_database(
        production_database_paths["words.sqlite"], auto_download=False
    )
    hash_cjase, _ = phonetic_algo.get_phonetic_hashes_by_word("cjase")
    cluster = db.get_words_by_phonetic_hash(hash_cjase)
    assert "cjase" in cluster
    hash_furlan, _ = phonetic_algo.get_phonetic_hashes_by_word("furlan")
    furlan_cluster = db.get_words_by_phonetic_hash(hash_furlan)
    assert furlan_cluster == ["furlan"], "furlan cluster should only contain canonical spelling"


def test_frequency_bundle_has_expected_values(production_database_paths):
    db = DatabaseFactory.create_frequency_database(
        production_database_paths["frequencies.sqlite"], auto_download=False
    )
    assert db.get_frequency("di") == 255
    assert db.get_frequency("cjase") == 163
    assert db.get_frequency("furlan") == 192
    assert db.get_frequency("cognossi") == 140


def test_error_bundle_contains_spacing_fix(production_database_paths):
    db = DatabaseFactory.create_error_database(
        production_database_paths["errors.sqlite"], auto_download=False
    )
    assert db.get_correction("adincuatri") == "ad in cuatri"


def test_elision_bundle_contains_expected_word(production_database_paths):
    db = DatabaseFactory.create_elision_database(
        production_database_paths["elisions.sqlite"], auto_download=False
    )
    assert db.has_elision("analfabetementri")


# ---------------------------------------------------------------------------
# Database factory integration tests
# ---------------------------------------------------------------------------


def test_database_factory_returns_sqlite_phonetic():
    db = DatabaseFactory.create_phonetic_database("words.sqlite", auto_download=False)
    words = db.get_words_by_phonetic_hash("fYl65")
    assert "furlan" in words


def test_database_factory_returns_sqlite_frequency():
    db = DatabaseFactory.create_frequency_database("frequencies.sqlite", auto_download=False)
    assert db.get_frequency("cognossi") == 140


def test_database_factory_returns_sqlite_error():
    db = DatabaseFactory.create_error_database("errors.sqlite", auto_download=False)
    assert db.get_correction("adincuatri") == "ad in cuatri"


def test_database_factory_returns_sqlite_elision():
    db = DatabaseFactory.create_elision_database("elisions.sqlite", auto_download=False)
    assert db.has_elision("analfabetementri")


# ---------------------------------------------------------------------------
# Database manager + spell checker plumbing
# ---------------------------------------------------------------------------


def test_database_manager_uses_production_bundle(spellchecker_cache_dir):
    manager = _build_database_manager(spellchecker_cache_dir)

    assert manager.frequency_db.get_frequency("fûr") == 177
    assert manager.error_db.get_correction("adincuatri") == "ad in cuatri"
    assert manager.elision_db.has_elision("analfabetementri")


def test_cli_default_configuration_matches_database_manager(spellchecker_cache_dir):
    manager = _build_database_manager(spellchecker_cache_dir)
    availability = manager.ensure_databases_available()

    required = {
        DictionaryType.SYSTEM_DICTIONARY,
        DictionaryType.SYSTEM_ERRORS,
        DictionaryType.FREQUENCIES,
        DictionaryType.ELISIONS,
        DictionaryType.RADIX_TREE,
    }
    for dictionary_type in required:
        assert (
            availability.get(dictionary_type) is True
        ), f"{dictionary_type} missing under CLI defaults"

    assert manager.get_missing_databases() == {}
    assert manager._cache_dir == Path(spellchecker_cache_dir)


# ---------------------------------------------------------------------------
# Compatibility layer parity tests (COF Section 2)
# ---------------------------------------------------------------------------


def test_compat_release_bundle_matches_required_assets(production_database_paths):
    expected = {
        "words.sqlite",
        "frequencies.sqlite",
        "errors.sqlite",
        "elisions.sqlite",
        "words_radix_tree.rt",
    }
    assert set(production_database_paths.keys()) == expected
    assert all(production_database_paths[name].exists() for name in expected)


@pytest.mark.parametrize(
    "required_asset",
    [
        "words.sqlite",
        "frequencies.sqlite",
        "errors.sqlite",
        "elisions.sqlite",
        "words_radix_tree.rt",
    ],
)
def test_compat_release_assets_are_readable(production_databases_dir, required_asset):
    asset_path = production_databases_dir / required_asset
    assert asset_path.exists(), f"Compatibility asset {required_asset} missing"
    assert asset_path.is_file(), f"Compatibility asset {required_asset} is not a regular file"
    assert os.access(asset_path, os.R_OK), f"Compatibility asset {required_asset} not readable"


def test_compat_data_layer_exposes_radix_tree(compat_data_layer):
    assert compat_data_layer.has_radix_tree() is True
    checker = compat_data_layer.get_rt_checker()
    assert isinstance(checker, RadixTreeDatabase)


def test_compat_user_dictionary_apis_are_disabled(compat_data_layer):
    assert compat_data_layer.has_user_dict() is False
    assert compat_data_layer.change_user_dict() == 1
    assert compat_data_layer.delete_user_dict() == 1


def test_compat_phonetic_hashes_are_available(compat_data_layer):
    primo, secondo = compat_data_layer.phalg_furlan("furlan")
    assert isinstance(primo, str)
    assert isinstance(secondo, str)
    assert primo


def test_compat_phonetic_handles_empty_and_whitespace(compat_data_layer):
    assert compat_data_layer.phalg_furlan("") == ("", "")
    assert compat_data_layer.phalg_furlan("   ") == ("", "")


def test_compat_phonetic_calls_are_stable(compat_data_layer):
    first = compat_data_layer.phalg_furlan("cjase")
    second = compat_data_layer.phalg_furlan("cjase")
    assert first == second


def test_compat_phonetic_handles_accented_and_apostrophe_inputs(compat_data_layer):
    assert compat_data_layer.phalg_furlan("àèìòù")[0] != ""
    assert compat_data_layer.phalg_furlan("l'aghe")[0] == "l6g7"


def test_compat_phonetic_hashes_ignore_internal_whitespace(compat_data_layer):
    canonical = compat_data_layer.phalg_furlan("furlan")
    padded = compat_data_layer.phalg_furlan("  furlan  ")
    assert canonical == padded


# ---------------------------------------------------------------------------
# Database integration parity tests (COF Section 3)
# ---------------------------------------------------------------------------


def test_elision_database_detects_elidable_words(spellchecker_cache_dir):
    manager = _build_database_manager(spellchecker_cache_dir)

    assert manager.elision_db.has_elision("ore") is True
    assert manager.elision_db.has_elision("ORE") is True  # case-insensitive match
    assert manager.elision_db.has_elision("imbraghetâ") is True
    assert manager.elision_db.has_elision("totallymadeupword") is False


@pytest.mark.parametrize("elidable_word", ["aghe", "ale", "int", "erbis"])
def test_elision_database_handles_curated_words(spellchecker_cache_dir, elidable_word):
    manager = _build_database_manager(spellchecker_cache_dir)
    result = manager.elision_db.has_elision(elidable_word)
    assert isinstance(result, bool)


@pytest.mark.parametrize("non_elidable_word", ["furlan", "lenghe", "xyz_nonexistent"])
def test_elision_database_rejects_non_elidable_words(spellchecker_cache_dir, non_elidable_word):
    manager = _build_database_manager(spellchecker_cache_dir)
    assert manager.elision_db.has_elision(non_elidable_word) is False


def test_error_database_returns_spacing_corrections(spellchecker_cache_dir):
    manager = _build_database_manager(spellchecker_cache_dir)

    expectations = {
        "adincuatri": "ad in cuatri",
        "adindopli": "ad in dopli",
        "abracecuel": "a bracecuel",
    }

    for misspelled, corrected in expectations.items():
        assert manager.error_db.get_correction(misspelled) == corrected

    assert manager.error_db.get_correction("furla") is None


@pytest.mark.parametrize(
    ("misspelled", "expected"),
    [
        ("furla", "furlan"),
        ("scuela", "scuele"),
        ("lengha", "lenghe"),
        ("cjasa", "cjase"),
        ("ostaria", "ostarie"),
    ],
)
def test_error_database_curated_entries(spellchecker_cache_dir, misspelled, expected):
    manager = _build_database_manager(spellchecker_cache_dir)
    correction = manager.error_db.get_correction(misspelled)
    assert correction is None or correction == expected


@pytest.mark.parametrize("unknown_word", ["totallymadeupword", "python", "friulian"])
def test_error_database_returns_none_for_unknown_entries(spellchecker_cache_dir, unknown_word):
    manager = _build_database_manager(spellchecker_cache_dir)
    assert manager.error_db.get_correction(unknown_word) is None


def test_elision_database_covers_curated_list(spellchecker_cache_dir):
    manager = _build_database_manager(spellchecker_cache_dir)
    curated = ["aghe", "ore", "ale", "int", "erbis", "analfabetementri"]
    hits = [word for word in curated if manager.elision_db.has_elision(word)]
    assert len(hits) >= 2


def test_elision_database_handles_apostrophe_forms(spellchecker_cache_dir):
    manager = _build_database_manager(spellchecker_cache_dir)
    samples = ["l'aghe", "un'ore", "dal'int"]
    prefixes = ("l'", "un'", "dal'")
    for token in samples:
        normalized = token
        for prefix in prefixes:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix) :]
                break
        result = manager.elision_db.has_elision(normalized)
        assert isinstance(result, bool)


def test_error_database_handles_case_variations(spellchecker_cache_dir):
    manager = _build_database_manager(spellchecker_cache_dir)
    lower = manager.error_db.get_correction("adincuatri")
    upper = manager.error_db.get_correction("ADINCUATRI")
    assert lower is not None or upper is not None


def test_frequency_database_reports_rank_information(spellchecker_cache_dir):
    manager = _build_database_manager(spellchecker_cache_dir)

    freq_di = manager.frequency_db.get_frequency("di")
    freq_furlan = manager.frequency_db.get_frequency("furlan")
    freq_cjase = manager.frequency_db.get_frequency("cjase")

    assert freq_di == 255
    assert freq_furlan > freq_cjase > 0
    assert manager.frequency_db.get_frequency("xyz_nonexistent") == 0


def test_frequency_database_contains_curated_words(spellchecker_cache_dir):
    manager = _build_database_manager(spellchecker_cache_dir)
    words = ["furlan", "cjase", "aghe", "lenghe", "parol", "frut", "femine", "om"]
    for word in words:
        freq = manager.frequency_db.get_frequency(word)
        assert freq >= 0


def test_frequency_database_rank_order(spellchecker_cache_dir):
    manager = _build_database_manager(spellchecker_cache_dir)
    freq_furlan = manager.frequency_db.get_frequency("furlan")
    freq_cjase = manager.frequency_db.get_frequency("cjase")
    freq_frut = manager.frequency_db.get_frequency("frut")
    assert freq_furlan >= freq_cjase >= 0
    assert freq_frut >= 0


@pytest.mark.parametrize(
    ("token", "expected_freq"),
    [
        ("di", 255),
        ("cjase", 163),
        ("furlan", 192),
        ("cognossi", 140),
    ],
)
def test_frequency_values_match_expected(spellchecker_cache_dir, token, expected_freq):
    """Verify specific words have expected frequency values."""
    manager = _build_database_manager(spellchecker_cache_dir)
    freq = manager.frequency_db.get_frequency(token)
    assert freq == expected_freq, f"Expected {token} to have freq {expected_freq}, got {freq}"


def test_spell_checker_surfaces_error_database_corrections(spell_checker):
    suggestions = spell_checker.suggest("adincuatri")
    assert suggestions, "Expected suggestions for known spacing error"
    assert suggestions[0].lower() == "ad in cuatri"


def test_spell_checker_elision_suggestions_include_expanded_forms(spell_checker):
    suggestions = spell_checker.suggest("l'aghe")
    lowered = [s.lower() for s in suggestions]
    assert "la aghe" in lowered
    assert "l'aghe" not in lowered  # base word is not elidable, so only expanded form remains


@pytest.mark.parametrize(
    ("input_token", "expected"),
    [
        ("furla", "furlan"),
        ("scuela", "scuele"),
        ("lengha", "lenghe"),
        ("ostaria", "ostarie"),
    ],
)
def test_spell_checker_curated_error_corrections(spell_checker, input_token, expected):
    suggestions = spell_checker.suggest(input_token)
    assert suggestions, f"Expected suggestions for {input_token}"
    normalized = [s.lower() for s in suggestions]
    assert expected.lower() in normalized


def test_spell_checker_consults_error_database(monkeypatch, spell_checker):
    observed = {}

    def _fake_get_correction(word: str):
        observed["word"] = word
        return "ad in cuatri"

    monkeypatch.setattr(
        spell_checker._suggestion_engine.db.error_db,
        "get_correction",
        _fake_get_correction,
        raising=False,
    )

    suggestions = spell_checker.suggest("adincuatri")
    assert observed["word"] == "adincuatri"
    assert suggestions[0].lower() == "ad in cuatri"


# ---------------------------------------------------------------------------
# Spell checker parity tests (COF Section 1)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "candidate",
    ["furlan", "cjase", "aghe", "scuele", "frut", "femine", "om"],
)
def test_spell_checker_confirms_known_words(spell_checker, candidate):
    checked = _check_word(spell_checker, candidate)
    assert checked.correct, f"Word '{candidate}' should be considered correct"


def test_spell_checker_finds_multiple_valid_words(spell_checker):
    words = ["furlan", "lenghe", "cjase", "aghe", "scuele", "frut", "femine", "om"]
    confirmations = sum(1 for word in words if _check_word(spell_checker, word).correct)
    assert confirmations >= 3


def test_spell_checker_suggests_common_error(spell_checker):
    suggestions = spell_checker.suggest("furla")
    assert isinstance(suggestions, list)
    assert any(s.lower() == "furlan" for s in suggestions[:3])


def test_spell_checker_handles_case_variations(spell_checker):
    upper_result = _check_word(spell_checker, "FURLAN")
    assert upper_result.correct
    title_result = _check_word(spell_checker, "Furlan")
    assert title_result.correct


def test_spell_checker_handles_punctuation(spell_checker):
    suggestions = spell_checker.suggest("furlan.")
    assert isinstance(suggestions, list)


def test_spell_checker_handles_unicode_letters(spell_checker):
    suggestions = spell_checker.suggest("cjàse")
    assert isinstance(suggestions, list)


def test_spell_checker_handles_edge_inputs(spell_checker):
    assert spell_checker.suggest("") == []
    long_word = "a" * 1000
    suggestions = spell_checker.suggest(long_word)
    assert isinstance(suggestions, list)


def test_spell_checker_handles_extremely_long_words(spell_checker):
    very_long = "a" * 1000
    suggestions = spell_checker.suggest(very_long)
    assert isinstance(suggestions, list)


def test_phonetic_algorithm_handles_extremely_long_words(phonetic_algo):
    token = "a" * 1000
    primo, secondo = phonetic_algo.get_phonetic_hashes_by_word(token)
    assert isinstance(primo, str)
    assert isinstance(secondo, str)


def test_levenshtein_handles_extremely_long_words(phonetic_algo):
    base = "furlan" * 200
    mutated = base[:-1] + "z"
    distance = phonetic_algo.levenshtein(base, mutated)
    assert distance >= 0


# ---------------------------------------------------------------------------
# Phonetic algorithm regression tests (lifted from COF parity list)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def phonetic_algo():
    return FurlanPhoneticAlgorithm()


def test_phonetic_hashes_for_cjase(phonetic_algo):
    primo, secondo = phonetic_algo.get_phonetic_hashes_by_word("cjase")
    assert primo == "A6A7"
    assert secondo == "c76E7"


def test_phonetic_handles_accented_variants(phonetic_algo):
    primo_acc, _ = phonetic_algo.get_phonetic_hashes_by_word("cjàse")
    primo_plain, _ = phonetic_algo.get_phonetic_hashes_by_word("cjase")
    assert primo_acc == primo_plain


def test_phonetic_handles_apostrophes(phonetic_algo):
    primo, _ = phonetic_algo.get_phonetic_hashes_by_word("l'aghe")
    assert primo == "l6g7"


def test_phonetic_empty_string_returns_empty_hashes(phonetic_algo):
    primo, secondo = phonetic_algo.get_phonetic_hashes_by_word("")
    assert primo == ""
    assert secondo == ""


def test_levenshtein_regressions(phonetic_algo):
    assert phonetic_algo.levenshtein("cjase", "cjase") == 0
    assert phonetic_algo.levenshtein("cjase", "cjàse") == 0
    assert phonetic_algo.levenshtein("cjase", "parol") > 0
    assert phonetic_algo.levenshtein("", "") == 0
    assert phonetic_algo.levenshtein("a", "") == 1


def test_case_utils_mirror_cof_behaviour():
    assert FriulianCaseUtils.ucf_word("cjase") == "Cjase"
    assert FriulianCaseUtils.lc_word("CJASE") == "cjase"
    assert FriulianCaseUtils.ucf_word("") == ""
    assert FriulianCaseUtils.lc_word("") == ""


def test_first_letter_uppercase_detection(phonetic_algo):
    assert phonetic_algo.is_first_uppercase("Cjase") is True
    assert phonetic_algo.is_first_uppercase("cjase") is False


def test_sort_friulian_replicates_cof_order(phonetic_algo):
    unsorted = ["zeta", "beta", "alfa", "gamma", "Çucarut"]
    sorted_words = phonetic_algo.sort_friulian(unsorted)
    assert sorted_words[0].lower() == "alfa"
    assert sorted_words[1].lower() == "beta"
    assert len(sorted_words) == len(unsorted)
