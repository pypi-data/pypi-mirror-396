# TODO - FurlanSpellChecker Performance Optimization

This document tracks planned activities for performance optimization.

## 🔴 High Priority - Critical Bottlenecks

### 1. ~~Remove asyncio.run() overhead in cof_protocol.py~~ ✅ COMPLETED
- **File:** `src/furlanspellchecker/cof_protocol.py`
- **Lines:** 153, 187
- **Solution implemented:** `check_word_str_sync()` with shared `_check_word_core()`
- **Result:** CLI now uses sync path, no event loop overhead

### 2. Pre-compute phonetic hashes in database
- **File:** `src/furlanspellchecker/suggestion_engine.py`
- **Method:** `_get_frequency_phonetic_candidates()` lines 440-489
- **Problem:** Computes phonetic hash for all 69,000+ words on each suggestion
- **Impact:** 8.2 seconds on first load, ~7ms per suggestion
- **Solution:** Create `phonetic_hashes.msgpack` with pre-computed hashes
- **Estimate:** 8-12 hours

### 3. Optimize RadixTree for edit-distance-1
- **File:** `src/furlanspellchecker/radix_tree.py`
- **Problem:** 3.86ms per ED1 query, too slow for batch operations
- **Impact:** ~35% of total suggest() time
- **Solution:** Investigate alternative structures (BK-tree, SymSpell)
- **Estimate:** 16-24 hours

---

## 🟡 Medium Priority - Structural Improvements

### 4. Result caching with LRU
- **Goal:** Avoid recomputation for already verified words
- **Implementation:**
  ```python
  from functools import lru_cache
  
  @lru_cache(maxsize=10000)
  def check_word_cached(self, word: str) -> CheckResult:
      ...
  ```
- **Estimate:** 2-4 hours

### 5. Batch processing for multiple checks
- **Goal:** Reduce overhead for long documents
- **API:**
  ```python
  def check_words_batch(words: List[str]) -> Dict[str, CheckResult]
  ```
- **Estimate:** 4-6 hours

### 6. More aggressive lazy loading
- **Goal:** Load only required databases
- **Improvement:** RadixTree loaded only when suggestions are needed
- **Estimate:** 2-3 hours

---

## 🟢 Low Priority - Nice to Have

### 7. Optimized binary database
- Evaluate `mmap` for direct access without full deserialization
- Potential savings: 50-80% loading time

### 8. Suggestion parallelization
- `multiprocessing.Pool` for suggestion computation
- Useful only for large batches (>1000 words)

### 9. ~~C Extension for Levenshtein~~ ✅ COMPLETED
- Implemented `rapidfuzz.distance.Levenshtein.distance` with vowel normalization
- Automatic fallback to phonetic implementation if rapidfuzz unavailable
- **Result:** -13% Levenshtein time, -17% suggest time

---

## 📊 CI/CD Integration

### GitHub Actions Workflow (Future)

```yaml
# .github/workflows/benchmark.yml
name: Performance Benchmark

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
      
      - name: Run benchmarks
        run: |
          python scripts/benchmark.py \
            --words 1000 \
            --warmup 3 \
            --output docs/benchmarks/ci_$(date +%Y%m%d_%H%M%S).json
      
      - name: Compare with baseline
        run: |
          python scripts/compare_benchmarks.py --vs-baseline --format json \
            > benchmark_comparison.json
      
      - name: Check for regressions
        run: |
          python -c "
          import json
          with open('benchmark_comparison.json') as f:
              data = json.load(f)
          # Fail if any metric regressed more than 10%
          for bench in data['benchmarks'].values():
              if 'delta' in bench:
                  for metric, delta in bench['delta'].items():
                      if metric != 'ops_per_sec' and delta > 10:
                          print(f'Regression: {metric} +{delta}%')
                          exit(1)
                      if metric == 'ops_per_sec' and delta < -10:
                          print(f'Regression: {metric} {delta}%')
                          exit(1)
          print('No regressions detected')
          "
      
      - name: Upload benchmark results
        uses: actions/upload-artifact@v4
        with:
          name: benchmark-results
          path: docs/benchmarks/*.json
```

### Pytest-benchmark Integration (Future)

```python
# tests/test_performance.py
import pytest
from furlanspellchecker import FurlanSpellChecker

@pytest.fixture(scope='module')
def spell_checker():
    return FurlanSpellChecker()

def test_check_word_performance(benchmark, spell_checker):
    """Benchmark: check_word must complete in < 2ms"""
    result = benchmark(spell_checker.check_word_sync, 'cjase')
    assert result.is_correct
    
def test_suggest_performance(benchmark, spell_checker):
    """Benchmark: suggest must complete in < 10ms"""
    result = benchmark(spell_checker.suggest, 'cjasa')
    assert len(result) > 0

# Run with: pytest tests/test_performance.py --benchmark-only
```

---

## 📈 Target Metrics

