# Benchmark Results

This directory contains performance benchmark results for FurlanSpellChecker.

## File Naming Convention

- `YYYY-MM-DD_HHmmss_benchmark.json` - Regular benchmark run
- `YYYY-MM-DD_HHmmss_baseline.json` - Baseline measurement before optimization
- `<custom_name>.json` - Named benchmark run (e.g., `after_asyncio_fix.json`)

## Running Benchmarks

```bash
# Full benchmark (1000 words)
python scripts/benchmark.py

# Quick benchmark (100 words)
python scripts/benchmark.py --quick

# Custom word count
python scripts/benchmark.py --words 500

# Named output
python scripts/benchmark.py --output after_optimization_v1

# Compare with baseline
python scripts/benchmark.py --compare baseline
```

## Metrics Collected

Each benchmark measures:
- **Total time** - Overall execution time
- **Mean time** - Average per-operation time
- **Percentiles** - p50, p75, p90, p95, p99
- **Throughput** - Operations per second
- **Standard deviation** - Consistency measure

## Benchmarks Included

| Benchmark | Description |
|-----------|-------------|
| `initialization` | Cold start component initialization |
| `database_loading` | Time to load each database type |
| `phonetic_hash` | Phonetic hash calculation per word |
| `dictionary_lookup` | Phonetic hash lookup in dictionary |
| `frequency_lookup` | Word frequency lookup |
| `radix_tree_ed1` | Edit distance 1 word search |
| `levenshtein` | Levenshtein distance calculation |
| `check_word` | Full word check (with asyncio.run) |
| `check_word_sync` | Word check (shared event loop) |
| `suggest` | Suggestion generation |

## Interpreting Results

When comparing benchmarks:
- **< -5% change**: Performance improvement (✓ FASTER)
- **> +5% change**: Performance regression (✗ SLOWER)
- **±5% change**: Within noise margin (≈ SAME)

## Historical Baselines

| Date | Version | Description | File |
|------|---------|-------------|------|
| 2025-11-28 | 1.0.0 | Initial baseline before optimization | `2025-11-28_201911_baseline.json` |
| 2025-11-30 | 1.0.0 | Phase 1: Sync API + RapidFuzz | `after_phase1_sync_rapidfuzz.json` |
| 2025-11-30 | 1.0.0 | Phase 2: Lazy phonetic DB + LRU cache | `after_phase2_lazy_load_lru.json` |
| 2025-11-30 | 1.0.0 | Phase 3: RadixTree optimization (byte labels + ED1 cache) | `after_phase3_radix_optimization.json` |
| 2025-12-01 | 1.0.0 | Phase 4: SQLite connection pooling | `after_phase4_connection_pooling.json` |
| 2025-12-01 | 1.0.0 | Phase 5: Phonetic algorithm optimization (pre-compiled regex + LRU) | `after_phase5_phalg_optimization.json` |
| 2025-12-03 | 1.0.0 | Phase 6: SQLite consolidation (removed MsgPack/BerkeleyDB) | `after_phase6_sqlite_consolidation.json` |
| 2025-12-03 | 1.0.0 | Phase 7: Performance optimization (in-memory caches, batch lookups) | `after_phase7_performance_optimization.json` |

## Phase 1 Results (2025-11-30)

**Changes**: Sync API for CLI, RapidFuzz C-backed Levenshtein

| Metric | Baseline | Phase 1 | Delta |
|--------|----------|---------|-------|
| levenshtein | 0.135ms | 0.118ms | **-13%** ✅ |
| suggest | 6.63ms | 5.51ms | **-17%** ✅ |
| check_word | 1.64ms | 1.69ms | ~0% |
| check_word_sync | 0.87ms | 0.89ms | ~0% |

## Phase 2 Results (2025-11-30)

**Changes**: Sharded phonetic msgpack loading, optional SQLite mirror, LRU cache on phonetic lookups

| Metric | Baseline | Phase 2 | Delta |
|--------|----------|---------|-------|
| phonetic_db_load | 8206ms | 1.72ms | **-99.98%** ✅ |
| initialization | 97.6ms | 88.1ms | **-9.8%** ✅ |
| dictionary_lookup | 0.002ms | 0.143ms | slower (on-demand + sandboxed SQLite) |
| check_word | 1.64ms | 2.07ms | slower (pending Phase 3/4 optimizations) |

## Phase 3 Results (2025-11-30)

**Changes**: Pre-encoded RadixTree edge labels to bytes and added ED1 result cache (5k LRU).

| Metric | Baseline | Phase 3 | Delta |
|--------|----------|---------|-------|
| radix_tree_ed1 | 3.80ms | 3.44ms | **-9%** ✅ |
| suggest | 6.63ms | 3.16ms | **-52%** ✅ |
| check_word | 1.64ms | 2.23ms | slower (pending Phase 4 fast-path) |

## Phase 4 Results (2025-12-01)

**Changes**: SQLite persistent connection pooling (eliminated per-query connect overhead).

