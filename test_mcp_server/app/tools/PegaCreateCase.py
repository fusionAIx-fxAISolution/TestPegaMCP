from __future__ import annotations

import asyncio
import json
import time
from collections import deque
from typing import Any

from mcp.server.fastmcp import FastMCP

from app.pega_client import PegaCaseClient
from app.PegaSettings import PegaSettings
 
 
class FixedWindowRateLimiter:

    def __init__(self, limit_per_minute: int, label: str) -> None:

        if limit_per_minute <= 0:

            raise ValueError("limit_per_minute must be > 0")

        self._limit = limit_per_minute

        self._label = label

        self._events: deque[float] = deque()

        self._lock = asyncio.Lock()
 
    async def acquire(self) -> None:

        now = time.monotonic()

        cutoff = now - 60.0
 
        async with self._lock:

            while self._events and self._events[0] <= cutoff:

                self._events.popleft()
 
            if len(self._events) >= self._limit:

                raise RuntimeError(

                    f"Rate limit exceeded for {self._label}: "

                    f"{self._limit} requests per 60 seconds"

                )
 
            self._events.append(now)
 
 
def register_pega_create_case_tool(

    mcp: FastMCP,

    pega_client: PegaCaseClient,

    settings: PegaSettings,

) -> None:

    create_limiter = FixedWindowRateLimiter(

        settings.create_calls_per_minute_limit,

        "pega_create_case",

    )
 
    def _build_default_create_payload(

        PolicyNumber: str | None = None,

        case_type_id: str | None = None,

    ) -> dict[str, Any]:

        # Build payload with case type and create process ID
        payload = {
            "caseTypeID": case_type_id or settings.allowed_case_type_id,
            "processID": settings.allowed_create_process_id,
        }

        # Start with default create content and add policy metadata if present
        content = dict(settings.default_create_content or {})
        if PolicyNumber:
            content["PolicyNumber"] = PolicyNumber
            content["pyLabel"] = f"Policy: {PolicyNumber}"

        if content:
            payload["content"] = content

        payload_size = len(json.dumps(payload))

        if payload_size > settings.max_create_payload_bytes:

            raise ValueError(

                f"create payload too large ({payload_size} bytes), "

                f"max is {settings.max_create_payload_bytes}"

            )

        return payload

    @mcp.tool(

        name="pega_create_case",

        description=(

            "Create a Pega Smart Claim Case. "

            "Specify policy number to store it in case properties. "

            "Optionally specify case type ID. "

            "Returns created case info including the case ID."

        ),

    )

    async def pega_create_case(

        PolicyNumber: str | None = None,

        case_type_id: str | None = None,

    ) -> dict[str, Any]:

        await create_limiter.acquire()

        payload = _build_default_create_payload(

            PolicyNumber=PolicyNumber,

            case_type_id=case_type_id,

        )

        return await pega_client.create_case(

            payload=payload,

            view_type="none",

            page_name=None,

            origin_channel=settings.default_origin_channel,

        )