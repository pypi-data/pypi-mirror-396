#!/usr/bin/env python3
"""
Convert TSV exports from COF Perl to SQLite format.

This script does NOT require bsddb3 - it reads TSV files exported by Perl.

Usage:
    1. First run the Perl export script:
       cd COF && perl util/export_databases_to_tsv.pl

    2. Then run this Python script:
       python scripts/convert_tsv_to_sqlite.py

Source: data/databases/tsv_export/*.tsv
Output: data/databases/*.sqlite
"""

import sqlite3
import sys
from pathlib import Path


def unescape_tsv(value: str) -> str:
    """Unescape TSV-escaped characters."""
    return value.replace("\\t", "\t").replace("\\n", "\n")


def convert_phonetic(source: Path, dest: Path) -> int:
    """Convert words.tsv to words.sqlite."""
    print(f"Converting phonetic: {source} -> {dest}")

    conn = sqlite3.connect(dest)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS phonetic (
            hash TEXT PRIMARY KEY,
            words TEXT NOT NULL
        )
    """
    )

    count = 0
    with open(source, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if "\t" not in line:
                continue
            parts = line.split("\t", 1)
            if len(parts) != 2:
                continue
            hash_str = unescape_tsv(parts[0])
            words_str = unescape_tsv(parts[1])
            conn.execute(
                "INSERT OR REPLACE INTO phonetic (hash, words) VALUES (?, ?)",
                (hash_str, words_str),
            )
            count += 1
            if count % 100000 == 0:
                print(f"  Processed {count:,} entries...")
                conn.commit()

    conn.commit()
    conn.execute("CREATE INDEX IF NOT EXISTS idx_hash ON phonetic(hash)")
    conn.close()

    print(f"  Done: {count:,} entries")
    return count


def convert_frequency(source: Path, dest: Path) -> int:
    """Convert frequencies.tsv to frequencies.sqlite."""
    print(f"Converting frequency: {source} -> {dest}")

    conn = sqlite3.connect(dest)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS frequencies (
            word TEXT PRIMARY KEY,
            frequency INTEGER NOT NULL
        )
    """
    )

    count = 0
    with open(source, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if "\t" not in line:
                continue
            parts = line.split("\t", 1)
            if len(parts) != 2:
                continue
            word = unescape_tsv(parts[0])
            freq = int(parts[1])
            conn.execute(
                "INSERT OR REPLACE INTO frequencies (word, frequency) VALUES (?, ?)",
                (word, freq),
            )
            count += 1

    conn.commit()
    conn.execute("CREATE INDEX IF NOT EXISTS idx_word ON frequencies(word)")
    conn.close()

    print(f"  Done: {count:,} entries")
    return count


def convert_errors(source: Path, dest: Path) -> int:
    """Convert errors.tsv to errors.sqlite."""
    print(f"Converting errors: {source} -> {dest}")

    conn = sqlite3.connect(dest)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS errors (
            error TEXT PRIMARY KEY,
            correction TEXT NOT NULL
        )
    """
    )

    count = 0
    with open(source, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if "\t" not in line:
                continue
            parts = line.split("\t", 1)
            if len(parts) != 2:
                continue
            error = unescape_tsv(parts[0])
            correction = unescape_tsv(parts[1])
            conn.execute(
                "INSERT OR REPLACE INTO errors (error, correction) VALUES (?, ?)",
                (error, correction),
            )
            count += 1

    conn.commit()
    conn.close()

    print(f"  Done: {count:,} entries")
    return count


def convert_elisions(source: Path, dest: Path) -> int:
    """Convert elisions.tsv to elisions.sqlite."""
    print(f"Converting elisions: {source} -> {dest}")

    conn = sqlite3.connect(dest)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS elisions (
            word TEXT PRIMARY KEY
        )
    """
    )

    count = 0
    with open(source, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if "\t" not in line:
                continue
            parts = line.split("\t", 1)
            word = unescape_tsv(parts[0])
            conn.execute(
                "INSERT OR REPLACE INTO elisions (word) VALUES (?)",
                (word,),
            )
            count += 1

    conn.commit()
    conn.close()

    print(f"  Done: {count:,} entries")
    return count


def main() -> None:
    base_dir = Path(__file__).parent.parent
    source_dir = base_dir / "data" / "databases" / "tsv_export"
    dest_dir = base_dir / "data" / "databases"

    if not source_dir.exists():
        print(f"ERROR: Source directory not found: {source_dir}")
        print("\nYou need to export from COF first:")
        print("  cd COF && perl util/export_databases_to_tsv.pl")
        sys.exit(1)

    dest_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("TSV -> SQLite Conversion (no bsddb3 required)")
    print("=" * 60)

    results = {}

    results["phonetic"] = convert_phonetic(
        source_dir / "words.tsv",
        dest_dir / "words.sqlite",
    )

    results["frequency"] = convert_frequency(
        source_dir / "frequencies.tsv",
        dest_dir / "frequencies.sqlite",
    )

    results["errors"] = convert_errors(
        source_dir / "errors.tsv",
        dest_dir / "errors.sqlite",
    )

    results["elisions"] = convert_elisions(
        source_dir / "elisions.tsv",
        dest_dir / "elisions.sqlite",
    )

    print("=" * 60)
    print("Summary:")
    for name, count in results.items():
        print(f"  {name}: {count:,} entries")
    print("=" * 60)
    print("Conversion complete!")


if __name__ == "__main__":
    main()
