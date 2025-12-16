from pydantic import BaseModel, ConfigDict
import datetime
import mcp.types as mt
from typing import Any, Optional


class LocalCapabilities(BaseModel):
    tools: dict[str, mt.Tool]
    resources: dict[str, mt.Resource]
    prompts: dict[str, mt.Prompt]
    synced_at: datetime.datetime


class PreRequest(BaseModel):
    method: str
    params: dict[str, Any] | None


class PostRequest(PreRequest):
    result: Optional[
        list[mt.ContentBlock]
        | tuple[list[mt.ContentBlock], dict[str, Any]]
        | list[mt.Tool]
        | list[mt.Resource]
        | None
    ]
    correlation_id: str
    inject_synthetic_tool_on_policy_block: bool | None = False


class ServerDetails(BaseModel):
    id: str
    name: str
    url: str
    transport_type: str
    transport_config: dict[str, Any] | None = None
    deployment_mode: str
    auth_type: Optional[str]
    requires_manual_oauth_setup: bool
    manual_oauth_client_id: Optional[str]
    description: str
    status: str
    version: int
    created_at: str
    updated_at: str
    created_by: str
    approved_by: str
    approved_at: str
    rejection_reason: Optional[str]
    sync_required: bool
    local_capabilities: LocalCapabilities | None

    model_config = ConfigDict(extra="ignore")
