"""Evaluate Python"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status
from plato._generated.models.evaluate_python_request import EvaluatePythonRequest


def _build_request_args(
    body: EvaluatePythonRequest,
) -> dict[str, Any]:
    """Build request arguments."""
    url = "/api/v1/evals/evaluate-python"

    return {
        "method": "POST",
        "url": url,
        "json": body.to_dict(),
    }


def sync(
    client: httpx.Client,
    body: EvaluatePythonRequest,
) -> Any:
    """Evaluate a python script."""

    request_args = _build_request_args(
        body=body,
    )

    response = client.request(**request_args)
    raise_for_status(response)
    return response.json()


async def asyncio(
    client: httpx.AsyncClient,
    body: EvaluatePythonRequest,
) -> Any:
    """Evaluate a python script."""

    request_args = _build_request_args(
        body=body,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return response.json()
