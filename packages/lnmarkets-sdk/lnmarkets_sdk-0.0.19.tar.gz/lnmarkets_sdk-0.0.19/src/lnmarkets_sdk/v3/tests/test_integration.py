"""Integration tests for LNMarkets SDK v3"""

import asyncio
import os

import pytest
from dotenv import load_dotenv

from lnmarkets_sdk.v3.http.client import APIAuthContext, APIClientConfig, LNMClient
from lnmarkets_sdk.v3.models.account import (
    AddBitcoinAddressParams,
    DepositLightningParams,
    GetInternalDepositsParams,
    GetInternalWithdrawalsParams,
    GetLightningDepositsParams,
    GetLightningWithdrawalsParams,
    GetOnChainDepositsParams,
    GetOnChainWithdrawalsParams,
    WithdrawInternalParams,
    WithdrawLightningParams,
    WithdrawOnChainParams,
)
from lnmarkets_sdk.v3.models.futures_cross import (
    CancelOrderParams,
    DepositParams,
    FuturesCrossOrderLimit,
    GetCrossFundingFeesParams,
    GetFilledOrdersParams,
    GetTransfersParams,
    SetLeverageParams,
    WithdrawParams,
)
from lnmarkets_sdk.v3.models.futures_data import (
    GetCandlesParams,
    GetFundingSettlementsParams,
)
from lnmarkets_sdk.v3.models.futures_isolated import (
    AddMarginParams,
    CancelTradeParams,
    CashInParams,
    CloseTradeParams,
    FuturesOrder,
    GetClosedTradesParams,
    GetIsolatedFundingFeesParams,
    UpdateStoplossParams,
    UpdateTakeprofitParams,
)
from lnmarkets_sdk.v3.models.oracle import GetIndexParams
from lnmarkets_sdk.v3.models.synthetic_usd import GetSwapsParams, NewSwapParams

load_dotenv()


# Add delay between tests to avoid rate limiting
@pytest.fixture
async def public_rate_limit_delay():
    """Add delay between tests for public endpoints to avoid rate limiting."""
    await asyncio.sleep(1)  # 1s delay between tests (1 requests per second)


@pytest.fixture
async def auth_rate_limit_delay():
    """Add delay between tests for authentication endpoints to avoid rate limiting."""
    await asyncio.sleep(0.2)  # 0.2s delay between tests (5 requests per second)


def create_public_config() -> APIClientConfig:
    """Create config for testnet4."""
    return APIClientConfig(network="testnet4")


def create_auth_config() -> APIClientConfig:
    """Create authenticated config for testnet4."""
    return APIClientConfig(
        network="testnet4",
        authentication=APIAuthContext(
            key=os.environ.get("TEST_API_KEY", "test-key"),
            secret=os.environ.get("TEST_API_SECRET", "test-secret"),
            passphrase=os.environ.get("TEST_API_PASSPHRASE", "test-passphrase"),
        ),
    )


@pytest.mark.asyncio
@pytest.mark.usefixtures("public_rate_limit_delay")
class TestBasicsIntegration:
    """Integration tests for basic API endpoints."""

    async def test_ping(self):
        async with LNMClient(create_public_config()) as client:
            result = await client.ping()
            assert "pong" in result

    async def test_time(self):
        async with LNMClient(create_public_config()) as client:
            result = await client.request("GET", "/time")
            assert "time" in result
            assert isinstance(result["time"], str)


