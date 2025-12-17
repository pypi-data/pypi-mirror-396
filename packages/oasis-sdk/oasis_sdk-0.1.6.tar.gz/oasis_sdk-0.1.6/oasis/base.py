from abc import ABC
from uuid import UUID
from oasis.config import DEFAULT_PROXY_URL
from oasis.utils import get_from_env

from .core.client_factory import HttpxFactory
from .core.context import RequestContext

class OasisBase(ABC):
    """
    공급자 래퍼들의 공통 부모

    * RequestContext & HttpxFactory 인스턴스 생성/보관
    * protected 멤버 `_ctx`, `_httpx` 노출
    """

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
    ) -> None:
        self._ctx = RequestContext(
            account_id=account_id,
            tenant_uuid=tenant_uuid,
            workspace_uuid=workspace_uuid,
            user_uuid=user_uuid,
            plugin_name=plugin_name,
            user_ip=user_ip,
            root_id=root_id,
            audit_state=audit_state,
        )
        self._httpx = HttpxFactory(self._ctx)

    @staticmethod
    def _resolve_base_url(url: str | None) -> str:
        return url or get_from_env("PROXY_URL", DEFAULT_PROXY_URL)