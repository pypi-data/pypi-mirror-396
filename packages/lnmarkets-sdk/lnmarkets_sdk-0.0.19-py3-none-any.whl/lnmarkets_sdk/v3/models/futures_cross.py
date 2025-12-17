from typing import Literal

from pydantic import BaseModel, Field, SkipValidation

from lnmarkets_sdk.v3._internal.models import UUID, BaseConfig, FromToLimitParams


class FuturesCrossOrderSideQuantity(BaseModel, BaseConfig):
    side: Literal["buy", "sell"] = Field(
        ..., description="Trade side: buy (long) or sell (short)"
    )
    quantity: int = Field(..., gt=0, description="Quantity of the position")
    client_id: str


class FuturesCrossOrderLimit(FuturesCrossOrderSideQuantity):
    type: Literal["limit"] = Field(..., description="Trade type: limit")
    price: float = Field(
        ..., gt=0, multiple_of=0.5, description="Price of the limit order"
    )


class FuturesCrossOrderMarket(FuturesCrossOrderSideQuantity):
    type: Literal["market"] = Field(..., description="Trade type: market")
    price: None = None


class FuturesCrossOpenOrder(BaseModel, BaseConfig):
    canceled: SkipValidation[Literal[False]] = False
    canceled_at: None = None
    created_at: SkipValidation[str]
    filled: SkipValidation[bool] = False
    filled_at: None = None
    id: SkipValidation[UUID]
    open: SkipValidation[bool] = True
    price: SkipValidation[float]
    quantity: SkipValidation[float]
    side: SkipValidation[Literal["buy", "sell"]]
    trading_fee: SkipValidation[float]
    type: SkipValidation[Literal["limit"]]
    client_id: SkipValidation[str] | None = None


class FuturesCrossFilledOrder(BaseModel, BaseConfig):
    canceled: SkipValidation[bool] = False
    canceled_at: None = None
    created_at: SkipValidation[str]
    filled: SkipValidation[bool] = True
    filled_at: SkipValidation[str] | None = Field(
        default=None, description="Timestamp when the order was filled"
    )
    id: SkipValidation[UUID]
    open: SkipValidation[bool] = False
    price: SkipValidation[float]
    quantity: SkipValidation[float]
    side: SkipValidation[Literal["buy", "sell"]]
    trading_fee: SkipValidation[float]
    type: SkipValidation[Literal["limit", "liquidation", "market"]]
    client_id: SkipValidation[str] | None = Field(default=None, description="Client ID")


class FuturesCrossCanceledOrder(BaseModel, BaseConfig):
    canceled: SkipValidation[bool] = True
    canceled_at: SkipValidation[str] | None
    created_at: SkipValidation[str]
    filled: SkipValidation[bool] = False
    filled_at: None = None
    id: SkipValidation[UUID]
    open: SkipValidation[bool] = False
    price: SkipValidation[float]
    quantity: SkipValidation[float]
    side: SkipValidation[Literal["buy", "sell"]]
    trading_fee: SkipValidation[float]
    type: SkipValidation[Literal["limit"]]
    client_id: SkipValidation[str] | None = Field(default=None, description="Client ID")


class FuturesCrossPosition(BaseModel, BaseConfig):
    delta_pl: SkipValidation[float] = Field(..., description="Delta P&L")
    entry_price: SkipValidation[float] | None = Field(
        default=None, description="Entry price"
    )
    funding_fees: SkipValidation[float] = Field(..., description="Funding fees")
    id: SkipValidation[UUID] = Field(..., description="Position ID")
    initial_margin: SkipValidation[float] = Field(..., description="Initial margin")
    leverage: SkipValidation[int] = Field(..., gt=0, description="Leverage")
    liquidation: SkipValidation[float] | None = Field(
        default=None, description="Liquidation price"
    )
    maintenance_margin: SkipValidation[float] = Field(
        ..., description="Maintenance margin"
    )
    margin: SkipValidation[float] = Field(..., description="Current margin")
    quantity: SkipValidation[float] = Field(..., description="Position quantity")
    running_margin: SkipValidation[float] = Field(..., description="Running margin")
    total_pl: SkipValidation[float] = Field(..., description="Total P&L")
    trading_fees: SkipValidation[float] = Field(..., description="Trading fees")
    updated_at: SkipValidation[str] = Field(..., description="Last update timestamp")


class FuturesCrossTransfer(BaseModel, BaseConfig):
    amount: SkipValidation[float]
    id: SkipValidation[UUID]
    time: SkipValidation[str]


class DepositParams(BaseModel, BaseConfig):
    amount: int = Field(..., gt=0, description="Amount to deposit (in satoshis)")


class WithdrawParams(BaseModel, BaseConfig):
    amount: int = Field(..., gt=0, description="Amount to withdraw (in satoshis)")


class SetLeverageParams(BaseModel, BaseConfig):
    leverage: float = Field(
        ..., ge=1, le=100, description="Leverage (between 1 and 100)"
    )


class CancelOrderParams(BaseModel, BaseConfig):
    id: UUID = Field(..., description="Cross order ID to cancel")


class GetFilledOrdersParams(FromToLimitParams): ...


class GetTransfersParams(FromToLimitParams): ...


class GetCrossFundingFeesParams(FromToLimitParams): ...
