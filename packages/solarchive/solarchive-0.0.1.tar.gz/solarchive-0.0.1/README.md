# solarchive

Python SDK for accessing Solana blockchain data from [solarchive.org](https://solarchive.org).

**solarchive** is a project to archive Solana's public transaction data and make it freely accessible in ergonomic formats (Apache Parquet) for developers, researchers, and the entire Solana community.

## Features

- Download Solana transaction, account, and token data in Parquet format
- Access historical data from 2020 to present
- No API keys or rate limits - direct HTTP access to data files
- Query data with DuckDB, pandas, Spark, or any Parquet-compatible tool
- Browse available datasets via index files
- Licensed under CC-BY-4.0

## Installation

```bash
pip install solarchive
```

## Usage

```python
from solarchive import SolArchive

# Initialize the client
client = SolArchive()

# List available transaction dates
dates = client.list_transaction_dates()
print(f"Available dates: {dates[:5]}...")

# Get index for a specific date
index = client.get_transaction_index("2025-11-01")
print(f"Files available: {len(index['files'])}")

# Download transaction data for a date
# Downloads all Parquet files for that date
client.download_transactions("2025-11-01", output_dir="./data/txs")

# Get account snapshots for a month
client.download_accounts("2025-12", output_dir="./data/accounts")

# Get token snapshots for a month
client.download_tokens("2024-09", output_dir="./data/tokens")
```

## Data Schema

The archive contains three main datasets:

1. **Transactions** - All non-vote transactions with signatures, fees, account changes, and token balances
   - Schema: `https://data.solarchive.org/schemas/solana/transactions.json`
   - Partitioned by day: `txs/YYYY-MM-DD/*.parquet`

2. **Accounts** - Periodic snapshots of account states including balances and program data
   - Schema: `https://data.solarchive.org/schemas/solana/accounts.json`
   - Partitioned by month: `accounts/YYYY-MM/*.parquet`

3. **Tokens** - Metadata snapshots for fungible and non-fungible tokens
   - Schema: `https://data.solarchive.org/schemas/solana/tokens.json`
   - Partitioned by month: `tokens/YYYY-MM/*.parquet`

## Development

This package requires Python 3.11 or higher.

```bash
# Install dependencies
pip install -e .

# Run the example
python main.py
```

## About solarchive.org

Visit [solarchive.org](https://solarchive.org) to explore the data directly in your browser using DuckDB-WASM, or to support the project. Hosting hundreds of terabytes costs nearly $10,000/year!

## License

MIT
