"""Analyze Labels"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status


def _build_request_args(
    session_id: str,
) -> dict[str, Any]:
    """Build request arguments."""
    url = f"/api/v1/session/{session_id}/analyze-labels"

    return {
        "method": "GET",
        "url": url,
    }


def sync(
    client: httpx.Client,
    session_id: str,
) -> Any:
    """Analyze labels from a session and propose a task prompt.
    This endpoint:
    1. Validates that the session has a test case with is_sample=true
    2. Extracts labels from scores with reasons
    3. Uses embeddings to detect outliers in labels
    4. If no outliers, generates a proposed task prompt and test case name
    5. Returns the analysis without creating anything"""

    request_args = _build_request_args(
        session_id=session_id,
    )

    response = client.request(**request_args)
    raise_for_status(response)
    return response.json()


async def asyncio(
    client: httpx.AsyncClient,
    session_id: str,
) -> Any:
    """Analyze labels from a session and propose a task prompt.
    This endpoint:
    1. Validates that the session has a test case with is_sample=true
    2. Extracts labels from scores with reasons
    3. Uses embeddings to detect outliers in labels
    4. If no outliers, generates a proposed task prompt and test case name
    5. Returns the analysis without creating anything"""

    request_args = _build_request_args(
        session_id=session_id,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return response.json()
