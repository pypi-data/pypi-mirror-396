"""Start Eval From Git"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status
from plato._generated.models.start_eval_from_git_request import StartEvalFromGitRequest


def _build_request_args(
    body: StartEvalFromGitRequest,
) -> dict[str, Any]:
    """Build request arguments."""
    url = "/api/v1/evals/git"

    return {
        "method": "POST",
        "url": url,
        "json": body.to_dict(),
    }


def sync(
    client: httpx.Client,
    body: StartEvalFromGitRequest,
) -> Any:
    """Start Eval From Git"""

    request_args = _build_request_args(
        body=body,
    )

    response = client.request(**request_args)
    raise_for_status(response)
    return response.json()


async def asyncio(
    client: httpx.AsyncClient,
    body: StartEvalFromGitRequest,
) -> Any:
    """Start Eval From Git"""

    request_args = _build_request_args(
        body=body,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return response.json()
