# LN Markets SDK v3

[![CI](https://github.com/ln-markets/sdk-python/actions/workflows/check.yml/badge.svg)](https://github.com/ln-markets/sdk-python/actions/workflows/check.yml)

This is the Python version of the LN Markets API SDK. It provides a client-based interface for interacting with the LN Markets API.

## Usage

For public endpoints, you can just do this:

```python
from lnmarkets_sdk.v3.http.client import LNMClient
import asyncio

async with LNMClient() as client:
  ticker = await client.futures.get_ticker()
  await asyncio.sleep(1)
  leaderboard = await client.futures.get_leaderboard()
```

Remember to sleep between requests, as the rate limit is 1 requests per second for public endpoints.

For endpoints that need authentication, you need to create an instance of the `LNMClient` class and provide your API credentials:

```python
from lnmarkets_sdk.v3.http.client import APIAuthContext, APIClientConfig, LNMClient

config = APIClientConfig(
    authentication=APIAuthContext(
        key=your_key,
        secret=your_secret,
        passphrase=your_passphrase,
    ),
    network="mainnet",
    timeout=60.0,  # 60 second timeout (default is 30s)
    )

async with LNMClient(config) as client:
  account = await client.account.get_account()
```

For endpoints that requires input parameters, you can find the corresponding models in the `lnmarkets_sdk.models` module.

```python

from lnmarkets_sdk.v3.http.client import APIAuthContext, APIClientConfig, LNMClient
from lnmarkets_sdk.v3.models.account import GetLightningDepositsParams

config = APIClientConfig(
    authentication=APIAuthContext(
        key=your_key,
        secret=your_secret,
        passphrase=your_passphrase,
    ),
    network="mainnet",
    timeout=60.0,  # 60 second timeout (default is 30s)
    )

async with LNMClient(config) as client:
    deposits = await client.account.get_lightning_deposits(
        GetLightningDepositsParams(limit=5)
    )
```

Check our [example](./examples/basic.py) for more details.

## Available Methods

🔒 = requires API credentials

```python
# Ping
client.ping()

# Account 🔒
client.account.get_account()
client.account.get_bitcoin_address()
client.account.add_bitcoin_address()
client.account.deposit_lightning()
client.account.withdraw_lightning()
client.account.withdraw_internal()
client.account.withdraw_on_chain()
client.account.get_lightning_deposits()
client.account.get_lightning_withdrawals()
client.account.get_internal_deposits()
client.account.get_internal_withdrawals()
client.account.get_on_chain_deposits()
client.account.get_on_chain_withdrawals()

# Futures
client.futures.get_ticker()
client.futures.get_leaderboard()
client.futures.get_candles()
client.futures.get_funding_settlements()

# Futures Isolated 🔒
client.futures.isolated.new_trade()
client.futures.isolated.get_running_trades()
client.futures.isolated.get_open_trades()
client.futures.isolated.get_closed_trades()
client.futures.isolated.close()
client.futures.isolated.cancel()
client.futures.isolated.cancel_all()
client.futures.isolated.add_margin()
client.futures.isolated.cash_in()
client.futures.isolated.update_stoploss()
client.futures.isolated.update_takeprofit()
client.futures.isolated.get_funding_fees()

# Futures Cross 🔒
client.futures.cross.new_order()
client.futures.cross.get_position()
client.futures.cross.get_open_orders()
client.futures.cross.get_filled_orders()
client.futures.cross.close()
client.futures.cross.cancel()
client.futures.cross.cancel_all()
client.futures.cross.deposit()
client.futures.cross.withdraw()
client.futures.cross.set_leverage()
client.futures.cross.get_transfers()
client.futures.cross.get_funding_fees()

# Oracle
client.oracle.get_index()
client.oracle.get_last_price()

# Synthetic USD
client.synthetic_usd.get_best_price()
client.synthetic_usd.get_swaps()  # 🔒
client.synthetic_usd.new_swap()   # 🔒
```

## API Reference

For full API documentation, see: [LNM API v3 Documentation](https://api.lnmarkets.com/v3)

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
