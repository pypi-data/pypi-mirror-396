"""Internal client utilities - not part of public API."""

import hashlib
import hmac
import json
from base64 import b64encode
from collections.abc import Mapping
from datetime import datetime
from types import UnionType
from typing import Any

import httpx
from pydantic import BaseModel, TypeAdapter, ValidationError

from .models import (
    APIAuthContext,
    APIError,
    APIException,
    APIHTTPException,
    APIMethod,
    APINetwork,
    APIValidationException,
)


def _float_to_int(value):
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def prepare_params(
    params: BaseModel | Mapping[str, object] | None,
) -> dict[str, Any] | None:
    """Convert params to dict for httpx."""
    if not params:
        return None

    if isinstance(params, BaseModel):
        params_dict = params.model_dump(mode="json", exclude_none=True, by_alias=True)
        return {key: _float_to_int(value) for key, value in params_dict.items()}
    return dict(params)


def _create_signature(
    secret: str, method: APIMethod, path: str, data: str
) -> tuple[str, str]:
    """Create HMAC signature for authentication."""
    timestamp = str(int(datetime.now().timestamp() * 1000))
    payload = timestamp + method.lower() + path + data
    hashed = hmac.new(
        bytes(secret, "utf-8"), bytes(payload, "utf-8"), hashlib.sha256
    ).digest()
    signature = b64encode(hashed).decode("utf-8")
    return timestamp, signature


def create_auth_headers(
    auth: APIAuthContext, method: APIMethod, path: str, data: str
) -> dict[str, str]:
    """Build authentication headers."""
    timestamp, signature = _create_signature(auth.secret, method, path, data)
    return {
        "lnm-access-key": auth.key,
        "lnm-access-passphrase": auth.passphrase,
        "lnm-access-timestamp": timestamp,
        "lnm-access-signature": signature,
    }


def get_hostname(network: APINetwork) -> str:
    """Get API hostname based on network."""
    return (
        "api.testnet4.lnmarkets.com" if network == "testnet4" else "api.lnmarkets.com"
    )


def parse_response[T](
    response: httpx.Response,
    model: type[T] | UnionType | None = None,
) -> T:
    """Parse and validate API response."""
    if not response.is_success:
        try:
            error_data = response.json()
            error = APIError.model_validate(error_data)
            raise APIException(
                f"API error: {response.status_code} [{error.code}] - {error.message}",
                error=error,
            )
        except (json.JSONDecodeError, ValidationError) as exc:
            raise APIHTTPException(
                f"HTTP {response.status_code}: {response.text}",
                status_code=response.status_code,
                response=response,
            ) from exc

    try:
        data = response.json()
    except json.JSONDecodeError as e:
        raise APIException(f"Failed to decode JSON response: {e}") from e

    if model is None:
        return data

    try:
        adapter = TypeAdapter(model)
        return adapter.validate_python(data)
    except ValidationError as e:
        raise APIValidationException(
            f"Response validation failed: {e}",
            validation_error=e,
        ) from e