| Operation | Baseline | Current (Phase 5) | Target | Status |
|-----------|----------|-------------------|--------|--------|
| Initialization | 265ms | 39ms | < 100ms | ✅ ACHIEVED |
| check_word (sync) | 1.04ms | 0.19ms | < 0.5ms | ✅ ACHIEVED |
| check_word (async) | 2.08ms | 1.17ms | < 1.0ms | ⚠️ CLOSE |
| suggest | 7.17ms | 0.76ms | < 2.0ms | ✅ ACHIEVED |
| RadixTree ED1 | 3.86ms | 3.21ms | < 1.0ms | 🔴 PENDING |
| Phonetic hash | 0.06ms | 0.03ms | < 0.05ms | ✅ ACHIEVED |
| Phonetic DB load | 8206ms | 1.76ms | < 500ms | ✅ ACHIEVED |

---

## 📝 Notes

- **Guiding principle:** NO functional changes. All existing tests must pass.
- **Approach:** Incremental changes, one bottleneck at a time, with benchmark after each modification.
- **Validation:** Use `scripts/compare_benchmarks.py --vs-baseline` after each optimization.

---

## ✅ Completed

- [x] Created `scripts/benchmark.py` - micro-level benchmark infrastructure
- [x] Created `docs/benchmarks/` - directory for historical results
- [x] Ran baseline benchmark (500 words)
- [x] Documented bottleneck analysis in `performance_analysis.md`
- [x] Created `scripts/compare_benchmarks.py` - benchmark comparison tool

### Phase 1 (2025-11-30) - Sync API + RapidFuzz
- [x] Removed `asyncio.run()` overhead in COF CLI (uses `check_word_str_sync()`)
- [x] Added shared `_check_word_core()` method for sync/async API
- [x] Replaced pure Python Levenshtein with `rapidfuzz` C-backed
- [x] Added automatic fallback if rapidfuzz unavailable
- [x] Updated `pyproject.toml` with `rapidfuzz>=3.0.0` dependency

**Phase 1 Results:**
| Metric | Baseline | After Phase 1 | Delta |
|--------|----------|---------------|-------|
| levenshtein | 0.135ms | 0.118ms | **-13%** |
| suggest | 6.63ms | 5.51ms | **-17%** |
| check_word_sync | 0.87ms | 0.89ms | ~0% (noise) |

### Phase 2 (2025-11-30) - Database lazy load + LRU cache
- [x] Added sharded phonetic msgpack loading with shared shard cache (3-char prefixes)
- [x] Optional SQLite mirror with in-memory journaling (`FSC_BUILD_PHONETIC_SQLITE=1`) for fast lookups
- [x] LRU cache (10k) on `find_by_phonetic_hash` with global shard reuse across instances
- [x] Benchmark saved: `docs/benchmarks/after_phase2_lazy_load_lru.json`

**Phase 2 Results:**
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| phonetic_db_load | 8206ms | 1.72ms | **-99.98%** |
| initialization | 97.6ms | 88.1ms | **-9.8%** |
| dictionary_lookup | 0.002ms | 0.143ms | slower (on-demand lookups) |

### Phase 3 (2025-11-30) - RadixTree optimization
- [x] Pre-encoded edge labels to bytes during load (no per-traversal encode)
- [x] Added ED1 result cache (`lru_cache(maxsize=5000)`) for repeated misspellings
- [x] Benchmark saved: `docs/benchmarks/after_phase3_radix_optimization.json`

**Phase 3 Results:**
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| radix_tree_ed1 | 3.80ms | 3.44ms | **-9%** |
| suggest | 6.63ms | 3.16ms | **-52%** |

### Phase 4 (2025-12-01) - SQLite Connection Pooling
- [x] Implemented persistent SQLite connections in `UserDictionaryDatabase`
- [x] Implemented persistent SQLite connections in `UserExceptionsDatabase`
- [x] Added `_get_connection()` lazy initialization method
- [x] Updated `close()` to properly release persistent connections
- [x] Fixed test fixtures to close connections before temp dir cleanup
- [x] Created `scripts/profile_hotspots.py` profiling tool
- [x] Benchmark saved: `docs/benchmarks/after_phase4_connection_pooling.json`

**Phase 4 Results:**
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| check_word_sync | 0.93ms | 0.24ms | **-74%** |
| suggest | 2.69ms | 0.83ms | **-69%** |
| sqlite3.connect calls | 6800 | 2 | **-99.97%** |

### Phase 5 (2025-12-01) - Phonetic Algorithm Optimization (`_phalg_furlan`)
- [x] Added `functools.lru_cache(maxsize=50000)` on `get_phonetic_hashes_by_word()`
- [x] Pre-compiled 24 regex patterns at module level (eliminated per-call compilation)
- [x] Replaced 20 vowel substitutions with `str.translate()` table
- [x] Added `str.maketrans()` for w/y/x removal
- [x] Removed `import re` from inside function
- [x] Benchmark saved: `docs/benchmarks/after_phase5_phalg_optimization.json`

**Phase 5 Results:**
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| phonetic_hash | 0.0598ms | 0.0286ms | **-52%** |
| suggest | 6.63ms | 0.76ms | **-89%** |
| check_word_sync | 0.87ms | 0.19ms | **-78%** |
| check_word | 1.64ms | 1.17ms | **-29%** |
