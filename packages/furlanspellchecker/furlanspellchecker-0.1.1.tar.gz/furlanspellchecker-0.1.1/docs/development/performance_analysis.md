# Performance Analysis: FurlanSpellChecker vs COF (Perl)

**Date**: 2025-11-28  
**Version**: Pre-optimization baseline  
**Author**: Performance Analysis Session

## Executive Summary

The Python FurlanSpellChecker implementation is **40-1000x slower** than the Perl COF implementation for spell checking operations. This document analyzes the root causes and identifies specific bottlenecks that can be optimized.

### Key Findings

| Metric | Perl COF | Python (Current) | Ratio |
|--------|----------|------------------|-------|
| Check 10K words | ~1.3s | ~57s | 44x slower |
| Suggest per word (correct) | ~0.4ms | ~11,000ms | 27,500x slower |
| Suggest per word (misspelled) | ~10ms | ~7,200ms | 720x slower |

### Baseline Benchmark Results (500 words)

```
Phonetic DB Loading:     8,206ms  ← Critical: 8+ seconds to load dictionary!
Radix Tree ED1:          3.86ms/word
Check Word (asyncio):    2.09ms/word
Check Word (sync loop):  1.05ms/word  ← 2x faster without asyncio.run()
Suggest:                 7.17ms/word
```

## Identified Bottlenecks

### Bottleneck #1: asyncio.run() per-word overhead ✅ RISOLTO (Phase 1)

**Location**: `src/furlan_spellchecker/cli/cof_protocol.py` lines 153, 187

**Problem**: Each word check called `asyncio.run()` which creates and destroys an event loop.

**Solution Implemented** (2025-11-30):
- Added `_check_word_core()` shared method in `spell_checker.py`
- Added `check_word_sync()` and `check_word_str_sync()` synchronous methods
- COF CLI now uses `check_word_str_sync()` directly
- Async `check_word_str()` delegates to sync version

**Files Changed**:
- `src/furlan_spellchecker/spellchecker/spell_checker.py`
- `src/furlan_spellchecker/cli/cof_protocol.py`

**Result**: CLI hot path no longer creates event loops per word

---

### Bottleneck #2: Phonetic Database Cold Load (8.2 seconds!) ✅ RESOLVED (Phase 2)

**Note**: This bottleneck analysis refers to the original msgpack implementation.
The subsequent SQLite migration (Phase 6) further improved performance, reliability,
and provided standard SQL tooling for database inspection and maintenance.

**Location**: `src/furlan_spellchecker/database/phonetic.py` - `PhoneticDatabaseMsgpack._load()`

**Problem**: Loading the phonetic msgpack database takes **8.2 seconds** on first access:

```
Phonetic DB: 8206.74ms
```

The `words.msgpack` file is 53MB and contains the entire dictionary with phonetic hash mappings.

**Root Cause**: 
1. msgpack deserialization of 53MB file is slow
2. No memory-mapped access or lazy loading
3. Full dictionary loaded even if only a few lookups needed

**Comparison with Perl**: 
- Perl COF uses BerkeleyDB which is memory-mapped
- Lookups are O(1) without loading entire DB into memory
- COF initializes in ~100ms vs Python's 8+ seconds

**Solution Implemented** (2025-11-30):
- Added sharded msgpack loading (3-character prefixes) with global shard cache reuse across instances
- Optional SQLite mirror (in-memory journaling) when `FSC_BUILD_PHONETIC_SQLITE=1` is set
- LRU (10k) on `find_by_phonetic_hash` plus short-circuit when SQLite already consulted
- Writable fallback cache under `.cache/phonetic_shards` and `.cache/phonetic_sqlite` (repo-local for sandbox)

**Files Changed**:
- `src/furlan_spellchecker/database/phonetic.py`
- Benchmark artifact: `docs/benchmarks/after_phase2_lazy_load_lru.json`

**Result**:
- Phonetic DB load: **8206ms → 1.72ms** (database_loading metric)
- Initialization: **97.6ms → 88.1ms**

---

### Bottleneck #3: RadixTree ED1 - 3.86ms per lookup ✅ RESOLVED (Phase 3)

**Location**: `src/furlan_spellchecker/database/radix_tree.py` - `BinaryRadixTree.get_words_ed1()`

**Problem**: Edit-distance-1 lookups were ~3.86ms/word due to per-traversal string encoding and no caching.

**Solution Implemented** (2025-11-30):
- Pre-encoded edge labels to bytes during tree load (no per-edge encode on traversal)
- Added `lru_cache(maxsize=5000)` for ED1 results (`get_words_ed1`)
- Kept COF-compatible markers and decoding logic intact

**Files Changed**:
- `src/furlan_spellchecker/database/radix_tree.py`
- Benchmark: `docs/benchmarks/after_phase3_radix_optimization.json`

**Result**:
- RadixTree ED1: **3.80ms → 3.44ms** (≈9% faster)
- Suggest: **6.63ms → 3.16ms** (≈2.1x faster) driven by cached ED1 reuse

---

