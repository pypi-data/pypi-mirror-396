from typing import Literal

from pydantic import BaseModel, Field, SkipValidation

from lnmarkets_sdk.v3._internal.models import UUID, BaseConfig, FromToLimitParams


class Account(BaseModel, BaseConfig):
    username: SkipValidation[str] = Field(..., description="Username of the user")
    synthetic_usd_balance: SkipValidation[float] = Field(
        ..., description="Synthetic USD balance of the user (in dollars)"
    )
    balance: SkipValidation[float] = Field(
        ..., description="Balance of the user (in satoshis)"
    )
    fee_tier: SkipValidation[int] = Field(..., description="Fee tier of the user")
    email: SkipValidation[str] | None = Field(
        default=None, description="Email of the user"
    )
    id: SkipValidation[UUID] = Field(
        ..., description="Unique identifier for this account"
    )
    linking_public_key: SkipValidation[str] | None = Field(
        default=None, description="Public key of the user"
    )


class OnChainDeposit(BaseModel, BaseConfig):
    """On-chain deposit item."""

    amount: SkipValidation[float] = Field(..., description="The amount of the deposit")
    block_height: SkipValidation[int] | None = Field(
        default=None, description="The block height of the deposit"
    )
    confirmations: SkipValidation[int] = Field(
        ..., description="The number of confirmations of the deposit"
    )
    created_at: SkipValidation[str] = Field(
        ..., description="The date the deposit was created"
    )
    id: SkipValidation[UUID] = Field(
        ..., description="The unique identifier for the deposit"
    )
    status: SkipValidation[Literal["MEMPOOL", "CONFIRMED", "IRREVERSIBLE"]] = Field(
        ..., description="The status of the deposit"
    )
    tx_id: SkipValidation[str] = Field(
        ..., description="The transaction ID of the deposit"
    )


class InternalDeposit(BaseModel, BaseConfig):
    """Internal deposit item."""

    amount: SkipValidation[float] = Field(
        ..., description="Amount of the deposit (in satoshis)"
    )
    created_at: SkipValidation[str] = Field(
        ..., description="Timestamp when the deposit was created"
    )
    from_username: SkipValidation[str] = Field(
        ..., description="Username of the sender"
    )
    id: SkipValidation[UUID] = Field(
        ..., description="Unique identifier for this deposit"
    )


class InternalWithdrawal(BaseModel, BaseConfig):
    """Internal withdrawal item."""

    amount: SkipValidation[float] = Field(
        ..., description="Amount of the transfer (in satoshis)"
    )
    created_at: SkipValidation[str] = Field(
        ..., description="Timestamp when the transfer was created"
    )
    id: SkipValidation[UUID] = Field(
        ..., description="Unique identifier for this transfer"
    )
    to_username: SkipValidation[str] = Field(
        ..., description="Username of the recipient"
    )


class LightningDeposits(BaseModel, BaseConfig):
    amount: SkipValidation[float] | None = Field(
        None, description="Amount of the deposit (in satoshis)"
    )
    comment: SkipValidation[str] | None = Field(
        default=None, description="Comment of the deposit"
    )
    created_at: SkipValidation[str] = Field(
        ..., description="Timestamp when the deposit was created"
    )
    id: SkipValidation[UUID] = Field(
        ..., description="Unique identifier for this deposit"
    )
    payment_hash: SkipValidation[str] | None = Field(
        default=None, description="Payment hash of the deposit"
    )
    settled_at: SkipValidation[str] | None = Field(
        default=None, description="Timestamp when the deposit was settled"
    )


class LightningWithdrawal(BaseModel, BaseConfig):
    """Lightning withdrawal item."""

    amount: SkipValidation[float] = Field(
        ..., description="Amount of the withdrawal (in satoshis)"
    )
    created_at: SkipValidation[str] = Field(
        ..., description="Timestamp when the withdrawal was created"
    )
    fee: SkipValidation[float] = Field(
        ..., description="Fee of the withdrawal (in satoshis)"
    )
    id: SkipValidation[UUID] = Field(
        ..., description="Unique identifier for the withdrawal"
    )
    payment_hash: SkipValidation[str] = Field(
        ..., description="Payment hash of the withdrawal"
    )
    status: SkipValidation[Literal["failed", "processed", "processing"]] = Field(
        ..., description="Status of the withdrawal"
    )


class OnChainWithdrawal(BaseModel, BaseConfig):
    """On-chain withdrawal item."""

    address: SkipValidation[str] = Field(..., description="Address to withdraw to")
    amount: SkipValidation[float] = Field(..., description="Amount to withdraw")
    created_at: SkipValidation[str] = Field(
        ..., description="Timestamp when the withdrawal was created"
    )
    fee: SkipValidation[float] | None = Field(
        default=None, description="Fee of the withdrawal (in satoshis)"
    )
    id: SkipValidation[UUID] = Field(
        ..., description="Unique identifier for the withdrawal"
    )
    status: SkipValidation[
        Literal["canceled", "pending", "processed", "processing", "rejected"]
    ] = Field(..., description="Status of the withdrawal")
    tx_id: SkipValidation[str] | None = Field(
        default=None, description="Transaction ID of the withdrawal"
    )


