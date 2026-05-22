#!/usr/bin/env python3
"""Tests for scitex_ssh._cli._mcp — `mcp` subgroup CLI.

All tests run real Click invocations against a live CliRunner — no
mocks. Multi-assert variants are collapsed via shared fixtures that
parse the JSON output once so each test stays single-assert (TQ007).
"""

from __future__ import annotations

import json

import pytest
from click.testing import CliRunner

from scitex_ssh._cli._mcp import mcp


# ---------------------------------------------------------------------
# Shared fixtures — parse JSON payloads once per test
# ---------------------------------------------------------------------


@pytest.fixture
def show_installation_payload() -> dict:
    runner = CliRunner()
    result = runner.invoke(mcp, ["show-installation", "--json"])
    assert result.exit_code == 0, result.output
    return json.loads(result.output)


@pytest.fixture
def list_tools_payload() -> dict:
    runner = CliRunner()
    result = runner.invoke(mcp, ["list-tools", "--json"])
    assert result.exit_code == 0, result.output
    return json.loads(result.output)


# ---------------------------------------------------------------------
# mcp --help — lists subcommands
# ---------------------------------------------------------------------


class TestMcpGroup:
    def test_help_invocation_exit_code_zero(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["--help"])
        # Assert
        assert result.exit_code == 0

    def test_help_lists_all_expected_subcommand_names(self) -> None:
        # Arrange
        runner = CliRunner()
        expected = ("start", "doctor", "show-installation", "list-tools")
        # Act
        result = runner.invoke(mcp, ["--help"])
        # Assert
        assert all(sub in result.output for sub in expected)


# ---------------------------------------------------------------------
# mcp start --dry-run
# ---------------------------------------------------------------------


class TestMcpStart:
    def test_dry_run_invocation_exit_code_zero(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["start", "--dry-run"])
        # Assert
        assert result.exit_code == 0

    def test_dry_run_output_says_dry_run(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["start", "--dry-run"])
        # Assert
        assert "DRY RUN" in result.output


# ---------------------------------------------------------------------
# mcp doctor
# ---------------------------------------------------------------------


class TestMcpDoctor:
    def test_doctor_invocation_exit_code_zero_or_one(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["doctor"])
        # Assert
        # 1 if optional deps (e.g. fastmcp) are missing — both are valid
        # outcomes for "doctor reports dependency status".
        assert result.exit_code in (0, 1)

    def test_doctor_output_mentions_fastmcp_dependency(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["doctor"])
        # Assert
        assert "fastmcp" in result.output

    def test_doctor_output_mentions_autossh_dependency(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["doctor"])
        # Assert
        assert "autossh" in result.output


# ---------------------------------------------------------------------
# mcp show-installation — text + JSON
# ---------------------------------------------------------------------


class TestMcpShowInstallationText:
    def test_text_invocation_exit_code_zero(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["show-installation"])
        # Assert
        assert result.exit_code == 0

    def test_text_output_includes_pip_install_command(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["show-installation"])
        # Assert
        assert "pip install scitex-ssh[mcp]" in result.output

    def test_text_output_includes_mcpservers_config_block(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["show-installation"])
        # Assert
        assert "mcpServers" in result.output


class TestMcpShowInstallationJson:
    def test_json_invocation_exit_code_zero(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["show-installation", "--json"])
        # Assert
        assert result.exit_code == 0

    def test_json_payload_install_command_matches_expected(
        self, show_installation_payload: dict
    ) -> None:
        # Arrange
        # Act
        install_cmd = show_installation_payload["install_command"]
        # Assert
        assert install_cmd == "pip install scitex-ssh[mcp]"

    def test_json_payload_config_mcpservers_includes_scitex_ssh(
        self, show_installation_payload: dict
    ) -> None:
        # Arrange
        # Act
        servers = show_installation_payload["config"]["mcpServers"]
        # Assert
        assert "scitex-ssh" in servers


# ---------------------------------------------------------------------
# mcp list-tools — text + JSON
# ---------------------------------------------------------------------


class TestMcpListTools:
    def test_default_invocation_exit_code_zero(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["list-tools"])
        # Assert
        assert result.exit_code == 0

    def test_default_output_lists_all_expected_tool_names(self) -> None:
        # Arrange
        runner = CliRunner()
        expected = ("tunnel_setup", "tunnel_status", "tunnel_remove")
        # Act
        result = runner.invoke(mcp, ["list-tools"])
        # Assert
        assert all(tool in result.output for tool in expected)

    def test_verbose_invocation_exit_code_zero(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["list-tools", "-v"])
        # Assert
        assert result.exit_code == 0

    def test_verbose_output_includes_setup_description_lead(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["list-tools", "-v"])
        # Assert
        assert "Set up" in result.output

    def test_very_verbose_invocation_exit_code_zero(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["list-tools", "-vv"])
        # Assert
        assert result.exit_code == 0

    def test_very_verbose_output_includes_params_label(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["list-tools", "-vv"])
        # Assert
        assert "params:" in result.output

    def test_json_invocation_exit_code_zero(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["list-tools", "--json"])
        # Assert
        assert result.exit_code == 0

    def test_json_payload_total_field_counts_three_tools(
        self, list_tools_payload: dict
    ) -> None:
        # Arrange
        # Act
        total = list_tools_payload["total"]
        # Assert
        assert total == 3

    def test_json_payload_tools_names_match_expected_set(
        self, list_tools_payload: dict
    ) -> None:
        # Arrange
        expected = {"tunnel_setup", "tunnel_status", "tunnel_remove"}
        # Act
        names = {t["name"] for t in list_tools_payload["tools"]}
        # Assert
        assert names == expected


# ---------------------------------------------------------------------
# Deprecated `installation` alias — error redirect to `show-installation`
# ---------------------------------------------------------------------


class TestDeprecatedInstallationAlias:
    def test_installation_alias_exit_code_two(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["installation"])
        # Assert
        assert result.exit_code == 2

    def test_installation_alias_output_points_to_show_installation(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["installation"])
        # Assert
        assert "show-installation" in result.output


# EOF