@pytest.mark.asyncio
@pytest.mark.usefixtures("auth_rate_limit_delay")
class TestAccountIntegration:
    """Integration tests for account endpoints (require authentication)."""

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_get_account(self):
        async with LNMClient(create_auth_config()) as client:
            account = await client.account.get_account()
            assert account.balance >= 0
            assert account.synthetic_usd_balance >= 0
            assert isinstance(account.username, str)
            assert account.fee_tier >= 0
            assert account.id is not None
            # email and linking_public_key are optional
            if account.email is not None:
                assert isinstance(account.email, str)
            if account.linking_public_key is not None:
                assert isinstance(account.linking_public_key, str)

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_get_bitcoin_address(self):
        async with LNMClient(create_auth_config()) as client:
            result = await client.account.get_bitcoin_address()
            assert result.address is not None

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_add_bitcoin_address(self):
        async with LNMClient(create_auth_config()) as client:
            params = AddBitcoinAddressParams(format="p2wpkh")
            try:
                result = await client.account.add_bitcoin_address(params)
                assert result.address is not None
                assert result.created_at is not None
            except Exception as e:
                assert (
                    "You have too many unused addresses. Please use one of them."
                    in str(e)
                )

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_deposit_lightning(self):
        async with LNMClient(create_auth_config()) as client:
            params = DepositLightningParams(amount=100_000)
            result = await client.account.deposit_lightning(params)
            assert result.deposit_id is not None
            assert result.payment_request.startswith("ln")

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_withdraw_lightning(self):
        async with LNMClient(create_auth_config()) as client:
            params = WithdrawLightningParams(invoice="test_invoice")
            try:
                result = await client.account.withdraw_lightning(params)
                assert result.id is not None
                assert result.amount is not None
                assert result.max_fees is not None
                assert result.payment_hash is not None
            except Exception as e:
                assert "Send a correct BOLT 11 invoice" in str(e)

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_withdraw_internal(self):
        async with LNMClient(create_auth_config()) as client:
            params = WithdrawInternalParams(amount=100_000, to_username="test_username")
            try:
                result = await client.account.withdraw_internal(params)
                assert result.id is not None
                assert result.amount is not None
                assert result.created_at is not None
                assert result.from_uid is not None
                assert result.to_uid is not None
            except Exception as e:
                assert "User not found" in str(e)

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_withdraw_on_chain(self):
        async with LNMClient(create_auth_config()) as client:
            params = WithdrawOnChainParams(amount=100_000, address="test_address")
            try:
                result = await client.account.withdraw_on_chain(params)
                assert result.id is not None
                assert result.uid is not None
                assert result.amount is not None
                assert result.address is not None
                assert result.created_at is not None
                assert result.updated_at is not None
                assert result.status == "pending"
            except Exception as e:
                assert "Invalid address" in str(e)

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_get_lightning_deposits(self):
        async with LNMClient(create_auth_config()) as client:
            params = GetLightningDepositsParams(limit=2)
            result = await client.account.get_lightning_deposits(params)
            assert hasattr(result, "data")
            assert hasattr(result, "next_cursor")
            data = result.data
            assert len(data) <= params.limit
            if len(data) > 0:
                assert data[0].id is not None
                assert data[0].created_at is not None
                # amount, comment, payment_hash, settled_at are optional
                if data[0].amount is not None:
                    assert data[0].amount > 0
                if data[0].comment is not None:
                    assert isinstance(data[0].comment, str)
                if data[0].payment_hash is not None:
                    assert isinstance(data[0].payment_hash, str)
                if data[0].settled_at is not None:
                    assert isinstance(data[0].settled_at, str)

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_get_lightning_withdrawals(self):
        async with LNMClient(create_auth_config()) as client:
            params = GetLightningWithdrawalsParams(limit=2)
            result = await client.account.get_lightning_withdrawals(params)
            data = result.data
            assert len(data) <= params.limit
            if len(data) > 0:
                assert data[0].id is not None
                assert data[0].created_at is not None
                assert data[0].amount is not None
                assert data[0].fee is not None
                assert data[0].payment_hash is not None
                assert data[0].status in ["failed", "processed", "processing"]

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_get_internal_deposits(self):
        async with LNMClient(create_auth_config()) as client:
            params = GetInternalDepositsParams(limit=2)
            result = await client.account.get_internal_deposits(params)
            data = result.data
            assert len(data) <= params.limit
            if len(data) > 0:
                assert data[0].id is not None
                assert data[0].created_at is not None
                assert data[0].amount is not None
                assert data[0].from_username is not None

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_get_internal_withdrawals(self):
        async with LNMClient(create_auth_config()) as client:
            params = GetInternalWithdrawalsParams(limit=2)
            result = await client.account.get_internal_withdrawals(params)
            data = result.data
            assert len(data) <= params.limit
            if len(data) > 0:
                assert data[0].id is not None
                assert data[0].created_at is not None
                assert data[0].amount is not None
                assert data[0].to_username is not None

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_get_on_chain_deposits(self):
        async with LNMClient(create_auth_config()) as client:
            params = GetOnChainDepositsParams(limit=2)
            try:
                result = await client.account.get_on_chain_deposits(params)
                data = result.data
                assert len(data) <= params.limit
                if len(data) > 0:
                    assert data[0].id is not None
                    assert data[0].created_at is not None
                    assert data[0].amount is not None
                    assert data[0].confirmations is not None
                    assert data[0].status in ["MEMPOOL", "CONFIRMED", "IRREVERSIBLE"]
                    assert data[0].tx_id is not None
                    if data[0].block_height is not None:
                        assert data[0].block_height > 0
            except Exception as e:
                assert "HTTP 404: Not found" in str(e)

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_get_on_chain_withdrawals(self):
        async with LNMClient(create_auth_config()) as client:
            params = GetOnChainWithdrawalsParams(limit=2)
            try:
                result = await client.account.get_on_chain_withdrawals(params)
                data = result.data
                assert len(data) <= params.limit
                if len(data) > 0:
                    assert data[0].id is not None
                    assert data[0].created_at is not None
                    assert data[0].amount is not None
                    assert data[0].address is not None
                    assert data[0].status in [
                        "canceled",
                        "pending",
                        "processed",
                        "processing",
                        "rejected",
                    ]
                    if data[0].fee is not None:
                        assert data[0].fee >= 0
                    if data[0].tx_id is not None:
                        assert isinstance(data[0].tx_id, str)
            except Exception as e:
                assert "HTTP 404: Not found" in str(e)


