#!/usr/bin/env python3
"""
Advanced profiling script for FurlanSpellChecker.

Provides multi-dimensional analysis to identify optimization opportunities:
- CPU profiling with cProfile (function-level hotspots)
- Memory profiling with tracemalloc (allocation tracking)
- Cache efficiency analysis (LRU hit/miss rates)
- Per-category breakdown (valid/misspelled/unknown words)
- JSON export for automated comparison

Usage:
    python scripts/profile_advanced.py
    python scripts/profile_advanced.py --output results.json
    python scripts/profile_advanced.py --export-pstats profile.pstats
"""

import argparse
import cProfile
import gc
import io
import json
import pstats
import sys
import time
import tracemalloc
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from furlan_spellchecker import FurlanSpellChecker
from furlan_spellchecker.config import FurlanSpellCheckerConfig
from furlan_spellchecker.dictionary import Dictionary
from furlan_spellchecker.spellchecker.text_processor import TextProcessor

# =============================================================================
# Test Data
# =============================================================================

TEST_WORDS = {
    "valid_short": ["aghe", "bon", "alt", "om", "an", "no", "sì", "ce", "jo"],
    "valid_long": ["marilenghe", "furlanofons", "agricolture", "universitât", "comunicazion"],
    "valid_accented": ["cjase", "čhase", "gjat", "ğjat", "lûs", "plui"],
    "misspelled_easy": ["cjasa", "marilengha", "agriculure", "univrsitat"],
    "misspelled_hard": ["furlanofone", "comunicasion", "agricoltur", "universtat"],
    "unknown": ["xyz123", "asdfghjkl", "qwerty", "notaword"],
}

ITERATIONS = 50  # Per category


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class TimingResult:
    """Timing results for an operation."""

    total_ms: float
    mean_ms: float
    min_ms: float
    max_ms: float
    ops_per_sec: float
    call_count: int


@dataclass
class MemoryResult:
    """Memory allocation results."""

    peak_mb: float
    current_mb: float
    top_allocations: list[dict[str, Any]]


@dataclass
class CacheStats:
    """LRU cache statistics."""

    name: str
    hits: int
    misses: int
    maxsize: int
    currsize: int
    hit_rate: float


@dataclass
class CategoryResult:
    """Results for a word category."""

    category: str
    word_count: int
    check_timing: TimingResult
    suggest_timing: TimingResult


@dataclass
class ProfilingReport:
    """Complete profiling report."""

    timestamp: str
    python_version: str
    iterations: int

    # Overall timing
    load_time_ms: float
    warmup_time_ms: float
    check_word_overall: TimingResult
    suggest_overall: TimingResult
    mixed_workload: TimingResult

    # Per-category breakdown
    category_results: list[CategoryResult]

    # Memory analysis
    memory: MemoryResult

    # Cache efficiency
    cache_stats: list[CacheStats]

    # Top hotspots (from cProfile)
    cpu_hotspots: list[dict[str, Any]]


# =============================================================================
# Profiling Functions
# =============================================================================


def create_spellchecker() -> FurlanSpellChecker:
    """Create and initialize FurlanSpellChecker instance."""
    config = FurlanSpellCheckerConfig()
    dictionary = Dictionary()
    text_processor = TextProcessor()
    return FurlanSpellChecker(dictionary=dictionary, text_processor=text_processor, config=config)


def time_operation(func, *args, iterations: int = 1) -> TimingResult:
    """Time an operation and return statistics."""
    times = []

    for _ in range(iterations):
        start = time.perf_counter()
        func(*args)
        elapsed = time.perf_counter() - start
        times.append(elapsed * 1000)  # Convert to ms

    total = sum(times)
    mean = total / len(times)

    return TimingResult(
        total_ms=total,
        mean_ms=mean,
        min_ms=min(times),
        max_ms=max(times),
        ops_per_sec=1000 / mean if mean > 0 else 0,
        call_count=iterations,
    )


def profile_check_word_category(
    checker: FurlanSpellChecker, words: list[str], iterations: int
) -> TimingResult:
    """Profile check_word for a specific word list."""
    times = []

    for _ in range(iterations):
        for word in words:
            start = time.perf_counter()
            checker.check_word_str_sync(word)
            elapsed = time.perf_counter() - start
            times.append(elapsed * 1000)

    total = sum(times)
    count = len(times)
    mean = total / count if count > 0 else 0

    return TimingResult(
        total_ms=total,
        mean_ms=mean,
        min_ms=min(times) if times else 0,
        max_ms=max(times) if times else 0,
        ops_per_sec=1000 / mean if mean > 0 else 0,
        call_count=count,
    )


