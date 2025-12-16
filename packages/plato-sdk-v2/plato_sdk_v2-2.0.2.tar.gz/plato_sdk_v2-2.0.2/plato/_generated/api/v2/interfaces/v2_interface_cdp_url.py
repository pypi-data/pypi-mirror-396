"""Interface Cdp Url"""

from __future__ import annotations

import httpx

from plato._generated.models.app_api_v2_schemas_interface_cdpurlresponse import AppApiV2SchemasInterfaceCdpurlresponse


def sync(
    client: httpx.Client,
    job_id: str,
    authorization: str | None = None,
    x_internal_service: str | None = None,
) -> AppApiV2SchemasInterfaceCdpurlresponse:
    """Get the CDP URL for a browser interface.

    Only available for browser interfaces.
    Use this URL with Playwright or Puppeteer to control the browser."""

    url = f"/api/v2/interface/{job_id}/cdp_url"

    headers: dict[str, str] = {}
    if authorization is not None:
        headers["authorization"] = authorization
    if x_internal_service is not None:
        headers["X-Internal-Service"] = x_internal_service

    response = client.request(
        "GET",
        url,
        headers=headers,
    )
    response.raise_for_status()

    return AppApiV2SchemasInterfaceCdpurlresponse.from_dict(response.json())


async def asyncio(
    client: httpx.AsyncClient,
    job_id: str,
    authorization: str | None = None,
    x_internal_service: str | None = None,
) -> AppApiV2SchemasInterfaceCdpurlresponse:
    """Get the CDP URL for a browser interface.

    Only available for browser interfaces.
    Use this URL with Playwright or Puppeteer to control the browser."""

    url = f"/api/v2/interface/{job_id}/cdp_url"

    headers: dict[str, str] = {}
    if authorization is not None:
        headers["authorization"] = authorization
    if x_internal_service is not None:
        headers["X-Internal-Service"] = x_internal_service

    response = await client.request(
        "GET",
        url,
        headers=headers,
    )
    response.raise_for_status()

    return AppApiV2SchemasInterfaceCdpurlresponse.from_dict(response.json())
