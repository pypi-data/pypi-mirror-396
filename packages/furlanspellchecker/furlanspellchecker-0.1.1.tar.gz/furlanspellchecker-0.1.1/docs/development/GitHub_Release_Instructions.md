# How to Release Database Files

This guide explains how to create a new GitHub Release for FurlanSpellChecker database files.

## 📋 Overview

Database files are distributed via **GitHub Releases** (not Git LFS) for:
- ✅ Unlimited storage and bandwidth
- ✅ On-demand downloads (not cloned with repository)
- ✅ SHA256 checksum verification
- ✅ Automatic download on first use by spell checker

**Current Release**: [v0.0.2-dictionaries-sqlite](https://github.com/daurmax/FurlanSpellChecker/releases/tag/0.0.2-dictionaries-sqlite)

## 🚀 Quick Start

### Prerequisites

1. **Python Dependencies**:
   ```bash
   pip install PyGithub
   ```

2. **GitHub Token**:
   - Create at: https://github.com/settings/tokens
   - Required scope: `repo` (full control)
   - Set environment variable:
     ```powershell
     $env:GITHUB_TOKEN = "ghp_your_token_here"
     ```

### Create a Release

```bash
# Navigate to project
cd c:\Progetti\Furlan\FurlanSpellChecker

# Run the release script
python scripts/create_database_release.py --tag v0.0.2-dictionaries-sqlite
```

The script will:
1. ✅ Calculate SHA256 checksums for all database files
2. ✅ Create GitHub Release with detailed metadata
3. ✅ Upload all 4 database ZIP files
4. ✅ Generate Python manifest code
5. ✅ Save checksums to JSON file

### Update the Manifest

After creating the release, copy the generated manifest code to `src/furlan_spellchecker/database/downloader.py`:

```python
DATABASE_MANIFEST = {
    "words.sqlite": {
        "url": f"https://github.com/{GITHUB_REPO}/releases/download/{RELEASE_TAG}/words_sqlite.zip",
        "sha256": "e74cddefd7738246...",  # ← Real checksum from script output
        "size_mb": 288.70,
    },
    "frequencies.sqlite": {
        "url": f"https://github.com/{GITHUB_REPO}/releases/download/{RELEASE_TAG}/frequencies_sqlite.zip",
        "sha256": "...",
        "size_mb": 2.02,
    },
    # ... etc
}
```

### Test the Download

```bash
python scripts/test_database_downloader.py
```

All tests should pass ✅

### Commit the Changes

```bash
git add src/furlan_spellchecker/database/downloader.py
git commit -m "feat: update database manifest with SHA256 checksums for v1.0.0"
```

## 📦 Preparing Database Files

Database files must be compressed as ZIP before release.

### From SQLite Files

If you have `.sqlite` files in `data/databases/`:

```powershell
cd data/databases

# Compress each database
Compress-Archive -Path words.sqlite -DestinationPath words_sqlite.zip -Force
Compress-Archive -Path frequencies.sqlite -DestinationPath frequencies_sqlite.zip -Force
Compress-Archive -Path elisions.sqlite -DestinationPath elisions_sqlite.zip -Force
Compress-Archive -Path errors.sqlite -DestinationPath errors_sqlite.zip -Force
Compress-Archive -Path words_radix_tree.rt -DestinationPath words_radix_tree_rt.zip -Force
```

### From COF Export

If you need to re-export from COF:

```bash
cd ../COF/database_export
perl export_all.pl
python convert_to_sqlite.py

# Copy to FurlanSpellChecker
cp output/*.sqlite ../../FurlanSpellChecker/data/databases/
```

## 🔄 When to Create a New Release

Create a new database release when:

- 📝 **Database content changes** (new words, corrections, etc.)
- 🐛 **Bug fixes** in database data (like the NULL frequency issue)
- 🔄 **Format migration** (e.g., SQLite → msgpack)
- 📈 **Version updates** (e.g., v1.0.0 → v1.1.0)

### Version Tagging Convention

Use semantic versioning with `-dictionaries-sqlite` suffix:

- `0.0.1-dictionaries-sqlite` - Initial SQLite release (legacy msgpack: 0.0.1-dictionaries)
- `0.0.2-dictionaries-sqlite` - Current release (optimized SQLite databases)
- `0.0.3-dictionaries-sqlite` - Future updates (new words, corrections)
- `0.1.0-dictionaries-sqlite` - Minor version (significant additions)
- `1.0.0-dictionaries-sqlite` - Major release (breaking changes)

## 📝 Script Reference

### create_database_release.py

**Location**: `scripts/create_database_release.py`

**Usage**:
```bash
python scripts/create_database_release.py [OPTIONS]

Options:
  --tag TAG                    Release tag (default: 0.0.2-dictionaries-sqlite)
  --databases-dir DIR          Database directory (default: data/databases)
  --force                      Overwrite existing release
  --help                       Show help message
```

**Examples**:
```bash
# Create release with default tag
python scripts/create_database_release.py

# Create release with custom tag
python scripts/create_database_release.py --tag 0.0.3-dictionaries-sqlite

# Overwrite existing release (use with caution!)
python scripts/create_database_release.py --force
```

**Output Files**:
- `data/databases/checksums_<tag>.json` - SHA256 checksums and metadata

## 🔍 Verifying the Release

### Check Release on GitHub

1. Go to: https://github.com/daurmax/FurlanSpellChecker/releases
2. Verify all 5 files are uploaded:
   - ✅ `words_sqlite.zip` (~289 MB)
   - ✅ `frequencies_sqlite.zip` (~2 MB)
   - ✅ `elisions_sqlite.zip` (~0.2 MB)
   - ✅ `errors_sqlite.zip` (~0.01 MB)
   - ✅ `words_radix_tree_rt.zip` (~9.7 MB)
3. Check release notes are complete

### Test Automatic Download

Clear cache and test download:

```bash
# Clear cache
rm -rf ~/.cache/furlan_spellchecker/databases  # Linux/Mac
Remove-Item -Recurse -Force $env:USERPROFILE\.cache\furlan_spellchecker\databases  # Windows

# Test download
python -c "from furlan_spellchecker.database import DatabaseFactory; db = DatabaseFactory().create_frequency_database(); print(f'Downloaded! Frequency of furlan: {db.get_frequency(\"furlan\")}')"
```

Expected output:
```
Downloading frequencies.sqlite from GitHub Releases...
Download progress: 100%
Extracting frequencies_sqlite.zip...
Downloaded! Frequency of furlan: 182
```

## 🐛 Troubleshooting

### "GITHUB_TOKEN environment variable not set"

Create a token at https://github.com/settings/tokens with `repo` scope, then:

```powershell
$env:GITHUB_TOKEN = "ghp_your_token_here"
```

### "Release already exists"

Use `--force` to overwrite (⚠️ **warning**: this deletes the old release):

```bash
python scripts/create_database_release.py --force
```

### "File not found: words_msgpack.zip"

Ensure you've created the ZIP files first (see "Preparing Database Files" above).

### "PyGithub not installed"

Install the dependency:

```bash
pip install PyGithub
```

### Download fails in tests

1. Check release is **public** (not draft)
2. Verify URLs in manifest match actual release URLs
3. Check SHA256 checksums are correct
4. Verify network connectivity

## 📊 Database Statistics

Current database sizes (v0.0.2-dictionaries-sqlite):

| Database | Compressed | Uncompressed | Records |
|----------|------------|--------------|------|
| words.sqlite | ~120 MB | 288.70 MB | 7.4M phonetic hashes, 10.1M words |
| frequencies.sqlite | ~0.8 MB | 2.02 MB | 69,051 entries |
| elisions.sqlite | ~0.09 MB | 0.21 MB | 10,604 words |
| errors.sqlite | ~0.005 MB | 0.01 MB | 301 patterns |
| words_radix_tree.rt | ~9.7 MB | 9.65 MB | Binary RadixTree |
| **Total** | **~130 MB** | **~300 MB** | - |

## 🔗 Related Documentation

- [Database Migration Strategy](./Database_Migration_Strategy.md) - Technical background
- [COF Parity Roadmap](./COF_Parity_Roadmap.md) - Migration phases
- [Main README](../../README.md) - Project overview

## 📄 Release Notes Template

The script automatically generates comprehensive release notes. For reference, see the [0.0.2-dictionaries-sqlite release](https://github.com/daurmax/FurlanSpellChecker/releases/tag/0.0.2-dictionaries-sqlite).
