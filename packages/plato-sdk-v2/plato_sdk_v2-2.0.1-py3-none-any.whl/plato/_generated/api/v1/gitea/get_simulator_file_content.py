"""Get Simulator File Content"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status
from plato._generated.models.file_content_response import FileContentResponse


def _build_request_args(
    simulator_id: int,
    file_path: str,
    ref: str | None | None = None,
    authorization: str | None = None,
    x_internal_service: str | None = None,
) -> dict[str, Any]:
    """Build request arguments."""
    url = f"/api/v1/gitea/simulators/{simulator_id}/repo/file-content"

    params: dict[str, Any] = {}
    if file_path is not None:
        params["file_path"] = file_path
    if ref is not None:
        params["ref"] = ref

    headers: dict[str, str] = {}
    if authorization is not None:
        headers["authorization"] = authorization
    if x_internal_service is not None:
        headers["X-Internal-Service"] = x_internal_service

    return {
        "method": "GET",
        "url": url,
        "params": params,
        "headers": headers,
    }


def sync(
    client: httpx.Client,
    simulator_id: int,
    file_path: str,
    ref: str | None | None = None,
    authorization: str | None = None,
    x_internal_service: str | None = None,
) -> FileContentResponse:
    """Get content of a specific file in a simulator's repository"""

    request_args = _build_request_args(
        simulator_id=simulator_id,
        file_path=file_path,
        ref=ref,
        authorization=authorization,
        x_internal_service=x_internal_service,
    )

    response = client.request(**request_args)
    raise_for_status(response)
    return FileContentResponse.from_dict(response.json())


async def asyncio(
    client: httpx.AsyncClient,
    simulator_id: int,
    file_path: str,
    ref: str | None | None = None,
    authorization: str | None = None,
    x_internal_service: str | None = None,
) -> FileContentResponse:
    """Get content of a specific file in a simulator's repository"""

    request_args = _build_request_args(
        simulator_id=simulator_id,
        file_path=file_path,
        ref=ref,
        authorization=authorization,
        x_internal_service=x_internal_service,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return FileContentResponse.from_dict(response.json())
