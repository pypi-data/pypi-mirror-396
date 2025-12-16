"""Convert Text To Structured Data"""

from __future__ import annotations

from typing import Any

import httpx

from plato._generated.errors import raise_for_status
from plato._generated.models.convert_text_to_structured_data_request import ConvertTextToStructuredDataRequest


def _build_request_args(
    body: ConvertTextToStructuredDataRequest,
) -> dict[str, Any]:
    """Build request arguments."""
    url = "/api/v1/testcases/convert-text-to-structured-data"

    return {
        "method": "POST",
        "url": url,
        "json": body.to_dict(),
    }


def sync(
    client: httpx.Client,
    body: ConvertTextToStructuredDataRequest,
) -> Any:
    """Convert text to structured data using AI based on the provided schema"""

    request_args = _build_request_args(
        body=body,
    )

    response = client.request(**request_args)
    raise_for_status(response)
    return response.json()


async def asyncio(
    client: httpx.AsyncClient,
    body: ConvertTextToStructuredDataRequest,
) -> Any:
    """Convert text to structured data using AI based on the provided schema"""

    request_args = _build_request_args(
        body=body,
    )

    response = await client.request(**request_args)
    raise_for_status(response)
    return response.json()
