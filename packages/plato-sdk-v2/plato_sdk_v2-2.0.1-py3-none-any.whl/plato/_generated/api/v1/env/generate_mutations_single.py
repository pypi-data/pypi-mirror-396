"""Generate Mutations Single"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status
from plato._generated.models.generate_mutations_single_request import GenerateMutationsSingleRequest


def _build_request_args(
    body: GenerateMutationsSingleRequest,
) -> dict[str, Any]:
    """Build request arguments."""
    url = "/api/v1/env/generate_mutations_single"

    return {
        "method": "POST",
        "url": url,
        "json": body.to_dict(),
    }


def sync(
    client: httpx.Client,
    body: GenerateMutationsSingleRequest,
) -> Any:
    """Generate mutations for a single test case with streaming progress."""

    request_args = _build_request_args(
        body=body,
    )

    response = client.request(**request_args)
    raise_for_status(response)
    return response.json()


async def asyncio(
    client: httpx.AsyncClient,
    body: GenerateMutationsSingleRequest,
) -> Any:
    """Generate mutations for a single test case with streaming progress."""

    request_args = _build_request_args(
        body=body,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return response.json()
