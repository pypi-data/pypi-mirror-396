import secrets, time
from dataclasses import dataclass, field, replace
from typing import Any
from uuid import UUID
import uuid
import os
from ..utils import get_user_ip  

@dataclass(frozen=True, slots=True)
class RequestContext:
    """요청 단위 불변 메타데이터"""

    account_id: str
    tenant_uuid: str | UUID
    workspace_uuid: str | UUID
    user_uuid: str | UUID
    plugin_name: str | None = None
    user_ip: str | None = None
    audit_state: bool = True
    root_id: str | None = None
    req_id: str = field(default_factory=lambda: secrets.token_hex(8))

    def __post_init__(self):
        if self.root_id is None:
            object.__setattr__(self, "root_id", self._make_root_id())
        if self.user_ip is None:
            object.__setattr__(self, "user_ip", get_user_ip())
        if self.plugin_name is None:
            object.__setattr__(self, "plugin_name", "default-plugin")

    @property
    def headers(self) -> dict[str, Any]:
        return {
            "ACCOUNT-ID": self.account_id,
            "TENANT-UUID": self.tenant_uuid,
            "WORKSPACE-UUID": self.workspace_uuid,
            "USER-UUID": self.user_uuid,
            "USER-IP": self.user_ip,
            "ROOT-ID": self.root_id,
            "REQUEST-ID": self.req_id,
            "AUDIT-STATE": str(self.audit_state).lower(),
            "PLUGIN-NAME": self.plugin_name,
            "SOURCE": os.uname().nodename,
        }

    def next(self) -> "RequestContext":
        """root_id는 고정하고 새 req_id만 부여"""
        return replace(self, req_id=secrets.token_hex(8))

    def _make_root_id(self) -> str:
        base = (
            f"{self.user_uuid}:{self.workspace_uuid}:{self.tenant_uuid}:"
            f"{int(time.time() * 1e6)}"
        )
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, base))
