"""Generate Mutations"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status
from plato._generated.models.generate_mutations_request import GenerateMutationsRequest


def _build_request_args(
    body: GenerateMutationsRequest,
) -> dict[str, Any]:
    """Build request arguments."""
    url = "/api/v1/env/generate_mutations"

    return {
        "method": "POST",
        "url": url,
        "json": body.to_dict(),
    }


def sync(
    client: httpx.Client,
    body: GenerateMutationsRequest,
) -> Any:
    """Generate mutations for a simulator or specific test cases."""

    request_args = _build_request_args(
        body=body,
    )

    response = client.request(**request_args)
    raise_for_status(response)
    return response.json()


async def asyncio(
    client: httpx.AsyncClient,
    body: GenerateMutationsRequest,
) -> Any:
    """Generate mutations for a simulator or specific test cases."""

    request_args = _build_request_args(
        body=body,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return response.json()
