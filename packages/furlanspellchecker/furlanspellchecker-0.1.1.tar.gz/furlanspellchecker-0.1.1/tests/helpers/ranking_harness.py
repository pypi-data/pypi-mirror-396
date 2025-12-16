"""Test helper for COF ranking parity.

This module centralizes loading the JSON ground-truth payload, sanity-checks
that the production SQLite bundle is available, and exposes a small API for
ranking-focused tests. The helper mirrors COF expectations so that the Python
port stays in lockstep with the original suite.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from furlan_spellchecker import (
    Dictionary,
    FurlanSpellChecker,
    FurlanSpellCheckerConfig,
    TextProcessor,
)
from furlan_spellchecker.phonetic import FurlanPhoneticAlgorithm

REQUIRED_DATABASE_FILES = (
    "words.sqlite",
    "frequencies.sqlite",
    "errors.sqlite",
    "elisions.sqlite",
    "words_radix_tree.rt",
)


@dataclass
class RankingHarness:
    """Utility wrapper that keeps ranking tests deterministic.

    The helper ensures that:
    - The JSON ground-truth fixture exists and is well-formed.
    - The checked-in SQLite bundle is available (so we never hit the network).
    - Tests can request ranked suggestions and expected COF orders via a single
      object, avoiding duplicated fixtures across modules.
    """

    project_root: Path
    ground_truth_path: Path
    database_dir: Path
    _ground_truth: Mapping[str, Mapping[str, object]]
    _cases: dict[str, list[str]]
    _spellchecker: FurlanSpellChecker
    _phonetic: FurlanPhoneticAlgorithm

    def __init__(
        self,
        project_root: Path | None = None,
        spellchecker: FurlanSpellChecker | None = None,
        ground_truth_path: Path | None = None,
        database_dir: Path | None = None,
    ) -> None:
        self.project_root = project_root or Path(__file__).resolve().parents[2]
        self.ground_truth_path = ground_truth_path or (
            self.project_root / "tests" / "assets" / "ranking_ground_truth.json"
        )
        self.database_dir = database_dir or (self.project_root / "data" / "databases")

        self._assert_ground_truth_present()
        self._assert_database_bundle()

        self._ground_truth = self._load_ground_truth()
        self._cases = {
            word: list(entry["suggestions"]) for word, entry in self._ground_truth.items()
        }

        self._spellchecker = spellchecker or self._build_spellchecker()
        self._phonetic = FurlanPhoneticAlgorithm()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    @property
    def spellchecker(self) -> FurlanSpellChecker:
        return self._spellchecker

    def expected_order(self, word: str) -> list[str]:
        if word not in self._cases:
            raise KeyError(f"Word '{word}' missing from ranking_ground_truth.json")
        return self._cases[word]

    def available_words(self) -> list[str]:
        return sorted(self._cases.keys())

    def require_words(self, words: Iterable[str]) -> None:
        missing = sorted({word for word in words if word not in self._cases})
        if missing:
            raise AssertionError(
                "Ground-truth JSON is missing words required by the test suite: "
                + ", ".join(missing)
            )

    def get_ranked_suggestions(self, word: str, limit: int | None = None) -> list[str]:
        suggestions = self._spellchecker.suggest(word)
        if limit is not None:
            return suggestions[:limit]
        return suggestions

    def friulian_sort(self, words: Sequence[str]) -> list[str]:
        return self._phonetic.sort_friulian(list(words))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _assert_ground_truth_present(self) -> None:
        if not self.ground_truth_path.exists():
            raise FileNotFoundError(
                "ranking_ground_truth.json not found. Run database_export/"
                "export_words.pl in the COF workspace to refresh the JSON bundle."
            )

    def _assert_database_bundle(self) -> None:
        missing = [
            name for name in REQUIRED_DATABASE_FILES if not (self.database_dir / name).exists()
        ]
        if missing:
            raise FileNotFoundError(
                "Missing SQLite bundle entries: {}. Run scripts/"
                "create_database_release.py (or fetch the release artifact) "
                "before executing ranking tests.".format(", ".join(sorted(missing)))
            )

    def _load_ground_truth(self) -> Mapping[str, Mapping[str, object]]:
        with self.ground_truth_path.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)

        malformed = [key for key, entry in payload.items() if "suggestions" not in entry]
        if malformed:
            raise ValueError(
                "ranking_ground_truth.json entries missing 'suggestions': "
                + ", ".join(sorted(malformed))
            )

        return payload

    def _build_spellchecker(self) -> FurlanSpellChecker:
        self._configure_local_downloader_cache()

        config = FurlanSpellCheckerConfig()
        dictionary = Dictionary()
        text_processor = TextProcessor()
        return FurlanSpellChecker(
            dictionary=dictionary, text_processor=text_processor, config=config
        )

    def _configure_local_downloader_cache(self) -> None:
        from furlan_spellchecker.database import downloader as downloader_module

        downloader_module._downloader_instance = downloader_module.DatabaseDownloader(
            cache_dir=self.database_dir
        )
