"""Generate Scoring Config From Sessions"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status
from plato._generated.models.generate_scoring_config_from_sessions_request import (
    GenerateScoringConfigFromSessionsRequest,
)


def _build_request_args(
    body: GenerateScoringConfigFromSessionsRequest,
) -> dict[str, Any]:
    """Build request arguments."""
    url = "/api/v1/testcases/generate-scoring-config-from-sessions"

    return {
        "method": "POST",
        "url": url,
        "json": body.to_dict(),
    }


def sync(
    client: httpx.Client,
    body: GenerateScoringConfigFromSessionsRequest,
) -> Any:
    """Generate a scoring config from specific session IDs.
    Uses ALL provided sessions for both mutations and output scoring types.

    RESTRICTED TO PLATO ORG ONLY (org_id == 5)."""

    request_args = _build_request_args(
        body=body,
    )

    response = client.request(**request_args)
    raise_for_status(response)
    return response.json()


async def asyncio(
    client: httpx.AsyncClient,
    body: GenerateScoringConfigFromSessionsRequest,
) -> Any:
    """Generate a scoring config from specific session IDs.
    Uses ALL provided sessions for both mutations and output scoring types.

    RESTRICTED TO PLATO ORG ONLY (org_id == 5)."""

    request_args = _build_request_args(
        body=body,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return response.json()