def profile_suggest_category(
    checker: FurlanSpellChecker, words: list[str], iterations: int
) -> TimingResult:
    """Profile suggest for a specific word list."""
    times = []

    for _ in range(iterations):
        for word in words:
            start = time.perf_counter()
            checker.suggest(word)
            elapsed = time.perf_counter() - start
            times.append(elapsed * 1000)

    total = sum(times)
    count = len(times)
    mean = total / count if count > 0 else 0

    return TimingResult(
        total_ms=total,
        mean_ms=mean,
        min_ms=min(times) if times else 0,
        max_ms=max(times) if times else 0,
        ops_per_sec=1000 / mean if mean > 0 else 0,
        call_count=count,
    )


def get_cache_stats(checker: FurlanSpellChecker) -> list[CacheStats]:
    """Extract LRU cache statistics from the spellchecker."""
    stats = []

    # Try to find cached functions

    # Search for lru_cache decorated functions
    try:
        # RadixTree ED1 cache
        radix = checker._db_manager.radix_tree
        if hasattr(radix, "get_words_ed1"):
            func = radix.get_words_ed1
            if hasattr(func, "cache_info"):
                info = func.cache_info()
                hit_rate = (
                    info.hits / (info.hits + info.misses) * 100
                    if (info.hits + info.misses) > 0
                    else 0
                )
                stats.append(
                    CacheStats(
                        name="RadixTree.get_words_ed1",
                        hits=info.hits,
                        misses=info.misses,
                        maxsize=info.maxsize or 0,
                        currsize=info.currsize,
                        hit_rate=hit_rate,
                    )
                )
    except Exception:
        pass

    try:
        # Phonetic DB cache
        phonetic = checker._db_manager.phonetic_db
        if hasattr(phonetic, "find_by_phonetic_hash"):
            func = phonetic.find_by_phonetic_hash
            if hasattr(func, "cache_info"):
                info = func.cache_info()
                hit_rate = (
                    info.hits / (info.hits + info.misses) * 100
                    if (info.hits + info.misses) > 0
                    else 0
                )
                stats.append(
                    CacheStats(
                        name="PhoneticDB.find_by_phonetic_hash",
                        hits=info.hits,
                        misses=info.misses,
                        maxsize=info.maxsize or 0,
                        currsize=info.currsize,
                        hit_rate=hit_rate,
                    )
                )
    except Exception:
        pass

    return stats


def analyze_memory(checker: FurlanSpellChecker, words: list[str]) -> MemoryResult:
    """Analyze memory allocations during operations."""
    gc.collect()
    tracemalloc.start()

    # Run operations
    for word in words:
        checker.check_word_str_sync(word)
        checker.suggest(word)

    current, peak = tracemalloc.get_traced_memory()
    snapshot = tracemalloc.take_snapshot()
    tracemalloc.stop()

    # Get top allocations
    top_stats = snapshot.statistics("lineno")[:10]
    top_allocations = []

    for stat in top_stats:
        top_allocations.append(
            {"file": str(stat.traceback), "size_kb": stat.size / 1024, "count": stat.count}
        )

    return MemoryResult(
        peak_mb=peak / 1024 / 1024,
        current_mb=current / 1024 / 1024,
        top_allocations=top_allocations,
    )


def extract_cpu_hotspots(profiler: cProfile.Profile, limit: int = 15) -> list[dict[str, Any]]:
    """Extract top CPU hotspots from profiler."""
    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats("cumtime")

    hotspots = []

    # Get raw stats
    for func, (_cc, nc, tt, ct, _callers) in stats.stats.items():
        filename, lineno, funcname = func

        # Filter to furlan_spellchecker only
        if "furlan_spellchecker" in filename:
            hotspots.append(
                {
                    "function": funcname,
                    "file": Path(filename).name,
                    "line": lineno,
                    "calls": nc,
                    "tottime_ms": tt * 1000,
                    "cumtime_ms": ct * 1000,
                    "percall_ms": (ct / nc * 1000) if nc > 0 else 0,
                }
            )

    # Sort by cumulative time and limit
    hotspots.sort(key=lambda x: x["cumtime_ms"], reverse=True)
    return hotspots[:limit]


# =============================================================================
# Main Profiling
# =============================================================================


