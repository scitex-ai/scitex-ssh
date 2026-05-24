#!/usr/bin/env python3
"""Tests for MCP server tools.

No mocks. Tool callables run the real `scitex_ssh.setup/status/remove`
against a fake `bash`/`systemctl` on $PATH (subprocess_shim) and a real
allowlist config (allow_tunnels). We assert on the real returned dict,
not on "was the delegate called".
"""

import asyncio

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

    def test_create_server_returns_an_object(self):
        # Arrange
        # Act
        server = create_server()
        # Assert
        assert server is not None

    def test_create_server_names_the_server_scitex_ssh(self):
        # Arrange
        # Act
        server = create_server()
        # Assert
        assert server.name == "scitex-ssh"

    def test_server_registers_the_three_tunnel_tools(self):
        # Arrange
        server = create_server()
        # Act
        names = {t.name for t in asyncio.run(server.list_tools())}
        # Assert
        assert {"tunnel_setup", "tunnel_status", "tunnel_remove"}.issubset(names)


class TestMCPTools:
    """MCP tool delegation tests — exercised against real collaborators."""

    def test_tunnel_setup_returns_success_when_script_exits_zero(
        self, subprocess_shim, allow_tunnels
    ):
        # Arrange
        subprocess_shim.install("bash", rc=0, stdout="started")
        tool_fn = _get_tool_fn(create_server(), "tunnel_setup")
        # Act
        result = tool_fn(
            port=2222, bastion_server="user@host", secret_key_path="/dev/null"
        )
        # Assert
        assert result["success"] is True

    def test_tunnel_setup_propagates_script_stdout(
        self, subprocess_shim, allow_tunnels
    ):
        # Arrange
        subprocess_shim.install("bash", rc=0, stdout="started")
        tool_fn = _get_tool_fn(create_server(), "tunnel_setup")
        # Act
        result = tool_fn(
            port=2222, bastion_server="user@host", secret_key_path="/dev/null"
        )
        # Assert
        assert result["stdout"] == "started"

    def test_tunnel_setup_reports_failure_when_script_exits_nonzero(
        self, subprocess_shim, allow_tunnels
    ):
        # Arrange
        subprocess_shim.install("bash", rc=1, stderr="boom")
        tool_fn = _get_tool_fn(create_server(), "tunnel_setup")
        # Act
        result = tool_fn(
            port=2222, bastion_server="user@host", secret_key_path="/dev/null"
        )
        # Assert
        assert result["success"] is False

    def test_tunnel_status_returns_success_for_all_tunnels(self, subprocess_shim):
        # Arrange — status is not allowlist-gated
        subprocess_shim.install("systemctl", rc=0, stdout="active")
        tool_fn = _get_tool_fn(create_server(), "tunnel_status")
        # Act
        result = tool_fn(port=None)
        # Assert
        assert result["success"] is True

    def test_tunnel_status_for_all_tunnels_runs_systemctl(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("systemctl", rc=0, stdout="active")
        tool_fn = _get_tool_fn(create_server(), "tunnel_status")
        # Act
        tool_fn(port=None)
        # Assert
        assert subprocess_shim.call_count("systemctl") == 1

    def test_tunnel_status_for_specific_port_queries_that_unit(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("systemctl", rc=0, stdout="port 2222 active")
        tool_fn = _get_tool_fn(create_server(), "tunnel_status")
        # Act
        tool_fn(port=2222)
        # Assert
        assert "autossh-tunnel-2222.service" in subprocess_shim.argv("systemctl")

    def test_tunnel_remove_returns_success_when_script_exits_zero(
        self, subprocess_shim, allow_tunnels
    ):
        # Arrange
        subprocess_shim.install("bash", rc=0, stdout="removed")
        tool_fn = _get_tool_fn(create_server(), "tunnel_remove")
        # Act
        result = tool_fn(port=2222)
        # Assert
        assert result["success"] is True

    def test_tunnel_remove_propagates_script_stdout(
        self, subprocess_shim, allow_tunnels
    ):
        # Arrange
        subprocess_shim.install("bash", rc=0, stdout="removed")
        tool_fn = _get_tool_fn(create_server(), "tunnel_remove")
        # Act
        result = tool_fn(port=2222)
        # Assert
        assert result["stdout"] == "removed"


# EOF