class DepositLightningResponse(BaseModel, BaseConfig):
    deposit_id: SkipValidation[UUID] = Field(..., description="Deposit ID")
    payment_request: SkipValidation[str] = Field(
        ..., description="Lightning payment request invoice"
    )


class WithdrawInternalResponse(BaseModel, BaseConfig):
    id: SkipValidation[UUID]
    created_at: SkipValidation[str]
    from_uid: SkipValidation[UUID]
    to_uid: SkipValidation[UUID]
    amount: SkipValidation[float]


class WithdrawOnChainResponse(BaseModel, BaseConfig):
    id: SkipValidation[UUID]
    uid: SkipValidation[UUID]
    amount: SkipValidation[float]
    address: SkipValidation[str]
    created_at: SkipValidation[str]
    updated_at: SkipValidation[str]
    block_id: SkipValidation[str] | None
    confirmation_height: SkipValidation[int] | None
    fee: SkipValidation[float] | None
    status: SkipValidation[Literal["pending"]]
    tx_id: None = None


class GetBitcoinAddressResponse(BaseModel, BaseConfig):
    address: SkipValidation[str] = Field(..., description="Bitcoin address")


class AddBitcoinAddressResponse(BaseModel, BaseConfig):
    address: SkipValidation[str] = Field(
        ..., description="The generated Bitcoin address"
    )
    created_at: SkipValidation[str] = Field(
        ..., description="The creation time of the address"
    )


class AddBitcoinAddressParams(BaseModel, BaseConfig):
    format: Literal["p2tr", "p2wpkh"] | None = Field(
        None, description="The format of the Bitcoin address"
    )


class DepositLightningParams(BaseModel, BaseConfig):
    amount: int = Field(..., gt=0, description="Amount to deposit (in satoshis)")
    comment: str | None = Field(default=None, description="Comment for the deposit")
    description_hash: str | None = Field(
        default=None,
        pattern=r"^[a-f0-9]{64}$",
        description="Description hash for the deposit",
    )


class WithdrawLightningParams(BaseModel, BaseConfig):
    invoice: str = Field(..., description="Lightning invoice to pay")


class WithdrawLightningResponse(BaseModel, BaseConfig):
    amount: SkipValidation[float] = Field(
        ..., description="Amount of the withdrawal (in satoshis)"
    )
    id: SkipValidation[UUID] = Field(
        ..., description="Unique identifier for the withdrawal"
    )
    max_fees: SkipValidation[float] = Field(
        ..., description="Maximum fees of the withdrawal (in satoshis)"
    )
    payment_hash: SkipValidation[str] = Field(
        ..., description="Payment hash of the withdrawal"
    )


class WithdrawInternalParams(BaseModel, BaseConfig):
    amount: float = Field(..., gt=0, description="Amount to withdraw (in satoshis)")
    to_username: str = Field(..., description="Username of the recipient")


class WithdrawOnChainParams(BaseModel, BaseConfig):
    address: str = Field(..., description="Bitcoin address to withdraw to")
    amount: float = Field(..., gt=0, description="Amount to withdraw (in satoshis)")


class GetLightningDepositsParams(FromToLimitParams):
    settled: bool | None = Field(default=None, description="Filter by settled deposits")


class GetLightningWithdrawalsParams(FromToLimitParams):
    status: Literal["failed", "processed", "processing"] | None = Field(
        default=None, description="Filter by withdrawal status"
    )


class GetInternalDepositsParams(FromToLimitParams): ...


class GetInternalWithdrawalsParams(FromToLimitParams): ...


class GetOnChainDepositsParams(FromToLimitParams):
    status: Literal["MEMPOOL", "CONFIRMED", "IRREVERSIBLE"] | None = Field(
        default=None, description="Filter by deposit status"
    )


class GetOnChainWithdrawalsParams(FromToLimitParams):
    status: (
        Literal["canceled", "pending", "processed", "processing", "rejected"] | None
    ) = Field(default=None, description="Filter by withdrawal status")


class Notification(BaseModel, BaseConfig):
    """Account notification model."""

    id: SkipValidation[UUID] = Field(
        ..., description="Unique identifier for the notification"
    )
    created_at: SkipValidation[str] = Field(
        ..., description="Timestamp when the notification was created"
    )
    message: SkipValidation[str] = Field(..., description="Notification message")
    read: SkipValidation[bool] = Field(
        default=False, description="Whether the notification has been read"
    )
    type: SkipValidation[str] | None = Field(
        default=None, description="Type of notification"
    )


class GetNotificationsParams(FromToLimitParams): ...
