"""Human In The Loop Scoring"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status
from plato._generated.models.human_in_the_loop_score_request import HumanInTheLoopScoreRequest


def _build_request_args(
    test_case_run_public_id: str,
    body: HumanInTheLoopScoreRequest,
) -> dict[str, Any]:
    """Build request arguments."""
    url = f"/api/v1/evals/scoring/human_in_the_loop/{test_case_run_public_id}"

    return {
        "method": "PUT",
        "url": url,
        "json": body.to_dict(),
    }


def sync(
    client: httpx.Client,
    test_case_run_public_id: str,
    body: HumanInTheLoopScoreRequest,
) -> Any:
    """Score a test case run with human feedback."""

    request_args = _build_request_args(
        test_case_run_public_id=test_case_run_public_id,
        body=body,
    )

    response = client.request(**request_args)
    raise_for_status(response)
    return response.json()


async def asyncio(
    client: httpx.AsyncClient,
    test_case_run_public_id: str,
    body: HumanInTheLoopScoreRequest,
) -> Any:
    """Score a test case run with human feedback."""

    request_args = _build_request_args(
        test_case_run_public_id=test_case_run_public_id,
        body=body,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return response.json()
