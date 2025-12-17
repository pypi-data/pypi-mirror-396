from typing import Literal

from pydantic import BaseModel, Field, SkipValidation

from lnmarkets_sdk.v3._internal.models import UUID, BaseConfig, FromToLimitParams

SwapAssets = Literal["BTC", "USD"]


class Swap(BaseModel, BaseConfig):
    created_at: SkipValidation[str]
    id: SkipValidation[UUID]
    in_amount: SkipValidation[float]
    in_asset: SkipValidation[str]
    out_amount: SkipValidation[float]
    out_asset: SkipValidation[str]


class CreateSwapOutput(BaseModel, BaseConfig):
    in_amount: SkipValidation[float] = Field(
        ...,
        description="Amount to swap (in satoshis if BTC, in dollars with 2 decimal places if USD)",
    )
    in_asset: SkipValidation[SwapAssets] = Field(..., description="Asset to swap from")
    out_amount: SkipValidation[float] = Field(
        ...,
        description="Amount received after conversion (in satoshis if BTC, in dollars with 2 decimal places if USD)",
    )
    out_asset: SkipValidation[SwapAssets] = Field(..., description="Asset to swap to")


class NewSwapParams(BaseModel, BaseConfig):
    in_amount: float = Field(
        ..., description="Amount to swap (in satoshis if BTC, in cents if USD)"
    )
    in_asset: SwapAssets = Field(..., description="Asset to swap from")
    out_asset: SwapAssets = Field(..., description="Asset to swap to")


class BestPriceParams(BaseModel, BaseConfig):
    in_amount: float
    in_asset: SwapAssets
    out_asset: SwapAssets


class BestPriceResponse(BaseModel, BaseConfig):
    ask_price: SkipValidation[float] = Field(..., description="Best ask price")
    bid_price: SkipValidation[float] = Field(..., description="Best bid price")


class GetSwapsParams(FromToLimitParams): ...
