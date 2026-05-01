#!/usr/bin/env python3
"""Tests for MCP server tools."""

import asyncio
from unittest.mock import patch

import pytest

try:
    from scitex_ssh._mcp._server import create_server

    HAS_FASTMCP = True
except ImportError:
    HAS_FASTMCP = False

pytestmark = pytest.mark.skipif(not HAS_FASTMCP, reason="fastmcp not installed")


def _get_tool_fn(server, name):
    """Resolve a tool's underlying callable via FastMCP's public async API."""
    tool = asyncio.run(server.get_tool(name))
    assert tool is not None, f"tool {name!r} not registered"
    return tool.fn


class TestCreateServer:
    """MCP server creation tests."""

    def test_create_server_returns_fastmcp(self):
        server = create_server()
        assert server is not None
        assert server.name == "scitex-ssh"

    def test_server_registers_expected_tools(self):
        server = create_server()
        names = {t.name for t in asyncio.run(server.list_tools())}
        assert {"tunnel_setup", "tunnel_status", "tunnel_remove"}.issubset(names)


class TestMCPTools:
    """MCP tool delegation tests."""

    @patch("scitex_ssh.setup")
    def test_tunnel_setup_delegates(self, mock_setup):
        mock_setup.return_value = {
            "success": True,
            "stdout": "started",
            "stderr": "",
        }
        server = create_server()
        tool_fn = _get_tool_fn(server, "tunnel_setup")
        result = tool_fn(
            port=2222, bastion_server="user@host", secret_key_path="/dev/null"
        )
        mock_setup.assert_called_once_with(2222, "user@host", "/dev/null")
        assert result["success"] is True

    @patch("scitex_ssh.status")
    def test_tunnel_status_delegates(self, mock_status):
        mock_status.return_value = {
            "success": True,
            "stdout": "active",
            "stderr": "",
        }
        server = create_server()
        tool_fn = _get_tool_fn(server, "tunnel_status")
        result = tool_fn(port=None)
        mock_status.assert_called_once_with(None)
        assert result["success"] is True

    @patch("scitex_ssh.status")
    def test_tunnel_status_with_port(self, mock_status):
        mock_status.return_value = {
            "success": True,
            "stdout": "port 2222 active",
            "stderr": "",
        }
        server = create_server()
        tool_fn = _get_tool_fn(server, "tunnel_status")
        tool_fn(port=2222)
        mock_status.assert_called_once_with(2222)

    @patch("scitex_ssh.remove")
    def test_tunnel_remove_delegates(self, mock_remove):
        mock_remove.return_value = {
            "success": True,
            "stdout": "removed",
            "stderr": "",
        }
        server = create_server()
        tool_fn = _get_tool_fn(server, "tunnel_remove")
        result = tool_fn(port=2222)
        mock_remove.assert_called_once_with(2222)
        assert result["success"] is True


# EOF
