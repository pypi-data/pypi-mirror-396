"""Test middleware functionality."""

import pytest
from unittest.mock import MagicMock
import mcp.types as mt
from fastmcp.server.middleware.middleware import MiddlewareContext
from fastmcp.tools.tool import ToolResult
from runlayer_cli.middleware import RunlayerMiddleware
from runlayer_cli.models import ServerDetails, PreRequest, PostRequest


def create_test_server(sync_required: bool = False) -> ServerDetails:
    """Helper to create test server details."""
    return ServerDetails(
        id="server-123",
        name="Test Server",
        url="http://test.example.com",
        transport_type="stdio",
        transport_config={},
        deployment_mode="local",
        auth_type=None,
        requires_manual_oauth_setup=False,
        manual_oauth_client_id=None,
        description="Test",
        status="active",
        version=1,
        created_at="2024-01-01T00:00:00",
        updated_at="2024-01-01T00:00:00",
        created_by="user",
        approved_by="admin",
        approved_at="2024-01-01T00:00:00",
        rejection_reason=None,
        sync_required=sync_required,
        local_capabilities=None,
    )


def test_server_details_allows_missing_transport_config():
    """Ensure transport_config can be missing for certain transports."""
    server = ServerDetails(
        id="server-456",
        name="SSE Server",
        url="http://sse.example.com",
        transport_type="sse",
        transport_config=None,
        deployment_mode="remote",
        auth_type=None,
        requires_manual_oauth_setup=False,
        manual_oauth_client_id=None,
        description="Test SSE server",
        status="active",
        version=1,
        created_at="2024-01-02T00:00:00",
        updated_at="2024-01-02T00:00:00",
        created_by="user",
        approved_by="admin",
        approved_at="2024-01-02T00:00:00",
        rejection_reason=None,
        sync_required=False,
        local_capabilities=None,
    )

    assert server.transport_config is None


@pytest.mark.asyncio
async def test_middleware_initialization():
    """Test that middleware initializes correctly."""
    mock_client = MagicMock()
    mock_proxy = MagicMock()
    server = create_test_server()

    middleware = RunlayerMiddleware(
        runlayer_api_client=mock_client, proxy=mock_proxy, server=server
    )

    assert middleware.runlayer_api_client == mock_client
    assert middleware.proxy == mock_proxy
    assert middleware.server == server
    assert middleware.sync_done is True


@pytest.mark.asyncio
async def test_middleware_sync_required():
    """Test that sync_done is set correctly based on sync_required."""
    mock_client = MagicMock()
    mock_proxy = MagicMock()
    server = create_test_server(sync_required=True)

    middleware = RunlayerMiddleware(
        runlayer_api_client=mock_client, proxy=mock_proxy, server=server
    )

    assert middleware.sync_done is False


@pytest.mark.asyncio
async def test_on_call_tool_calls_pre_and_post():
    """Test that on_call_tool calls pre and post with correct data."""
    mock_client = MagicMock()
    mock_proxy = MagicMock()
    server = create_test_server()

    mock_client.pre.return_value = MagicMock(
        status_code=200, json=lambda: {"correlation_id": "corr-123"}
    )
    mock_client.post.return_value = MagicMock(status_code=200)

    middleware = RunlayerMiddleware(
        runlayer_api_client=mock_client, proxy=mock_proxy, server=server
    )

    mock_context = MagicMock(spec=MiddlewareContext)
    mock_context.message = mt.CallToolRequestParams(
        name="test_tool", arguments={"arg": "value"}
    )

    mock_result = MagicMock(spec=ToolResult)
    mock_result.to_mcp_result.return_value = [
        mt.TextContent(type="text", text="result")
    ]

    async def mock_call_next(context):
        return mock_result

    result = await middleware.on_call_tool(mock_context, mock_call_next)

    mock_client.pre.assert_called_once()
    pre_call_args = mock_client.pre.call_args
    assert pre_call_args[0][0] == "server-123"
    assert isinstance(pre_call_args[0][1], PreRequest)
    assert pre_call_args[0][1].method == "tools/call"

    mock_client.post.assert_called_once()
    post_call_args = mock_client.post.call_args
    assert post_call_args[0][0] == "server-123"
    assert isinstance(post_call_args[0][1], PostRequest)
    assert post_call_args[0][1].correlation_id == "corr-123"
    assert post_call_args[0][1].method == "tools/call"

    assert result == mock_result


@pytest.mark.asyncio
async def test_on_list_tools_calls_pre_and_post():
    """Test that on_list_tools calls pre and post with correct data."""
    mock_client = MagicMock()
    mock_proxy = MagicMock()
    server = create_test_server()

    mock_client.pre.return_value = MagicMock(
        status_code=200, json=lambda: {"correlation_id": "corr-456"}
    )
    mock_client.post.return_value = MagicMock(
        status_code=200,
        json=lambda: [
            {
                "name": "test_tool",
                "description": "A test tool",
                "inputSchema": {"type": "object"},
            }
        ],
    )

    middleware = RunlayerMiddleware(
        runlayer_api_client=mock_client, proxy=mock_proxy, server=server
    )

    mock_context = MagicMock(spec=MiddlewareContext)
    mock_context.message = mt.ListToolsRequest(method="tools/list")

    mock_tool = MagicMock()
    mock_tool.to_mcp_tool.return_value = {
        "name": "test_tool",
        "description": "A test tool",
        "inputSchema": {"type": "object", "properties": {}},
    }

    async def mock_call_next(context):
        return [mock_tool]

    result = await middleware.on_list_tools(mock_context, mock_call_next)  # type: ignore

    mock_client.pre.assert_called_once()
    pre_call_args = mock_client.pre.call_args
    assert pre_call_args[0][0] == "server-123"
    assert isinstance(pre_call_args[0][1], PreRequest)
    assert pre_call_args[0][1].method == "tools/list"
    assert pre_call_args[0][1].params is None

    mock_client.post.assert_called_once()
    post_call_args = mock_client.post.call_args
    assert post_call_args[0][0] == "server-123"
    assert isinstance(post_call_args[0][1], PostRequest)
    assert post_call_args[0][1].correlation_id == "corr-456"
    assert post_call_args[0][1].method == "tools/list"

    mock_tool.to_mcp_tool.assert_called_once()

    assert isinstance(result, list)