### Bottleneck #4: SQLite Connection Per-Query Overhead ✅ RESOLVED (Phase 4)

**Location**: 
- `src/furlan_spellchecker/database/user_dictionary.py` - `UserDictionaryDatabase._connect()`
- `src/furlan_spellchecker/database/user_exceptions.py` - `UserExceptionsDatabase._connect()`

**Problem**: Each database query opened a new SQLite connection:
- 6800 `sqlite3.connect()` calls for 1700 operations
- 1.28s spent in `connect()` (35% of total time)
- 1.18s spent in `execute()` (32% of total time)

**Root Cause Identified via cProfile Profiling**:
```
ncalls  tottime  percall  cumtime  percall filename:lineno(function)
6800    1.137    0.000    1.276    0.000 {built-in method _sqlite3.connect}
6800    1.179    0.000    1.179    0.000 {method 'execute' of 'sqlite3.Cursor' objects}
```

**Solution Implemented** (2025-12-01):
- Added persistent SQLite connection (`_conn`) to both database classes
- `_get_connection()` returns cached connection (lazy initialization)
- `_connect()` context manager now reuses persistent connection
- `close()` properly releases connection for cleanup
- Updated test fixtures to call `close()` before temp directory cleanup

**Files Changed**:
- `src/furlan_spellchecker/database/user_dictionary.py`
- `src/furlan_spellchecker/database/user_exceptions.py`
- `tests/test_user_databases.py` (fixture teardown fixes)

**Result**:
- check_word_sync: **0.93ms → 0.24ms** (**-74%**)
- suggest: **2.69ms → 0.83ms** (**-69%**)
- sqlite3.connect calls: **6800 → 2** (per session)

---

### Bottleneck #5: Phonetic Algorithm (`_phalg_furlan`) - Per-call Regex Compilation ✅ RESOLVED (Phase 5)

**Location**: `src/furlan_spellchecker/phonetic/furlan_phonetic.py` - `_phalg_furlan()`

**Problem**: The phonetic hash algorithm was recompiling 30+ regex patterns on every call:
- `import re` inside the function
- All `re.sub()` calls compiled patterns on-the-fly
- 20 individual `.replace()` calls for vowel normalization
- Profiler showed 0.169ms/call (1724ms for 10200 calls)

**Solution Implemented** (2025-12-01):
- Added `functools.lru_cache(maxsize=50000)` on `get_phonetic_hashes_by_word()`
- Pre-compiled 24 regex patterns as module-level constants (`_RE_*`)
- Replaced vowel normalization with `str.translate(_VOWEL_NORMALIZE_TABLE)`
- Added `str.maketrans()` table for w/y/x removal
- Moved `import re` to module level

**Files Changed**:
- `src/furlan_spellchecker/phonetic/furlan_phonetic.py`
- Benchmark: `docs/benchmarks/after_phase5_phalg_optimization.json`

**Result**:
- phonetic_hash: **0.0598ms → 0.0286ms** (**-52%**)
- suggest: **6.63ms → 0.76ms** (**-89%**)
- check_word_sync: **0.87ms → 0.19ms** (**-78%**)

---

### Bottleneck #6: Levenshtein Distance - Pure Python ✅ RISOLTO (Phase 1)

**Location**: `src/furlan_spellchecker/spellchecker/suggestion_engine.py` - `SuggestionEngine._levenshtein()`

**Problem**: Levenshtein was computed in pure Python (0.135ms/pair).

**Solution Implemented** (2025-11-30):
- Added `rapidfuzz>=3.0.0` dependency in `pyproject.toml`
- `_levenshtein()` now uses `rapidfuzz.distance.Levenshtein.distance`
- Includes vowel normalization (`_normalize_vowels()`) for Friulian
- Automatic fallback to `phonetic.levenshtein()` if rapidfuzz unavailable

**Files Changed**:
- `src/furlan_spellchecker/spellchecker/suggestion_engine.py`
- `pyproject.toml`

**Result**:
- Levenshtein: 0.135ms → 0.118ms (**-13%**)
- Suggest: 6.63ms → 5.51ms (**-17%**)

---

### Bottleneck #5: Suggestion Engine - Multiple Database Queries

**Location**: `src/furlan_spellchecker/spellchecker/suggestion_engine.py`

**Problem**: Each `suggest()` call makes multiple database queries:

```python
def _cof_basic_suggestions(self, word, lower_word, case_class):
    # 1. Phonetic lookup (system dict) - 2 hash lookups
    phonetic_sys = self._get_phonetic_candidates(lower_word)
    
    # 2. User dictionary lookup
    user_phonetic = self.db.sqlite_db.get_user_dictionary_suggestions(...)
    
    # 3. RadixTree ED1 lookup (SLOW: 3.86ms)
    self._add_radix_edit_distance_candidates(lower_word, ...)
    
    # 4. Error database lookup
    error_correction = self.db.error_db.get_correction(word)
    
    # 5. User error lookup
    user_correction = self.db.sqlite_db.find_in_user_errors_database(word)
```

