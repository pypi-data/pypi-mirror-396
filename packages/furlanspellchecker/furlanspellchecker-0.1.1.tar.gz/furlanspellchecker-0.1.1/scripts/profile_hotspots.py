#!/usr/bin/env python3
"""
Profiling script to identify performance hotspots in FurlanSpellChecker.

This script profiles check_word and suggest operations to find the real
bottlenecks using cProfile, excluding database loading time.

Usage:
    python scripts/profile_hotspots.py
    python -m cProfile -s cumtime scripts/profile_hotspots.py
"""

import cProfile
import io
import pstats
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from furlan_spellchecker import FurlanSpellChecker
from furlan_spellchecker.config import FurlanSpellCheckerConfig
from furlan_spellchecker.dictionary import Dictionary
from furlan_spellchecker.spellchecker.text_processor import TextProcessor


def create_spellchecker() -> FurlanSpellChecker:
    """Create and initialize FurlanSpellChecker instance."""
    config = FurlanSpellCheckerConfig()
    dictionary = Dictionary()
    text_processor = TextProcessor()
    return FurlanSpellChecker(dictionary=dictionary, text_processor=text_processor, config=config)


# Test words representing different scenarios
TEST_WORDS = {
    "valid_short": ["aghe", "bon", "alt", "om", "an"],
    "valid_long": ["marilenghe", "furlanofons", "agricolture", "universitât"],
    "misspelled": ["cjasa", "marilengha", "agriculure", "univrsitat"],
    "unknown": ["xyz123", "asdfghjkl", "qwerty", "notaword"],
}

# Number of iterations for each operation
ITERATIONS = 100


def warmup(checker: FurlanSpellChecker) -> None:
    """Warm up the checker to ensure caches are populated."""
    print("Warming up...")
    for _category, words in TEST_WORDS.items():
        for word in words:
            checker.check_word_str_sync(word)
            checker.suggest(word)
    print("Warmup complete.\n")


def profile_check_word(checker: FurlanSpellChecker) -> None:
    """Profile check_word operations."""
    all_words = [w for words in TEST_WORDS.values() for w in words]
    for _ in range(ITERATIONS):
        for word in all_words:
            checker.check_word_str_sync(word)


def profile_suggest(checker: FurlanSpellChecker) -> None:
    """Profile suggest operations."""
    all_words = [w for words in TEST_WORDS.values() for w in words]
    for _ in range(ITERATIONS):
        for word in all_words:
            checker.suggest(word)


def profile_mixed(checker: FurlanSpellChecker) -> None:
    """Profile realistic mixed workload (check then suggest if invalid)."""
    all_words = [w for words in TEST_WORDS.values() for w in words]
    for _ in range(ITERATIONS):
        for word in all_words:
            is_valid = checker.check_word_str_sync(word)
            if not is_valid:
                checker.suggest(word)


def run_profiling():
    """Run profiling and print results."""

    # Load checker (excluded from profiling)
    print("=" * 70)
    print("FurlanSpellChecker Profiling")
    print("=" * 70)
    print("\nLoading spell checker (not profiled)...")

    load_start = time.perf_counter()
    checker = create_spellchecker()
    load_time = time.perf_counter() - load_start
    print(f"Load time: {load_time * 1000:.2f}ms\n")

    # Warmup
    warmup(checker)

    # Calculate total operations
    num_words = sum(len(words) for words in TEST_WORDS.values())
    total_ops = num_words * ITERATIONS

    print("Test configuration:")
    print(f"  - Words per category: {[len(w) for w in TEST_WORDS.values()]}")
    print(f"  - Total unique words: {num_words}")
    print(f"  - Iterations: {ITERATIONS}")
    print(f"  - Total operations per test: {total_ops}")
    print()

    # Profile check_word
    print("-" * 70)
    print("Profiling check_word()")
    print("-" * 70)

    profiler = cProfile.Profile()
    profiler.enable()

    start = time.perf_counter()
    profile_check_word(checker)
    elapsed = time.perf_counter() - start

    profiler.disable()

    print(f"\nTotal time: {elapsed * 1000:.2f}ms for {total_ops} calls")
    print(f"Average: {elapsed / total_ops * 1000:.4f}ms per call")
    print("\nTop 15 functions by cumulative time:")

    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats("cumtime")
    stats.print_stats(15)
    print(stream.getvalue())

    # Profile suggest
    print("-" * 70)
    print("Profiling suggest()")
    print("-" * 70)

    profiler = cProfile.Profile()
    profiler.enable()

    start = time.perf_counter()
    profile_suggest(checker)
    elapsed = time.perf_counter() - start

    profiler.disable()

    print(f"\nTotal time: {elapsed * 1000:.2f}ms for {total_ops} calls")
    print(f"Average: {elapsed / total_ops * 1000:.4f}ms per call")
    print("\nTop 15 functions by cumulative time:")

    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats("cumtime")
    stats.print_stats(15)
    print(stream.getvalue())

    # Profile mixed workload
    print("-" * 70)
    print("Profiling mixed workload (check + suggest if invalid)")
    print("-" * 70)

    profiler = cProfile.Profile()
    profiler.enable()

    start = time.perf_counter()
    profile_mixed(checker)
    elapsed = time.perf_counter() - start

    profiler.disable()

    print(f"\nTotal time: {elapsed * 1000:.2f}ms")
    print("\nTop 20 functions by cumulative time:")

    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats("cumtime")
    stats.print_stats(20)
    print(stream.getvalue())

    # Summary by module
    print("=" * 70)
    print("Summary: Time by module (from mixed workload)")
    print("=" * 70)

    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats("cumtime")
    stats.print_stats(50)
    output = stream.getvalue()

    # Parse and aggregate by module
    module_times = {}
    for line in output.split("\n"):
        if "furlan_spellchecker" in line:
            parts = line.strip().split()
            if len(parts) >= 6:
                try:
                    cumtime = float(parts[3])
                    func_info = parts[5] if len(parts) > 5 else ""
                    if "(" in func_info:
                        module = func_info.split("(")[0]
                        if module not in module_times:
                            module_times[module] = 0
                        module_times[module] += cumtime
                except (ValueError, IndexError):
                    pass

    if module_times:
        print("\nAggregated time by file:")
        for module, time_val in sorted(module_times.items(), key=lambda x: -x[1]):
            print(f"  {time_val:.4f}s  {module}")

    print("\n" + "=" * 70)
    print("Profiling complete!")
    print("=" * 70)


if __name__ == "__main__":
    run_profiling()
