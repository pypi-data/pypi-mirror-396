"""Create Browser Interface"""

from __future__ import annotations

import httpx

from plato._generated.models.browser_interface_option import BrowserInterfaceOption
from plato._generated.models.interface_info import InterfaceInfo


def sync(
    client: httpx.Client,
    body: BrowserInterfaceOption,
    authorization: str | None = None,
    x_internal_service: str | None = None,
) -> InterfaceInfo:
    """Create a browser interface.

    Browser interfaces provide CDP (Chrome DevTools Protocol) access for
    Playwright/Puppeteer control, plus screenshot capabilities."""

    url = "/api/v2/interface/browser/create"

    headers: dict[str, str] = {}
    if authorization is not None:
        headers["authorization"] = authorization
    if x_internal_service is not None:
        headers["X-Internal-Service"] = x_internal_service

    response = client.request(
        "POST",
        url,
        json=body.to_dict(),
        headers=headers,
    )
    response.raise_for_status()

    return InterfaceInfo.from_dict(response.json())


async def asyncio(
    client: httpx.AsyncClient,
    body: BrowserInterfaceOption,
    authorization: str | None = None,
    x_internal_service: str | None = None,
) -> InterfaceInfo:
    """Create a browser interface.

    Browser interfaces provide CDP (Chrome DevTools Protocol) access for
    Playwright/Puppeteer control, plus screenshot capabilities."""

    url = "/api/v2/interface/browser/create"

    headers: dict[str, str] = {}
    if authorization is not None:
        headers["authorization"] = authorization
    if x_internal_service is not None:
        headers["X-Internal-Service"] = x_internal_service

    response = await client.request(
        "POST",
        url,
        json=body.to_dict(),
        headers=headers,
    )
    response.raise_for_status()

    return InterfaceInfo.from_dict(response.json())