**Additionally**: For each candidate found, there are:
- Frequency lookups
- Levenshtein distance calculations
- Case transformations

**Solution Options**:
1. **Batch database queries** (prepare all hashes, query once)
2. **Cache suggestion results** (LRU cache for recent words)
3. **Parallel database queries** (asyncio.gather for I/O operations)
4. **Skip expensive operations for correct words** (fast path)

**Estimated Improvement**: 3-10x for suggest operations

---

## Unused/Dead Code Identified

### `_get_frequency_phonetic_candidates()` - O(n) Full Table Scan

**Location**: `src/furlan_spellchecker/spellchecker/suggestion_engine.py` lines 440-489

**Problem**: This method is **defined but never called**, but if it were used it would be catastrophic:

```python
def _get_frequency_phonetic_candidates(self, lower_word, h1, h2):
    # Opens SQLite connection
    cursor.execute("SELECT Key FROM Data WHERE Value IS NOT NULL AND Key != ''")
    all_words = [row[0] for row in cursor.fetchall()]  # ~69,000 words!
    
    # For EACH word, compute phonetic hash
    for word in all_words:
        word_h1, word_h2 = self.phonetic.get_phonetic_hashes_by_word(word)
        # Compare...
```

This would take 69,000 × 0.07ms = ~4.8 seconds per call!

**Action**: Verify this method is truly unused and remove it.

---

## Priority Optimization Roadmap

### Phase 1: Quick Wins (2-5x improvement) ✅ COMPLETATO

1. **Remove asyncio overhead in COF CLI** ✅
   - Implemented `check_word_str_sync()` with shared `_check_word_core()`
   - Effort: Low, Impact: CLI no longer creates event loops

2. **Use rapidfuzz library** ✅
   - Replaced pure Python with C-backed `rapidfuzz.distance.Levenshtein`
   - Added vowel normalization for Friulian accuracy
   - Effort: Low, Impact: -13% Levenshtein, -17% suggest

### Phase 2: Database Optimization (10-50x improvement)

3. **Optimize phonetic database loading**
   - Switch to SQLite with index OR
   - Use pickle/marshal for faster deserialization
   - Effort: Medium, Impact: 10-50x for initialization

4. **Add suggestion caching**
   - LRU cache for recent words
   - Effort: Low, Impact: Variable (depends on repetition)

### Phase 3: Algorithm Optimization (5-20x improvement)

5. **Optimize RadixTree operations**
   - Cython or Rust extension
   - Effort: High, Impact: 5-20x for suggest

6. **Fast path for correct words**
   - Skip suggestion generation for dictionary words
   - Effort: Low, Impact: Significant for check-only operations

---

## Monitoring and Validation

### Running Benchmarks

```bash
# Run full benchmark
python scripts/benchmark.py --words 1000 --output after_fix_v1

# Compare with baseline
python scripts/benchmark.py --compare baseline
```

### Expected Test Invariants

All optimizations MUST preserve:
1. 100% compatibility with Perl COF output format
2. Same words marked correct/incorrect
3. Same suggestions returned (order may vary if non-deterministic)

Run compatibility tests after each change:
```bash
pytest tests/test_cof_compatibility.py -v
pytest tests/test_core.py -v
```

---

## Appendix: Benchmark Data

### Baseline Results (2025-11-28)

```json
{
  "phonetic_hash": {"mean_ms": 0.0684, "throughput_ops_per_sec": 14614},
  "dictionary_lookup": {"mean_ms": 0.0027, "throughput_ops_per_sec": 374447},
  "frequency_lookup": {"mean_ms": 0.0013, "throughput_ops_per_sec": 773515},
  "radix_tree_ed1": {"mean_ms": 3.8598, "throughput_ops_per_sec": 259},
  "levenshtein": {"mean_ms": 0.1329, "throughput_ops_per_sec": 7527},
  "check_word": {"mean_ms": 2.0876, "throughput_ops_per_sec": 479},
  "check_word_sync": {"mean_ms": 1.0473, "throughput_ops_per_sec": 955},
  "suggest": {"mean_ms": 7.1727, "throughput_ops_per_sec": 139}
}
```

### Target Performance (Post-optimization)

| Operation | Baseline | Phase 5 | Target | Status |
|-----------|----------|---------|--------|--------|
| Initialization | 8,200ms | 39ms | 200ms | ✅ EXCEEDED |
| Check word | 2.1ms | 0.19ms | 0.5ms | ✅ EXCEEDED |
| Suggest word | 7.2ms | 0.76ms | 2.0ms | ✅ EXCEEDED |
| Phonetic hash | 0.06ms | 0.03ms | 0.05ms | ✅ EXCEEDED |
| Throughput (check) | 479/sec | 5,390/sec | 2,000/sec | ✅ EXCEEDED |
| Throughput (suggest) | 139/sec | 1,324/sec | 500/sec | ✅ EXCEEDED |

---

## References

- Baseline benchmark: `docs/benchmarks/baseline.json`
- COF Perl source: `../COF/lib/COF/SpellChecker.pm`
- Comparison tests: `tests/test_cof_compatibility.py`
