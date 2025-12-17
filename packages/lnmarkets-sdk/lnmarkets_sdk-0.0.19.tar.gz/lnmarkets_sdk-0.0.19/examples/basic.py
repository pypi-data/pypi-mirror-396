"""
Example usage of the v3 client-based API.
"""

import asyncio
import os
from pprint import pprint

from dotenv import load_dotenv

from lnmarkets_sdk.v3.http.client import APIAuthContext, APIClientConfig, LNMClient
from lnmarkets_sdk.v3.models.account import GetLightningDepositsParams
from lnmarkets_sdk.v3.models.futures_cross import FuturesCrossOrderLimit
from lnmarkets_sdk.v3.models.futures_data import (
    GetCandlesParams,
    GetFundingSettlementsParams,
)
from lnmarkets_sdk.v3.models.futures_isolated import (
    GetClosedTradesParams,
    GetIsolatedFundingFeesParams,
    UpdateTakeprofitParams,
)
from lnmarkets_sdk.v3.models.oracle import GetLastPriceParams

load_dotenv()


async def example_public_endpoints():
    """Example: Make public requests without authentication."""
    print("\n" + "=" * 80)
    print("PUBLIC ENDPOINTS EXAMPLE")
    print("=" * 80)

    # Create client without authentication for public endpoints
    # The httpx.AsyncClient is created once and reuses connections
    async with LNMClient(APIClientConfig(network="mainnet")) as client:
        # All these requests share the same connection pool
        print("\n🔄 Making multiple requests with connection reuse...")

        # Get futures ticker
        ticker = await client.futures.get_ticker()
        print("\n--- Futures Ticker ---")
        pprint(ticker.model_dump(), indent=2, width=100)

        # Get leaderboard
        await asyncio.sleep(1)
        leaderboard = await client.futures.get_leaderboard()
        print("\n--- Leaderboard (Top 3 Daily) ---")
        pprint(leaderboard.daily[:3], indent=2, width=100)

        # Get oracle data
        await asyncio.sleep(1)
        oracle_index = await client.oracle.get_index()
        print("\n--- Oracle Index (Latest) ---")
        pprint(oracle_index[0].model_dump() if oracle_index else "No data", indent=2)

        # Get synthetic USD best price
        await asyncio.sleep(1)
        best_price = await client.synthetic_usd.get_best_price()
        print("\n--- Synthetic USD Best Price ---")
        pprint(best_price.model_dump(), indent=2)

        # Ping the API
        await asyncio.sleep(1)
        ping_response = await client.ping()
        print("\n--- Ping ---")
        print(f"Response: {ping_response}")

        # Get server time
        await asyncio.sleep(1)
        time_response = await client.time()
        print("\n--- Server Time ---")
        print(f"Response: {time_response}")

        # Get futures candles
        await asyncio.sleep(1)
        candles_params = GetCandlesParams(
            from_="2024-01-01T00:00:00.000Z",
            range="1h",
            limit=5,
        )
        candles = await client.futures.get_candles(candles_params)
        print("\n--- Futures Candles (Last 5) ---")
        for candle in candles.data[:3]:  # Show first 3
            print(
                f"Time: {candle.time}, OHLC: {candle.open}/{candle.high}/{candle.low}/{candle.close}"
            )

        # Get funding settlements
        await asyncio.sleep(1)
        funding_settlements = await client.futures.get_funding_settlements(
            GetFundingSettlementsParams(limit=5)
        )
        print("\n--- Funding Settlements (Last 5) ---")
        for settlement in funding_settlements.data[:3]:  # Show first 3
            print(
                f"Rate: {settlement.funding_rate}, Price: {settlement.fixing_price}, Time: {settlement.time}"
            )

        # Get oracle last price
        await asyncio.sleep(1)
        last_prices = await client.oracle.get_last_price(GetLastPriceParams(limit=5))
        print("\n--- Oracle Last Price (Last 5) ---")
        for price in last_prices[:3]:  # Show first 3
            print(f"Price: {price.last_price}, Time: {price.time}")


