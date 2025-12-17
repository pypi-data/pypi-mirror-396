from __future__ import annotations

import contextlib
from typing import Iterator, AsyncIterator

import httpx

from .context import RequestContext
from .transports import HeaderTransport  # import 경로 확인


class HttpxFactory:
    """
    RequestContext로부터 httpx Client/AsyncClient를 생성.
    """

    def __init__(self, ctx: RequestContext, *, timeout: float = 30.0, base_url: str=None) -> None:
        self._ctx = ctx
        self._timeout = timeout
        self._base_url = base_url

    @contextlib.contextmanager
    def client(self) -> Iterator[httpx.Client]:
        with httpx.Client(
            base_url=self._base_url,
            transport=HeaderTransport(self._ctx, inner=httpx.HTTPTransport()),
            timeout=self._timeout,
        ) as client:
            yield client

    def build_sync(self) -> httpx.Client:
        return httpx.Client(
            base_url=self._base_url,
            transport=HeaderTransport(self._ctx, inner=httpx.HTTPTransport()),
            timeout=self._timeout,
        )

    @contextlib.asynccontextmanager
    async def async_client(self) -> AsyncIterator[httpx.AsyncClient]:
        async with httpx.AsyncClient(
            base_url=self._base_url,
            transport=HeaderTransport(self._ctx, inner=httpx.AsyncHTTPTransport()),
            timeout=self._timeout,
        ) as client:
            yield client

    def build_async(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self._base_url,
            transport=HeaderTransport(self._ctx, inner=httpx.AsyncHTTPTransport()),
            timeout=self._timeout,
        )