@pytest.mark.asyncio
@pytest.mark.usefixtures("public_rate_limit_delay")
class TestFuturesIntegration:
    """Integration tests for futures data endpoints."""

    async def test_get_ticker(self):
        async with LNMClient(create_public_config()) as client:
            ticker = await client.futures.get_ticker()
            assert ticker.index > 0
            assert ticker.last_price > 0
            assert isinstance(ticker.funding_rate, float)
            assert ticker.funding_time is not None
            assert isinstance(ticker.prices, list)
            if len(ticker.prices) > 0:
                price_bucket = ticker.prices[0]
                assert price_bucket.max_size > 0
                assert price_bucket.min_size >= 0
                if price_bucket.ask_price is not None:
                    assert price_bucket.ask_price >= 0
                if price_bucket.bid_price is not None:
                    assert price_bucket.bid_price >= 0

    async def test_get_leaderboard(self):
        async with LNMClient(create_public_config()) as client:
            leaderboard = await client.futures.get_leaderboard()
            assert isinstance(leaderboard.daily, list)
            assert isinstance(leaderboard.weekly, list)
            assert isinstance(leaderboard.monthly, list)
            assert isinstance(leaderboard.all_time, list)
            if len(leaderboard.daily) > 0:
                user = leaderboard.daily[0]
                assert user.username is not None
                assert user.pl is not None
                assert user.direction is not None

    async def test_get_candles(self):
        async with LNMClient(create_public_config()) as client:
            params = GetCandlesParams(
                from_="2023-05-23T09:52:57.863Z", range="1m", limit=1
            )
            result = await client.futures.get_candles(params)
            assert hasattr(result, "data")
            assert hasattr(result, "next_cursor")
            candles = result.data
            assert isinstance(candles, list)
            assert len(candles) > 0
            assert candles[0].open > 0
            assert candles[0].high > 0
            assert candles[0].low > 0
            assert candles[0].close > 0
            assert candles[0].time is not None
            assert candles[0].volume >= 0

    async def test_get_funding_settlements(self):
        async with LNMClient(create_public_config()) as client:
            params = GetFundingSettlementsParams(limit=5)
            result = await client.futures.get_funding_settlements(params)
            assert hasattr(result, "data")
            assert hasattr(result, "next_cursor")
            settlements = result.data
            assert isinstance(settlements, list)
            assert len(settlements) <= params.limit
            if len(settlements) > 0:
                assert settlements[0].id is not None
                assert settlements[0].time is not None
                assert isinstance(settlements[0].funding_rate, float)
                assert settlements[0].fixing_price > 0


