from pydantic import BaseModel, Field, SkipValidation

from lnmarkets_sdk.v3._internal.models import BaseConfig, FromToLimitParams


class OracleIndex(BaseModel, BaseConfig):
    index: SkipValidation[float] = Field(..., description="Index value")
    time: SkipValidation[str] = Field(
        ..., description="Time as a string value in ISO format"
    )


class OracleLastPrice(BaseModel, BaseConfig):
    last_price: SkipValidation[float] = Field(..., description="Last price value")
    time: SkipValidation[str] = Field(
        ..., description="Timestamp as a string value in ISO format"
    )


class GetIndexParams(FromToLimitParams): ...


class GetLastPriceParams(FromToLimitParams): ...
