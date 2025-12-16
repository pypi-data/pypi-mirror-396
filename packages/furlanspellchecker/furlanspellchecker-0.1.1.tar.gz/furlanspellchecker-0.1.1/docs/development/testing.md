# Testing Guide

This document covers running tests for FurlanSpellChecker and known issues/gotchas.

## Quick Start

```bash
# Activate virtual environment
cd FurlanSpellChecker
..\.venv\Scripts\Activate.ps1  # Windows
source ../.venv/bin/activate   # Linux/Mac

# Run all tests
python -m pytest tests/ --tb=no -q

# Run specific test file
python -m pytest tests/test_core.py

# Run with verbose output
python -m pytest tests/ -v
```

## Test Suite Summary

| Test File | Tests | Description |
|-----------|-------|-------------|
| `test_core.py` | 83 | Core parity tests with SQLite databases |
| `test_phonetic_algorithm.py` | 230 | Phonetic algorithm correctness |
| `test_radix_tree.py` | ~50 | Radix tree lookup tests |
| `test_suggestions.py` | ~100 | Suggestion engine tests |
| `test_utilities.py` | ~50 | Utility function tests |
| **Total** | **733** | All tests should pass |

## Expected Test Duration

- **Full suite**: ~11-12 minutes (733 tests)
- **test_core.py**: ~4-5 minutes (83 tests)
- **Per-test average**: ~0.9 seconds

### Why Tests Are Slow

The spell checker tests are inherently slow because:

1. **Database Loading**: The `words.sqlite` file is **289 MB** and contains ~10.1M words with 7.4M phonetic hashes. Loading this into memory takes time.

2. **Async Event Loop Creation**: Many tests use `asyncio.run()` which creates a new event loop for each call. This adds overhead:
   ```python
   # Slow: 5 calls with separate event loops (~8.77s)
   for i in range(5):
       asyncio.run(sp.check_word(word))
   
   # Fast: 5 calls within single loop (~0.01s)
   async def batch():
       for i in range(5):
           await sp.check_word(word)
   asyncio.run(batch())
   ```

3. **Session-scoped Fixtures**: The `patch_database_io` fixture patches database paths at session scope, which ensures all tests use the local SQLite databases instead of downloading.

## ⚠️ Known Issues

### VS Code Terminal Background Execution

**Problem**: When running tests in VS Code's integrated terminal with background execution, tests may be interrupted by a `KeyboardInterrupt` after ~20-30 seconds.

**Symptom**:
```
tests\test_core.py ......
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! KeyboardInterrupt !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
C:\...\msgpack\__init__.py:47: KeyboardInterrupt
6 passed in 22.59s
```

**Cause**: VS Code's terminal may send SIGINT when:
- Commands are run in background mode
- The terminal appears "idle" for too long
- Piping output through PowerShell commands like `Tee-Object` or `Select-Object`

**Solution**: Run tests directly without background execution:
```powershell
# ✅ CORRECT - Run in foreground
python -m pytest tests/ --tb=no -q

# ❌ AVOID - Background with sleep
Start-Job { python -m pytest tests/ }
Start-Sleep 600
```

### Test Output Buffering with PowerShell Pipes

**Problem**: Using PowerShell pipes can cause tests to appear stuck:
```powershell
# ❌ May appear to hang
python -m pytest tests/ -v 2>&1 | Tee-Object -FilePath output.txt

# ❌ May appear to hang  
python -m pytest tests/ -v 2>&1 | Select-Object -Last 50
```

**Solution**: Run without pipes and redirect at the end:
```powershell
# ✅ Works correctly
python -m pytest tests/ -v > output.txt 2>&1
```

## Database Requirements

Tests require the production SQLite databases in `data/databases/`:

| File | Size | Content |
|------|------|------|
| `words.sqlite` | 289 MB | Phonetic hash → words mapping |
| `frequencies.sqlite` | 2 MB | Word → frequency rank |
| `errors.sqlite` | 0.01 MB | Common errors → corrections |
| `elisions.sqlite` | 0.2 MB | Elidable words |
| `words_radix_tree.rt` | 9.7 MB | Binary RadixTree for lookups |

If databases are missing, download from [GitHub Releases](https://github.com/daurmax/FurlanSpellChecker/releases).

## Running Specific Test Categories

```bash
# Bundle/database tests only
python -m pytest tests/test_core.py -k "bundle" -v

# Spell checker tests only  
python -m pytest tests/test_core.py -k "spell_checker" -v

# Exclude slow spell checker tests
python -m pytest tests/test_core.py -k "not spell_checker" -v

# Phonetic algorithm tests
python -m pytest tests/test_phonetic_algorithm.py -v
```

## Debugging Test Failures

```bash
# Show full traceback
python -m pytest tests/ --tb=long

# Stop on first failure
python -m pytest tests/ -x

# Show local variables in traceback
python -m pytest tests/ --tb=long -l

# Run with print statements visible
python -m pytest tests/ -s
```

## CI/CD Considerations

For automated pipelines:

1. **Timeout**: Set job timeout to at least 15 minutes
2. **Memory**: Ensure at least 1GB available (for loading words.msgpack)
3. **No background**: Run pytest directly, not in background jobs
4. **Database caching**: Cache `data/databases/` between runs to avoid re-downloading

Example GitHub Actions:
```yaml
- name: Run tests
  timeout-minutes: 15
  run: |
    python -m pytest tests/ --tb=short -q
```

## Test Architecture

```
tests/
├── conftest.py              # Shared fixtures (patch_database_io, etc.)
├── database_utils.py        # Database path utilities
├── test_core.py             # Core parity tests
├── test_phonetic_algorithm.py
├── test_radix_tree.py
├── test_suggestions.py
├── test_utilities.py
└── data/                    # Test-specific data files
```

### Key Fixtures

- `patch_database_io` (session, autouse): Redirects all database access to local SQLite files
- `production_database_bundle`: Paths to all production SQLite database files
- `spell_checker`: Pre-configured FurlanSpellChecker instance
- `sample_dictionary`: In-memory dictionary for unit tests

## Troubleshooting

### "Production SQLite databases missing"
```
pytest.skip: Production SQLite databases missing: words.sqlite, ...
```
**Fix**: Download databases from GitHub Releases or run `scripts/create_database_release.py`

### Tests hang at 6-7 tests
This is likely the VS Code terminal issue. Run in a separate terminal or use foreground execution.

### "Database file not found: words.sqlite"
The `patch_database_io` fixture may not be active. Ensure you're running from the `FurlanSpellChecker` directory.

### Very slow first test (~10s)
Normal - the first test loads the 289MB words.sqlite into memory. Subsequent tests reuse the cached data.
