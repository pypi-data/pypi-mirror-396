"""Internal HTTP client - not part of public API."""

import json
import re
from collections.abc import Mapping
from urllib.parse import urlencode

import httpx
from pydantic import BaseModel

from .models import APIAuthContext, APIMethod
from .utils import create_auth_headers, prepare_params


class BaseClient:
    """Internal HTTP client for making requests."""

    def __init__(
        self,
        base_url: str,
        timeout: float,
        auth: APIAuthContext | None = None,
        custom_headers: dict[str, str] | None = None,
    ):
        self.base_url = base_url
        self.timeout = timeout
        self.auth = auth
        self.custom_headers = custom_headers or {}
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "BaseClient":
        """Enter async context manager."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={**self.custom_headers},
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context manager."""
        if self._client:
            await self._client.aclose()

    async def request(
        self,
        method: APIMethod,
        path: str,
        params: BaseModel | Mapping[str, object] | None = None,
        credentials: bool = False,
    ) -> httpx.Response:
        """Make HTTP request and return response."""
        if not self._client:
            raise RuntimeError("Client must be used within async context manager")

        params_dict = prepare_params(params)
        headers = {}

        if credentials:
            if not self.auth:
                raise ValueError("Authentication required but no credentials provided")

            data = ""
            if params_dict:
                if method == "GET":
                    data = f"?{urlencode(params_dict)}"
                    data = re.sub(r"=(True)", "=true", data)
                    data = re.sub(r"=(False)", "=false", data)
                else:
                    data = json.dumps(params_dict, separators=(",", ":"))
                    headers.update({"Content-Type": "application/json"})

            auth_headers = create_auth_headers(self.auth, method, f"/v3{path}", data)
            headers.update(auth_headers)

        # Use httpx native parameter handling
        if method == "GET":
            return await self._client.request(
                method, path, params=params_dict, headers=headers if headers else None
            )
        else:
            return await self._client.request(
                method, path, json=params_dict, headers=headers if headers else None
            )
