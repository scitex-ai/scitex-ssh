#!/usr/bin/env python3
"""Tests for scitex_ssh._cli._mcp — `mcp` subgroup CLI."""

import json

from click.testing import CliRunner

from scitex_ssh._cli._mcp import mcp


class TestMcpGroup:
    def test_help_lists_subcommands(self):
        runner = CliRunner()
        result = runner.invoke(mcp, ["--help"])
        assert result.exit_code == 0
        for sub in ("start", "doctor", "show-installation", "list-tools"):
            assert sub in result.output


class TestMcpStart:
    def test_dry_run_does_not_spawn_server(self):
        runner = CliRunner()
        result = runner.invoke(mcp, ["start", "--dry-run"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.output


class TestMcpDoctor:
    def test_doctor_runs_and_reports(self):
        runner = CliRunner()
        result = runner.invoke(mcp, ["doctor"])
        # 0 if both deps present, 1 if any missing — both are valid run states.
        assert result.exit_code in (0, 1)
        assert "fastmcp" in result.output
        assert "autossh" in result.output


class TestMcpShowInstallation:
    def test_text_output(self):
        runner = CliRunner()
        result = runner.invoke(mcp, ["show-installation"])
        assert result.exit_code == 0
        assert "pip install scitex-ssh[mcp]" in result.output
        assert "mcpServers" in result.output

    def test_json_output(self):
        runner = CliRunner()
        result = runner.invoke(mcp, ["show-installation", "--json"])
        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["install_command"] == "pip install scitex-ssh[mcp]"
        assert "scitex-ssh" in payload["config"]["mcpServers"]


class TestMcpListTools:
    def test_default_lists_tool_names(self):
        runner = CliRunner()
        result = runner.invoke(mcp, ["list-tools"])
        assert result.exit_code == 0
        for tool in ("tunnel_setup", "tunnel_status", "tunnel_remove"):
            assert tool in result.output

    def test_verbose_includes_descriptions(self):
        runner = CliRunner()
        result = runner.invoke(mcp, ["list-tools", "-v"])
        assert result.exit_code == 0
        assert "Set up" in result.output

    def test_very_verbose_includes_params(self):
        runner = CliRunner()
        result = runner.invoke(mcp, ["list-tools", "-vv"])
        assert result.exit_code == 0
        assert "params:" in result.output

    def test_json_emits_structured_payload(self):
        runner = CliRunner()
        result = runner.invoke(mcp, ["list-tools", "--json"])
        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["total"] == 3
        names = {t["name"] for t in payload["tools"]}
        assert {"tunnel_setup", "tunnel_status", "tunnel_remove"} == names


class TestDeprecatedInstallationAlias:
    def test_installation_alias_errors_with_redirect(self):
        runner = CliRunner()
        result = runner.invoke(mcp, ["installation"])
        assert result.exit_code == 2
        assert "show-installation" in result.output


# EOF
