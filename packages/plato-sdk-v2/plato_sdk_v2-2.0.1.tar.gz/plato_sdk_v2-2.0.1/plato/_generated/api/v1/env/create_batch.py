"""Create Batch"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status
from plato._generated.models.make_env_batch_request import MakeEnvBatchRequest
from plato._generated.models.make_env_batch_response import MakeEnvBatchResponse


def _build_request_args(
    body: MakeEnvBatchRequest,
    authorization: str | None = None,
    x_api_key: str | None = None,
) -> dict[str, Any]:
    """Build request arguments."""
    url = "/api/v1/env/make_batch"

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
    body: MakeEnvBatchRequest,
    authorization: str | None = None,
    x_api_key: str | None = None,
) -> MakeEnvBatchResponse:
    """Create multiple environments in a single request.

    All environments are created successfully or the entire batch fails.
    If any environment fails to create, all successfully created environments
    are cleaned up and an error is returned."""

    request_args = _build_request_args(
        body=body,
        authorization=authorization,
        x_api_key=x_api_key,
    )

    response = client.request(**request_args)
    raise_for_status(response)
    return MakeEnvBatchResponse.from_dict(response.json())


async def asyncio(
    client: httpx.AsyncClient,
    body: MakeEnvBatchRequest,
    authorization: str | None = None,
    x_api_key: str | None = None,
) -> MakeEnvBatchResponse:
    """Create multiple environments in a single request.

    All environments are created successfully or the entire batch fails.
    If any environment fails to create, all successfully created environments
    are cleaned up and an error is returned."""

    request_args = _build_request_args(
        body=body,
        authorization=authorization,
        x_api_key=x_api_key,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return MakeEnvBatchResponse.from_dict(response.json())
