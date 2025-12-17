from typing import Literal

from pydantic import BaseModel, Field, SkipValidation, model_validator

from lnmarkets_sdk.v3._internal.models import UUID, BaseConfig, FromToLimitParams


class FuturesOrder(BaseModel, BaseConfig):
    leverage: float = Field(..., description="Leverage of the position")
    side: Literal["buy", "sell"] = Field(
        ..., description="Trade side: buy (long) or sell (short)"
    )
    stoploss: float | None = Field(
        default=None,
        ge=0,
        multiple_of=0.5,
        description="Stop loss price level (0 if not set)",
    )
    takeprofit: float | None = Field(
        default=None,
        ge=0,
        multiple_of=0.5,
        description="Take profit price level (0 if not set)",
    )
    margin: int | None = Field(
        default=None, description="Margin of the position (in satoshis)"
    )
    quantity: int | None = Field(
        default=None, description="Quantity of the position (in USD)"
    )
    price: float | None = Field(
        default=None, gt=0, multiple_of=0.5, description="Price of the limit order"
    )
    type: Literal["limit", "market"] = Field(
        ..., description="Trade type: limit (limit) or market (market)"
    )
    client_id: str | None = Field(
        default=None, description="Unique client ID for the trade"
    )

    @model_validator(mode="after")
    def validate_schema(self):
        if (self.quantity is None) == (self.margin is None):
            raise ValueError("Exactly one of quantity or margin must be set")
        if self.type == "limit" and self.price is None:
            raise ValueError("'price' is required when type='limit'")
        if self.type == "market" and self.price is not None:
            raise ValueError("'price' must not be set when type='market'")
        return self


class FuturesTrade(BaseModel, BaseConfig):
    canceled: SkipValidation[bool]
    closed: SkipValidation[bool]
    closed_at: SkipValidation[str] | None = None
    closing_fee: SkipValidation[float]
    created_at: SkipValidation[str]
    entry_margin: SkipValidation[float] | None = None
    entry_price: SkipValidation[float] | None = None
    exit_price: SkipValidation[float] | None = None
    filled_at: SkipValidation[str] | None = None
    id: SkipValidation[UUID]
    leverage: SkipValidation[float]
    liquidation: SkipValidation[float]
    maintenance_margin: SkipValidation[float]
    margin: SkipValidation[float]
    open: SkipValidation[bool]
    opening_fee: SkipValidation[float]
    pl: SkipValidation[float]
    price: SkipValidation[float]
    quantity: SkipValidation[float]
    running: SkipValidation[bool]
    side: SkipValidation[Literal["buy", "sell"]]
    stoploss: SkipValidation[float]
    sum_funding_fees: SkipValidation[float]
    takeprofit: SkipValidation[float]
    type: SkipValidation[Literal["limit", "market"]]
    client_id: SkipValidation[str] | None = None


class FuturesOpenTrade(FuturesTrade):
    canceled: SkipValidation[bool] = False
    closed: SkipValidation[bool] = False
    closed_at: None = None
    filled_at: None = None
    running: SkipValidation[bool] = False
    type: SkipValidation[Literal["limit"]] = "limit"


class FuturesRunningTrade(FuturesTrade):
    canceled: SkipValidation[bool] = False
    closed: SkipValidation[bool] = False
    closed_at: None = None
    filled_at: SkipValidation[str] | None = None
    running: SkipValidation[bool] = True


class FuturesClosedTrade(FuturesTrade):
    canceled: SkipValidation[bool] = False
    closed: SkipValidation[bool] = True
    closed_at: SkipValidation[str] = ""
    exit_price: SkipValidation[float] = 0.0
    filled_at: SkipValidation[str] = ""
    open: SkipValidation[bool] = False
    running: SkipValidation[bool] = False


class FuturesCanceledTrade(FuturesTrade):
    canceled: SkipValidation[bool] = True
    closed: SkipValidation[bool] = False
    closed_at: SkipValidation[str] = ""
    filled_at: None = None
    open: SkipValidation[bool] = False
    running: SkipValidation[bool] = False
    type: SkipValidation[Literal["limit"]] = "limit"


class AddMarginParams(BaseModel, BaseConfig):
    amount: int = Field(..., gt=0, description="Amount of margin to add (in satoshis)")
    id: UUID = Field(..., description="Trade ID")


class CancelTradeParams(BaseModel, BaseConfig):
    id: UUID = Field(..., description="Trade ID to cancel")


class CashInParams(BaseModel, BaseConfig):
    amount: int = Field(..., gt=0, description="Amount to cash in (in satoshis)")
    id: UUID = Field(..., description="Trade ID")


class CloseTradeParams(BaseModel, BaseConfig):
    id: UUID = Field(..., description="Trade ID to close")


class UpdateStoplossParams(BaseModel, BaseConfig):
    id: UUID = Field(..., description="Trade ID")
    value: float = Field(..., description="New stop loss price level")


class UpdateTakeprofitParams(BaseModel, BaseConfig):
    id: UUID = Field(..., description="Trade ID")
    value: float = Field(..., description="New take profit price level")


class GetClosedTradesParams(FromToLimitParams): ...


class GetIsolatedFundingFeesParams(FromToLimitParams):
    trade_id: UUID | None = None
