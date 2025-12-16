# Ethereal Python SDK

A Python library for interacting with the Ethereal trading platform. This SDK provides tools for trading, managing positions, and accessing market data.

## SDK Documentation

For full documentation, visit the [documentation site](https://meridianxyz.github.io/ethereal-py-sdk/).

## Installation

### Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver:

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install the SDK
uv add ethereal-sdk
```

### Using pip

```bash
pip install ethereal-sdk
```

uvloop installs automatically on CPython for macOS/Linux; Windows and other platforms fall back to asyncio.

## Quick Start

The SDK provides two client types:

**AsyncRESTClient** (Recommended for new applications):

```python
import asyncio
from decimal import Decimal
from ethereal import AsyncRESTClient

async def main():
    client = await AsyncRESTClient.create({
        "base_url": "https://api.etherealtest.net",
        "chain_config": {
            "rpc_url": "https://rpc.etherealtest.net",
            "private_key": "your_private_key",  # optional - required for trading
        }
    })

    # Get market data
    products = await client.list_products()
    product_ids = [p.id for p in products]
    prices = await client.list_market_prices(product_ids=product_ids)

    # Place an order (requires private key)
    await client.create_order(
        order_type="LIMIT",
        quantity=Decimal("1.0"),
        side=0,  # 0 for buy, 1 for sell
        price=Decimal("100.0"),
        ticker="BTCUSD"
    )

    await client.close()

asyncio.run(main())
```

**RESTClient** (Synchronous):

```python
from decimal import Decimal
from ethereal import RESTClient

client = RESTClient({
    "base_url": "https://api.etherealtest.net",
    "chain_config": {
        "rpc_url": "https://rpc.etherealtest.net",
        "private_key": "your_private_key",  # optional - required for trading
    }
})

# Get market data
products = client.list_products()

# Place an order (requires private key)
order = client.create_order(
    order_type="LIMIT",
    quantity=Decimal("1.0"),
    side=0,
    price=Decimal("100.0"),
    ticker="BTCUSD"
)
```

## Development

To set up the development environment:

```bash
# Clone the repository
git clone git@github.com:meridianxyz/ethereal-py-sdk.git
cd ethereal-py-sdk

# Install dependencies with uv
uv sync

# Run tests
uv run pytest

# Run the linter
uv run ruff check --fix

# Run the example CLI
uv run python -i examples/cli.py
```

## Main Features

### Market Data

- List available trading products
- Get current market prices
- View market order book
- Track funding rates

### Trading

- Place market and limit orders
- Cancel orders
- View order history
- Track trades and fills

### Account Management

- Manage subaccounts
- View positions
- Track token balances
- Handle deposits and withdrawals

### Websocket Support

- Real-time market data
- Live order book updates

## Configuration

The SDK can be configured with these options:

- `private_key`: Your private key for authentication
- `base_url`: API endpoint (default: "https://api.etherealtest.net")
- `timeout`: Request timeout in seconds
- `verbose`: Enable debug logging
- `rate_limit_headers`: Enable rate limit headers

The SDK automatically enables uvloop on supported platforms and transparently falls back to the built-in asyncio loop elsewhere.

## Examples

### Get Market Data

```python
async def get_market_data():
    client = await AsyncRESTClient.create({"base_url": "https://api.etherealtest.net"})

    # List all available products
    products = await client.list_products()

    # Get current prices
    all_product_ids = [product.id for product in products]
    prices = await client.list_market_prices(product_ids=all_product_ids)

    # View market liquidity
    products_by_ticker = await client.products_by_ticker()
    btc_product_id = products_by_ticker['BTCUSD'].id
    liquidity = await client.get_market_liquidity(product_id=btc_product_id)

    await client.close()

asyncio.run(get_market_data())
```

### Manage Orders

```python
async def manage_orders():
    config = {
        "base_url": "https://api.etherealtest.net",
        "chain_config": {
            "rpc_url": "https://rpc.etherealtest.net",
            "private_key": "your_private_key"
        }
    }
    client = await AsyncRESTClient.create(config)

    # Place a limit order
    order = await client.create_order(
        order_type="LIMIT",
        quantity=Decimal("1.0"),
        side=0,
        price=Decimal("100.0"),
        ticker="BTCUSD"
    )

    # Cancel an order
    subaccounts = await client.subaccounts()
    await client.cancel_orders(
        order_ids=["<uuid of order>"],
        sender=client.chain.address,
        subaccount=subaccounts[0].name
    )

    # View order history
    subaccount_id = subaccounts[0].id
    orders = await client.list_orders(subaccount_id=subaccount_id)

    await client.close()

asyncio.run(manage_orders())
```

### Account Operations

```python
async def account_operations():
    config = {
        "base_url": "https://api.etherealtest.net",
        "chain_config": {
            "rpc_url": "https://rpc.etherealtest.net",
            "private_key": "your_private_key"
        }
    }
    client = await AsyncRESTClient.create(config)

    # List subaccounts
    subaccounts = await client.subaccounts()

    # View positions
    positions = await client.list_positions(subaccount_id=subaccounts[0].id)

    # Get token balances
    balances = await client.get_subaccount_balances(subaccount_id=subaccounts[0].id)

    await client.close()

asyncio.run(account_operations())
```

## Error Handling

The SDK includes built-in error handling for:

- Invalid requests
- Authentication errors
- Rate limiting
- Network issues

## Ethereal Documentation

For full documentation, visit our [documentation site](https://docs.ethereal.trade).

## Support

For issues and questions, please refer to the project's issue tracker or documentation.
