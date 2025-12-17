from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lnmarkets_sdk.v3.http.client import LNMClient

from lnmarkets_sdk.v3._internal.models import PaginatedResponse
from lnmarkets_sdk.v3.models.synthetic_usd import (
    BestPriceResponse,
    CreateSwapOutput,
    GetSwapsParams,
    NewSwapParams,
    Swap,
)


class SyntheticUSDClient:
    """Client for Synthetic USD swap endpoints."""

    def __init__(self, client: "LNMClient"):
        self._client = client

    async def get_best_price(self):
        """
        Get best price for USD swaps.

        Example:
        ```python
        async with LNMClient(config) as client:
            price = await client.synthetic_usd.get_best_price()
            print(f"Ask: {price.ask_price}, Bid: {price.bid_price}")
        ```
        """
        return await self._client.request(
            "GET",
            "/synthetic-usd/best-price",
            credentials=False,
            response_model=BestPriceResponse,
        )

    async def get_swaps(self, params: GetSwapsParams | None = None):
        """
        Get swap history.

        Example:
        ```python
        from lnmarkets_sdk.v3.models.synthetic_usd import GetSwapsParams

        async with LNMClient(config) as client:
            params = GetSwapsParams(limit=10)
            response = await client.synthetic_usd.get_swaps(params)
            for swap in response.data:
                print(f"Swap: {swap.in_asset} -> {swap.out_asset}")
            if response.next_cursor:
                print(f"Next cursor: {response.next_cursor}")
        ```
        """
        return await self._client.request(
            "GET",
            "/synthetic-usd/swaps",
            params=params,
            credentials=True,
            response_model=PaginatedResponse[Swap],
        )

    async def new_swap(self, params: NewSwapParams):
        """
        Create a new USD swap.

        Example:
        ```python
        from lnmarkets_sdk.v3.models.synthetic_usd import NewSwapParams

        async with LNMClient(config) as client:
            params = NewSwapParams(
                in_amount=100,
                in_asset="USD",
                out_asset="BTC"
            )
            swap = await client.synthetic_usd.new_swap(params)
            print(f"Received: {swap.out_amount} {swap.out_asset}")
        ```
        """
        return await self._client.request(
            "POST",
            "/synthetic-usd/swap",
            params=params,
            credentials=True,
            response_model=CreateSwapOutput,
        )
