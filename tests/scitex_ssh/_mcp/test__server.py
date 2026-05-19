#!/usr/bin/env python3
"""Tests for MCP server tools."""

import asyncio
from unittest.mock import patch

import pytest

pytest.importorskip("fastmcp")

from scitex_ssh._mcp._server import create_server  # noqa: E402


def _get_tool_fn(server, name):
    """Resolve a tool's underlying callable via FastMCP's public async API."""
    tool = asyncio.run(server.get_tool(name))
    assert tool is not None, f"tool {name!r} not registered"
    return tool.fn


class TestCreateServer:
    """MCP server creation tests."""

    def test_create_server_returns_fastmcp_server_is_not_none(self):
        # Arrange
        # Arrange
        # Act
        server = create_server()
        # Act
        # Assert
        # Assert
        assert server is not None

    def test_create_server_returns_fastmcp_server_name_equals_scitex_ssh(self):
        # Arrange
        # Arrange
        # Act
        server = create_server()
        # Act
        # Assert
        # Assert
        assert server.name == "scitex-ssh"


    def test_server_registers_expected_tools(self):
        # Arrange
        # Arrange
        server = create_server()
        # Act
        # Act
        names = {t.name for t in asyncio.run(server.list_tools())}
        # Assert
        # Assert
        assert {"tunnel_setup", "tunnel_status", "tunnel_remove"}.issubset(names)


class TestMCPTools:
    """MCP tool delegation tests."""

    @patch("scitex_ssh.setup")
    def test_tunnel_setup_delegates(self, mock_setup):
        # Arrange
        # Arrange
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
        # Act
        # Act
        mock_setup.assert_called_once_with(2222, "user@host", "/dev/null")
        # Assert
        # Assert
        assert result["success"] is True

    @patch("scitex_ssh.status")
    def test_tunnel_status_delegates(self, mock_status):
        # Arrange
        # Arrange
        mock_status.return_value = {
            "success": True,
            "stdout": "active",
            "stderr": "",
        }
        server = create_server()
        tool_fn = _get_tool_fn(server, "tunnel_status")
        result = tool_fn(port=None)
        # Act
        # Act
        mock_status.assert_called_once_with(None)
        # Assert
        # Assert
        assert result["success"] is True

    @patch("scitex_ssh.status")
    def test_tunnel_status_with_port(self, mock_status):
        # Arrange
        # Act
        # Assert
        # Arrange
        # Act
        # Assert
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
        # Arrange
        # Arrange
        mock_remove.return_value = {
            "success": True,
            "stdout": "removed",
            "stderr": "",
        }
        server = create_server()
        tool_fn = _get_tool_fn(server, "tunnel_remove")
        result = tool_fn(port=2222)
        # Act
        # Act
        mock_remove.assert_called_once_with(2222)
        # Assert
        # Assert
        assert result["success"] is True


# EOF
