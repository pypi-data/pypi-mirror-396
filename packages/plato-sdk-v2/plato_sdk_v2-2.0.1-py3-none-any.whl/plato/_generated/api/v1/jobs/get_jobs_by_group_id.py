"""Get Jobs By Group Id"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status


def _build_request_args(
    job_group_id: str,
    authorization: str | None = None,
    x_internal_service: str | None = None,
) -> dict[str, Any]:
    """Build request arguments."""
    url = f"/api/v1/jobs/group/{job_group_id}"

    headers: dict[str, str] = {}
    if authorization is not None:
        headers["authorization"] = authorization
    if x_internal_service is not None:
        headers["X-Internal-Service"] = x_internal_service

    return {
        "method": "GET",
        "url": url,
        "headers": headers,
    }


def sync(
    client: httpx.Client,
    job_group_id: str,
    authorization: str | None = None,
    x_internal_service: str | None = None,
) -> Any:
    """Get all jobs associated with a specific job group ID"""

    request_args = _build_request_args(
        job_group_id=job_group_id,
        authorization=authorization,
        x_internal_service=x_internal_service,
    )

    response = client.request(**request_args)
    raise_for_status(response)
    return response.json()


async def asyncio(
    client: httpx.AsyncClient,
    job_group_id: str,
    authorization: str | None = None,
    x_internal_service: str | None = None,
) -> Any:
    """Get all jobs associated with a specific job group ID"""

    request_args = _build_request_args(
        job_group_id=job_group_id,
        authorization=authorization,
        x_internal_service=x_internal_service,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return response.json()
