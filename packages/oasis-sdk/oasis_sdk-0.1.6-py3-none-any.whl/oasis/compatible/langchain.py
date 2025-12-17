from typing import Any
from uuid import UUID

import httpx
from langchain_openai import ChatOpenAI as _ChatOpenAI, OpenAIEmbeddings as _OpenAIEmbeddings
from pydantic import PrivateAttr

from ..base import OasisBase
from ..errors import OasisRateLimitError
from ..core.client_factory import HttpxFactory


class ChatOasis(OasisBase, _ChatOpenAI):
    """
    LangChain `ChatOpenAI` 래퍼.
    """

    _client: httpx.Client = PrivateAttr()
    _async_client: httpx.AsyncClient = PrivateAttr()

    def __init__(
        self,
        *,
        account_id: str,
        tenant_uuid: str | UUID,
        workspace_uuid: str | UUID,
        user_uuid: str | UUID,
        plugin_name: str | None = None,
        user_ip: str | None = None,
        root_id: str | None = None,
        audit_state: bool = True,
        proxy_url: str | None = None,
        httpx_factory: HttpxFactory | None = None,
        **lc_kw: Any,
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
        factory = httpx_factory or HttpxFactory(self._ctx, base_url=base_url)
        sync_cli = factory.build_sync()
        async_cli = factory.build_async()

        lc_kw.setdefault("openai_api_key", "proxy_handle")
        lc_kw.setdefault("base_url", base_url)
        lc_kw.setdefault("http_client", sync_cli)
        lc_kw.setdefault("http_async_client", async_cli)

        try:
            _ChatOpenAI.__init__(self, **lc_kw)
        except Exception as exc:
            if "RateLimitError" in exc.__class__.__name__:
                raise OasisRateLimitError.from_openai(exc) from exc
            raise

        self._client = sync_cli
        self._async_client = async_cli
        self._closed = False

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

    async def arerank(
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
        if not self._closed:
            self._client.close()
            self._closed = True

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
            self._client.close()
            self._closed = True


class OasisEmbedding(OasisBase, _OpenAIEmbeddings):
    """
    LangChain `OpenAIEmbeddings` 래퍼 (표준 OpenAI API용).
    """

    _client: httpx.Client = PrivateAttr()
    _async_client: httpx.AsyncClient = PrivateAttr()

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
        **lc_kw: Any,
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
        factory = httpx_factory or HttpxFactory(self._ctx, base_url=base_url)
        sync_cli = factory.build_sync()
        async_cli = factory.build_async()

        lc_kw.setdefault("openai_api_key", "proxy_handle")
        lc_kw.setdefault("base_url", base_url)
        lc_kw.setdefault("http_client", sync_cli)
        lc_kw.setdefault("http_async_client", async_cli)

        try:
            _OpenAIEmbeddings.__init__(self, **lc_kw)
        except Exception as exc:
            if "RateLimitError" in exc.__class__.__name__:
                raise OasisRateLimitError.from_openai(exc) from exc
            raise

        self._client = sync_cli
        self._async_client = async_cli
        self._closed = False

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

    async def arerank(
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

    def close(self) -> None:
        if not self._closed:
            self._client.close()
            self._closed = True

    async def aclose(self) -> None:
        if not self._closed:
            await self._async_client.aclose()
            self._client.close()
            self._closed = True

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

    async def __aenter__(self):
        base_enter = getattr(super(), "__aenter__", None)
        if callable(base_enter):
            await base_enter()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        base_exit = getattr(super(), "__aexit__", None)
        if callable(base_exit):
            await base_exit(exc_type, exc, tb)
        await self.aclose()
