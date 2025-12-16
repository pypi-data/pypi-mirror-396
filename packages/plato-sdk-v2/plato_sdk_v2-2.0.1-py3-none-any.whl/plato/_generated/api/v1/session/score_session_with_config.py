"""Score Session With Config"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status
from plato._generated.models.score_with_config_request import ScoreWithConfigRequest


def _build_request_args(
    session_id: str,
    body: ScoreWithConfigRequest,
) -> dict[str, Any]:
    """Build request arguments."""
    url = f"/api/v1/session/{session_id}/score-with-config"

    return {
        "method": "POST",
        "url": url,
        "json": body.to_dict(),
    }


def sync(
    client: httpx.Client,
    session_id: str,
    body: ScoreWithConfigRequest,
) -> Any:
    """Score a session with an arbitrary scoring config (does not save to database).

    RESTRICTED TO PLATO ORG ONLY (org_id == 5)."""

    request_args = _build_request_args(
        session_id=session_id,
        body=body,
    )

    response = client.request(**request_args)
    raise_for_status(response)
    return response.json()


async def asyncio(
    client: httpx.AsyncClient,
    session_id: str,
    body: ScoreWithConfigRequest,
) -> Any:
    """Score a session with an arbitrary scoring config (does not save to database).

    RESTRICTED TO PLATO ORG ONLY (org_id == 5)."""

    request_args = _build_request_args(
        session_id=session_id,
        body=body,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return response.json()