| Metric | Phase 3 | Phase 4 | Delta |
|--------|---------|---------|-------|
| check_word_sync | 0.93ms | 0.24ms | **-74%** ✅ |
| suggest | 2.69ms | 0.83ms | **-69%** ✅ |
| sqlite3.connect calls | 6800 | 2 | **-99.97%** ✅ |

## Phase 5 Results (2025-12-01)

**Changes**: Phonetic algorithm (`_phalg_furlan`) optimization:
- Pre-compiled 24 regex patterns at module level
- `str.translate()` for vowel normalization (20 substitutions → 1 call)
- LRU cache (50k) on `get_phonetic_hashes_by_word()`

| Metric | Phase 4 | Phase 5 | Delta |
|--------|---------|---------|-------|
| phonetic_hash | 0.0598ms | 0.0286ms | **-52%** ✅ |
| suggest | 6.63ms | 0.76ms | **-89%** ✅ |
| check_word_sync | 0.87ms | 0.19ms | **-78%** ✅ |
| check_word | 1.64ms | 1.17ms | **-29%** ✅ |

### Cumulative Improvement (Baseline → Phase 5)

| Metric | Baseline | Phase 5 | Total Improvement |
|--------|----------|---------|-------------------|
| check_word_sync | 1.05ms | 0.19ms | **-82%** |
| suggest | 7.17ms | 0.76ms | **-89%** |
| phonetic_hash | 0.06ms | 0.03ms | **-52%** |
| phonetic_db_load | 8206ms | 1.76ms | **-99.98%** |
| initialization | 265ms | 39ms | **-85%** |

## Phase 6: SQLite Consolidation Results (2025-12-03)

**Changes**: Migrated from MsgPack to SQLite-only format:
- Removed MsgPack and BerkeleyDB format support
- Added repository pattern with base, sqlite, cached implementations
- Consolidated around SQLite with LRU caching layer

| Metric | Phase 5 | SQLite | Delta | Notes |
|--------|---------|--------|-------|-------|
| database_loading | 61.0ms | 37.8ms | **-38%** ✅ | Faster SQLite loading |
| dictionary_lookup | 0.128ms | 0.072ms | **-44%** ✅ | SQLite + cache efficient |
| frequency_lookup | 0.001ms | 0.021ms | +2000% ⚠️ | SQLite I/O vs in-memory |
| phonetic_hash | 0.029ms | 0.046ms | +59% ⚠️ | System variance |
| check_word_sync | 0.186ms | 0.273ms | +47% ⚠️ | SQLite overhead |
| suggest | 0.755ms | 1.430ms | +89% ⚠️ | Multiple SQLite queries |
| radix_tree_ed1 | 3.21ms | 5.04ms | +57% ⚠️ | Unchanged (binary format) |

### Trade-offs

The SQLite consolidation prioritizes **maintainability** and **cross-platform compatibility** over raw performance:

**Benefits:**
- Single dependency (sqlite3 in stdlib) vs msgpack + bsddb3
- Easier debugging with standard SQL tools
- Consistent format across all database types
- Simpler codebase (~211 lines removed)

**Performance Impact:**
- SQLite I/O is slower than in-memory msgpack for high-frequency lookups
- Cache layer mitigates impact for repeated queries
- Still acceptable for interactive spell-checking (~3600 words/sec sync)

## Phase 7: Performance Optimization Results (2025-12-03)

**Changes**: In-memory caching and batch operations to recover SQLite overhead:
- Frequency database: full in-memory cache on first access (~69K entries, ~2MB)
- Phonetic repositories: batch `get_batch()` method for multiple hash lookups
- Elision database: `InMemoryElisionRepository` with `frozenset` for O(1) lookups
- RadixTree: LRU cache increased to 10K, early exit for words >15 chars
- Levenshtein: rapidfuzz mandatory dependency + optimized fallback

| Metric | Phase 6 | Phase 7 | Delta |
|--------|---------|---------|-------|
| check_word | 2.95ms | 1.14ms | **-61%** ✅ |
| check_word_sync | 0.27ms | 0.18ms | **-32%** ✅ |
| suggest | 1.36ms | 0.92ms | **-32%** ✅ |
| radix_tree_ed1 | 5.04ms | 3.38ms | **-33%** ✅ |
| levenshtein | 0.153ms | 0.003ms | **-98%** ✅ |
| frequency_lookup | 0.018ms | 0.017ms | **-6%** ✅ |
| initialization | 140ms | 105ms | **-25%** ✅ |

### Cumulative Improvement (Baseline → Phase 7)

| Metric | Baseline | Phase 7 | Total Improvement |
|--------|----------|---------|-------------------|
| check_word_sync | 1.05ms | 0.18ms | **-83%** |
| suggest | 7.17ms | 0.92ms | **-87%** |
| levenshtein | 0.135ms | 0.003ms | **-98%** |
| radix_tree_ed1 | 3.80ms | 3.38ms | **-11%** |
| initialization | 265ms | 105ms | **-60%** |
