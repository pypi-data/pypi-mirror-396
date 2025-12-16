"""Basic on_message middleware for MCP CLI with OAuth support."""

from fastmcp.server.middleware.middleware import Middleware, MiddlewareContext, CallNext
import structlog
import mcp.types as mt
from runlayer_cli.api import RunlayerClient

from fastmcp.server.proxy import FastMCPProxy
from fastmcp.tools.tool import ToolResult
from fastmcp.server.proxy import ProxyTool
from runlayer_cli.models import (
    PreRequest,
    PostRequest,
    ServerDetails,
)

logger = structlog.get_logger()


class RunlayerMiddleware(Middleware):
    def __init__(
        self,
        runlayer_api_client: RunlayerClient,
        proxy: FastMCPProxy,
        server: ServerDetails,
    ):
        self.runlayer_api_client = runlayer_api_client
        self.server = server
        self.proxy = proxy
        self.sync_done = not self.server.sync_required

    async def on_call_tool(
        self,
        context: MiddlewareContext[mt.CallToolRequestParams],
        call_next: CallNext[mt.CallToolRequestParams, ToolResult],
    ) -> ToolResult:
        payload = PreRequest(method="tools/call", params=context.message.model_dump())

        pre_response = self.runlayer_api_client.pre(self.server.id, payload)
        if pre_response.status_code != 200:
            raise Exception(pre_response.json())

        correlation_id = pre_response.json()["correlation_id"]
        quick_tool_result = pre_response.json().get("quick_tool_result")
        if quick_tool_result:
            return ToolResult(content=quick_tool_result)

        result = await call_next(context)

        post_payload = PostRequest(
            result=result.to_mcp_result(),
            **(payload.model_dump() or {}),
            correlation_id=correlation_id,
        )

        post_response = self.runlayer_api_client.post(self.server.id, post_payload)
        if post_response.status_code != 200:
            raise Exception(post_response.json())

        return result

    async def on_list_tools(  # type: ignore
        self,
        context: MiddlewareContext[mt.ListToolsRequest],
        call_next: CallNext[mt.ListToolsRequest, list[mt.Tool]],
    ) -> list[ProxyTool]:
        payload = PreRequest(method="tools/list", params=None)

        pre_response = self.runlayer_api_client.pre(self.server.id, payload)
        if pre_response.status_code != 200:
            raise Exception(pre_response.json())

        correlation_id = pre_response.json()["correlation_id"]

        result = await call_next(context)

        post_payload = PostRequest(
            result=[t.to_mcp_tool() for t in result],  # type: ignore
            **(payload.model_dump() or {}),
            correlation_id=correlation_id,
            inject_synthetic_tool_on_policy_block=True,
        )

        post_response = self.runlayer_api_client.post(self.server.id, post_payload)
        if post_response.status_code != 200:
            raise Exception(post_response.json())

        filtered_result = [
            ProxyTool.from_mcp_tool(self.proxy, mt.Tool.model_validate(t))  # type: ignore
            for t in post_response.json()
        ]

        return filtered_result
