#!/usr/bin/env python3
"""Tests for scitex-ssh CLI."""

from unittest.mock import patch

from click.testing import CliRunner

from scitex_ssh.cli import main


class TestCLI:
    """CLI command tests."""

    def test_help_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["--help"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_help_tunnel_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["--help"])
        # Act
        # Assert
        # Assert
        assert "tunnel" in result.output

    def test_help_exec_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["--help"])
        # Act
        # Assert
        # Assert
        assert "exec" in result.output

    def test_help_copy_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["--help"])
        # Act
        # Assert
        # Assert
        assert "copy" in result.output

    def test_help_attach_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["--help"])
        # Act
        # Assert
        # Assert
        assert "attach" in result.output


    def test_help_short_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["-h"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_help_short_tunnel_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["-h"])
        # Act
        # Assert
        # Assert
        assert "tunnel" in result.output


    def test_version_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["-V"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_version_scitex_ssh_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["-V"])
        # Act
        # Assert
        # Assert
        assert "scitex-ssh" in result.output


    def test_help_recursive_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["--help-recursive"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_help_recursive_setup_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["--help-recursive"])
        # Act
        # Assert
        # Assert
        assert "setup" in result.output

    def test_help_recursive_remove_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["--help-recursive"])
        # Act
        # Assert
        # Assert
        assert "remove" in result.output

    def test_help_recursive_status_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["--help-recursive"])
        # Act
        # Assert
        # Assert
        assert "status" in result.output

    def test_help_recursive_mcp_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["--help-recursive"])
        # Act
        # Assert
        # Assert
        assert "mcp" in result.output


    def test_no_subcommand_shows_help_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, [])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_no_subcommand_shows_help_tunnel_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, [])
        # Act
        # Assert
        # Assert
        assert "tunnel" in result.output


    def test_setup_help_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["setup-tunnel", "--help"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_setup_help_port_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["setup-tunnel", "--help"])
        # Act
        # Assert
        # Assert
        assert "--port" in result.output

    def test_setup_help_bastion_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["setup-tunnel", "--help"])
        # Act
        # Assert
        # Assert
        assert "--bastion" in result.output

    def test_setup_help_secret_key_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["setup-tunnel", "--help"])
        # Act
        # Assert
        # Assert
        assert "--secret-key" in result.output


    def test_remove_help_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["remove-tunnel", "--help"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_remove_help_port_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["remove-tunnel", "--help"])
        # Act
        # Assert
        # Assert
        assert "--port" in result.output


    def test_status_help_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["show-status", "--help"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_status_help_port_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["show-status", "--help"])
        # Act
        # Assert
        # Assert
        assert "--port" in result.output


    @patch("scitex_ssh.status")
    def test_status_invocation_result_exit_code_equals_n_0(self, mock_status):
        # Arrange
        # Arrange
        mock_status.return_value = {
            "success": True,
            "stdout": "active tunnels",
            "stderr": "",
        }
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["show-status"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    @patch("scitex_ssh.status")
    def test_status_invocation_active_tunnels_in_result_output(self, mock_status):
        # Arrange
        # Arrange
        mock_status.return_value = {
            "success": True,
            "stdout": "active tunnels",
            "stderr": "",
        }
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["show-status"])
        # Act
        # Assert
        # Assert
        assert "active tunnels" in result.output


    @patch("scitex_ssh.status")
    def test_status_with_stderr(self, mock_status):
        # Arrange
        # Arrange
        mock_status.return_value = {
            "success": False,
            "stdout": "",
            "stderr": "some error",
        }
        runner = CliRunner()
        # Act
        # Act
        result = runner.invoke(main, ["show-status"])
        # Assert
        # Assert
        assert result.exit_code == 0

    @patch("scitex_ssh.setup")
    def test_setup_success_result_exit_code_equals_n_0(self, mock_setup):
        # Arrange
        # Arrange
        mock_setup.return_value = {
            "success": True,
            "stdout": "service started",
            "stderr": "",
        }
        runner = CliRunner()
        # Act
        result = runner.invoke(
            main,
            ["setup-tunnel", "-p", "2222", "-b", "user@host", "-s", "/dev/null"],
        )
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    @patch("scitex_ssh.setup")
    def test_setup_success_successfully_in_result_output(self, mock_setup):
        # Arrange
        # Arrange
        mock_setup.return_value = {
            "success": True,
            "stdout": "service started",
            "stderr": "",
        }
        runner = CliRunner()
        # Act
        result = runner.invoke(
            main,
            ["setup-tunnel", "-p", "2222", "-b", "user@host", "-s", "/dev/null"],
        )
        # Act
        # Assert
        # Assert
        assert "successfully" in result.output


    @patch("scitex_ssh.setup")
    def test_setup_failure_result_exit_code_0(self, mock_setup):
        # Arrange
        # Arrange
        mock_setup.return_value = {
            "success": False,
            "stdout": "",
            "stderr": "permission denied",
        }
        runner = CliRunner()
        # Act
        # Act
        result = runner.invoke(
            main,
            ["setup-tunnel", "-p", "2222", "-b", "user@host", "-s", "/dev/null"],
        )
        # Assert
        # Assert
        assert result.exit_code != 0

    @patch("scitex_ssh.remove")
    def test_remove_success_result_exit_code_equals_n_0(self, mock_remove):
        # Arrange
        # Arrange
        mock_remove.return_value = {
            "success": True,
            "stdout": "removed",
            "stderr": "",
        }
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["remove-tunnel", "-p", "2222"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    @patch("scitex_ssh.remove")
    def test_remove_success_removed_in_result_output_lower(self, mock_remove):
        # Arrange
        # Arrange
        mock_remove.return_value = {
            "success": True,
            "stdout": "removed",
            "stderr": "",
        }
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["remove-tunnel", "-p", "2222"])
        # Act
        # Assert
        # Assert
        assert "removed" in result.output.lower()


    @patch("scitex_ssh.remove")
    def test_remove_failure_result_exit_code_0(self, mock_remove):
        # Arrange
        # Arrange
        mock_remove.return_value = {
            "success": False,
            "stdout": "",
            "stderr": "not found",
        }
        runner = CliRunner()
        # Act
        # Act
        result = runner.invoke(main, ["remove-tunnel", "-p", "2222"])
        # Assert
        # Assert
        assert result.exit_code != 0

    def test_setup_missing_required(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        # Act
        result = runner.invoke(main, ["setup-tunnel"])
        # Assert
        # Assert
        assert result.exit_code != 0

    def test_remove_missing_required(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        # Act
        result = runner.invoke(main, ["remove-tunnel"])
        # Assert
        # Assert
        assert result.exit_code != 0


class TestIntrospect:
    """list-python-apis tests."""

    def test_list_python_apis_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["list-python-apis"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_list_python_apis_setup_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["list-python-apis"])
        # Act
        # Assert
        # Assert
        assert "setup" in result.output

    def test_list_python_apis_remove_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["list-python-apis"])
        # Act
        # Assert
        # Assert
        assert "remove" in result.output

    def test_list_python_apis_status_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["list-python-apis"])
        # Act
        # Assert
        # Assert
        assert "status" in result.output


    def test_list_python_apis_verbose_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["list-python-apis", "-v"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_list_python_apis_verbose_available_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["list-python-apis", "-v"])
        # Act
        # Assert
        # Assert
        assert "AVAILABLE" in result.output


    def test_list_python_apis_very_verbose_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["list-python-apis", "-vv"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_list_python_apis_very_verbose_setup_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["list-python-apis", "-vv"])
        # Act
        # Assert
        # Assert
        assert "setup" in result.output