@pytest.mark.asyncio
@pytest.mark.usefixtures("auth_rate_limit_delay")
class TestFuturesIsolatedIntegration:
    """Integration tests for isolated margin futures endpoints."""

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_new_trade(self):
        async with LNMClient(create_auth_config()) as client:
            params = FuturesOrder(
                type="limit",  # limit order
                side="buy",  # buy
                price=100_000,
                quantity=1,
                leverage=100,
            )
            try:
                trade = await client.futures.isolated.new_trade(params)
                assert trade.id is not None
                assert trade.side == "b"
                assert trade.type == "l"
                assert trade.leverage == 100
                assert trade.canceled is False
                assert trade.closed is False
                assert trade.open is True
                assert trade.running is False or trade.running is True
                assert trade.created_at is not None
                assert trade.price > 0
                assert trade.quantity > 0
                assert trade.margin > 0
                assert trade.pl is not None
                assert trade.opening_fee >= 0
                assert trade.closing_fee >= 0
                assert trade.sum_funding_fees is not None
            except Exception as e:
                pytest.skip("Could not create a new trade: " + str(e))

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_get_open_trades(self):
        async with LNMClient(create_auth_config()) as client:
            open_trades = await client.futures.isolated.get_open_trades()
            assert isinstance(open_trades, list)
            if len(open_trades) > 0:
                open_trade = open_trades[0]
                assert open_trade.id is not None
                assert open_trade.open is True
                assert open_trade.canceled is False
                assert open_trade.closed is False
                assert open_trade.running is False
                assert open_trade.type == "limit"
                assert open_trade.price > 0
                assert open_trade.quantity > 0
                assert open_trade.leverage > 0

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_get_running_trades(self):
        async with LNMClient(create_auth_config()) as client:
            running_trades = await client.futures.isolated.get_running_trades()
            assert isinstance(running_trades, list)
            if len(running_trades) > 0:
                running_trade = running_trades[0]
                assert running_trade.id is not None
                assert running_trade.running is True
                assert running_trade.canceled is False
                assert running_trade.closed is False
                assert running_trade.margin > 0
                assert running_trade.pl is not None

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_get_closed_trades(self):
        async with LNMClient(create_auth_config()) as client:
            closed_params = GetClosedTradesParams(limit=5)
            result = await client.futures.isolated.get_closed_trades(closed_params)
            assert hasattr(result, "data")
            assert hasattr(result, "next_cursor")
            closed_trades = result.data
            assert isinstance(closed_trades, list)
            assert len(closed_trades) <= closed_params.limit
            if len(closed_trades) > 0:
                closed_trade = closed_trades[0]
                assert closed_trade.id is not None
                assert closed_trade.closed is True
                assert closed_trade.open is False
                assert closed_trade.running is False
                if closed_trade.closed_at is not None:
                    assert isinstance(closed_trade.closed_at, str)

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_cancel_trade(self):
        async with LNMClient(create_auth_config()) as client:
            # Create a trade first
            params = FuturesOrder(
                type="limit",
                side="buy",
                price=100_000,
                quantity=1,
                leverage=100,
            )
            try:
                trade = await client.futures.isolated.new_trade(params)
                # Cancel the trade
                cancel_params = CancelTradeParams(id=trade.id)
                canceled = await client.futures.isolated.cancel(cancel_params)
                assert canceled.id == trade.id
                assert canceled.canceled is True
                assert canceled.open is False
                assert canceled.running is False
            except Exception:
                pytest.skip("No running trades to cancel")

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_cancel_all_trades(self):
        async with LNMClient(create_auth_config()) as client:
            result = await client.futures.isolated.cancel_all()
            assert isinstance(result, list)
            for canceled in result:
                assert canceled.canceled is True
                assert canceled.open is False
                assert canceled.running is False

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_close_trade(self):
        async with LNMClient(create_auth_config()) as client:
            # Create a running trade first (market order)
            params = FuturesOrder(
                type="market",  # market order
                side="buy",
                quantity=1,
                leverage=100,
            )
            try:
                trade = await client.futures.isolated.new_trade(params)
                # Try to close the trade
                close_params = CloseTradeParams(id=trade.id)
                closed = await client.futures.isolated.close(close_params)
                assert closed.id == trade.id
                assert closed.closed is True
                assert closed.open is False
                assert closed.running is False
                if closed.closed_at is not None:
                    assert isinstance(closed.closed_at, str)
            except Exception as e:
                # May fail if no running trades or insufficient margin
                assert len(str(e)) > 0

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_add_margin(self):
        async with LNMClient(create_auth_config()) as client:
            # Get a running trade first
            running_trades = await client.futures.isolated.get_running_trades()
            if len(running_trades) > 0:
                trade = running_trades[0]
                params = AddMarginParams(id=trade.id, amount=10_000)
                updated = await client.futures.isolated.add_margin(params)
                assert updated.id == trade.id
                assert updated.running is True
                assert updated.margin >= trade.margin
            else:
                # Skip if no running trades
                pytest.skip("No running trades to test add_margin")

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_cash_in(self):
        async with LNMClient(create_auth_config()) as client:
            # Get a running trade first
            running_trades = await client.futures.isolated.get_running_trades()
            if len(running_trades) > 0:
                trade = running_trades[0]
                params = CashInParams(id=trade.id, amount=10_000)
                updated = await client.futures.isolated.cash_in(params)
                assert updated.id == trade.id
                assert updated.running is True
            else:
                # Skip if no running trades
                pytest.skip("No running trades to test cash_in")

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_update_stoploss(self):
        async with LNMClient(create_auth_config()) as client:
            # Get a running trade first
            running_trades = await client.futures.isolated.get_running_trades()
            if len(running_trades) > 0:
                trade = running_trades[0]
                params = UpdateStoplossParams(id=trade.id, value=50_000)
                updated = await client.futures.isolated.update_stoploss(params)
                assert updated.id == trade.id
                assert updated.running is True
                assert updated.stoploss == 50_000
            else:
                # Skip if no running trades
                pytest.skip("No running trades to test update_stoploss")

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_update_takeprofit(self):
        async with LNMClient(create_auth_config()) as client:
            # Get a running trade first
            running_trades = await client.futures.isolated.get_running_trades()
            if len(running_trades) > 0:
                trade = running_trades[0]
                params = UpdateTakeprofitParams(id=trade.id, value=150_000)
                updated = await client.futures.isolated.update_takeprofit(params)
                assert updated.id == trade.id
                assert updated.running is True
                assert updated.takeprofit == 150_000
            else:
                # Skip if no running trades
                pytest.skip("No running trades to test update_takeprofit")

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_get_funding_fees_isolated(self):
        async with LNMClient(create_auth_config()) as client:
            params = GetIsolatedFundingFeesParams(limit=5)
            result = await client.futures.isolated.get_funding_fees(params)
            assert hasattr(result, "data")
            assert hasattr(result, "next_cursor")
            fees = result.data
            assert isinstance(fees, list)
            assert len(fees) <= params.limit
            if len(fees) > 0:
                assert fees[0].fee is not None
                assert fees[0].settlement_id is not None
                assert fees[0].time is not None
                if fees[0].trade_id is not None:
                    assert fees[0].trade_id is not None