async def example_authenticated_endpoints():
    """Example: Use authenticated endpoints with credentials."""
    print("\n" + "=" * 80)
    print("AUTHENTICATED ENDPOINTS EXAMPLE")
    print("=" * 80)

    key = os.getenv("V3_API_KEY")
    secret = os.getenv("V3_API_KEY_SECRET")
    passphrase = os.getenv("V3_API_KEY_PASSPHRASE")
    print(f"key: {key}")
    print(f"secret: {secret}")
    print(f"passphrase: {passphrase}")

    if not (key and secret and passphrase):
        print("\n⚠️  Skipping authenticated example:")
        print("    Please set V3_API_KEY, V3_API_KEY_SECRET, and V3_API_KEY_PASSPHRASE")
        return

    # Create config with authentication and custom timeout
    config = APIClientConfig(
        authentication=APIAuthContext(
            key=key,
            secret=secret,
            passphrase=passphrase,
        ),
        network="mainnet",
        timeout=60.0,  # 60 second timeout (default is 30s)
    )

    async with LNMClient(config) as client:
        print("\n🔐 Using authenticated endpoints with connection pooling...")

        # Get account info
        account = await client.account.get_account()
        print("\n--- Account Info ---")
        print(f"Username: {account.username}")
        print(f"Balance: {account.balance} sats")
        print(f"Synthetic USD Balance: {account.synthetic_usd_balance}")

        # Get Bitcoin address
        btc_address = await client.account.get_bitcoin_address()
        print("\n--- Bitcoin Deposit Address ---")
        print(f"Address: {btc_address.address}")

        # Get lightning deposits (last 5)
        deposits_response = await client.account.get_lightning_deposits(
            GetLightningDepositsParams(from_="1970-01-01T00:00:00.000Z", limit=5)
        )
        print(
            f"\n--- Recent Lightning Deposits (Last {len(deposits_response.data)}) ---"
        )
        for deposit in deposits_response.data:
            print(f"Deposits {deposit.amount} sats at {deposit.created_at}")

        # Get running trades
        running_trades = await client.futures.isolated.get_running_trades()
        print("\n--- Running Isolated Trades ---")
        print(f"Count: {len(running_trades)}")
        for trade in running_trades[:3]:  # Show first 3
            side = "LONG" if trade.side == "buy" else "SHORT"
            print(
                f"  {side} - Margin: {trade.margin} sats, Leverage: {trade.leverage}x, PL: {trade.pl} sats"
            )

        # Get open trades
        await asyncio.sleep(1)
        open_trades = await client.futures.isolated.get_open_trades()
        print(f"\n--- Open Isolated Trades (Count: {len(open_trades)}) ---")
        for trade in open_trades[:3]:  # Show first 3
            side = "LONG" if trade.side == "b" else "SHORT"
            print(f"  {side} - Price: {trade.price}, Quantity: {trade.quantity}")

        # Get closed trades
        await asyncio.sleep(1)
        closed_trades = await client.futures.isolated.get_closed_trades(
            GetClosedTradesParams(limit=5)
        )
        print(f"\n--- Closed Isolated Trades (Last {len(closed_trades.data)}) ---")
        for trade in closed_trades.data[:3]:  # Show first 3
            side = "LONG" if trade.side == "b" else "SHORT"
            print(f"  {side} - PL: {trade.pl} sats, Closed: {trade.closed}")

        # Get isolated funding fees
        await asyncio.sleep(1)
        isolated_fees = await client.futures.isolated.get_funding_fees(
            GetIsolatedFundingFeesParams(limit=5)
        )
        print(f"\n--- Isolated Funding Fees (Last {len(isolated_fees.data)}) ---")
        for fee in isolated_fees.data[:3]:  # Show first 3
            print(f"Fee: {fee.fee} sats, Time: {fee.time}")

        # Get cross margin position
        try:
            position = await client.futures.cross.get_position()
            print("\n--- Cross Margin Position ---")
            print(f"Quantity: {position.quantity}")
            print(f"Margin: {position.margin} sats")
            print(f"Leverage: {position.leverage}x")
            print(f"Total PL: {position.total_pl} sats")
        except Exception as e:
            print(f"Error: {e}")

        # Open a new cross order
        try:
            print("\n--- Try to open a new cross order ---")
            order_params = FuturesCrossOrderLimit(
                type="limit",
                price=101000,
                quantity=10,
                side="sell",
                client_id="custom-ref-123",
            )
            new_order = await client.futures.cross.new_order(order_params)
            print(f"New order: {new_order}")
        except Exception as e:
            print(f"Error: {e}")

        print("\n --- Update take profit ---")
        trade_id = "41ee6f7e-7cee-4c3b-b9f3-962d4b3b97c6"
        params = UpdateTakeprofitParams(id=trade_id, value=100_000)
        updated = await client.futures.isolated.update_takeprofit(params)
        print(f"New take profit: {updated.takeprofit}")


async def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("LN MARKETS V3 CLIENT EXAMPLES")
    print("=" * 80)

    await example_public_endpoints()
    await example_authenticated_endpoints()

    print("\n" + "=" * 80)
    print("EXAMPLES COMPLETE")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
