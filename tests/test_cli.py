#!/usr/bin/env python3
"""Tests for scitex-tunnel CLI."""

from unittest.mock import patch

from click.testing import CliRunner

from scitex_tunnel.cli import main


class TestCLI:
    """CLI command tests."""

    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "setup" in result.output
        assert "remove" in result.output
        assert "status" in result.output

    def test_help_short(self):
        runner = CliRunner()
        result = runner.invoke(main, ["-h"])
        assert result.exit_code == 0
        assert "setup" in result.output

    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(main, ["-V"])
        assert result.exit_code == 0
        assert "scitex-tunnel" in result.output

    def test_help_recursive(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--help-recursive"])
        assert result.exit_code == 0
        assert "setup" in result.output
        assert "remove" in result.output
        assert "status" in result.output
        assert "mcp" in result.output

    def test_no_subcommand_shows_help(self):
        runner = CliRunner()
        result = runner.invoke(main, [])
        assert result.exit_code == 0
        assert "setup" in result.output

    def test_setup_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["setup", "--help"])
        assert result.exit_code == 0
        assert "--port" in result.output
        assert "--bastion" in result.output
        assert "--secret-key" in result.output

    def test_remove_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["remove", "--help"])
        assert result.exit_code == 0
        assert "--port" in result.output

    def test_status_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["status", "--help"])
        assert result.exit_code == 0
        assert "--port" in result.output

    @patch("scitex_tunnel.status")
    def test_status_invocation(self, mock_status):
        mock_status.return_value = {
            "success": True,
            "stdout": "active tunnels",
            "stderr": "",
        }
        runner = CliRunner()
        result = runner.invoke(main, ["status"])
        assert result.exit_code == 0
        assert "active tunnels" in result.output

    @patch("scitex_tunnel.status")
    def test_status_with_stderr(self, mock_status):
        mock_status.return_value = {
            "success": False,
            "stdout": "",
            "stderr": "some error",
        }
        runner = CliRunner()
        result = runner.invoke(main, ["status"])
        assert result.exit_code == 0

    @patch("scitex_tunnel.setup")
    def test_setup_success(self, mock_setup):
        mock_setup.return_value = {
            "success": True,
            "stdout": "service started",
            "stderr": "",
        }
        runner = CliRunner()
        result = runner.invoke(
            main, ["setup", "-p", "2222", "-b", "user@host", "-s", "/dev/null"]
        )
        assert result.exit_code == 0
        assert "successfully" in result.output

    @patch("scitex_tunnel.setup")
    def test_setup_failure(self, mock_setup):
        mock_setup.return_value = {
            "success": False,
            "stdout": "",
            "stderr": "permission denied",
        }
        runner = CliRunner()
        result = runner.invoke(
            main, ["setup", "-p", "2222", "-b", "user@host", "-s", "/dev/null"]
        )
        assert result.exit_code != 0

    @patch("scitex_tunnel.remove")
    def test_remove_success(self, mock_remove):
        mock_remove.return_value = {
            "success": True,
            "stdout": "removed",
            "stderr": "",
        }
        runner = CliRunner()
        result = runner.invoke(main, ["remove", "-p", "2222"])
        assert result.exit_code == 0
        assert "removed" in result.output.lower()

    @patch("scitex_tunnel.remove")
    def test_remove_failure(self, mock_remove):
        mock_remove.return_value = {
            "success": False,
            "stdout": "",
            "stderr": "not found",
        }
        runner = CliRunner()
        result = runner.invoke(main, ["remove", "-p", "2222"])
        assert result.exit_code != 0

    def test_setup_missing_required(self):
        runner = CliRunner()
        result = runner.invoke(main, ["setup"])
        assert result.exit_code != 0

    def test_remove_missing_required(self):
        runner = CliRunner()
        result = runner.invoke(main, ["remove"])
        assert result.exit_code != 0


class TestIntrospect:
    """list-python-apis tests."""

    def test_list_python_apis(self):
        runner = CliRunner()
        result = runner.invoke(main, ["list-python-apis"])
        assert result.exit_code == 0
        assert "setup" in result.output
        assert "remove" in result.output
        assert "status" in result.output

    def test_list_python_apis_verbose(self):
        runner = CliRunner()
        result = runner.invoke(main, ["list-python-apis", "-v"])
        assert result.exit_code == 0
        assert "AVAILABLE" in result.output

    def test_list_python_apis_very_verbose(self):
        runner = CliRunner()
        result = runner.invoke(main, ["list-python-apis", "-vv"])
        assert result.exit_code == 0
        assert "setup" in result.output


class TestMCPCli:
    """MCP CLI subcommand tests."""

    def test_mcp_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["mcp", "--help"])
        assert result.exit_code == 0
        assert "start" in result.output
        assert "list-tools" in result.output

    def test_mcp_list_tools(self):
        runner = CliRunner()
        result = runner.invoke(main, ["mcp", "list-tools"])
        assert result.exit_code == 0
        assert "tunnel_setup" in result.output
        assert "tunnel_status" in result.output
        assert "tunnel_remove" in result.output

    def test_mcp_list_tools_verbose(self):
        runner = CliRunner()
        result = runner.invoke(main, ["mcp", "list-tools", "-v"])
        assert result.exit_code == 0
        assert "Set up" in result.output

    def test_mcp_list_tools_very_verbose(self):
        runner = CliRunner()
        result = runner.invoke(main, ["mcp", "list-tools", "-vv"])
        assert result.exit_code == 0
        assert "params:" in result.output


# EOF