def run_advanced_profiling(
    output_file: str | None = None, pstats_file: str | None = None, verbose: bool = True
) -> ProfilingReport:
    """Run comprehensive profiling and generate report."""

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    if verbose:
        print("=" * 70)
        print("FurlanSpellChecker Advanced Profiling")
        print("=" * 70)
        print(f"\nTimestamp: {timestamp}")
        print(f"Python: {sys.version.split()[0]}")
        print(f"Iterations per category: {ITERATIONS}")
        print()

    # ==========================================================================
    # 1. Load and warmup
    # ==========================================================================
    if verbose:
        print("Phase 1: Loading and warmup...")

    load_start = time.perf_counter()
    checker = create_spellchecker()
    load_time = (time.perf_counter() - load_start) * 1000

    if verbose:
        print(f"  Load time: {load_time:.2f}ms")

    # Warmup
    warmup_start = time.perf_counter()
    all_words = [w for words in TEST_WORDS.values() for w in words]
    for word in all_words:
        checker.check_word_str_sync(word)
        checker.suggest(word)
    warmup_time = (time.perf_counter() - warmup_start) * 1000

    if verbose:
        print(f"  Warmup time: {warmup_time:.2f}ms")
        print()

    # ==========================================================================
    # 2. Per-category profiling
    # ==========================================================================
    if verbose:
        print("Phase 2: Per-category analysis...")
        print("-" * 70)

    category_results = []

    for category, words in TEST_WORDS.items():
        check_timing = profile_check_word_category(checker, words, ITERATIONS)
        suggest_timing = profile_suggest_category(checker, words, ITERATIONS)

        result = CategoryResult(
            category=category,
            word_count=len(words),
            check_timing=check_timing,
            suggest_timing=suggest_timing,
        )
        category_results.append(result)

        if verbose:
            print(f"\n  {category} ({len(words)} words):")
            print(
                f"    check_word:  {check_timing.mean_ms:.4f}ms/word  (total: {check_timing.total_ms:.1f}ms)"
            )
            print(
                f"    suggest:     {suggest_timing.mean_ms:.4f}ms/word  (total: {suggest_timing.total_ms:.1f}ms)"
            )

    if verbose:
        print()

    # ==========================================================================
    # 3. Overall profiling with cProfile
    # ==========================================================================
    if verbose:
        print("Phase 3: CPU profiling (cProfile)...")
        print("-" * 70)

    profiler = cProfile.Profile()
    profiler.enable()

    overall_start = time.perf_counter()

    # Check word overall
    for _ in range(ITERATIONS):
        for word in all_words:
            checker.check_word_str_sync(word)

    check_elapsed = time.perf_counter() - overall_start

    # Suggest overall
    suggest_start = time.perf_counter()
    for _ in range(ITERATIONS):
        for word in all_words:
            checker.suggest(word)

    suggest_elapsed = time.perf_counter() - suggest_start

    # Mixed workload
    mixed_start = time.perf_counter()
    for _ in range(ITERATIONS):
        for word in all_words:
            is_valid = checker.check_word_str_sync(word)
            if not is_valid:
                checker.suggest(word)

    mixed_elapsed = time.perf_counter() - mixed_start

    profiler.disable()

    # Save pstats if requested
    if pstats_file:
        profiler.dump_stats(pstats_file)
        if verbose:
            print(f"  pstats saved to: {pstats_file}")
            print(f"  View with: python -m snakeviz {pstats_file}")

    # Calculate timing results
    total_words = len(all_words)
    total_check_ops = total_words * ITERATIONS
    total_suggest_ops = total_words * ITERATIONS

    check_overall = TimingResult(
        total_ms=check_elapsed * 1000,
        mean_ms=check_elapsed * 1000 / total_check_ops,
        min_ms=0,  # Not tracked per-op
        max_ms=0,
        ops_per_sec=total_check_ops / check_elapsed,
        call_count=total_check_ops,
    )

    suggest_overall = TimingResult(
        total_ms=suggest_elapsed * 1000,
        mean_ms=suggest_elapsed * 1000 / total_suggest_ops,
        min_ms=0,
        max_ms=0,
        ops_per_sec=total_suggest_ops / suggest_elapsed,
        call_count=total_suggest_ops,
    )

    mixed_overall = TimingResult(
        total_ms=mixed_elapsed * 1000,
        mean_ms=mixed_elapsed * 1000 / (total_words * ITERATIONS),
        min_ms=0,
        max_ms=0,
        ops_per_sec=(total_words * ITERATIONS) / mixed_elapsed,
        call_count=total_words * ITERATIONS,
    )

    if verbose:
        print(
            f"\n  check_word overall: {check_overall.mean_ms:.4f}ms/op ({check_overall.ops_per_sec:.0f} ops/sec)"
        )
        print(
            f"  suggest overall:    {suggest_overall.mean_ms:.4f}ms/op ({suggest_overall.ops_per_sec:.0f} ops/sec)"
        )
        print(
            f"  mixed workload:     {mixed_overall.mean_ms:.4f}ms/op ({mixed_overall.ops_per_sec:.0f} ops/sec)"
        )
        print()

    # Extract hotspots
    cpu_hotspots = extract_cpu_hotspots(profiler)

    if verbose:
        print("  Top 10 CPU hotspots (furlan_spellchecker only):")
        for i, h in enumerate(cpu_hotspots[:10], 1):
            print(f"    {i:2}. {h['function']:40} {h['cumtime_ms']:8.1f}ms  ({h['calls']} calls)")
        print()

    # ==========================================================================
    # 4. Cache analysis
    # ==========================================================================
    if verbose:
        print("Phase 4: Cache efficiency analysis...")
        print("-" * 70)

    cache_stats = get_cache_stats(checker)

    if verbose:
        if cache_stats:
            for cs in cache_stats:
                print(f"  {cs.name}:")
                print(f"    Hits: {cs.hits}, Misses: {cs.misses}, Hit Rate: {cs.hit_rate:.1f}%")
                print(f"    Size: {cs.currsize}/{cs.maxsize}")
        else:
            print("  No LRU caches found or accessible")
        print()

    # ==========================================================================
    # 5. Memory analysis
    # ==========================================================================
    if verbose:
        print("Phase 5: Memory analysis...")
        print("-" * 70)

    memory = analyze_memory(checker, all_words[:20])  # Sample for memory analysis

    if verbose:
        print(f"  Peak memory: {memory.peak_mb:.2f} MB")
        print(f"  Current memory: {memory.current_mb:.2f} MB")
        print("\n  Top memory allocations:")
        for i, alloc in enumerate(memory.top_allocations[:5], 1):
            print(f"    {i}. {alloc['size_kb']:.1f} KB ({alloc['count']} objects)")
        print()

    # ==========================================================================
    # Build report
    # ==========================================================================
    report = ProfilingReport(
        timestamp=timestamp,
        python_version=sys.version.split()[0],
        iterations=ITERATIONS,
        load_time_ms=load_time,
        warmup_time_ms=warmup_time,
        check_word_overall=check_overall,
        suggest_overall=suggest_overall,
        mixed_workload=mixed_overall,
        category_results=category_results,
        memory=memory,
        cache_stats=cache_stats,
        cpu_hotspots=cpu_hotspots,
    )

    # ==========================================================================
    # Summary
    # ==========================================================================
    if verbose:
        print("=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"\n  Load time:        {load_time:.2f}ms")
        print(
            f"  check_word:       {check_overall.mean_ms:.4f}ms/op  ({check_overall.ops_per_sec:.0f} ops/sec)"
        )
        print(
            f"  suggest:          {suggest_overall.mean_ms:.4f}ms/op  ({suggest_overall.ops_per_sec:.0f} ops/sec)"
        )
        print(f"  Peak memory:      {memory.peak_mb:.2f} MB")

        if cache_stats:
            avg_hit_rate = sum(cs.hit_rate for cs in cache_stats) / len(cache_stats)
            print(f"  Avg cache hit:    {avg_hit_rate:.1f}%")

        print("\n  Per-category suggest times:")
        for cr in sorted(category_results, key=lambda x: x.suggest_timing.mean_ms, reverse=True):
            print(f"    {cr.category:20} {cr.suggest_timing.mean_ms:.4f}ms/word")

        print()

    # ==========================================================================
    # Export JSON
    # ==========================================================================
    if output_file:
        # Convert dataclasses to dict for JSON serialization
        def to_dict(obj):
            if hasattr(obj, "__dataclass_fields__"):
                return {k: to_dict(v) for k, v in asdict(obj).items()}
            elif isinstance(obj, list):
                return [to_dict(item) for item in obj]
            elif isinstance(obj, dict):
                return {k: to_dict(v) for k, v in obj.items()}
            return obj

        report_dict = to_dict(report)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)

        if verbose:
            print(f"Report saved to: {output_file}")

    return report


# =============================================================================
# CLI
# =============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Advanced profiling for FurlanSpellChecker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/profile_advanced.py
  python scripts/profile_advanced.py --output profile_report.json
  python scripts/profile_advanced.py --export-pstats profile.pstats

  # View pstats with snakeviz:
  pip install snakeviz
  python -m snakeviz profile.pstats
        """,
    )

    parser.add_argument("--output", "-o", help="Output JSON file for the profiling report")

    parser.add_argument(
        "--export-pstats", "-p", help="Export cProfile data to pstats file (for snakeviz)"
    )

    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress verbose output")

    args = parser.parse_args()

    run_advanced_profiling(
        output_file=args.output, pstats_file=args.export_pstats, verbose=not args.quiet
    )


if __name__ == "__main__":
    main()
