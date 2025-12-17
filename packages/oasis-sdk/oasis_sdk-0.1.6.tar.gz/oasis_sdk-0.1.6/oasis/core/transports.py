import asyncio
import logging
from typing import Final

import httpx
from httpx import AsyncHTTPTransport, BaseTransport, HTTPTransport, Request, Response

from .context import RequestContext

log: Final = logging.getLogger(__name__)


class HeaderTransport(BaseTransport):
    """
    모든 요청 전에 Oasis 헤더를 삽입하고 DEBUG 로그를 남기는 공통 transport.
    - sync:  httpx.HTTPTransport (기본)
    - async: httpx.AsyncHTTPTransport (기본)
    """

    def __init__(
        self,
        ctx: RequestContext,
        *,
        inner: BaseTransport | None = None,
    ) -> None:
        default_inner = (
            AsyncHTTPTransport()
            if hasattr(httpx, "AsyncHTTPTransport")
            and asyncio.get_event_loop().is_running()
            else HTTPTransport()
        )
        self._ctx = ctx
        self._inner: HTTPTransport | AsyncHTTPTransport = inner or default_inner

    def handle_request(self, request: Request) -> Response:  # type: ignore[override]
        injected = self._inject_headers(request)
        self._debug_request(injected)

        response = self._inner.handle_request(injected)  # type: ignore[attr-defined]
        self._debug_response(response)
        return response

    async def handle_async_request(self, request: Request) -> Response:  # type: ignore[override]
        injected = self._inject_headers(request)
        self._debug_request(injected)

        response = await self._inner.handle_async_request(injected)  # type: ignore[attr-defined]
        self._debug_response(response)
        return response

    def close(self) -> None:
        if hasattr(self._inner, "close"):
            self._inner.close()

    async def aclose(self) -> None:
        if hasattr(self._inner, "aclose"):
            await self._inner.aclose()

    def _inject_headers(self, request: Request) -> Request:
        request.headers.update(self._ctx.next().headers)
        return request

    @staticmethod
    def _debug_request(request: Request) -> None:
        if log.isEnabledFor(logging.DEBUG):
            log.debug("→ %s %s", request.method, request.url)

    @staticmethod
    def _debug_response(response: Response) -> None:
        if log.isEnabledFor(logging.DEBUG):
            try:
                url = response.request.url if response.request else "<no-request>"
            except Exception:
                url = "<no-request>"
            log.debug("← %s %s", response.status_code, url)
