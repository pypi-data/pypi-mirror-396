from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lnmarkets_sdk.v3.http.client import LNMClient

from lnmarkets_sdk.v3._internal.models import PaginatedResponse
from lnmarkets_sdk.v3.models.funding_fees import FundingFees
from lnmarkets_sdk.v3.models.futures_isolated import (
    AddMarginParams,
    CancelTradeParams,
    CashInParams,
    CloseTradeParams,
    FuturesCanceledTrade,
    FuturesClosedTrade,
    FuturesOpenTrade,
    FuturesOrder,
    FuturesRunningTrade,
    GetClosedTradesParams,
    GetIsolatedFundingFeesParams,
    UpdateStoplossParams,
    UpdateTakeprofitParams,
)


class FuturesIsolatedClient:
    """Client for isolated futures margin endpoints."""

    def __init__(self, client: "LNMClient"):
        self._client = client

    async def new_trade(self, params: FuturesOrder):
        """
        Open a new isolated margin futures trade.

        Example:
        ```python
        from lnmarkets_sdk.v3.models.futures_isolated import FuturesOrder

        async with LNMClient(config) as client:
            params = FuturesOrder(
                type="limit",  # limit order
                side="buy",  # buy
                price=100_000,
                quantity=1,
                leverage=100,
                stoploss=90_000,  # optional stop loss
                takeprofit=110_000,  # optional take profit
            )
            trade = await client.futures.isolated.new_trade(params)
            print(f"Trade ID: {trade.id}")
        ```
        """
        return await self._client.request(
            "POST",
            "/futures/isolated/trade",
            params=params,
            credentials=True,
            response_model=FuturesRunningTrade | FuturesOpenTrade,
        )

    async def get_running_trades(self):
        """
        Get all running isolated margin trades.

        Example:
        ```python
        async with LNMClient(config) as client:
            trades = await client.futures.isolated.get_running_trades()
            for trade in trades:
                print(f"Trade ID: {trade.id}, P&L: {trade.pl}")
        ```
        """
        return await self._client.request(
            "GET",
            "/futures/isolated/trades/running",
            credentials=True,
            response_model=list[FuturesRunningTrade],
        )

    async def get_open_trades(self):
        """
        Get all open isolated margin trades.

        Example:
        ```python
        async with LNMClient(config) as client:
            trades = await client.futures.isolated.get_open_trades()
            for trade in trades:
                print(f"Trade ID: {trade.id}, Price: {trade.price}")
        ```
        """
        return await self._client.request(
            "GET",
            "/futures/isolated/trades/open",
            credentials=True,
            response_model=list[FuturesOpenTrade],
        )

    async def get_closed_trades(self, params: GetClosedTradesParams | None = None):
        """
        Get closed isolated margin trades history.

        Example:
        ```python
        from lnmarkets_sdk.v3.models.futures_isolated import GetClosedTradesParams

        async with LNMClient(config) as client:
            params = GetClosedTradesParams(limit=10)
            response = await client.futures.isolated.get_closed_trades(params)
            for trade in response.data:
                print(f"Trade ID: {trade.id}, P&L: {trade.pl}")
            if response.next_cursor:
                print(f"Next cursor: {response.next_cursor}")
        ```
        """
        return await self._client.request(
            "GET",
            "/futures/isolated/trades/closed",
            params=params,
            credentials=True,
            response_model=PaginatedResponse[FuturesClosedTrade | FuturesCanceledTrade],
        )

    async def close(self, params: CloseTradeParams):
        """
        Close an isolated margin trade.

        Example:
        ```python
        from lnmarkets_sdk.v3.models.futures_isolated import CloseTradeParams

        async with LNMClient(config) as client:
            params = CloseTradeParams(id=trade_id)
            closed = await client.futures.isolated.close(params)
            print(f"Closed: {closed.closed}, P&L: {closed.pl}")
        ```
        """
        return await self._client.request(
            "POST",
            "/futures/isolated/trade/close",
            params=params,
            credentials=True,
            response_model=FuturesClosedTrade,
        )

    async def cancel(self, params: CancelTradeParams):
        """
        Cancel an isolated margin trade.

        Example:
        ```python
        from lnmarkets_sdk.v3.models.futures_isolated import CancelTradeParams

        async with LNMClient(config) as client:
            params = CancelTradeParams(id=trade_id)
            canceled = await client.futures.isolated.cancel(params)
            print(f"Canceled: {canceled.canceled}")
        ```
        """
        return await self._client.request(
            "POST",
            "/futures/isolated/trade/cancel",
            params=params,
            credentials=True,
            response_model=FuturesCanceledTrade,
        )

    async def cancel_all(self):
        """
        Cancel all isolated margin trades.

        Example:
        ```python
        async with LNMClient(config) as client:
            canceled = await client.futures.isolated.cancel_all()
            print(f"Canceled {len(canceled)} trades")
        ```
        """
        return await self._client.request(
            "POST",
            "/futures/isolated/trades/cancel-all",
            credentials=True,
            response_model=list[FuturesCanceledTrade],
        )

    async def add_margin(self, params: AddMarginParams):
        """
        Add margin to an isolated trade.

        Example:
        ```python
        from lnmarkets_sdk.v3.models.futures_isolated import AddMarginParams

        async with LNMClient(config) as client:
            params = AddMarginParams(id=trade_id, amount=10_000)
            updated = await client.futures.isolated.add_margin(params)
            print(f"New margin: {updated.margin}")
        ```
        """
        return await self._client.request(
            "POST",
            "/futures/isolated/trade/add-margin",
            params=params,
            credentials=True,
            response_model=FuturesRunningTrade,
        )

    async def cash_in(self, params: CashInParams):
        """
        Cash in on an isolated trade.

        Example:
        ```python
        from lnmarkets_sdk.v3.models.futures_isolated import CashInParams

        async with LNMClient(config) as client:
            params = CashInParams(id=trade_id, amount=10_000)
            updated = await client.futures.isolated.cash_in(params)
            print(f"Trade margin: {updated.margin}")
        ```
        """
        return await self._client.request(
            "POST",
            "/futures/isolated/trade/cash-in",
            params=params,
            credentials=True,
            response_model=FuturesRunningTrade,
        )

    async def update_stoploss(self, params: UpdateStoplossParams):
        """
        Update stop loss for an isolated trade.

        Example:
        ```python
        from lnmarkets_sdk.v3.models.futures_isolated import UpdateStoplossParams

        async with LNMClient(config) as client:
            params = UpdateStoplossParams(id=trade_id, value=90000)
            updated = await client.futures.isolated.update_stoploss(params)
            print(f"New stop loss: {updated.stoploss}")
        ```
        """
        return await self._client.request(
            "PUT",
            "/futures/isolated/trade/stoploss",
            params=params,
            credentials=True,
            response_model=FuturesRunningTrade,
        )

    async def update_takeprofit(self, params: UpdateTakeprofitParams):
        """
        Update take profit for an isolated trade.

        Example:
        ```python
        from lnmarkets_sdk.v3.models.futures_isolated import UpdateTakeprofitParams

        async with LNMClient(config) as client:
            params = UpdateTakeprofitParams(id=trade_id, value=10000)
            updated = await client.futures.isolated.update_takeprofit(params)
            print(f"New take profit: {updated.takeprofit}")
        ```
        """
        print(f"params: {params}")
        return await self._client.request(
            "PUT",
            "/futures/isolated/trade/takeprofit",
            params=params,
            credentials=True,
            response_model=FuturesRunningTrade,
        )

    async def get_funding_fees(
        self, params: GetIsolatedFundingFeesParams | None = None
    ):
        """
        Get funding fees for isolated trades.

        Example:
        ```python
        from lnmarkets_sdk.v3.models.futures_isolated import GetIsolatedFundingFeesParams

        async with LNMClient(config) as client:
            params = GetIsolatedFundingFeesParams(limit=10, trade_id=trade_id)
            response = await client.futures.isolated.get_funding_fees(params)
            for fee in response.data:
                print(f"Fee: {fee.fee}, Time: {fee.time}")
            if response.next_cursor:
                print(f"Next cursor: {response.next_cursor}")
        ```
        """
        return await self._client.request(
            "GET",
            "/futures/isolated/funding-fees",
            params=params,
            credentials=True,
            response_model=PaginatedResponse[FundingFees],
        )

    async def get_canceled_trades(self, params: GetClosedTradesParams | None = None):
        """
        Get canceled isolated margin trades history.

        Example:
        ```python
        from lnmarkets_sdk.v3.models.futures_isolated import GetClosedTradesParams

        async with LNMClient(config) as client:
            params = GetClosedTradesParams(limit=10)
            response = await client.futures.isolated.get_canceled_trades(params)
            for trade in response.data:
                print(f"Trade ID: {trade.id}, Canceled: {trade.canceled}")
            if response.next_cursor:
                print(f"Next cursor: {response.next_cursor}")
        ```
        """
        return await self._client.request(
            "GET",
            "/futures/isolated/trades/canceled",
            params=params,
            credentials=True,
            response_model=PaginatedResponse[FuturesCanceledTrade],
        )
