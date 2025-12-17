"""
Database downloader for EthniData
Downloads the full v3.0.0 database (5.8M records) on first use
"""

import os
import urllib.request
import shutil
from pathlib import Path
from typing import Optional

# Database versions and URLs
DATABASES = {
    'v2.0.0': {
        'url': 'https://github.com/teyfikoz/ethnidata/releases/download/v2.0.0/ethnidata_v2.db',
        'size': '75 MB',
        'records': '415K',
        'filename': 'ethnidata.db'
    },
    'v3.0.0': {
        'url': 'https://github.com/teyfikoz/ethnidata/releases/download/v3.0.0/ethnidata_v3.db',
        'size': '1.1 GB',
        'records': '5.8M',
        'filename': 'ethnidata_v3.db'
    }
}

DEFAULT_VERSION = 'v2.0.0'  # Included in package
FULL_VERSION = 'v3.0.0'     # Downloaded on demand

class DatabaseDownloader:
    """Handles database downloads"""

    def __init__(self, package_dir: Path):
        self.package_dir = package_dir
        self.db_path = package_dir / "ethnidata.db"
        self.v3_path = package_dir / "ethnidata_v3.db"

    def check_database(self, version: str = DEFAULT_VERSION) -> bool:
        """Check if database exists"""
        if version == 'v2.0.0':
            return self.db_path.exists()
        elif version == 'v3.0.0':
            return self.v3_path.exists()
        return False

    def download_database(self, version: str = FULL_VERSION, force: bool = False) -> str:
        """
        Download database if not exists

        Args:
            version: Database version to download ('v2.0.0' or 'v3.0.0')
            force: Force download even if exists

        Returns:
            Path to database file
        """
        if version not in DATABASES:
            raise ValueError(f"Unknown version: {version}. Available: {list(DATABASES.keys())}")

        db_info = DATABASES[version]
        target_path = self.v3_path if version == 'v3.0.0' else self.db_path

        # Check if already exists
        if target_path.exists() and not force:
            print(f"✅ Database {version} already exists ({db_info['records']} records)")
            return str(target_path)

        print(f"\n📥 Downloading EthniData {version} database...")
        print(f"   Records: {db_info['records']}")
        print(f"   Size: {db_info['size']}")
        print(f"   This may take a few minutes...")

        try:
            # Download with progress
            def report_progress(block_num, block_size, total_size):
                downloaded = block_num * block_size
                percent = min(downloaded * 100 / total_size, 100)
                print(f"\r   Progress: {percent:.1f}%", end='', flush=True)

            urllib.request.urlretrieve(
                db_info['url'],
                target_path,
                reporthook=report_progress
            )
            print(f"\n✅ Download complete: {target_path}")
            return str(target_path)

        except Exception as e:
            print(f"\n❌ Download failed: {e}")
            print(f"\n💡 You can manually download from:")
            print(f"   {db_info['url']}")
            print(f"   And save it as: {target_path}")
            raise

    def get_database_path(self, prefer_v3: bool = False) -> str:
        """
        Get database path, downloading if necessary

        Args:
            prefer_v3: If True, use v3.0.0 (5.8M records) instead of v2.0.0 (415K records)

        Returns:
            Path to database file
        """
        if prefer_v3:
            # Try to use v3, download if not exists
            if not self.v3_path.exists():
                print(f"\n🚀 EthniData v3.0.0 offers 14x more data (5.8M vs 415K records)!")
                print(f"   Would you like to download it? ({DATABASES['v3.0.0']['size']})")
                response = input("   Download v3.0.0? [y/N]: ").strip().lower()

                if response in ['y', 'yes']:
                    return self.download_database('v3.0.0')
                else:
                    print(f"   Using v2.0.0 ({DATABASES['v2.0.0']['records']} records)")
                    return str(self.db_path)
            return str(self.v3_path)
        else:
            # Use v2 (included in package)
            if not self.db_path.exists():
                raise FileNotFoundError(
                    f"Database not found at {self.db_path}. "
                    f"Please reinstall: pip install --upgrade --force-reinstall ethnidata"
                )
            return str(self.db_path)


def download_v3_database(package_dir: Optional[Path] = None) -> str:
    """
    Convenience function to download v3.0.0 database

    Args:
        package_dir: Package directory (auto-detected if None)

    Returns:
        Path to downloaded database
    """
    if package_dir is None:
        package_dir = Path(__file__).parent

    downloader = DatabaseDownloader(package_dir)
    return downloader.download_database('v3.0.0')
