#!/usr/bin/env python3
"""
Benchmark Comparison Tool for FurlanSpellChecker

Compares two benchmark JSON files and shows performance delta.
Useful for tracking performance changes over time and detecting regressions.

Usage:
    python compare_benchmarks.py baseline.json current.json
    python compare_benchmarks.py --latest  # Compare two most recent benchmarks
    python compare_benchmarks.py --vs-baseline  # Compare latest vs baseline
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any


# ANSI color codes for terminal output
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    @classmethod
    def disable(cls):
        """Disable colors for non-terminal output"""
        cls.GREEN = cls.RED = cls.YELLOW = cls.BLUE = cls.BOLD = cls.RESET = ""


def load_benchmark(file_path: Path) -> dict[str, Any]:
    """Load benchmark results from JSON file"""
    with open(file_path, encoding="utf-8") as f:
        return json.load(f)


def find_benchmarks_dir() -> Path:
    """Find the benchmarks directory"""
    script_dir = Path(__file__).parent
    benchmarks_dir = script_dir.parent / "docs" / "benchmarks"
    if not benchmarks_dir.exists():
        raise FileNotFoundError(f"Benchmarks directory not found: {benchmarks_dir}")
    return benchmarks_dir


def get_benchmark_files(benchmarks_dir: Path) -> list[Path]:
    """Get all benchmark JSON files sorted by date (newest first)"""
    files = list(benchmarks_dir.glob("*.json"))
    files = [f for f in files if f.name != "README.md"]

    # Sort by modification time, newest first
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return files


def get_baseline_file(benchmarks_dir: Path) -> Path | None:
    """Get the baseline benchmark file"""
    baseline = benchmarks_dir / "baseline.json"
    if baseline.exists():
        return baseline

    # Look for files with 'baseline' in name
    for f in benchmarks_dir.glob("*baseline*.json"):
        return f

    return None


def calculate_delta(old_val: float, new_val: float) -> tuple[float, str]:
    """
    Calculate percentage delta between old and new values.
    Returns (delta_percent, direction) where direction indicates improvement/regression.

    For timing metrics: negative delta = improvement (faster)
    For throughput metrics: positive delta = improvement (more ops/sec)
    """
    if old_val == 0:
        return 0.0, "unchanged"

    delta = ((new_val - old_val) / old_val) * 100
    return delta, "changed"


def format_delta(delta: float, metric_type: str) -> str:
    """
    Format delta with color based on improvement/regression.

    Args:
        delta: Percentage change
        metric_type: 'time' (lower is better) or 'throughput' (higher is better)
    """
    if abs(delta) < 1.0:
        return f"{Colors.BLUE}~{delta:+.1f}%{Colors.RESET}"

    # For time: negative = faster = improvement
    # For throughput: positive = more ops = improvement
    is_improvement = (metric_type == "time" and delta < 0) or (
        metric_type == "throughput" and delta > 0
    )

    if is_improvement:
        return f"{Colors.GREEN}{delta:+.1f}%{Colors.RESET}"
    else:
        return f"{Colors.RED}{delta:+.1f}%{Colors.RESET}"


def compare_benchmarks(old_data: dict[str, Any], new_data: dict[str, Any]) -> dict[str, Any]:
    """
    Compare two benchmark results and return delta analysis.
    """
    comparison = {
        "old_timestamp": old_data.get("timestamp", "unknown"),
        "new_timestamp": new_data.get("timestamp", "unknown"),
        "old_version": old_data.get("version", "unknown"),
        "new_version": new_data.get("version", "unknown"),
        "benchmarks": {},
    }

    old_benchmarks = old_data.get("benchmarks", {})
    new_benchmarks = new_data.get("benchmarks", {})

    # Get all benchmark names from both files
    all_names = set(old_benchmarks.keys()) | set(new_benchmarks.keys())

    for name in sorted(all_names):
        old_bench = old_benchmarks.get(name)
        new_bench = new_benchmarks.get(name)

        if old_bench is None:
            comparison["benchmarks"][name] = {"status": "new", "new": new_bench}
        elif new_bench is None:
            comparison["benchmarks"][name] = {"status": "removed", "old": old_bench}
        else:
            bench_comparison = {"status": "compared", "old": {}, "new": {}, "delta": {}}

            # Compare mean time
            if "mean_ms" in old_bench and "mean_ms" in new_bench:
                delta, _ = calculate_delta(old_bench["mean_ms"], new_bench["mean_ms"])
                bench_comparison["old"]["mean_ms"] = old_bench["mean_ms"]
                bench_comparison["new"]["mean_ms"] = new_bench["mean_ms"]
                bench_comparison["delta"]["mean_ms"] = delta

            # Compare throughput
            if "ops_per_sec" in old_bench and "ops_per_sec" in new_bench:
                delta, _ = calculate_delta(old_bench["ops_per_sec"], new_bench["ops_per_sec"])
                bench_comparison["old"]["ops_per_sec"] = old_bench["ops_per_sec"]
                bench_comparison["new"]["ops_per_sec"] = new_bench["ops_per_sec"]
                bench_comparison["delta"]["ops_per_sec"] = delta

            # Compare p95
            if "p95_ms" in old_bench and "p95_ms" in new_bench:
                delta, _ = calculate_delta(old_bench["p95_ms"], new_bench["p95_ms"])
                bench_comparison["old"]["p95_ms"] = old_bench["p95_ms"]
                bench_comparison["new"]["p95_ms"] = new_bench["p95_ms"]
                bench_comparison["delta"]["p95_ms"] = delta

            comparison["benchmarks"][name] = bench_comparison

    return comparison


def print_comparison_report(comparison: dict[str, Any], format: str = "terminal"):
    """Print formatted comparison report"""
    if format == "json":
        print(json.dumps(comparison, indent=2))
        return

    print(f"\n{Colors.BOLD}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}BENCHMARK COMPARISON REPORT{Colors.RESET}")
    print(f"{'=' * 70}")
    print(
        f"\n{Colors.BLUE}Old:{Colors.RESET} {comparison['old_timestamp']} (v{comparison['old_version']})"
    )
    print(
        f"{Colors.BLUE}New:{Colors.RESET} {comparison['new_timestamp']} (v{comparison['new_version']})"
    )

    # Summary counts
    improved = 0
    regressed = 0
    unchanged = 0
    new_benchmarks = 0
    removed_benchmarks = 0

    benchmarks = comparison["benchmarks"]

    print(f"\n{Colors.BOLD}DETAILED RESULTS{Colors.RESET}")
    print("-" * 70)

    # Print header
    print(f"{'Benchmark':<25} {'Metric':<12} {'Old':>12} {'New':>12} {'Delta':>12}")
    print("-" * 70)

    for name, bench in sorted(benchmarks.items()):
        if bench["status"] == "new":
            print(f"{name:<25} {Colors.GREEN}[NEW]{Colors.RESET}")
            new_benchmarks += 1
            continue

        if bench["status"] == "removed":
            print(f"{name:<25} {Colors.YELLOW}[REMOVED]{Colors.RESET}")
            removed_benchmarks += 1
            continue

        # Print benchmark comparisons
        first_line = True
        for metric in ["mean_ms", "ops_per_sec", "p95_ms"]:
            if metric not in bench["delta"]:
                continue

            old_val = bench["old"][metric]
            new_val = bench["new"][metric]
            delta = bench["delta"][metric]

            # Determine metric type for coloring
            metric_type = "throughput" if metric == "ops_per_sec" else "time"

            # Track improvements/regressions (using 5% threshold)
            if abs(delta) > 5:
                if (metric_type == "time" and delta < 0) or (
                    metric_type == "throughput" and delta > 0
                ):
                    improved += 1
                else:
                    regressed += 1
            else:
                unchanged += 1

            bench_name = name if first_line else ""
            metric_name = metric.replace("_", " ")
            delta_str = format_delta(delta, metric_type)

            if metric == "ops_per_sec":
                print(
                    f"{bench_name:<25} {metric_name:<12} {old_val:>12,.0f} {new_val:>12,.0f} {delta_str:>20}"
                )
            else:
                print(
                    f"{bench_name:<25} {metric_name:<12} {old_val:>12.4f} {new_val:>12.4f} {delta_str:>20}"
                )

            first_line = False

        print()  # Empty line between benchmarks

    # Summary
    print(f"\n{Colors.BOLD}SUMMARY{Colors.RESET}")
    print("-" * 70)

    total_metrics = improved + regressed + unchanged
    if total_metrics > 0:
        print(f"  {Colors.GREEN}Improved:{Colors.RESET}  {improved} metrics (>5% faster/better)")
        print(f"  {Colors.RED}Regressed:{Colors.RESET} {regressed} metrics (>5% slower/worse)")
        print(f"  {Colors.BLUE}Unchanged:{Colors.RESET} {unchanged} metrics (<5% change)")

    if new_benchmarks:
        print(f"  New benchmarks: {new_benchmarks}")
    if removed_benchmarks:
        print(f"  Removed benchmarks: {removed_benchmarks}")

    # Overall assessment
    print(f"\n{Colors.BOLD}ASSESSMENT:{Colors.RESET}", end=" ")
    if regressed > improved:
        print(f"{Colors.RED}⚠️  Performance regression detected!{Colors.RESET}")
    elif improved > regressed:
        print(f"{Colors.GREEN}✓ Performance improvement!{Colors.RESET}")
    else:
        print(f"{Colors.BLUE}→ No significant change{Colors.RESET}")

    print()


def save_comparison(comparison: dict[str, Any], output_path: Path):
    """Save comparison results to JSON file"""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2)
    print(f"Comparison saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Compare benchmark results for FurlanSpellChecker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Compare two specific files
    python compare_benchmarks.py old.json new.json

    # Compare two most recent benchmarks
    python compare_benchmarks.py --latest

    # Compare latest benchmark vs baseline
    python compare_benchmarks.py --vs-baseline

    # Output as JSON
    python compare_benchmarks.py --latest --format json

    # Save comparison to file
    python compare_benchmarks.py --latest --output comparison.json
""",
    )

    parser.add_argument("old_file", nargs="?", help="Path to old benchmark JSON file")
    parser.add_argument("new_file", nargs="?", help="Path to new benchmark JSON file")
    parser.add_argument("--latest", action="store_true", help="Compare two most recent benchmarks")
    parser.add_argument(
        "--vs-baseline", action="store_true", help="Compare latest benchmark against baseline"
    )
    parser.add_argument(
        "--format",
        choices=["terminal", "json"],
        default="terminal",
        help="Output format (default: terminal)",
    )
    parser.add_argument("--output", "-o", type=Path, help="Save comparison to JSON file")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    parser.add_argument(
        "--threshold",
        type=float,
        default=5.0,
        help="Percentage threshold for significance (default: 5.0)",
    )

    args = parser.parse_args()

    if args.no_color or args.format == "json":
        Colors.disable()

    try:
        benchmarks_dir = find_benchmarks_dir()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Determine which files to compare
    if args.latest:
        files = get_benchmark_files(benchmarks_dir)
        if len(files) < 2:
            print("Error: Need at least 2 benchmark files for --latest comparison", file=sys.stderr)
            return 1
        new_file = files[0]
        old_file = files[1]

    elif args.vs_baseline:
        baseline = get_baseline_file(benchmarks_dir)
        if baseline is None:
            print("Error: No baseline file found in benchmarks directory", file=sys.stderr)
            return 1
        files = get_benchmark_files(benchmarks_dir)
        # Get most recent non-baseline file
        latest = None
        for f in files:
            if "baseline" not in f.name.lower():
                latest = f
                break
        if latest is None:
            print("Error: No non-baseline benchmark files found", file=sys.stderr)
            return 1
        old_file = baseline
        new_file = latest

    elif args.old_file and args.new_file:
        old_file = Path(args.old_file)
        new_file = Path(args.new_file)

        if not old_file.exists():
            print(f"Error: File not found: {old_file}", file=sys.stderr)
            return 1
        if not new_file.exists():
            print(f"Error: File not found: {new_file}", file=sys.stderr)
            return 1
    else:
        parser.print_help()
        return 1

    # Load and compare
    try:
        old_data = load_benchmark(old_file)
        new_data = load_benchmark(new_file)
    except Exception as e:
        print(f"Error loading benchmark files: {e}", file=sys.stderr)
        return 1

    print(f"Comparing: {old_file.name} → {new_file.name}")

    comparison = compare_benchmarks(old_data, new_data)

    # Output
    print_comparison_report(comparison, args.format)

    if args.output:
        save_comparison(comparison, args.output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
