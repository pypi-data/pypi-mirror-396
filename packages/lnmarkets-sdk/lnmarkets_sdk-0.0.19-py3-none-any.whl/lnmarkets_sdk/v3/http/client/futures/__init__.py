from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lnmarkets_sdk.v3.http.client import LNMClient

from lnmarkets_sdk.v3._internal.models import PaginatedResponse
from lnmarkets_sdk.v3.models.funding_fees import FundingSettlement
from lnmarkets_sdk.v3.models.futures_data import (
    Candle,
    GetCandlesParams,
    GetFundingSettlementsParams,
    Leaderboard,
    Ticker,
)

from .cross import FuturesCrossClient
from .isolated import FuturesIsolatedClient


class FuturesClient:
    """Client for futures trading endpoints."""

    def __init__(self, client: "LNMClient"):
        self._client = client
        self.isolated = FuturesIsolatedClient(client)
        self.cross = FuturesCrossClient(client)

    async def get_ticker(self):
        """
        Get current futures ticker data.

        Example:
        ```python
        async with LNMClient(config) as client:
            ticker = await client.futures.get_ticker()
            print(f"Index: {ticker.index}, Last Price: {ticker.last_price}")
            print(f"Funding Rate: {ticker.funding_rate}")
            if ticker.prices:
                print(f"Best bid: {ticker.prices[0].bid_price}")
        ```
        """
        return await self._client.request(
            "GET",
            "/futures/ticker",
            credentials=False,
            response_model=Ticker,
        )

    async def get_leaderboard(self):
        """
        Get futures trading leaderboard.

        Example:
        ```python
        async with LNMClient(config) as client:
            leaderboard = await client.futures.get_leaderboard()
            if leaderboard.daily:
                print(f"Daily top: {leaderboard.daily[0].username}")
            if leaderboard.all_time:
                print(f"All-time top: {leaderboard.all_time[0].username}")
        ```
        """
        return await self._client.request(
            "GET",
            "/futures/leaderboard",
            credentials=False,
            response_model=Leaderboard,
        )

    async def get_candles(self, params: GetCandlesParams):
        """
        Get OHLC candle data.

        Example:
        ```python
        from lnmarkets_sdk.v3.models.futures_data import GetCandlesParams

        async with LNMClient(config) as client:
            params = GetCandlesParams(
                from_="2023-05-23T09:52:57.863Z",
                range="1h",
                limit=100,
                to="2023-05-24T09:52:57.863Z"
            )
            response = await client.futures.get_candles(params)
            for candle in response.data:
                print(f"Time: {candle.time}, OHLC: {candle.open}/{candle.high}/{candle.low}/{candle.close}")
            if response.next_cursor:
                print(f"Next cursor: {response.next_cursor}")
        ```
        """
        return await self._client.request(
            "GET",
            "/futures/candles",
            params=params,
            credentials=False,
            response_model=PaginatedResponse[Candle],
        )

    async def get_funding_settlements(
        self, params: GetFundingSettlementsParams | None = None
    ):
        """
        Get funding settlement history.

        Example:
        ```python
        from lnmarkets_sdk.v3.models.futures_data import GetFundingSettlementsParams

        async with LNMClient(config) as client:
            params = GetFundingSettlementsParams(limit=10)
            response = await client.futures.get_funding_settlements(params)
            for settlement in response.data:
                print(f"Rate: {settlement.funding_rate}, Price: {settlement.fixing_price}")
            if response.next_cursor:
                print(f"Next cursor: {response.next_cursor}")
        ```
        """
        return await self._client.request(
            "GET",
            "/futures/funding-settlements",
            params=params,
            credentials=False,
            response_model=PaginatedResponse[FundingSettlement],
        )
