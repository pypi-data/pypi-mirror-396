from typing import Literal

from pydantic import BaseModel, Field, SkipValidation

from lnmarkets_sdk.v3._internal.models import BaseConfig, FromToLimitParams

CandleResolution = Literal[
    "1m",
    "3m",
    "5m",
    "10m",
    "15m",
    "30m",
    "45m",
    "1h",
    "2h",
    "3h",
    "4h",
    "1d",
    "1w",
    "1month",
    "3months",
]


class PriceBucket(BaseModel, BaseConfig):
    """Price bucket for ticker."""

    ask_price: SkipValidation[float] | None = Field(
        default=None, description="Current best ask/sell price available (in USD)"
    )
    bid_price: SkipValidation[float] | None = Field(
        default=None, description="Current best bid price available (in USD)"
    )
    max_size: SkipValidation[int] = Field(
        ..., description="Maximum order size (in BTC)"
    )
    min_size: SkipValidation[int] = Field(
        ..., description="Minimum order size (in BTC)"
    )


class Ticker(BaseModel, BaseConfig):
    """Futures ticker data."""

    funding_rate: SkipValidation[float] = Field(..., description="Current funding rate")
    funding_time: SkipValidation[str] = Field(
        ...,
        description="ISO date string when the next funding rate will be established",
    )
    index: SkipValidation[float] = Field(
        ...,
        description="Bitcoin price index aggregated from multiple exchanges (in USD)",
    )
    last_price: SkipValidation[float] = Field(
        ..., description="Last executed trade price on the platform (in USD)"
    )
    prices: list[PriceBucket] = Field(
        ..., description="Price buckets for different order sizes"
    )


class Candle(BaseModel, BaseConfig):
    """OHLC candlestick data."""

    close: SkipValidation[float] = Field(..., description="Closing price")
    high: SkipValidation[float] = Field(..., description="Highest price")
    low: SkipValidation[float] = Field(..., description="Lowest price")
    open: SkipValidation[float] = Field(..., description="Opening price")
    time: SkipValidation[str] = Field(..., description="Timestamp in ISO format")
    volume: SkipValidation[float] = Field(..., description="Trading volume")


class UserInfo(BaseModel, BaseConfig):
    """User leaderboard info."""

    direction: SkipValidation[int]
    pl: SkipValidation[float]
    username: SkipValidation[str]


class Leaderboard(BaseModel, BaseConfig):
    """Futures leaderboard data."""

    all_time: list[UserInfo] = Field(
        validation_alias="all-time", serialization_alias="all-time"
    )
    daily: list[UserInfo]
    monthly: list[UserInfo]
    weekly: list[UserInfo]


class GetCandlesParams(BaseModel, BaseConfig):
    from_: str = Field(
        ...,
        validation_alias="from",
        serialization_alias="from",
        description="Start date as a string value in ISO format",
    )
    range: CandleResolution = Field(
        default="1m", description="Resolution of the OHLC candle"
    )
    limit: int = Field(
        default=1000,
        ge=1,
        le=1000,
        description="Number of entries to return (max 1000, default 1000)",
    )
    to: str | None = Field(
        default=None, description="End date as a string value in ISO format"
    )
    cursor: str | None = Field(
        default=None, description="Pagination cursor for fetching next page"
    )


class GetFundingSettlementsParams(FromToLimitParams): ...
