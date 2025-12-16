#!/usr/bin/env python3
"""
Script to create GitHub Release with database files.

This script automates the process of:
1. Calculating SHA256 checksums for all database ZIP files
2. Creating a GitHub Release with proper metadata
3. Uploading all database files to the release
4. Updating the downloader.py manifest with checksums

Requirements:
    pip install PyGithub

Environment:
    GITHUB_TOKEN: Personal access token with 'repo' scope
                  (Create at: https://github.com/settings/tokens)

Usage:
    # Set environment variable
    $env:GITHUB_TOKEN = "your_token_here"

    # Run script
    python scripts/create_database_release.py

    # Or with custom tag
    python scripts/create_database_release.py --tag 0.0.1-dictionaries
"""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

try:
    from github import Github, GithubException
except ImportError:
    print("❌ Error: PyGithub not installed")
    print("Install with: pip install PyGithub")
    sys.exit(1)


class DatabaseReleaseCreator:
    """Creates a GitHub Release with database files."""

    REPO_OWNER = "daurmax"
    REPO_NAME = "FurlanSpellChecker"

    DATABASE_FILES = [
        "words_sqlite.zip",
        "frequencies_sqlite.zip",
        "elisions_sqlite.zip",
        "errors_sqlite.zip",
        "words_radix_tree.zip",
    ]

    RELEASE_NOTES_TEMPLATE = """# Database Files for FurlanSpellChecker {version}

This release contains the SQLite-format database files required by FurlanSpellChecker.

## 🔄 What's New

- **Format Migration**: msgpack → SQLite for better reliability and Windows compatibility
- **Windows Compatibility**: Eliminates bsddb3 dependency issues on Windows/Python 3.13
- **Indexed Queries**: Optimized database structure with proper indexes
- **Full Phonetic Data**: 7,430,427 phonetic hash entries for comprehensive spell checking

## 📦 Files Included

| File | Size | SHA256 | Description |
|------|------|--------|-------------|
{file_table}

## 🚀 Usage

You don't need to download these files manually!

FurlanSpellChecker will automatically:
- Download required databases on first use
- Cache them locally in `~/.cache/furlan_spellchecker/databases`
- Verify integrity using SHA256 checksums
- Extract files automatically

## 🔧 Manual Installation (Optional)

If you prefer to download manually or have network restrictions:

```bash
# 1. Download the ZIP files from this release
# 2. Extract to cache directory:
mkdir -p ~/.cache/furlan_spellchecker/databases
cd ~/.cache/furlan_spellchecker/databases

# Extract each file
unzip words_sqlite.zip
unzip frequencies_sqlite.zip
unzip elisions_sqlite.zip
unzip errors_sqlite.zip
unzip words_radix_tree.zip
```

## 📊 Database Statistics

| Database | Records | Description |
|----------|---------|-------------|
| Phonetic (words) | 7,430,427 | Phonetic hash → word cluster mapping |
| Frequencies | 69,051 | Word frequency scores for ranking |
| Elisions | 10,604 | Words supporting apostrophe contractions |
| Errors | 301 | Common spelling error → correction patterns |
| Radix Tree | - | Prefix search tree for word lookup |

**Format**: SQLite 3 (Python `sqlite3` module compatible)

## 🔗 Related

- **Main Repository**: [FurlanSpellChecker](https://github.com/daurmax/FurlanSpellChecker)
- **Previous Release**: [0.0.1-dictionaries](https://github.com/daurmax/FurlanSpellChecker/releases/tag/0.0.1-dictionaries) (MsgPack format)
- **Source Data**: Exported from COF (Coretor Ortografic Furlan)

## 📄 License

These database files are derived from COF (Coretor Ortografic Furlan) and distributed under the same license as the main project.

**Note**: This is a data-only release. For the FurlanSpellChecker code, see the main releases.

## 🔐 File Integrity

All files can be verified using the SHA256 checksums listed above:

```bash
# Verify downloaded file
sha256sum words_sqlite.zip
certutil -hashfile words_sqlite.zip SHA256  # Windows
```
"""

    def __init__(self, token: str, databases_dir: Path):
        """
        Initialize the release creator.

        Args:
            token: GitHub personal access token
            databases_dir: Directory containing database ZIP files
        """
        self.github = Github(token)
        self.databases_dir = Path(databases_dir)

        # Get repository
        try:
            self.repo = self.github.get_repo(f"{self.REPO_OWNER}/{self.REPO_NAME}")
            print(f"✓ Connected to repository: {self.REPO_OWNER}/{self.REPO_NAME}")
        except GithubException as e:
            print(f"❌ Failed to access repository: {e}")
            sys.exit(1)

    def calculate_checksums(self) -> dict[str, tuple[str, int]]:
        """
        Calculate SHA256 checksums for all database files.

        Returns:
            Dictionary mapping filename to (checksum, size_bytes)
        """
        print("\n📊 Calculating checksums...")
        checksums = {}

        for filename in self.DATABASE_FILES:
            filepath = self.databases_dir / filename

            if not filepath.exists():
                print(f"❌ File not found: {filepath}")
                sys.exit(1)

            # Calculate SHA256
            sha256 = hashlib.sha256()
            size = 0

            with open(filepath, "rb") as f:
                while chunk := f.read(8192):
                    sha256.update(chunk)
                    size += len(chunk)

            checksum = sha256.hexdigest()
            checksums[filename] = (checksum, size)

            size_mb = size / (1024 * 1024)
            print(f"  ✓ {filename}")
            print(f"    Size: {size_mb:.2f} MB")
            print(f"    SHA256: {checksum}")

        return checksums

    def create_file_table(self, checksums: dict[str, tuple[str, int]]) -> str:
        """
        Create markdown table of files with checksums.

        Args:
            checksums: Dictionary of filename -> (checksum, size)

        Returns:
            Markdown table string
        """
        descriptions = {
            "words_sqlite.zip": "Phonetic dictionary (COF export)",
            "frequencies_sqlite.zip": "Word frequency data for ranking",
            "elisions_sqlite.zip": "Elision rules (10,600+ words)",
            "errors_sqlite.zip": "Common error corrections (~300 patterns)",
            "words_radix_tree.zip": "Radix tree for prefix search",
        }

        rows = []
        for filename in self.DATABASE_FILES:
            checksum, size = checksums[filename]
            size_mb = size / (1024 * 1024)
            desc = descriptions.get(filename, "Database file")

            # Truncate checksum for readability
            short_checksum = f"`{checksum[:16]}...`"

            rows.append(f"| `{filename}` | {size_mb:.2f} MB | {short_checksum} | {desc} |")

        return "\n".join(rows)

    def create_release_notes(self, tag: str, checksums: dict[str, tuple[str, int]]) -> str:
        """
        Generate release notes from template.

        Args:
            tag: Release tag (e.g., "v1.0.0-databases")
            checksums: File checksums

        Returns:
            Release notes markdown
        """
        version = tag.replace("-databases", "")
        file_table = self.create_file_table(checksums)

        return self.RELEASE_NOTES_TEMPLATE.format(
            version=version,
            file_table=file_table,
            owner=self.REPO_OWNER,
            repo=self.REPO_NAME,
        )

    def check_release_exists(self, tag: str) -> bool:
        """
        Check if a release with the given tag already exists.

        Args:
            tag: Release tag to check

        Returns:
            True if release exists
        """
        try:
            self.repo.get_release(tag)
            return True
        except GithubException:
            return False

    def create_release(
        self, tag: str, checksums: dict[str, tuple[str, int]], force: bool = False
    ) -> any:
        """
        Create GitHub Release.

        Args:
            tag: Release tag (e.g., "v1.0.0-databases")
            checksums: File checksums
            force: If True, delete existing release

        Returns:
            Created release object
        """
        print(f"\n🚀 Creating release: {tag}")

        # Check if release exists
        if self.check_release_exists(tag):
            if force:
                print(f"⚠️  Release {tag} already exists. Deleting...")
                try:
                    release = self.repo.get_release(tag)
                    release.delete_release()
                    print("  ✓ Deleted existing release")
                except GithubException as e:
                    print(f"❌ Failed to delete release: {e}")
                    sys.exit(1)
            else:
                print(f"❌ Release {tag} already exists. Use --force to overwrite.")
                sys.exit(1)

        # Generate release notes
        notes = self.create_release_notes(tag, checksums)

        # Create release
        try:
            release = self.repo.create_git_release(
                tag=tag,
                name=f"Database Files for FurlanSpellChecker {tag.replace('-databases', '')}",
                message=notes,
                draft=False,
                prerelease=True,  # Mark as pre-release (data-only)
            )
            print(f"✓ Created release: {release.html_url}")
            return release

        except GithubException as e:
            print(f"❌ Failed to create release: {e}")
            sys.exit(1)

    def upload_assets(self, release: any, checksums: dict[str, tuple[str, int]]) -> None:
        """
        Upload database files to release.

        Args:
            release: GitHub release object
            checksums: File checksums (for verification)
        """
        print("\n📤 Uploading assets...")

        for filename in self.DATABASE_FILES:
            filepath = self.databases_dir / filename

            print(f"  Uploading {filename}...", end=" ", flush=True)

            try:
                asset = release.upload_asset(
                    path=str(filepath),
                    label=filename,
                    content_type="application/zip",
                )
                print(f"✓ ({asset.size / (1024 * 1024):.2f} MB)")

            except GithubException as e:
                print(f"❌ Failed: {e}")
                sys.exit(1)

    def generate_manifest_code(self, tag: str, checksums: dict[str, tuple[str, int]]) -> str:
        """
        Generate Python code for downloader.py manifest.

        Args:
            tag: Release tag
            checksums: File checksums

        Returns:
            Python code string
        """
        manifest_entries = []

        mapping = {
            "words_sqlite.zip": "words.sqlite",
            "frequencies_sqlite.zip": "frequencies.sqlite",
            "elisions_sqlite.zip": "elisions.sqlite",
            "errors_sqlite.zip": "errors.sqlite",
            "words_radix_tree.zip": "words_radix_tree.rt",
        }

        for zip_file, db_file in mapping.items():
            checksum, size = checksums[zip_file]
            size_mb = size / (1024 * 1024)

            entry = f"""    "{db_file}": {{
        "url": f"https://github.com/{self.REPO_OWNER}/{self.REPO_NAME}/releases/download/{tag}/{zip_file}",
        "sha256": "{checksum}",
        "size_mb": {size_mb:.2f},
    }}"""
            manifest_entries.append(entry)

        return "DATABASE_MANIFEST = {\n" + ",\n".join(manifest_entries) + "\n}"

    def save_checksums(self, tag: str, checksums: dict[str, tuple[str, int]]) -> None:
        """
        Save checksums and manifest to JSON file.

        Args:
            tag: Release tag
            checksums: File checksums
        """
        output_file = self.databases_dir / f"checksums_{tag}.json"

        data = {
            "tag": tag,
            "files": {
                filename: {
                    "sha256": checksum,
                    "size_bytes": size,
                    "size_mb": round(size / (1024 * 1024), 2),
                }
                for filename, (checksum, size) in checksums.items()
            },
            "manifest_code": self.generate_manifest_code(tag, checksums),
        }

        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)

        print(f"\n💾 Checksums saved to: {output_file}")

    def run(self, tag: str, force: bool = False) -> None:
        """
        Run the complete release creation process.

        Args:
            tag: Release tag
            force: Overwrite existing release
        """
        print("=" * 70)
        print("🎯 GitHub Release Creator for FurlanSpellChecker Databases")
        print("=" * 70)

        # Calculate checksums
        checksums = self.calculate_checksums()

        # Save checksums to file
        self.save_checksums(tag, checksums)

        # Create release
        release = self.create_release(tag, checksums, force)

        # Upload assets
        self.upload_assets(release, checksums)

        # Show summary
        print("\n" + "=" * 70)
        print("✅ RELEASE CREATED SUCCESSFULLY!")
        print("=" * 70)
        print(f"\nRelease URL: {release.html_url}")
        print("\nNext steps:")
        print("1. Update src/furlan_spellchecker/database/downloader.py with the manifest:")
        print(f"   See: {self.databases_dir}/checksums_{tag}.json")
        print("2. Test download: python scripts/test_database_downloader.py")
        print(
            "3. Commit changes: git commit -m 'feat: update database manifest with SHA256 checksums'"
        )

        # Print manifest code
        print("\n📝 Copy this to downloader.py DATABASE_MANIFEST:\n")
        print(self.generate_manifest_code(tag, checksums))


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Create GitHub Release with database files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/create_database_release.py
  python scripts/create_database_release.py --tag 0.0.1-dictionaries
  python scripts/create_database_release.py --force  # Overwrite existing

