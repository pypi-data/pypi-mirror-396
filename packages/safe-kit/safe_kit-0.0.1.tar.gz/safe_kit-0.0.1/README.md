# Safe Kit (Python)

A Python implementation of the [Safe Protocol Kit](https://github.com/safe-global/safe-core-sdk), designed to mirror the developer experience of the official Node.js SDK.

## Features

- **DX First**: Intuitive API for interacting with Safe smart accounts.
- **Type Safe**: Built with Pydantic and fully typed for robust development.
- **Modern Stack**: Uses Web3.py, Eth-account, and Python 3.10+.

## Installation

```bash
poetry install
```

## Usage

See `examples/basic_usage.py` for a quick start guide.

```python
from safe_kit.safe import Safe
from eth_account import Account

# Initialize
owner = Account.create()
safe = Safe.create(
    eth_adapter=...,
    safe_address="0x..."
)

# Create Transaction
tx = safe.create_transaction(...)
```
# safe-kit
