from typing import Any
from uuid import UUID

import httpx
from openai import RateLimitError as _RateLimitError
from openai import OpenAI as _OpenAI
from openai import AsyncOpenAI as _AsyncOpenAI

from ..core.client_factory import HttpxFactory
from ..errors import OasisRateLimitError
from ..base import OasisBase

class Oasis(OasisBase, _OpenAI):
    """
    동기 OpenAI SDK 래퍼 (httpx.Client 직접 생성 방식).
    """

    def __init__(
        self,
        *,
        account_id: str,
        tenant_uuid: str | UUID,
        user_uuid: str | UUID,
        workspace_uuid: str | UUID = None,
        plugin_name: str | None = None,
        user_ip: str | None = None,
        root_id: str | None = None,
        audit_state: bool = True,
        proxy_url: str | None = None,
        httpx_factory: HttpxFactory | None = None,
        **openai_kw: Any,
    ) -> None:
        
        super().__init__(
            account_id=account_id,
            tenant_uuid=tenant_uuid,
            workspace_uuid=workspace_uuid,
            user_uuid=user_uuid,
            plugin_name=plugin_name,
            user_ip=user_ip,
            root_id=root_id,
            audit_state=audit_state,
        )
        base_url = self._resolve_base_url(proxy_url)
        self._httpx_factory = httpx_factory or HttpxFactory(self._ctx, base_url=base_url)
        self._client: httpx.Client = self._httpx_factory.build_sync()

        openai_kw.setdefault("api_key", "proxy_handle")
        openai_kw.setdefault("base_url", base_url)
        openai_kw.setdefault("http_client", self._client)

        try:
            _OpenAI.__init__(self, **openai_kw)
        except _RateLimitError as exc:
            raise OasisRateLimitError.from_openai(exc) from exc

        self._closed: bool = False
    
    def rerank(
        self,
        model: str,
        query: str,
        documents: list[str],
        top_n: int | None = None,
        **kwargs,
    ) -> dict:

        payload = {
            "model": model,
            "query": query,
            "documents": documents,
            **kwargs,
        }
        if top_n is not None:
            payload["top_n"] = top_n

        url = self._client.base_url.join("rerank")

        response = self._client.post(
            url,
            json=payload,
        )

        response.raise_for_status()
        return response.json()

    def __enter__(self):
        base_enter = getattr(super(), "__enter__", None)
        if callable(base_enter):
            base_enter()
        return self

    def __exit__(self, exc_type, exc, tb):
        base_exit = getattr(super(), "__exit__", None)
        if callable(base_exit):
            base_exit(exc_type, exc, tb)

        self.close()

    def close(self) -> None:
        """컨텍스트를 사용하지 않을 때 수동으로 자원 정리."""
        if not self._closed:
            self._client.close()
            self._closed = True


class AsyncOasis(OasisBase, _AsyncOpenAI):
    """
    비동기 OpenAI SDK 래퍼 (직접 httpx.AsyncClient 생성 방식).
    """

    def __init__(
        self,
        *,
        account_id: str,
        tenant_uuid: str | UUID,
        user_uuid: str | UUID,
        workspace_uuid: str | UUID = None,
        plugin_name: str | None = None,
        user_ip: str | None = None,
        root_id: str | None = None,
        audit_state: bool = True,
        proxy_url: str | None = None,
        httpx_factory: HttpxFactory | None = None,
        **openai_kw: Any,
    ) -> None:
        
        super().__init__(
            account_id=account_id,
            tenant_uuid=tenant_uuid,
            workspace_uuid=workspace_uuid,
            user_uuid=user_uuid,
            plugin_name=plugin_name,
            user_ip=user_ip,
            root_id=root_id,
            audit_state=audit_state,
        )
        base_url = self._resolve_base_url(proxy_url)
        self._httpx_factory = httpx_factory or HttpxFactory(self._ctx, base_url=base_url)
        self._async_client: httpx.AsyncClient = self._httpx_factory.build_async()

        openai_kw.setdefault("api_key", "proxy_handle")
        openai_kw.setdefault("base_url", base_url)
        openai_kw.setdefault("http_client", self._async_client)

        try:
            _AsyncOpenAI.__init__(self, **openai_kw)
        except _RateLimitError as exc:
            raise OasisRateLimitError.from_openai(exc) from exc

        self._closed = False
    
    async def rerank(
        self,
        model: str,
        query: str,
        documents: list[str],
        top_n: int | None = None,
        **kwargs,
    ) -> dict:

        payload = {
            "model": model,
            "query": query,
            "documents": documents,
            **kwargs,
        }
        if top_n is not None:
            payload["top_n"] = top_n

        url = self._async_client.base_url.join("rerank")

        response = await self._async_client.post(
            url,
            json=payload,
        )
        
        response.raise_for_status()
        return response.json()

    async def __aenter__(self):
        base_enter = getattr(super(), "__aenter__", None)
        if callable(base_enter):
            await base_enter()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        base_exit = getattr(super(), "__aexit__", None)
        if callable(base_exit):
            await base_exit(exc_type, exc, tb)

        if not self._closed:
            await self._async_client.aclose()
            self._closed = True

    async def aclose(self) -> None:
        if not self._closed:
            await self._async_client.aclose()
            self._closed = True