class TestMCPCli:
    """MCP CLI subcommand tests."""

    def test_mcp_help_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["mcp", "--help"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_mcp_help_start_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["mcp", "--help"])
        # Act
        # Assert
        # Assert
        assert "start" in result.output

    def test_mcp_help_list_tools_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["mcp", "--help"])
        # Act
        # Assert
        # Assert
        assert "list-tools" in result.output


    def test_mcp_list_tools_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["mcp", "list-tools"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_mcp_list_tools_tunnel_setup_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["mcp", "list-tools"])
        # Act
        # Assert
        # Assert
        assert "tunnel_setup" in result.output

    def test_mcp_list_tools_tunnel_status_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["mcp", "list-tools"])
        # Act
        # Assert
        # Assert
        assert "tunnel_status" in result.output

    def test_mcp_list_tools_tunnel_remove_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["mcp", "list-tools"])
        # Act
        # Assert
        # Assert
        assert "tunnel_remove" in result.output


    def test_mcp_list_tools_verbose_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["mcp", "list-tools", "-v"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_mcp_list_tools_verbose_set_up_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["mcp", "list-tools", "-v"])
        # Act
        # Assert
        # Assert
        assert "Set up" in result.output


    def test_mcp_list_tools_very_verbose_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["mcp", "list-tools", "-vv"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_mcp_list_tools_very_verbose_params_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["mcp", "list-tools", "-vv"])
        # Act
        # Assert
        # Assert
        assert "params:" in result.output


    def test_mcp_doctor_result_exit_code_in_n_0_1(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["mcp", "doctor"])
        # Act
        # Assert
        # Assert
        assert result.exit_code in (0, 1)  # 1 if deps missing (e.g., CI)

    def test_mcp_doctor_fastmcp_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["mcp", "doctor"])
        # Act
        # Assert
        # Assert
        assert "fastmcp" in result.output


    def test_mcp_installation_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["mcp", "show-installation"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0, result.output

    def test_mcp_installation_pip_install_scitex_ssh_mcp_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["mcp", "show-installation"])
        # Act
        # Assert
        # Assert
        assert "pip install scitex-ssh[mcp]" in result.output

    def test_mcp_installation_mcpservers_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["mcp", "show-installation"])
        # Act
        # Assert
        # Assert
        assert "mcpServers" in result.output


    @patch("scitex_ssh.setup")
    def test_setup_env_var_fallback_error_result_exit_code_0(self, mock_setup):
        # Arrange
        # Arrange
        mock_setup.side_effect = ValueError("bastion_server is required")
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["setup-tunnel", "-p", "2222"])
        # Act
        # Assert
        # Assert
        assert result.exit_code != 0

    @patch("scitex_ssh.setup")
    def test_setup_env_var_fallback_error_bastion_server_is_required_in_result_output(self, mock_setup):
        # Arrange
        # Arrange
        mock_setup.side_effect = ValueError("bastion_server is required")
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["setup-tunnel", "-p", "2222"])
        # Act
        # Assert
        # Assert
        assert "bastion_server is required" in result.output



# EOF
