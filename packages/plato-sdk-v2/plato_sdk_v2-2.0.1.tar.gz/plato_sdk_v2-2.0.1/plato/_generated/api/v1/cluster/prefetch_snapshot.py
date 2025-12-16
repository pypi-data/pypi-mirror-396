"""Prefetch Snapshot"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status
from plato._generated.models.prefetch_request import PrefetchRequest
from plato._generated.models.prefetch_response import PrefetchResponse


def _build_request_args(
    body: PrefetchRequest,
    authorization: str | None = None,
    x_internal_service: str | None = None,
) -> dict[str, Any]:
    """Build request arguments."""
    url = "/api/v1/cluster/prefetch"

    headers: dict[str, str] = {}
    if authorization is not None:
        headers["authorization"] = authorization
    if x_internal_service is not None:
        headers["X-Internal-Service"] = x_internal_service

    return {
        "method": "POST",
        "url": url,
        "json": body.to_dict(),
        "headers": headers,
    }


def sync(
    client: httpx.Client,
    body: PrefetchRequest,
    authorization: str | None = None,
    x_internal_service: str | None = None,
) -> PrefetchResponse:
    """Submit a snapshot prefetch request to all active Firecracker worker instances.

    Requires authentication (either internal service token OR user JWT).

    This endpoint will:
    1. Get all active dispatcher/worker instances
    2. Extract unique instance IDs
    3. Build SnapshotConfig from artifact_id or service/version/dataset
    4. Send a VMSnapshotFetchRequestEvent to each instance's snapshot-fetch queue

    Each instance's SnapshotManagerAgent will receive the request and download
    the snapshot lineage if it's not already available locally.

    Args:
        prefetch_request: The snapshot to prefetch (artifact_id OR service/version/dataset)

    Returns:
        PrefetchResponse with list of notified instances"""

    request_args = _build_request_args(
        body=body,
        authorization=authorization,
        x_internal_service=x_internal_service,
    )

    response = client.request(**request_args)
    raise_for_status(response)
    return PrefetchResponse.from_dict(response.json())


async def asyncio(
    client: httpx.AsyncClient,
    body: PrefetchRequest,
    authorization: str | None = None,
    x_internal_service: str | None = None,
) -> PrefetchResponse:
    """Submit a snapshot prefetch request to all active Firecracker worker instances.

    Requires authentication (either internal service token OR user JWT).

    This endpoint will:
    1. Get all active dispatcher/worker instances
    2. Extract unique instance IDs
    3. Build SnapshotConfig from artifact_id or service/version/dataset
    4. Send a VMSnapshotFetchRequestEvent to each instance's snapshot-fetch queue

    Each instance's SnapshotManagerAgent will receive the request and download
    the snapshot lineage if it's not already available locally.

    Args:
        prefetch_request: The snapshot to prefetch (artifact_id OR service/version/dataset)

    Returns:
        PrefetchResponse with list of notified instances"""

    request_args = _build_request_args(
        body=body,
        authorization=authorization,
        x_internal_service=x_internal_service,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return PrefetchResponse.from_dict(response.json())
