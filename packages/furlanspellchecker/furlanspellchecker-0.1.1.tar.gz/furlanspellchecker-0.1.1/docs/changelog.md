# Changelog

All notable changes to FurlanSpellChecker will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-12-11

### Fixed
- GitHub Actions workflow: upgraded Sigstore action to v3.0.0 to fix deprecated artifact actions
- PyPI Trusted Publisher configuration for automated releases

## [0.1.0] - 2025-12-11

First stable release of FurlanSpellChecker with complete spell checking pipeline and SQLite database migration.

### Added
- **Complete spell checking pipeline** for Friulian language with tokenization and suggestion engine
- **Interactive CLI mode** with colored output and multilingual interface (English, Friulian, Italian)
- **COF protocol compatibility mode** for automation and testing with Perl COF implementation
- **Database management commands**: `download-dicts`, `db-status`, `extract-dicts`
- **Automatic database download** from GitHub Releases with SHA256 verification
- **RadixTree implementation** for fast word lookups with edit-distance-1 search
- **Friulian-specific phonetic algorithm** for improved suggestion quality
- **User dictionaries** with SQLite-based personal word lists and exceptions
- **Comprehensive test suite**: 733 tests achieving 100% COF parity
- **Performance benchmarking** infrastructure with detailed metrics
- **CLI commands**: `lookup`, `suggest`, `check`, `file`, `interactive`, `cof-cli`

### Changed
- **BREAKING**: Migrated from msgpack to SQLite database format for all dictionaries
- **Database architecture**: All system databases now use SQLite (~300 MB total)
  - `words.sqlite`: 289 MB (7.4M phonetic hashes, 10.1M words)
  - `frequencies.sqlite`: 2 MB (69,051 entries)
  - `elisions.sqlite`: 0.2 MB (10,604 words)
  - `errors.sqlite`: 0.01 MB (301 patterns)
- **License**: Changed from MIT to Creative Commons Attribution-NonCommercial 4.0 International
- **Distribution**: Database files distributed via GitHub Releases (tag: 0.0.2-dictionaries-sqlite)

### Performance
- **40-1000x performance improvements** over initial baseline:
  - Phase 1: Sync API + RapidFuzz C-backed Levenshtein (-13% to -17%)
  - Phase 2: Lazy phonetic DB loading (8206ms → 1.72ms, -99.98%)
  - Phase 3: RadixTree optimization with byte labels and ED1 cache
  - Phase 4: SQLite connection pooling
  - Phase 5: Phonetic algorithm optimization (pre-compiled regex + LRU)
  - Phase 6: SQLite consolidation (removed msgpack/BerkeleyDB)
  - Phase 7: In-memory caches and batch lookups
- **Database loading**: Optimized initialization from 8+ seconds to <100ms
- **Spell checking**: ~1-2ms per word for typical operations

### Fixed
- **Database corruption issue**: Resolved 29.2% NULL frequency values for Friulian accented words
- **Encoding issues**: Proper handling of Friulian diacritics (à, è, ì, ò, ù, â, ê, î, ô, û, ç)
- **RadixTree edge cases**: Comprehensive handling of special characters and empty inputs
- **Async event loop overhead**: Eliminated per-word event loop creation in CLI

### Documentation
- Complete API documentation with usage examples
- Architecture documentation with module overview and design patterns
- Performance analysis with detailed bottleneck identification
- Testing guide with troubleshooting for known issues
- Database migration strategy and release instructions
- COF parity roadmap with traceability matrices

### Testing
- **733 tests** with 100% pass rate across all platforms
- **COF compatibility tests**: 100% parity with original Perl implementation
- **Integration tests**: End-to-end pipeline testing with DatabaseManager
- **Performance tests**: Batch processing and stress testing
- **Property-based tests**: Hypothesis-driven edge case coverage

## [0.0.0] - 2025-09-18

Initial project skeleton and packaging for FurlanSpellChecker.

### Added
- Project skeleton mirroring CoretorOrtograficFurlan-Core concepts
- Core interfaces and entity classes
- Basic dictionary and phonetic algorithm skeletons
- Spell checking pipeline and service scaffolding
- CLI entrypoint and example usage
- Packaging, CI configuration, and developer tooling

### Notes
- This release provides structure only; core algorithms are placeholders and
	will be implemented in subsequent releases.