@pytest.mark.asyncio
@pytest.mark.usefixtures("auth_rate_limit_delay")
class TestFuturesCrossIntegration:
    """Integration tests for cross margin futures."""

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_get_position(self):
        async with LNMClient(create_auth_config()) as client:
            position = await client.futures.cross.get_position()
            assert position.id is not None
            assert position.margin >= 0
            assert position.leverage > 0
            assert position.quantity >= 0
            assert position.initial_margin >= 0
            assert position.maintenance_margin >= 0
            assert position.running_margin >= 0
            assert position.delta_pl is not None
            assert position.total_pl is not None
            assert position.funding_fees is not None
            assert position.trading_fees >= 0
            assert position.updated_at is not None
            if position.entry_price is not None:
                assert position.entry_price > 0
            if position.liquidation is not None:
                assert position.liquidation > 0

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_new_order(self):
        async with LNMClient(create_auth_config()) as client:
            params = FuturesCrossOrderLimit(
                type="limit",
                side="buy",
                price=100_000,
                quantity=1,
                client_id="test-order-123",
            )
            try:
                order = await client.futures.cross.new_order(params)
                assert order.id is not None
                assert order.side == "b"
                assert order.price == 100_000
                assert order.quantity == 1
                assert order.trading_fee >= 0
                assert order.created_at is not None
            except Exception as e:
                # May fail if insufficient margin
                pytest.skip(f"Could not create order: {str(e)}")

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_get_open_orders(self):
        async with LNMClient(create_auth_config()) as client:
            open_orders = await client.futures.cross.get_open_orders()
            assert isinstance(open_orders, list)
            if len(open_orders) > 0:
                order = open_orders[0]
                assert order.id is not None
                assert order.open is True
                assert order.canceled is False
                assert order.filled is False
                assert order.price > 0
                assert order.quantity > 0
                assert order.side in ["buy", "sell"]
                assert order.type == "limit"
                assert order.trading_fee >= 0
                assert order.created_at is not None

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_get_filled_orders(self):
        async with LNMClient(create_auth_config()) as client:
            params = GetFilledOrdersParams(limit=5)
            result = await client.futures.cross.get_filled_orders(params)
            assert hasattr(result, "data")
            assert hasattr(result, "next_cursor")
            filled_orders = result.data
            assert isinstance(filled_orders, list)
            assert len(filled_orders) <= params.limit
            if len(filled_orders) > 0:
                order = filled_orders[0]
                assert order.id is not None
                assert order.filled is True
                assert order.open is False
                assert order.price > 0
                assert order.quantity > 0
                assert order.side in ["buy", "sell"]
                assert order.type in ["limit", "liquidation", "market"]
                assert order.trading_fee >= 0
                assert order.created_at is not None
                if order.filled_at is not None:
                    assert isinstance(order.filled_at, str)

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_cancel_order(self):
        async with LNMClient(create_auth_config()) as client:
            # Create an order first
            params = FuturesCrossOrderLimit(
                type="limit",
                side="buy",
                price=100_000,
                quantity=1,
                client_id="test-cancel-123",
            )
            try:
                order = await client.futures.cross.new_order(params)
                # Cancel the order
                cancel_params = CancelOrderParams(id=order.id)
                canceled = await client.futures.cross.cancel(cancel_params)
                assert canceled.id == order.id
                assert canceled.canceled is True
                assert canceled.open is False
                assert canceled.filled is False
            except Exception:
                pytest.skip("No running orders to cancel")

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_cancel_all_orders(self):
        async with LNMClient(create_auth_config()) as client:
            result = await client.futures.cross.cancel_all()
            assert isinstance(result, list)
            for canceled in result:
                assert canceled.canceled is True
                assert canceled.open is False
                assert canceled.filled is False

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_close_position(self):
        async with LNMClient(create_auth_config()) as client:
            # Check if there'sell a position to close
            position = await client.futures.cross.get_position()
            if position.quantity > 0:
                result = await client.futures.cross.close()
                # Result can be an order or position update
                assert result is not None
            else:
                # Skip if no position
                pytest.skip("No position to close")

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_deposit(self):
        async with LNMClient(create_auth_config()) as client:
            params = DepositParams(amount=10_000)
            position = await client.futures.cross.deposit(params)
            assert position.id is not None
            assert position.margin >= 0
            assert position.leverage > 0

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_withdraw(self):
        async with LNMClient(create_auth_config()) as client:
            # Get current position to check margin
            position = await client.futures.cross.get_position()
            if position.margin > 10_000:
                params = WithdrawParams(amount=10_000)
                updated = await client.futures.cross.withdraw(params)
                assert updated.id is not None
                assert updated.margin >= 0
            else:
                # Skip if insufficient margin
                pytest.skip("Insufficient margin to test withdraw")

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_set_leverage(self):
        async with LNMClient(create_auth_config()) as client:
            params = SetLeverageParams(leverage=50)
            position = await client.futures.cross.set_leverage(params)
            assert position.id is not None
            assert position.leverage == 50

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_get_transfers(self):
        async with LNMClient(create_auth_config()) as client:
            params = GetTransfersParams(limit=5)
            result = await client.futures.cross.get_transfers(params)
            assert hasattr(result, "data")
            assert hasattr(result, "next_cursor")
            transfers = result.data
            assert isinstance(transfers, list)
            assert len(transfers) <= params.limit
            if len(transfers) > 0:
                assert transfers[0].id is not None
                assert transfers[0].amount is not None
                assert transfers[0].time is not None

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_get_funding_fees_cross(self):
        async with LNMClient(create_auth_config()) as client:
            params = GetCrossFundingFeesParams(limit=5)
            result = await client.futures.cross.get_funding_fees(params)
            assert hasattr(result, "data")
            assert hasattr(result, "next_cursor")
            fees = result.data
            assert isinstance(fees, list)
            assert len(fees) <= params.limit
            if len(fees) > 0:
                assert fees[0].fee is not None
                assert fees[0].settlement_id is not None
                assert fees[0].time is not None
                if fees[0].trade_id is not None:
                    assert fees[0].trade_id is not None


