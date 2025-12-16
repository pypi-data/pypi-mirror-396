#!/usr/bin/env python3
"""
Performance Benchmark Suite for FurlanSpellChecker.

This script provides micro-level benchmarks for measuring execution time
of critical operations. Results are saved to docs/benchmarks/ for historical
tracking across code changes.

Usage:
    python scripts/benchmark.py                    # Run all benchmarks
    python scripts/benchmark.py --quick            # Quick run (100 words)
    python scripts/benchmark.py --words 1000       # Custom word count
    python scripts/benchmark.py --output results   # Custom output name
    python scripts/benchmark.py --compare baseline # Compare with previous run

Results are saved as JSON with the following metrics:
- Total execution time
- Per-operation time (mean, median, p50, p95, p99)
- Throughput (operations/second)
- Memory usage (if available)
"""

import argparse
import json
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Add src to path for imports
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))


def get_test_words(count: int = 1000) -> list[str]:
    """
    Load test words from the comparison test suite.

    Falls back to a default set if the 10K file is not available.
    """
    test_words_file = (
        PROJECT_ROOT.parent / "CompareCOFImplementations" / "output" / "test_words_10k.txt"
    )

    words = []

    if test_words_file.exists():
        with open(test_words_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith("#"):
                    continue
                words.append(line)
                if len(words) >= count:
                    break

    if not words:
        # Fallback default words for testing
        words = [
            "furlan",
            "lenghe",
            "cjase",
            "aghe",
            "scuele",
            "parol",
            "frut",
            "femine",
            "om",
            "furlane",
            "cjasa",
            "preo",
            "lengha",
            "belo",
            "gnòf",
            "gnùf",
            "çucarut",
            "pôc",
            "lûs",
            "vêr",
            "l'aghe",
            "d'estât",
            "un'ore",
            "preon.",
            "xyzqwerty",
            "blablabla",
        ] * (count // 26 + 1)
        words = words[:count]

    return words


class BenchmarkTimer:
    """Context manager for timing operations."""

    def __init__(self):
        self.start_time: float = 0
        self.end_time: float = 0
        self.elapsed_ms: float = 0

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.end_time = time.perf_counter()
        self.elapsed_ms = (self.end_time - self.start_time) * 1000


def calculate_percentiles(times: list[float]) -> dict[str, float]:
    """Calculate statistical percentiles for timing data."""
    if not times:
        return {"p50": 0, "p75": 0, "p90": 0, "p95": 0, "p99": 0}

    sorted_times = sorted(times)
    n = len(sorted_times)

    def percentile(p: float) -> float:
        k = (n - 1) * p / 100
        f = int(k)
        c = f + 1 if f + 1 < n else f
        return (
            sorted_times[f] + (k - f) * (sorted_times[c] - sorted_times[f])
            if f != c
            else sorted_times[f]
        )

    return {
        "p50": round(percentile(50), 4),
        "p75": round(percentile(75), 4),
        "p90": round(percentile(90), 4),
        "p95": round(percentile(95), 4),
        "p99": round(percentile(99), 4),
    }


# Version of the benchmark format
BENCHMARK_VERSION = "1.0.0"


class Benchmark:
    """Main benchmark runner class."""

    def __init__(self, word_count: int = 1000, verbose: bool = True):
        self.word_count = word_count
        self.verbose = verbose
        self.results: dict[str, Any] = {
            "version": BENCHMARK_VERSION,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "word_count": word_count,
                "python_version": sys.version,
                "platform": sys.platform,
            },
            "benchmarks": {},
        }

        # Lazy-loaded components
        self._spell_checker = None
        self._dictionary = None
        self._text_processor = None
        self._suggestion_engine = None
        self._phonetic_algo = None
        self._db_manager = None

    def log(self, msg: str):
        """Print message if verbose mode is enabled."""
        if self.verbose:
            print(msg)

    def _init_components(self):
        """Initialize spell checker components (lazy loading)."""
        if self._spell_checker is not None:
            return

        self.log("Initializing spell checker components...")
        init_start = time.perf_counter()

        from furlan_spellchecker.config.schemas import FurlanSpellCheckerConfig
        from furlan_spellchecker.database import DatabaseManager
        from furlan_spellchecker.dictionary.dictionary import Dictionary
        from furlan_spellchecker.phonetic.furlan_phonetic import FurlanPhoneticAlgorithm
        from furlan_spellchecker.spellchecker.spell_checker import FurlanSpellChecker
        from furlan_spellchecker.spellchecker.suggestion_engine import SuggestionEngine
        from furlan_spellchecker.spellchecker.text_processor import TextProcessor

        self._dictionary = Dictionary()
        self._text_processor = TextProcessor()
        self._config = FurlanSpellCheckerConfig()
        self._db_manager = DatabaseManager(self._config)
        self._phonetic_algo = FurlanPhoneticAlgorithm()
        self._spell_checker = FurlanSpellChecker(
            self._dictionary, self._text_processor, self._config
        )
        self._suggestion_engine = SuggestionEngine(
            db_manager=self._db_manager, phonetic=self._phonetic_algo, max_suggestions=10
        )

        init_time = (time.perf_counter() - init_start) * 1000
        self.log(f"  Initialization completed in {init_time:.2f}ms")

        self.results["metadata"]["initialization_time_ms"] = round(init_time, 2)

    def benchmark_initialization(self) -> dict[str, Any]:
        """
        Benchmark: Component initialization time.

        Measures how long it takes to initialize all spell checker components
        from scratch (cold start scenario).
        """
        self.log("\n=== Benchmark: Initialization ===")

        times = []

        # Run multiple iterations to get stable measurement
        for i in range(3):
            # Force reimport by clearing cached modules
            modules_to_clear = [k for k in sys.modules.keys() if "furlan_spellchecker" in k]
            for mod in modules_to_clear:
                del sys.modules[mod]

            with BenchmarkTimer() as timer:
                from furlan_spellchecker.config.schemas import FurlanSpellCheckerConfig
                from furlan_spellchecker.dictionary.dictionary import Dictionary
                from furlan_spellchecker.spellchecker.spell_checker import FurlanSpellChecker
                from furlan_spellchecker.spellchecker.text_processor import TextProcessor

                dictionary = Dictionary()
                text_processor = TextProcessor()
                config = FurlanSpellCheckerConfig()
                FurlanSpellChecker(dictionary, text_processor, config)

            times.append(timer.elapsed_ms)
            self.log(f"  Iteration {i + 1}: {timer.elapsed_ms:.2f}ms")

        # Reset internal state
        self._spell_checker = None

        result = {
            "name": "initialization",
            "description": "Cold start initialization of all components",
            "iterations": len(times),
            "times_ms": times,
            "mean_ms": round(statistics.mean(times), 2),
            "stdev_ms": round(statistics.stdev(times), 2) if len(times) > 1 else 0,
            "min_ms": round(min(times), 2),
            "max_ms": round(max(times), 2),
        }

        self.log(f"  Mean: {result['mean_ms']:.2f}ms (±{result['stdev_ms']:.2f}ms)")
        return result

    def benchmark_database_loading(self) -> dict[str, Any]:
        """
        Benchmark: Database loading time.

        Measures time to load each database type (phonetic, frequency, etc.)
        """
        self.log("\n=== Benchmark: Database Loading ===")

        from furlan_spellchecker.config.schemas import FurlanSpellCheckerConfig
        from furlan_spellchecker.database import DatabaseManager

        config = FurlanSpellCheckerConfig()

        db_times = {}

        # Phonetic database
        with BenchmarkTimer() as timer:
            db_manager = DatabaseManager(config)
            _ = db_manager.phonetic_db.find_by_phonetic_hash("test")
        db_times["phonetic_db"] = timer.elapsed_ms
        self.log(f"  Phonetic DB: {timer.elapsed_ms:.2f}ms")

        # Frequency database
        with BenchmarkTimer() as timer:
            _ = db_manager.frequency_db.get_frequency("furlan")
        db_times["frequency_db"] = timer.elapsed_ms
        self.log(f"  Frequency DB: {timer.elapsed_ms:.2f}ms")

        # Elision database
        with BenchmarkTimer() as timer:
            _ = db_manager.elision_db.has_elision("aghe")
        db_times["elision_db"] = timer.elapsed_ms
        self.log(f"  Elision DB: {timer.elapsed_ms:.2f}ms")

        # Error database
        with BenchmarkTimer() as timer:
            _ = db_manager.error_db.get_correction("cjasa")
        db_times["error_db"] = timer.elapsed_ms
        self.log(f"  Error DB: {timer.elapsed_ms:.2f}ms")

        # Radix tree
        with BenchmarkTimer() as timer:
            _ = db_manager.radix_tree.has_word("furlan")
        db_times["radix_tree"] = timer.elapsed_ms
        self.log(f"  Radix Tree: {timer.elapsed_ms:.2f}ms")

        total = sum(db_times.values())

        result = {
            "name": "database_loading",
            "description": "Time to load each database type (first access)",
            "databases": db_times,
            "total_ms": round(total, 2),
        }

        self.log(f"  Total: {total:.2f}ms")
        return result

    def benchmark_phonetic_hash(self, words: list[str]) -> dict[str, Any]:
        """
        Benchmark: Phonetic hash calculation.

        Measures time to compute phonetic hashes for words.
        """
        self.log(f"\n=== Benchmark: Phonetic Hash ({len(words)} words) ===")

        from furlan_spellchecker.phonetic.furlan_phonetic import FurlanPhoneticAlgorithm

        phonetic = FurlanPhoneticAlgorithm()
        times = []

        # Warm-up
        for word in words[:10]:
            phonetic.get_phonetic_hashes_by_word(word)

        # Benchmark
        for word in words:
            with BenchmarkTimer() as timer:
                phonetic.get_phonetic_hashes_by_word(word)
            times.append(timer.elapsed_ms)

        percentiles = calculate_percentiles(times)
        total_time = sum(times)
        throughput = len(words) / (total_time / 1000) if total_time > 0 else 0

        result = {
            "name": "phonetic_hash",
            "description": "Phonetic hash calculation per word",
            "word_count": len(words),
            "total_ms": round(total_time, 2),
            "mean_ms": round(statistics.mean(times), 4),
            "stdev_ms": round(statistics.stdev(times), 4) if len(times) > 1 else 0,
            "min_ms": round(min(times), 4),
            "max_ms": round(max(times), 4),
            "percentiles_ms": percentiles,
            "throughput_ops_per_sec": round(throughput, 2),
        }

        self.log(f"  Total: {result['total_ms']:.2f}ms")
        self.log(f"  Mean: {result['mean_ms']:.4f}ms/word")
        self.log(f"  P95: {percentiles['p95']:.4f}ms")
        self.log(f"  Throughput: {throughput:.0f} words/sec")

        return result

    def benchmark_check_word(self, words: list[str]) -> dict[str, Any]:
        """
        Benchmark: Word checking (check_word_str).

        Measures time to check if words are spelled correctly.
        """
        self.log(f"\n=== Benchmark: Check Word ({len(words)} words) ===")

        self._init_components()

        import asyncio

        times = []

        # Warm-up
        for word in words[:10]:
            asyncio.run(self._spell_checker.check_word_str(word))

        # Benchmark
        for word in words:
            with BenchmarkTimer() as timer:
                asyncio.run(self._spell_checker.check_word_str(word))
            times.append(timer.elapsed_ms)

        percentiles = calculate_percentiles(times)
        total_time = sum(times)
        throughput = len(words) / (total_time / 1000) if total_time > 0 else 0

        result = {
            "name": "check_word",
            "description": "check_word_str() per word (includes asyncio.run overhead)",
            "word_count": len(words),
            "total_ms": round(total_time, 2),
            "mean_ms": round(statistics.mean(times), 4),
            "stdev_ms": round(statistics.stdev(times), 4) if len(times) > 1 else 0,
            "min_ms": round(min(times), 4),
            "max_ms": round(max(times), 4),
            "percentiles_ms": percentiles,
            "throughput_ops_per_sec": round(throughput, 2),
        }

        self.log(f"  Total: {result['total_ms']:.2f}ms")
        self.log(f"  Mean: {result['mean_ms']:.4f}ms/word")
        self.log(f"  P95: {percentiles['p95']:.4f}ms")
        self.log(f"  Throughput: {throughput:.0f} words/sec")

        return result

    def benchmark_check_word_sync(self, words: list[str]) -> dict[str, Any]:
        """
        Benchmark: Word checking (synchronous, no asyncio overhead).

        Creates ProcessedWord directly and calls check_word to measure
        actual checking time without asyncio.run() overhead.
        """
        self.log(f"\n=== Benchmark: Check Word Sync ({len(words)} words) ===")

        self._init_components()

        import asyncio

        from furlan_spellchecker.entities.processed_element import ProcessedWord

        times = []

        # Create a single event loop for all operations
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Warm-up
            for word in words[:10]:
                pw = ProcessedWord(word)
                loop.run_until_complete(self._spell_checker.check_word(pw))

            # Benchmark
            for word in words:
                pw = ProcessedWord(word)
                with BenchmarkTimer() as timer:
                    loop.run_until_complete(self._spell_checker.check_word(pw))
                times.append(timer.elapsed_ms)
        finally:
            loop.close()

        percentiles = calculate_percentiles(times)
        total_time = sum(times)
        throughput = len(words) / (total_time / 1000) if total_time > 0 else 0

        result = {
            "name": "check_word_sync",
            "description": "check_word() with shared event loop (reduced asyncio overhead)",
            "word_count": len(words),
            "total_ms": round(total_time, 2),
            "mean_ms": round(statistics.mean(times), 4),
            "stdev_ms": round(statistics.stdev(times), 4) if len(times) > 1 else 0,
            "min_ms": round(min(times), 4),
            "max_ms": round(max(times), 4),
            "percentiles_ms": percentiles,
            "throughput_ops_per_sec": round(throughput, 2),
        }

        self.log(f"  Total: {result['total_ms']:.2f}ms")
        self.log(f"  Mean: {result['mean_ms']:.4f}ms/word")
        self.log(f"  P95: {percentiles['p95']:.4f}ms")
        self.log(f"  Throughput: {throughput:.0f} words/sec")

        return result

    def benchmark_suggest(self, words: list[str]) -> dict[str, Any]:
        """
        Benchmark: Suggestion generation.

        Measures time to generate spelling suggestions for words.
        """
        self.log(f"\n=== Benchmark: Suggest ({len(words)} words) ===")

        self._init_components()

        times = []

        # Warm-up
        for word in words[:5]:
            self._suggestion_engine.suggest(word)

        # Benchmark
        for word in words:
            with BenchmarkTimer() as timer:
                self._suggestion_engine.suggest(word)
            times.append(timer.elapsed_ms)

        percentiles = calculate_percentiles(times)
        total_time = sum(times)
        throughput = len(words) / (total_time / 1000) if total_time > 0 else 0

        result = {
            "name": "suggest",
            "description": "SuggestionEngine.suggest() per word",
            "word_count": len(words),
            "total_ms": round(total_time, 2),
            "mean_ms": round(statistics.mean(times), 4),
            "stdev_ms": round(statistics.stdev(times), 4) if len(times) > 1 else 0,
            "min_ms": round(min(times), 4),
            "max_ms": round(max(times), 4),
            "percentiles_ms": percentiles,
            "throughput_ops_per_sec": round(throughput, 2),
        }

        self.log(f"  Total: {result['total_ms']:.2f}ms")
        self.log(f"  Mean: {result['mean_ms']:.4f}ms/word")
        self.log(f"  P95: {percentiles['p95']:.4f}ms")
        self.log(f"  Throughput: {throughput:.0f} words/sec")

        return result

    def benchmark_dictionary_lookup(self, words: list[str]) -> dict[str, Any]:
        """
        Benchmark: Dictionary lookup operations.

        Measures time for phonetic hash lookups in the dictionary.
        """
        self.log(f"\n=== Benchmark: Dictionary Lookup ({len(words)} words) ===")

        self._init_components()

        times = []

        # Warm-up
        for word in words[:10]:
            h1, h2 = self._phonetic_algo.get_phonetic_hashes_by_word(word)
            self._db_manager.phonetic_db.find_by_phonetic_hash(h1)

        # Benchmark
        for word in words:
            h1, h2 = self._phonetic_algo.get_phonetic_hashes_by_word(word)
            with BenchmarkTimer() as timer:
                self._db_manager.phonetic_db.find_by_phonetic_hash(h1)
                if h1 != h2:
                    self._db_manager.phonetic_db.find_by_phonetic_hash(h2)
            times.append(timer.elapsed_ms)

        percentiles = calculate_percentiles(times)
        total_time = sum(times)
        throughput = len(words) / (total_time / 1000) if total_time > 0 else 0

        result = {
            "name": "dictionary_lookup",
            "description": "Phonetic hash lookup in dictionary",
            "word_count": len(words),
            "total_ms": round(total_time, 2),
            "mean_ms": round(statistics.mean(times), 4),
            "stdev_ms": round(statistics.stdev(times), 4) if len(times) > 1 else 0,
            "min_ms": round(min(times), 4),
            "max_ms": round(max(times), 4),
            "percentiles_ms": percentiles,
            "throughput_ops_per_sec": round(throughput, 2),
        }

        self.log(f"  Total: {result['total_ms']:.2f}ms")
        self.log(f"  Mean: {result['mean_ms']:.4f}ms/word")
        self.log(f"  P95: {percentiles['p95']:.4f}ms")
        self.log(f"  Throughput: {throughput:.0f} words/sec")

        return result

    def benchmark_radix_tree(self, words: list[str]) -> dict[str, Any]:
        """
        Benchmark: RadixTree edit distance 1 lookup.

        Measures time to find words within edit distance 1.
        """
        self.log(f"\n=== Benchmark: RadixTree ED1 ({len(words)} words) ===")

        self._init_components()

        times = []

        # Warm-up
        for word in words[:10]:
            self._db_manager.radix_tree.get_words_ed1(word.lower())

        # Benchmark
        for word in words:
            with BenchmarkTimer() as timer:
                self._db_manager.radix_tree.get_words_ed1(word.lower())
            times.append(timer.elapsed_ms)

        percentiles = calculate_percentiles(times)
        total_time = sum(times)
        throughput = len(words) / (total_time / 1000) if total_time > 0 else 0

        result = {
            "name": "radix_tree_ed1",
            "description": "RadixTree get_words_ed1() per word",
            "word_count": len(words),
            "total_ms": round(total_time, 2),
            "mean_ms": round(statistics.mean(times), 4),
            "stdev_ms": round(statistics.stdev(times), 4) if len(times) > 1 else 0,
            "min_ms": round(min(times), 4),
            "max_ms": round(max(times), 4),
            "percentiles_ms": percentiles,
            "throughput_ops_per_sec": round(throughput, 2),
        }

        self.log(f"  Total: {result['total_ms']:.2f}ms")
        self.log(f"  Mean: {result['mean_ms']:.4f}ms/word")
        self.log(f"  P95: {percentiles['p95']:.4f}ms")
        self.log(f"  Throughput: {throughput:.0f} words/sec")

        return result

    def benchmark_frequency_lookup(self, words: list[str]) -> dict[str, Any]:
        """
        Benchmark: Frequency database lookup.

        Measures time to look up word frequencies.
        """
        self.log(f"\n=== Benchmark: Frequency Lookup ({len(words)} words) ===")

        self._init_components()

        times = []

        # Warm-up
        for word in words[:10]:
            self._db_manager.frequency_db.get_frequency(word)

        # Benchmark
        for word in words:
            with BenchmarkTimer() as timer:
                self._db_manager.frequency_db.get_frequency(word)
            times.append(timer.elapsed_ms)

        percentiles = calculate_percentiles(times)
        total_time = sum(times)
        throughput = len(words) / (total_time / 1000) if total_time > 0 else 0

        result = {
            "name": "frequency_lookup",
            "description": "FrequencyDatabase.get_frequency() per word",
            "word_count": len(words),
            "total_ms": round(total_time, 2),
            "mean_ms": round(statistics.mean(times), 4),
            "stdev_ms": round(statistics.stdev(times), 4) if len(times) > 1 else 0,
            "min_ms": round(min(times), 4),
            "max_ms": round(max(times), 4),
            "percentiles_ms": percentiles,
            "throughput_ops_per_sec": round(throughput, 2),
        }

        self.log(f"  Total: {result['total_ms']:.2f}ms")
        self.log(f"  Mean: {result['mean_ms']:.4f}ms/word")
        self.log(f"  P95: {percentiles['p95']:.4f}ms")
        self.log(f"  Throughput: {throughput:.0f} words/sec")

        return result

    def benchmark_levenshtein(self, words: list[str]) -> dict[str, Any]:
        """
        Benchmark: Levenshtein distance calculation.

        Measures time to compute edit distance between word pairs.
        """
        self.log(f"\n=== Benchmark: Levenshtein ({len(words)} pairs) ===")

        from furlan_spellchecker.phonetic.furlan_phonetic import FurlanPhoneticAlgorithm

        phonetic = FurlanPhoneticAlgorithm()

        # Create word pairs for comparison
        pairs = [(words[i], words[(i + 1) % len(words)]) for i in range(len(words))]

        times = []

        # Warm-up
        for w1, w2 in pairs[:10]:
            phonetic.levenshtein(w1, w2)

        # Benchmark
        for w1, w2 in pairs:
            with BenchmarkTimer() as timer:
                phonetic.levenshtein(w1, w2)
            times.append(timer.elapsed_ms)

        percentiles = calculate_percentiles(times)
        total_time = sum(times)
        throughput = len(pairs) / (total_time / 1000) if total_time > 0 else 0

        result = {
            "name": "levenshtein",
            "description": "Levenshtein distance calculation per word pair",
            "pair_count": len(pairs),
            "total_ms": round(total_time, 2),
            "mean_ms": round(statistics.mean(times), 4),
            "stdev_ms": round(statistics.stdev(times), 4) if len(times) > 1 else 0,
            "min_ms": round(min(times), 4),
            "max_ms": round(max(times), 4),
            "percentiles_ms": percentiles,
            "throughput_ops_per_sec": round(throughput, 2),
        }

        self.log(f"  Total: {result['total_ms']:.2f}ms")
        self.log(f"  Mean: {result['mean_ms']:.4f}ms/pair")
        self.log(f"  P95: {percentiles['p95']:.4f}ms")
        self.log(f"  Throughput: {throughput:.0f} pairs/sec")

        return result

    def run_all(self) -> dict[str, Any]:
        """Run all benchmarks and return results."""
        self.log("FurlanSpellChecker Performance Benchmark")
        self.log("========================================")
        self.log(f"Word count: {self.word_count}")
        self.log(f"Timestamp: {self.results['timestamp']}")

        words = get_test_words(self.word_count)
        self.log(f"Loaded {len(words)} test words")

        # Run benchmarks
        self.results["benchmarks"]["initialization"] = self.benchmark_initialization()
        self.results["benchmarks"]["database_loading"] = self.benchmark_database_loading()
        self.results["benchmarks"]["phonetic_hash"] = self.benchmark_phonetic_hash(words)
        self.results["benchmarks"]["dictionary_lookup"] = self.benchmark_dictionary_lookup(words)
        self.results["benchmarks"]["frequency_lookup"] = self.benchmark_frequency_lookup(words)
        self.results["benchmarks"]["radix_tree_ed1"] = self.benchmark_radix_tree(words)
        self.results["benchmarks"]["levenshtein"] = self.benchmark_levenshtein(words)
        self.results["benchmarks"]["check_word"] = self.benchmark_check_word(words)
        self.results["benchmarks"]["check_word_sync"] = self.benchmark_check_word_sync(words)
        self.results["benchmarks"]["suggest"] = self.benchmark_suggest(
            words[: min(100, len(words))]
        )  # Limit suggest due to slowness

        # Summary
        self.log("\n" + "=" * 50)
        self.log("SUMMARY")
        self.log("=" * 50)

        for name, bench in self.results["benchmarks"].items():
            if "mean_ms" in bench:
                self.log(
                    f"  {name}: {bench['mean_ms']:.4f}ms/op, {bench.get('throughput_ops_per_sec', 'N/A')} ops/sec"
                )
            elif "total_ms" in bench:
                self.log(f"  {name}: {bench['total_ms']:.2f}ms total")

        return self.results

    def save_results(self, output_name: str | None = None, is_baseline: bool = False) -> Path:
        """Save benchmark results to JSON file.

        Args:
            output_name: Custom output filename (without .json extension)
            is_baseline: If True, use _baseline suffix instead of _benchmark
        """
        benchmarks_dir = PROJECT_ROOT / "docs" / "benchmarks"
        benchmarks_dir.mkdir(parents=True, exist_ok=True)

        if output_name:
            filename = f"{output_name}.json"
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            suffix = "baseline" if is_baseline else "benchmark"
            filename = f"{timestamp}_{suffix}.json"

        output_path = benchmarks_dir / filename

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        self.log(f"\nResults saved to: {output_path}")
        return output_path


def compare_benchmarks(file1: Path, file2: Path) -> None:
    """Compare two benchmark result files and show differences."""
    with open(file1) as f:
        results1 = json.load(f)
    with open(file2) as f:
        results2 = json.load(f)

    print("\nBenchmark Comparison")
    print("====================")
    print(f"Baseline: {file1.name}")
    print(f"Current:  {file2.name}")
    print()

    benchmarks1 = results1.get("benchmarks", {})
    benchmarks2 = results2.get("benchmarks", {})

    all_keys = set(benchmarks1.keys()) | set(benchmarks2.keys())

    print(f"{'Benchmark':<25} {'Baseline':>12} {'Current':>12} {'Delta':>12} {'Change':>10}")
    print("-" * 75)

    for key in sorted(all_keys):
        b1 = benchmarks1.get(key, {})
        b2 = benchmarks2.get(key, {})

        # Get mean_ms or total_ms
        v1 = b1.get("mean_ms") or b1.get("total_ms", 0)
        v2 = b2.get("mean_ms") or b2.get("total_ms", 0)

        if v1 and v2:
            delta = v2 - v1
            change_pct = ((v2 - v1) / v1) * 100 if v1 > 0 else 0

            # Color coding: green for improvement, red for regression
            if change_pct < -5:
                indicator = "✓ FASTER"
            elif change_pct > 5:
                indicator = "✗ SLOWER"
            else:
                indicator = "≈ SAME"

            print(
                f"{key:<25} {v1:>12.4f} {v2:>12.4f} {delta:>+12.4f} {change_pct:>+9.1f}%  {indicator}"
            )
        else:
            print(f"{key:<25} {'N/A':>12} {'N/A':>12} {'N/A':>12} {'N/A':>10}")


def main():
    parser = argparse.ArgumentParser(description="FurlanSpellChecker Performance Benchmark Suite")
    parser.add_argument(
        "--words",
        "-w",
        type=int,
        default=1000,
        help="Number of words to use for benchmarking (default: 1000)",
    )
    parser.add_argument("--quick", "-q", action="store_true", help="Quick run with 100 words")
    parser.add_argument(
        "--output", "-o", type=str, default=None, help="Output filename (without .json extension)"
    )
    parser.add_argument(
        "--compare", "-c", type=str, default=None, help="Compare with a previous benchmark file"
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress verbose output")
    parser.add_argument(
        "--baseline",
        action="store_true",
        help="Mark this run as a baseline (uses _baseline suffix in filename)",
    )

    args = parser.parse_args()

    word_count = 100 if args.quick else args.words

    benchmark = Benchmark(word_count=word_count, verbose=not args.quiet)
    benchmark.run_all()
    output_path = benchmark.save_results(args.output, is_baseline=args.baseline)

    if args.compare:
        compare_path = PROJECT_ROOT / "docs" / "benchmarks" / args.compare
        if not compare_path.suffix:
            compare_path = compare_path.with_suffix(".json")

        if compare_path.exists():
            compare_benchmarks(compare_path, output_path)
        else:
            print(f"Warning: Comparison file not found: {compare_path}")


if __name__ == "__main__":
    main()
