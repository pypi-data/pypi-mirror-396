import sys
from pathlib import Path

import pytest

# Ensure the project src/ directory is importable for tests run from repository root
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from furlan_spellchecker import (  # noqa: E402
    Dictionary,
    FurlanSpellChecker,
    FurlanSpellCheckerConfig,
    SpellCheckPipeline,
    TextProcessor,
)

# ---------------------------------------------------------------------------
# Global fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Return repository root for reference in tests."""
    return ROOT


@pytest.fixture(scope="session")
def production_databases_dir(project_root: Path) -> Path:
    """Location of the SQLite databases mirrored from the GitHub release."""
    return project_root / "data" / "databases"


@pytest.fixture(scope="session")
def production_database_paths(production_databases_dir: Path):
    """Mapping between canonical database names and the checked-in release payloads."""
    mapping = {
        "words_radix_tree.rt": production_databases_dir / "words_radix_tree.rt",
        "words.sqlite": production_databases_dir / "words.sqlite",
        "frequencies.sqlite": production_databases_dir / "frequencies.sqlite",
        "errors.sqlite": production_databases_dir / "errors.sqlite",
        "elisions.sqlite": production_databases_dir / "elisions.sqlite",
    }
    required = [
        "words.sqlite",
        "frequencies.sqlite",
        "errors.sqlite",
        "elisions.sqlite",
        "words_radix_tree.rt",
    ]
    missing = [name for name in required if not mapping[name].exists()]
    if missing:
        instructions = (
            "Production SQLite databases missing: {}. "
            "Run scripts/create_database_release.py or download the artifacts from "
            "https://github.com/daurmax/FurlanSpellChecker/releases"
        ).format(", ".join(sorted(missing)))
        pytest.skip(instructions)
    return mapping


@pytest.fixture(scope="session")
def production_database_bundle(production_database_paths):
    """Full database bundle (system dictionaries plus radix tree)."""
    return dict(production_database_paths)


@pytest.fixture(scope="session", autouse=True)
def patch_database_io(production_database_bundle):
    """Force the database layer to reuse the checked-in SQLite release bundle during tests."""
    from furlan_spellchecker.database import downloader, factory

    patcher = pytest.MonkeyPatch()
    original_resolve = factory.DatabaseFactory._resolve_database_path
    original_download = downloader.download_database
    original_get_path = downloader.DatabaseDownloader.get_database_path

    def _resolve(db_path, auto_download: bool = True):
        candidate = Path(db_path)
        if candidate.name in production_database_bundle:
            return production_database_bundle[candidate.name]
        return original_resolve(db_path, auto_download)

    def _download(database_name: str):
        if database_name in production_database_bundle:
            return production_database_bundle[database_name]
        return original_download(database_name)

    def _get_database_path(self, database_name: str):
        if database_name in production_database_bundle:
            return production_database_bundle[database_name]
        return original_get_path(self, database_name)

    patcher.setattr(factory.DatabaseFactory, "_resolve_database_path", staticmethod(_resolve))
    patcher.setattr(downloader, "download_database", _download)
    patcher.setattr(downloader.DatabaseDownloader, "get_database_path", _get_database_path)

    yield production_database_bundle
    patcher.undo()


@pytest.fixture(scope="session")
def spellchecker_cache_dir(tmp_path_factory, production_database_bundle):
    """Dedicated cache directory for tests using bundled databases."""
    cache_dir = tmp_path_factory.mktemp("spellchecker_cache")
    return cache_dir


@pytest.fixture(scope="session")
def real_databases():
    """Verify SQLite databases are available for testing."""
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent))
    from database_utils import ensure_databases_extracted, get_database_paths, verify_database_files

    # Ensure databases are extracted from ZIP files if needed
    ensure_databases_extracted()

    # Verify all databases are accessible
    if not verify_database_files():
        pytest.skip("Real SQLite databases not available or corrupted")

    return get_database_paths()


@pytest.fixture(scope="session")
def real_db_manager(real_databases, production_database_paths):
    """Create a DatabaseManager using real SQLite databases.

    Uses conftest.py's patch_database_io which redirects all database
    accesses to the production SQLite bundle in data/databases/.
    """
    from furlan_spellchecker.database.manager import DatabaseManager

    # Create config - the patch_database_io fixture handles routing to SQLite files
    config = FurlanSpellCheckerConfig()

    # Create DatabaseManager - it will use SQLite databases via the patched factory
    db_manager = DatabaseManager(config)

    return db_manager


@pytest.fixture(scope="session")
def real_suggestion_engine(real_db_manager):
    """Create a SuggestionEngine with real databases.

    No max_suggestions limit (like COF) - returns all suggestions.
    """
    from furlan_spellchecker.phonetic.furlan_phonetic import FurlanPhoneticAlgorithm
    from furlan_spellchecker.spellchecker.suggestion_engine import SuggestionEngine

    phonetic_algo = FurlanPhoneticAlgorithm()
    return SuggestionEngine(db_manager=real_db_manager, phonetic=phonetic_algo)


@pytest.fixture
def sample_dictionary():
    """Create a dictionary with sample Friulian words."""
    dictionary = Dictionary()

    # Add some basic Friulian words
    words = [
        "cjase",
        "fradi",
        "sûr",
        "mari",
        "pari",
        "fi",
        "aghe",
        "pan",
        "vin",
        "lait",
        "cjar",
        "pes",
        "biel",
        "brut",
        "grant",
        "piçul",
        "bon",
        "catîf",
        "jessi",
        "vê",
        "fâ",
        "lâ",
        "vignî",
        "dî",
        "savê",
    ]

    for word in words:
        dictionary.add_word(word)

    return dictionary


@pytest.fixture
def spell_check_pipeline(sample_dictionary):
    """Create a spell check pipeline with sample dictionary."""
    return SpellCheckPipeline(dictionary=sample_dictionary)


@pytest.fixture
def spell_checker(spellchecker_cache_dir):
    """Create a FurlanSpellChecker wired against the in-repo production databases."""
    config = FurlanSpellCheckerConfig()
    config.dictionary.cache_directory = str(spellchecker_cache_dir)
    dictionary = Dictionary()
    text_processor = TextProcessor()
    return FurlanSpellChecker(dictionary=dictionary, text_processor=text_processor, config=config)


@pytest.fixture
def test_data_dir():
    """Get the test data directory path."""
    return Path(__file__).parent / "data"


@pytest.fixture
def sample_friulian_text():
    """Sample Friulian text for testing."""
    return "Cheste e je une frâs in furlan cun cualchi peraule."