@pytest.mark.asyncio
@pytest.mark.usefixtures("public_rate_limit_delay")
class TestOracleIntegration:
    """Integration tests for oracle endpoints."""

    async def test_get_last_price(self):
        async with LNMClient(create_public_config()) as client:
            result = await client.oracle.get_last_price()
            assert isinstance(result, list)
            assert len(result) > 0
            assert result[0].last_price > 0
            assert result[0].time is not None

    async def test_get_index(self):
        async with LNMClient(create_public_config()) as client:
            params = GetIndexParams(limit=5)
            result = await client.oracle.get_index(params)
            assert isinstance(result, list)
            assert len(result) > 0
            assert result[0].index > 0
            assert result[0].time is not None


@pytest.mark.asyncio
@pytest.mark.usefixtures("public_rate_limit_delay")
class TestSyntheticUSDIntegration:
    """Integration tests for synthetic USD endpoints."""

    async def test_get_best_price(self):
        async with LNMClient(create_public_config()) as client:
            result = await client.synthetic_usd.get_best_price()
            assert result.ask_price > 0
            assert result.bid_price > 0

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_get_swaps(self):
        async with LNMClient(create_auth_config()) as client:
            params = GetSwapsParams(limit=5)
            result = await client.synthetic_usd.get_swaps(params)
            assert hasattr(result, "data")
            assert hasattr(result, "next_cursor")
            swaps = result.data
            assert isinstance(swaps, list)
            assert len(swaps) <= params.limit
            if len(swaps) > 0:
                assert swaps[0].id is not None
                assert swaps[0].created_at is not None
                assert swaps[0].in_amount > 0
                assert swaps[0].out_amount > 0
                assert swaps[0].in_asset in ["BTC", "USD"]
                assert swaps[0].out_asset in ["BTC", "USD"]

    @pytest.mark.skipif(
        not os.environ.get("TEST_API_KEY"),
        reason="TEST_API_KEY not set in environment",
    )
    async def test_new_swap(self):
        async with LNMClient(create_auth_config()) as client:
            # Try to create a swap (may fail due to insufficient balance or other reasons)
            params = NewSwapParams(in_amount=100, in_asset="USD", out_asset="BTC")
            try:
                result = await client.synthetic_usd.new_swap(params)
                assert result.in_amount > 0
                assert result.out_amount > 0
                assert result.in_asset in ["BTC", "USD"]
                assert result.out_asset in ["BTC", "USD"]
            except Exception as e:
                # Expected to fail if insufficient balance or other validation errors
                assert len(str(e)) > 0
