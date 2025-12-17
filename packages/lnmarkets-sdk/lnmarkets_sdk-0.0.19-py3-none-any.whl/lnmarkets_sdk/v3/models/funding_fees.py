from pydantic import BaseModel, Field, SkipValidation

from lnmarkets_sdk.v3._internal.models import UUID, BaseConfig


class FundingFees(BaseModel, BaseConfig):
    """Funding fee entry."""

    fee: SkipValidation[float] = Field(..., description="Funding fee amount")
    settlement_id: SkipValidation[UUID] = Field(
        ..., description="Funding settlement ID"
    )
    time: SkipValidation[str] = Field(..., description="Timestamp in ISO format")
    trade_id: SkipValidation[UUID] | None = Field(
        default=None, description="Associated trade ID"
    )


class FundingSettlement(BaseModel, BaseConfig):
    """Funding settlement entry."""

    funding_rate: SkipValidation[float] = Field(..., description="Funding rate")
    id: SkipValidation[UUID] = Field(..., description="Funding settlement ID")
    fixing_price: SkipValidation[float] = Field(..., description="Fixing price")
    time: SkipValidation[str] = Field(..., description="Funding settlement time")
