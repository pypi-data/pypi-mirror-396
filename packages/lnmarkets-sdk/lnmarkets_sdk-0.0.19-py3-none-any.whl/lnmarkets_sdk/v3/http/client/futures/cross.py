from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lnmarkets_sdk.v3.http.client import LNMClient

from lnmarkets_sdk.v3._internal.models import PaginatedResponse
from lnmarkets_sdk.v3.models.funding_fees import FundingFees
from lnmarkets_sdk.v3.models.futures_cross import (
    CancelOrderParams,
    DepositParams,
    FuturesCrossCanceledOrder,
    FuturesCrossFilledOrder,
    FuturesCrossOpenOrder,
    FuturesCrossOrderLimit,
    FuturesCrossOrderMarket,
    FuturesCrossPosition,
    FuturesCrossTransfer,
    GetCrossFundingFeesParams,
    GetFilledOrdersParams,
    GetTransfersParams,
    SetLeverageParams,
    WithdrawParams,
)


class FuturesCrossClient:
    """Client for cross margin futures endpoints."""

    def __init__(self, client: "LNMClient"):
        self._client = client

    async def new_order(
        self, params: FuturesCrossOrderLimit | FuturesCrossOrderMarket
    ) -> FuturesCrossOpenOrder | FuturesCrossFilledOrder | FuturesCrossCanceledOrder:
        """
        Place a new cross margin order.

        Example:
        ```python
        from lnmarkets_sdk.v3.models.futures_cross import FuturesCrossOrderLimit

        async with LNMClient(config) as client:
            params = FuturesCrossOrderLimit(
                type="limit",
                side="buy",
                price=100_000,
                quantity=1,
                client_id="my-order-123"
            )
            order = await client.futures.cross.new_order(params)
            print(f"Order ID: {order.id}")
        ```
        """
        return await self._client.request(
            "POST",
            "/futures/cross/order",
            params=params,
            credentials=True,
            response_model=FuturesCrossOpenOrder
            | FuturesCrossFilledOrder
            | FuturesCrossCanceledOrder,
        )

    async def get_position(self):
        """
        Get current cross margin position.

        Example:
        ```python
        async with LNMClient(config) as client:
            position = await client.futures.cross.get_position()
            print(f"Margin: {position.margin}, P&L: {position.total_pl}")
        ```
        """
        return await self._client.request(
            "GET",
            "/futures/cross/position",
            credentials=True,
            response_model=FuturesCrossPosition,
        )

    async def get_open_orders(self):
        """
        Get all open cross margin orders.

        Example:
        ```python
        async with LNMClient(config) as client:
            orders = await client.futures.cross.get_open_orders()
            for order in orders:
                print(f"Order ID: {order.id}, Price: {order.price}")
        ```
        """
        return await self._client.request(
            "GET",
            "/futures/cross/orders/open",
            credentials=True,
            response_model=list[FuturesCrossOpenOrder],
        )

    async def get_filled_orders(self, params: GetFilledOrdersParams | None = None):
        """
        Get filled cross margin orders history.

        Example:
        ```python
        from lnmarkets_sdk.v3.models.futures_cross import GetFilledOrdersParams

        async with LNMClient(config) as client:
            params = GetFilledOrdersParams(limit=10)
            response = await client.futures.cross.get_filled_orders(params)
            for order in response.data:
                print(f"Order ID: {order.id}, Type: {order.type}")
            if response.next_cursor:
                print(f"Next cursor: {response.next_cursor}")
        ```
        """
        return await self._client.request(
            "GET",
            "/futures/cross/orders/filled",
            params=params,
            credentials=True,
            response_model=PaginatedResponse[FuturesCrossFilledOrder],
        )

    async def close(
        self,
    ) -> FuturesCrossOpenOrder | FuturesCrossFilledOrder | FuturesCrossCanceledOrder:
        """
        Close cross margin position.

        Example:
        ```python
        async with LNMClient(config) as client:
            result = await client.futures.cross.close()
            print(f"Position closed: {result}")
        ```
        """
        return await self._client.request(
            "POST",
            "/futures/cross/position/close",
            credentials=True,
            response_model=FuturesCrossOpenOrder
            | FuturesCrossFilledOrder
            | FuturesCrossCanceledOrder,
        )

    async def cancel(self, params: CancelOrderParams):
        """
        Cancel a cross margin order.

        Example:
        ```python
        from lnmarkets_sdk.v3.models.futures_cross import CancelOrderParams

        async with LNMClient(config) as client:
            params = CancelOrderParams(id=order_id)
            canceled = await client.futures.cross.cancel(params)
            print(f"Canceled: {canceled.canceled}")
        ```
        """
        return await self._client.request(
            "POST",
            "/futures/cross/order/cancel",
            params=params,
            credentials=True,
            response_model=FuturesCrossCanceledOrder,
        )

    async def cancel_all(self):
        """
        Cancel all cross margin orders.

        Example:
        ```python
        async with LNMClient(config) as client:
            canceled = await client.futures.cross.cancel_all()
            print(f"Canceled {len(canceled)} orders")
        ```
        """
        return await self._client.request(
            "POST",
            "/futures/cross/orders/cancel-all",
            credentials=True,
            response_model=list[FuturesCrossCanceledOrder],
        )

    async def deposit(self, params: DepositParams):
        """
        Deposit funds to cross margin account.

        Example:
        ```python
        from lnmarkets_sdk.v3.models.futures_cross import DepositParams

        async with LNMClient(config) as client:
            params = DepositParams(amount=100_000)
            position = await client.futures.cross.deposit(params)
            print(f"New margin: {position.margin}")
        ```
        """
        return await self._client.request(
            "POST",
            "/futures/cross/deposit",
            params=params,
            credentials=True,
            response_model=FuturesCrossPosition,
        )

    async def withdraw(self, params: WithdrawParams):
        """
        Withdraw funds from cross margin account.

        Example:
        ```python
        from lnmarkets_sdk.v3.models.futures_cross import WithdrawParams

        async with LNMClient(config) as client:
            params = WithdrawParams(amount=50_000)
            position = await client.futures.cross.withdraw(params)
            print(f"Remaining margin: {position.margin}")
        ```
        """
        return await self._client.request(
            "POST",
            "/futures/cross/withdraw",
            params=params,
            credentials=True,
            response_model=FuturesCrossPosition,
        )

    async def set_leverage(self, params: SetLeverageParams):
        """
        Set leverage for cross margin trading.

        Example:
        ```python
        from lnmarkets_sdk.v3.models.futures_cross import SetLeverageParams

        async with LNMClient(config) as client:
            params = SetLeverageParams(leverage=50)
            position = await client.futures.cross.set_leverage(params)
            print(f"New leverage: {position.leverage}")
        ```
        """
        return await self._client.request(
            "PUT",
            "/futures/cross/leverage",
            params=params,
            credentials=True,
            response_model=FuturesCrossPosition,
        )

    async def get_transfers(self, params: GetTransfersParams | None = None):
        """
        Get cross margin transfer history.

        Example:
        ```python
        from lnmarkets_sdk.v3.models.futures_cross import GetTransfersParams

        async with LNMClient(config) as client:
            params = GetTransfersParams(limit=10)
            response = await client.futures.cross.get_transfers(params)
            for transfer in response.data:
                print(f"Transfer: {transfer.id}, Amount: {transfer.amount}")
            if response.next_cursor:
                print(f"Next cursor: {response.next_cursor}")
        ```
        """
        return await self._client.request(
            "GET",
            "/futures/cross/transfers",
            params=params,
            credentials=True,
            response_model=PaginatedResponse[FuturesCrossTransfer],
        )

    async def get_funding_fees(self, params: GetCrossFundingFeesParams | None = None):
        """
        Get funding fees for cross margin.

        Example:
        ```python
        from lnmarkets_sdk.v3.models.futures_cross import GetCrossFundingFeesParams

        async with LNMClient(config) as client:
            params = GetCrossFundingFeesParams(limit=10)
            response = await client.futures.cross.get_funding_fees(params)
            for fee in response.data:
                print(f"Fee: {fee.fee}, Time: {fee.time}")
            if response.next_cursor:
                print(f"Next cursor: {response.next_cursor}")
        ```
        """
        return await self._client.request(
            "GET",
            "/futures/cross/funding-fees",
            params=params,
            credentials=True,
            response_model=PaginatedResponse[FundingFees],
        )
