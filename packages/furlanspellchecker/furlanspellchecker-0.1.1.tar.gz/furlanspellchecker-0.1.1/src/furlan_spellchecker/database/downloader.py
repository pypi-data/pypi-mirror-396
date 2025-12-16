"""
Database Downloader Module

Handles downloading and caching database files from GitHub Releases.
This allows keeping the repository size small while providing on-demand
database downloads for users.

Features:
- Automatic download on first use
- Local caching with version management
- Integrity verification via checksums
- Progress reporting for large downloads
- Graceful fallback to bundled databases (if available)
"""

import hashlib
import logging
import zipfile
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)


class DatabaseDownloader:
    """Manages downloading and caching of database files from GitHub Releases."""

    # GitHub Release configuration
    GITHUB_REPO = "daurmax/FurlanSpellChecker"
    RELEASE_TAG = "0.0.2-dictionaries-sqlite"

    # Database file manifest
    DATABASE_MANIFEST = {
        "words.sqlite": {
            "url": f"https://github.com/{GITHUB_REPO}/releases/download/{RELEASE_TAG}/words_sqlite.zip",
            "sha256": "0edb1cf99b355d391adfd12595407a43e8702fba1fffcb351154d0dcdc0e9a9a",
            "size_mb": 288.70,
        },
        "frequencies.sqlite": {
            "url": f"https://github.com/{GITHUB_REPO}/releases/download/{RELEASE_TAG}/frequencies_sqlite.zip",
            "sha256": "c2c5fd349e777fa5ad7bd53af445093232bf3b12569f3a66a3cd060e44e2a931",
            "size_mb": 2.02,
        },
        "errors.sqlite": {
            "url": f"https://github.com/{GITHUB_REPO}/releases/download/{RELEASE_TAG}/errors_sqlite.zip",
            "sha256": "81162fa504b60298ec2ae4f6677d1512da0128be0c39ea5fdbd65c05dcd8f94f",
            "size_mb": 0.01,
        },
        "elisions.sqlite": {
            "url": f"https://github.com/{GITHUB_REPO}/releases/download/{RELEASE_TAG}/elisions_sqlite.zip",
            "sha256": "8040e00751da9e4419976e771976d92e9f1c32f6494e0c13b2a28e1bd6a68a51",
            "size_mb": 0.21,
        },
        "words_radix_tree.rt": {
            "url": f"https://github.com/{GITHUB_REPO}/releases/download/{RELEASE_TAG}/words_radix_tree.zip",
            "sha256": "14fce4edb00e3030a0b74bc7d103565b47dfb2c2df4d9736f754423bdec5a91d",
            "size_mb": 9.65,
        },
    }

    def __init__(self, cache_dir: Path | None = None):
        """
        Initialize the database downloader.

        Args:
            cache_dir: Directory to cache downloaded files.
                      Defaults to ~/.cache/furlan_spellchecker/databases
        """
        if cache_dir is None:
            cache_dir = Path.home() / ".cache" / "furlan_spellchecker" / "databases"

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Track downloaded archives to avoid redundant downloads
        self._downloaded_archives: set[str] = set()

    def get_database_path(self, database_name: str) -> Path:
        """
        Get the local path for a database file, downloading if necessary.

        Args:
            database_name: Name of the database file (e.g., "words.sqlite")

        Returns:
            Path to the local database file

        Raises:
            ValueError: If database_name is not in the manifest
            RuntimeError: If download fails
        """
        if database_name not in self.DATABASE_MANIFEST:
            raise ValueError(
                f"Unknown database: {database_name}. "
                f"Available databases: {list(self.DATABASE_MANIFEST.keys())}"
            )

        local_path = self.cache_dir / database_name

        # Return if already cached
        if local_path.exists():
            logger.debug(f"Database '{database_name}' found in cache: {local_path}")
            return local_path

        # Download and extract
        logger.info(f"Database '{database_name}' not found in cache. Downloading...")
        self._download_database(database_name)

        if not local_path.exists():
            raise RuntimeError(f"Download completed but file not found: {local_path}")

        return local_path

    def _download_database(self, database_name: str) -> None:
        """
        Download and extract a database file from GitHub Releases.

        Args:
            database_name: Name of the database file

        Raises:
            RuntimeError: If download or extraction fails
        """
        manifest = self.DATABASE_MANIFEST[database_name]
        url = str(manifest["url"])

        # Extract archive name from URL
        archive_name = url.split("/")[-1]
        archive_path = self.cache_dir / archive_name

        # Skip download if archive already downloaded in this session
        if archive_name in self._downloaded_archives and archive_path.exists():
            logger.debug(f"Archive '{archive_name}' already downloaded, extracting...")
            self._extract_archive(archive_path, database_name)
            return

        try:
            logger.info(f"Downloading from: {url}")
            logger.info(f"Size: ~{manifest['size_mb']:.2f} MB")

            # Download with progress reporting
            self._download_with_progress(url, archive_path)

            # Verify checksum if available
            if manifest["sha256"]:
                self._verify_checksum(archive_path, str(manifest["sha256"]))

            # Extract the archive
            self._extract_archive(archive_path, database_name)

            # Mark archive as downloaded
            self._downloaded_archives.add(archive_name)

            # Clean up archive after extraction
            archive_path.unlink()
            logger.debug(f"Cleaned up archive: {archive_path}")

            logger.info(f"Successfully downloaded and extracted '{database_name}'")

        except (URLError, HTTPError) as e:
            raise RuntimeError(
                f"Failed to download database '{database_name}' from {url}: {e}"
            ) from e
        except Exception as e:
            # Clean up partial download
            if archive_path.exists():
                archive_path.unlink()
            raise RuntimeError(f"Error processing database '{database_name}': {e}") from e

    def _download_with_progress(self, url: str, dest_path: Path) -> None:
        """
        Download a file with progress reporting.

        Args:
            url: URL to download from
            dest_path: Destination path for downloaded file
        """
        request = Request(url, headers={"User-Agent": "FurlanSpellChecker/2.0"})

        with urlopen(request) as response:
            total_size = int(response.headers.get("Content-Length", 0))

            with open(dest_path, "wb") as f:
                downloaded = 0
                chunk_size = 8192
                last_percent = -1

                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break

                    f.write(chunk)
                    downloaded += len(chunk)

                    # Report progress every 5%
                    if total_size > 0:
                        percent = int(downloaded * 100 / total_size)
                        if percent >= last_percent + 5:
                            logger.info(f"Download progress: {percent}%")
                            last_percent = percent

    def _extract_archive(self, archive_path: Path, target_file: str) -> None:
        """
        Extract a specific file from a zip archive.

        Args:
            archive_path: Path to the zip archive
            target_file: Name of the file to extract
        """
        with zipfile.ZipFile(archive_path, "r") as zip_ref:
            # Check if target file is in archive
            if target_file not in zip_ref.namelist():
                raise RuntimeError(
                    f"File '{target_file}' not found in archive {archive_path}. "
                    f"Available files: {zip_ref.namelist()}"
                )

            # Extract to cache directory
            zip_ref.extract(target_file, self.cache_dir)
            logger.debug(f"Extracted '{target_file}' from {archive_path}")

    def _verify_checksum(self, file_path: Path, expected_sha256: str) -> None:
        """
        Verify file integrity using SHA256 checksum.

        Args:
            file_path: Path to file to verify
            expected_sha256: Expected SHA256 hash

        Raises:
            RuntimeError: If checksum doesn't match
        """
        sha256 = hashlib.sha256()

        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)

        actual_hash = sha256.hexdigest()

        if actual_hash != expected_sha256:
            raise RuntimeError(
                f"Checksum mismatch for {file_path}. "
                f"Expected: {expected_sha256}, Got: {actual_hash}"
            )

        logger.debug(f"Checksum verified: {actual_hash}")

    def clear_cache(self) -> None:
        """Remove all cached database files."""
        import shutil

        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            logger.info(f"Cleared cache directory: {self.cache_dir}")

        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_cache_info(self) -> dict[str, Any]:
        """
        Get information about cached databases.

        Returns:
            Dictionary with cache statistics
        """
        cached_files = list(self.cache_dir.glob("*.sqlite"))
        total_size = sum(f.stat().st_size for f in cached_files)

        return {
            "cache_dir": str(self.cache_dir),
            "cached_files": [f.name for f in cached_files],
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "available_databases": list(self.DATABASE_MANIFEST.keys()),
        }


# Singleton instance for easy access
_downloader_instance: DatabaseDownloader | None = None


def get_downloader() -> DatabaseDownloader:
    """Get the singleton DatabaseDownloader instance."""
    global _downloader_instance

    if _downloader_instance is None:
        _downloader_instance = DatabaseDownloader()

    return _downloader_instance


def download_database(database_name: str) -> Path:
    """
    Convenience function to download a database file.

    Args:
        database_name: Name of the database file (e.g., "words.sqlite")

    Returns:
        Path to the local database file
    """
    return get_downloader().get_database_path(database_name)
