from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lnmarkets_sdk.v3.http.client import LNMClient

from lnmarkets_sdk.v3.models.oracle import (
    GetIndexParams,
    GetLastPriceParams,
    OracleIndex,
    OracleLastPrice,
)


class OracleClient:
    """Client for oracle data endpoints."""

    def __init__(self, client: "LNMClient"):
        self._client = client

    async def get_index(self, params: GetIndexParams | None = None):
        """
        Get index data.

        Example:
        ```python
        from lnmarkets_sdk.v3.models.oracle import GetIndexParams

        async with LNMClient(config) as client:
            params = GetIndexParams(limit=10, from_="2023-05-23T09:52:57.863Z")
            indices = await client.oracle.get_index(params)
            for index in indices:
                print(f"Index: {index.index}, Time: {index.time}")
        ```
        """
        return await self._client.request(
            "GET",
            "/oracle/index",
            params=params,
            credentials=False,
            response_model=list[OracleIndex],
        )

    async def get_last_price(
        self, params: GetLastPriceParams | None = None
    ) -> list[OracleLastPrice]:
        """
        Get last price data.

        Example:
        ```python
        from lnmarkets_sdk.v3.models.oracle import GetLastPriceParams

        async with LNMClient(config) as client:
            params = GetLastPriceParams(limit=10, from_="2023-05-23T09:52:57.863Z")
            prices = await client.oracle.get_last_price(params)
            for price in prices:
                print(f"Price: {price.last_price}, Time: {price.time}")
        ```
        """
        return await self._client.request(
            "GET",
            "/oracle/last-price",
            params=params,
            credentials=False,
            response_model=list[OracleLastPrice],
        )
