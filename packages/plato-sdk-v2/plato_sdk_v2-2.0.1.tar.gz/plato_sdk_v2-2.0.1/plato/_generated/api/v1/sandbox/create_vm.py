"""Create Vm"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status
from plato._generated.models.create_vmrequest import CreateVMRequest
from plato._generated.models.create_vmresponse import CreateVMResponse


def _build_request_args(
    body: CreateVMRequest,
    authorization: str | None = None,
    x_api_key: str | None = None,
) -> dict[str, Any]:
    """Build request arguments."""
    url = "/api/v1/sandbox/public-build/vm/create"

    headers: dict[str, str] = {}
    if authorization is not None:
        headers["authorization"] = authorization
    if x_api_key is not None:
        headers["X-API-Key"] = x_api_key

    return {
        "method": "POST",
        "url": url,
        "json": body.to_dict(),
        "headers": headers,
    }


def sync(
    client: httpx.Client,
    body: CreateVMRequest,
    authorization: str | None = None,
    x_api_key: str | None = None,
) -> CreateVMResponse:
    """Create Vm"""

    request_args = _build_request_args(
        body=body,
        authorization=authorization,
        x_api_key=x_api_key,
    )

    response = client.request(**request_args)
    raise_for_status(response)
    return CreateVMResponse.from_dict(response.json())


async def asyncio(
    client: httpx.AsyncClient,
    body: CreateVMRequest,
    authorization: str | None = None,
    x_api_key: str | None = None,
) -> CreateVMResponse:
    """Create Vm"""

    request_args = _build_request_args(
        body=body,
        authorization=authorization,
        x_api_key=x_api_key,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return CreateVMResponse.from_dict(response.json())
