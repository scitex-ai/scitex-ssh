#!/usr/bin/env python3
"""Tests for MCP server tools.

Uses ``create_server(setup_fn=..., status_fn=..., remove_fn=...)`` —
production accepts injectable callables so we exercise the real
``FastMCP`` tool wiring against hand-rolled fakes (no ``unittest.mock``).
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

import pytest

pytest.importorskip("fastmcp")

from scitex_ssh._mcp._server import create_server  # noqa: E402


# ---------------------------------------------------------------------
# Hand-rolled delegate fakes — record every call as a flat dict so tests
# can assert on call shape and stage return values per case.
# ---------------------------------------------------------------------


@dataclass
class _FakeDelegate:
    """Records positional + keyword args from each call."""

    return_value: dict = field(
        default_factory=lambda: {"success": True, "stdout": "", "stderr": ""}
    )
    calls: list[tuple[tuple[Any, ...], dict[str, Any]]] = field(default_factory=list)

    def __call__(self, *args, **kwargs) -> dict:
        self.calls.append((args, dict(kwargs)))
        return dict(self.return_value)


def _get_tool_fn(server, name):
    """Resolve a tool's underlying callable via FastMCP's public async API."""
    tool = asyncio.run(server.get_tool(name))
    assert tool is not None, f"tool {name!r} not registered"
    return tool.fn


# ---------------------------------------------------------------------
# create_server — bare construction surface
# ---------------------------------------------------------------------


class TestCreateServer:
    """MCP server creation tests."""

    def test_create_server_returns_non_none_fastmcp_instance(self) -> None:
        # Arrange
        # Act
        server = create_server()
        # Assert
        assert server is not None

    def test_create_server_names_the_server_scitex_ssh(self) -> None:
        # Arrange
        # Act
        server = create_server()
        # Assert
        assert server.name == "scitex-ssh"

    def test_create_server_registers_tunnel_setup_status_remove_tools(self) -> None:
        # Arrange
        server = create_server()
        expected = {"tunnel_setup", "tunnel_status", "tunnel_remove"}
        # Act
        names = {t.name for t in asyncio.run(server.list_tools())}
        # Assert
        assert expected.issubset(names)


# ---------------------------------------------------------------------
# Tool delegation — verify each tool calls its injected callable with
# the correct positional shape, and that the tool's return value is
# threaded through.
# ---------------------------------------------------------------------


class TestTunnelSetupTool:
    def test_tunnel_setup_forwards_positional_args_to_setup_fn(self) -> None:
        # Arrange
        fake_setup = _FakeDelegate(
            return_value={"success": True, "stdout": "started", "stderr": ""}
        )
        server = create_server(setup_fn=fake_setup)
        tool_fn = _get_tool_fn(server, "tunnel_setup")
        # Act
        tool_fn(port=2222, bastion_server="user@host", secret_key_path="/dev/null")
        # Assert
        assert fake_setup.calls[0][0] == (2222, "user@host", "/dev/null")

    def test_tunnel_setup_returns_setup_fn_result_to_caller(self) -> None:
        # Arrange
        fake_setup = _FakeDelegate(
            return_value={"success": True, "stdout": "started", "stderr": ""}
        )
        server = create_server(setup_fn=fake_setup)
        tool_fn = _get_tool_fn(server, "tunnel_setup")
        # Act
        result = tool_fn(
            port=2222, bastion_server="user@host", secret_key_path="/dev/null"
        )
        # Assert
        assert result["success"] is True


class TestTunnelStatusTool:
    def test_tunnel_status_no_port_forwards_none_to_status_fn(self) -> None:
        # Arrange
        fake_status = _FakeDelegate(
            return_value={"success": True, "stdout": "active", "stderr": ""}
        )
        server = create_server(status_fn=fake_status)
        tool_fn = _get_tool_fn(server, "tunnel_status")
        # Act
        tool_fn(port=None)
        # Assert
        assert fake_status.calls[0][0] == (None,)

    def test_tunnel_status_returns_status_fn_result_to_caller(self) -> None:
        # Arrange
        fake_status = _FakeDelegate(
            return_value={"success": True, "stdout": "active", "stderr": ""}
        )
        server = create_server(status_fn=fake_status)
        tool_fn = _get_tool_fn(server, "tunnel_status")
        # Act
        result = tool_fn(port=None)
        # Assert
        assert result["success"] is True

    def test_tunnel_status_with_port_forwards_int_to_status_fn(self) -> None:
        # Arrange
        fake_status = _FakeDelegate(
            return_value={
                "success": True,
                "stdout": "port 2222 active",
                "stderr": "",
            }
        )
        server = create_server(status_fn=fake_status)
        tool_fn = _get_tool_fn(server, "tunnel_status")
        # Act
        tool_fn(port=2222)
        # Assert
        assert fake_status.calls[0][0] == (2222,)


class TestTunnelRemoveTool:
    def test_tunnel_remove_forwards_port_to_remove_fn(self) -> None:
        # Arrange
        fake_remove = _FakeDelegate(
            return_value={"success": True, "stdout": "removed", "stderr": ""}
        )
        server = create_server(remove_fn=fake_remove)
        tool_fn = _get_tool_fn(server, "tunnel_remove")
        # Act
        tool_fn(port=2222)
        # Assert
        assert fake_remove.calls[0][0] == (2222,)

    def test_tunnel_remove_returns_remove_fn_result_to_caller(self) -> None:
        # Arrange
        fake_remove = _FakeDelegate(
            return_value={"success": True, "stdout": "removed", "stderr": ""}
        )
        server = create_server(remove_fn=fake_remove)
        tool_fn = _get_tool_fn(server, "tunnel_remove")
        # Act
        result = tool_fn(port=2222)
        # Assert
        assert result["success"] is True


# EOF
