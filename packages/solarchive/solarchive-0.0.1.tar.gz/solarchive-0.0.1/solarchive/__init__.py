"""
solarchive - Python SDK for solarchive.org

This module provides a client for downloading and working with Solana blockchain
data from solarchive.org, including transactions, accounts, and token metadata.

All data is provided as Apache Parquet files, partitioned by date (transactions)
or month (accounts, tokens).
"""

import httpx
from pathlib import Path
from typing import List, Dict, Any


class SolArchive:
    """Client for downloading Solana blockchain data from solarchive.org."""

    def __init__(self, base_url: str = "https://data.solarchive.org"):
        """
        Initialize the SolArchive client.

        Args:
            base_url: Base URL for the data endpoint (default: https://data.solarchive.org)
        """
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(timeout=30.0)

    def _get_index(self, path: str) -> Dict[str, Any]:
        """
        Fetch an index.json file from the archive.

        Args:
            path: Path to the index file (e.g., 'txs/2025-11-01/index.json')

        Returns:
            Parsed JSON index data
        """
        url = f"{self.base_url}/{path}"
        response = self.client.get(url)
        response.raise_for_status()
        return response.json()

    def get_root_index(self) -> Dict[str, Any]:
        """
        Get the root index listing all available datasets.

        Returns:
            Root index data with dataset information
        """
        return self._get_index("index.json")

    def list_transaction_dates(self) -> List[str]:
        """
        List all available transaction dates.

        Returns:
            List of date strings in YYYY-MM-DD format
        """
        index = self._get_index("txs/index.json")
        return index.get("partitions", [])

    def list_account_months(self) -> List[str]:
        """
        List all available account snapshot months.

        Returns:
            List of month strings in YYYY-MM format
        """
        index = self._get_index("accounts/index.json")
        return index.get("partitions", [])

    def list_token_months(self) -> List[str]:
        """
        List all available token snapshot months.

        Returns:
            List of month strings in YYYY-MM format
        """
        index = self._get_index("tokens/index.json")
        return index.get("partitions", [])

    def get_transaction_index(self, date: str) -> Dict[str, Any]:
        """
        Get the index for a specific transaction date.

        Args:
            date: Date in YYYY-MM-DD format

        Returns:
            Index data including list of files and metadata
        """
        return self._get_index(f"txs/{date}/index.json")

    def get_account_index(self, month: str) -> Dict[str, Any]:
        """
        Get the index for a specific account snapshot month.

        Args:
            month: Month in YYYY-MM format

        Returns:
            Index data including list of files and metadata
        """
        return self._get_index(f"accounts/{month}/index.json")

    def get_token_index(self, month: str) -> Dict[str, Any]:
        """
        Get the index for a specific token snapshot month.

        Args:
            month: Month in YYYY-MM format

        Returns:
            Index data including list of files and metadata
        """
        return self._get_index(f"tokens/{month}/index.json")

    def download_file(self, url: str, output_path: Path) -> None:
        """
        Download a single file from the archive.

        Args:
            url: Full URL to the file
            output_path: Local path to save the file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with self.client.stream("GET", url) as response:
            response.raise_for_status()
            with open(output_path, "wb") as f:
                for chunk in response.iter_bytes(chunk_size=8192):
                    f.write(chunk)

    def download_transactions(
        self, date: str, output_dir: str = "./data/txs"
    ) -> List[Path]:
        """
        Download all transaction files for a specific date.

        Args:
            date: Date in YYYY-MM-DD format
            output_dir: Directory to save files

        Returns:
            List of downloaded file paths
        """
        index = self.get_transaction_index(date)
        output_path = Path(output_dir) / date
        downloaded = []

        for file_info in index.get("files", []):
            file_url = file_info["url"]
            file_name = Path(file_url).name
            local_path = output_path / file_name

            print(f"Downloading {file_name}...")
            self.download_file(file_url, local_path)
            downloaded.append(local_path)

        return downloaded

    def download_accounts(
        self, month: str, output_dir: str = "./data/accounts"
    ) -> List[Path]:
        """
        Download all account snapshot files for a specific month.

        Args:
            month: Month in YYYY-MM format
            output_dir: Directory to save files

        Returns:
            List of downloaded file paths
        """
        index = self.get_account_index(month)
        output_path = Path(output_dir) / month
        downloaded = []

        for file_info in index.get("files", []):
            file_url = file_info["url"]
            file_name = Path(file_url).name
            local_path = output_path / file_name

            print(f"Downloading {file_name}...")
            self.download_file(file_url, local_path)
            downloaded.append(local_path)

        return downloaded

    def download_tokens(
        self, month: str, output_dir: str = "./data/tokens"
    ) -> List[Path]:
        """
        Download all token snapshot files for a specific month.

        Args:
            month: Month in YYYY-MM format
            output_dir: Directory to save files

        Returns:
            List of downloaded file paths
        """
        index = self.get_token_index(month)
        output_path = Path(output_dir) / month
        downloaded = []

        for file_info in index.get("files", []):
            file_url = file_info["url"]
            file_name = Path(file_url).name
            local_path = output_path / file_name

            print(f"Downloading {file_name}...")
            self.download_file(file_url, local_path)
            downloaded.append(local_path)

        return downloaded

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