Environment:
  GITHUB_TOKEN must be set with a personal access token
  Create at: https://github.com/settings/tokens
        """,
    )

    parser.add_argument(
        "--tag", default="0.0.1-dictionaries", help="Release tag (default: 0.0.1-dictionaries)"
    )

    parser.add_argument(
        "--databases-dir",
        type=Path,
        default=Path(__file__).parent.parent / "data" / "databases",
        help="Directory containing database ZIP files",
    )

    parser.add_argument(
        "--force", action="store_true", help="Overwrite existing release if it exists"
    )

    args = parser.parse_args()

    # Check for GitHub token
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("❌ Error: GITHUB_TOKEN environment variable not set")
        print("\nCreate a personal access token at:")
        print("  https://github.com/settings/tokens")
        print("\nThen set it:")
        print('  $env:GITHUB_TOKEN = "your_token_here"  # PowerShell')
        print('  export GITHUB_TOKEN="your_token_here"  # Bash')
        sys.exit(1)

    # Check databases directory
    if not args.databases_dir.exists():
        print(f"❌ Error: Databases directory not found: {args.databases_dir}")
        sys.exit(1)

    # Create and run
    creator = DatabaseReleaseCreator(token, args.databases_dir)
    creator.run(args.tag, args.force)


if __name__ == "__main__":
    main()
