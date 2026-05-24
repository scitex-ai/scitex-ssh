#!/usr/bin/env python3
"""Tests for scitex_ssh._cli._mcp — `mcp` subgroup CLI.

No mocks. Each test runs the real Click command and asserts one thing;
shared `--json` invocations are lifted into fixtures so every test stays
single-assertion.
"""

from __future__ import annotations

import json

import pytest
from click.testing import CliRunner

from scitex_ssh._cli._mcp import mcp


@pytest.fixture
def install_payload():
    """Parse `mcp show-installation --json` once."""
    result = CliRunner().invoke(mcp, ["show-installation", "--json"])
    assert result.exit_code == 0, result.output
    return json.loads(result.output)


@pytest.fixture
def list_tools_payload():
    """Parse `mcp list-tools --json` once."""
    result = CliRunner().invoke(mcp, ["list-tools", "--json"])
    assert result.exit_code == 0, result.output
    return json.loads(result.output)


class TestMcpGroup:
    def test_help_exits_zero(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["--help"])
        # Assert
        assert result.exit_code == 0

    def test_help_lists_all_subcommands(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["--help"])
        # Assert
        assert all(
            sub in result.output
            for sub in ("start", "doctor", "show-installation", "list-tools")
        )


class TestMcpStart:
    def test_dry_run_exits_zero(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["start", "--dry-run"])
        # Assert
        assert result.exit_code == 0

    def test_dry_run_announces_dry_run(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["start", "--dry-run"])
        # Assert
        assert "DRY RUN" in result.output


class TestMcpDoctor:
    def test_doctor_exits_zero_or_one(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["doctor"])
        # Assert
        assert result.exit_code in (0, 1)

    def test_doctor_mentions_fastmcp(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["doctor"])
        # Assert
        assert "fastmcp" in result.output

    def test_doctor_mentions_autossh(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["doctor"])
        # Assert
        assert "autossh" in result.output


class TestMcpShowInstallation:
    def test_text_output_exits_zero(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["show-installation"])
        # Assert
        assert result.exit_code == 0

    def test_text_output_shows_pip_install_command(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["show-installation"])
        # Assert
        assert "pip install scitex-ssh[mcp]" in result.output

    def test_text_output_shows_mcp_servers_block(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["show-installation"])
        # Assert
        assert "mcpServers" in result.output

    def test_json_output_exits_zero(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["show-installation", "--json"])
        # Assert
        assert result.exit_code == 0

    def test_json_payload_carries_install_command(self, install_payload):
        # Arrange
        payload = install_payload
        # Act
        install_command = payload["install_command"]
        # Assert
        assert install_command == "pip install scitex-ssh[mcp]"

    def test_json_payload_registers_the_server(self, install_payload):
        # Arrange
        payload = install_payload
        # Act
        servers = payload["config"]["mcpServers"]
        # Assert
        assert "scitex-ssh" in servers


class TestMcpListTools:
    def test_default_lists_tools_exits_zero(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["list-tools"])
        # Assert
        assert result.exit_code == 0

    def test_default_lists_all_tunnel_tool_names(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["list-tools"])
        # Assert
        assert all(
            tool in result.output
            for tool in ("tunnel_setup", "tunnel_status", "tunnel_remove")
        )

    def test_verbose_exits_zero(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["list-tools", "-v"])
        # Assert
        assert result.exit_code == 0

    def test_verbose_includes_tool_descriptions(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["list-tools", "-v"])
        # Assert
        assert "Set up" in result.output

    def test_very_verbose_exits_zero(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["list-tools", "-vv"])
        # Assert
        assert result.exit_code == 0

    def test_very_verbose_includes_params(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["list-tools", "-vv"])
        # Assert
        assert "params:" in result.output

    def test_json_output_exits_zero(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["list-tools", "--json"])
        # Assert
        assert result.exit_code == 0

    def test_json_payload_reports_three_tools(self, list_tools_payload):
        # Arrange
        payload = list_tools_payload
        # Act
        total = payload["total"]
        # Assert
        assert total == 3

    def test_json_payload_lists_the_three_tunnel_tools(self, list_tools_payload):
        # Arrange
        payload = list_tools_payload
        # Act
        names = {t["name"] for t in payload["tools"]}
        # Assert
        assert {"tunnel_setup", "tunnel_status", "tunnel_remove"} == names


class TestDeprecatedInstallationAlias:
    def test_installation_alias_exits_two(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["installation"])
        # Assert
        assert result.exit_code == 2

    def test_installation_alias_redirects_to_show_installation(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["installation"])
        # Assert
        assert "show-installation" in result.output


# EOF
