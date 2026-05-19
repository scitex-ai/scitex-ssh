#!/usr/bin/env python3
"""Tests for scitex_ssh._cli._mcp — `mcp` subgroup CLI."""

import json

from click.testing import CliRunner

from scitex_ssh._cli._mcp import mcp


class TestMcpGroup:
    def test_help_lists_subcommands_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["--help"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_help_lists_subcommands_all_sub_in_result_output_for_sub_in_start_doctor_show_instal(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["--help"])
        # Act
        # Assert
        # Assert
        assert all(sub in result.output for sub in ('start', 'doctor', 'show-installation', 'list-tools'))



class TestMcpStart:
    def test_dry_run_does_not_spawn_server_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["start", "--dry-run"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_dry_run_does_not_spawn_server_dry_run_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["start", "--dry-run"])
        # Act
        # Assert
        # Assert
        assert "DRY RUN" in result.output



class TestMcpDoctor:
    def test_doctor_runs_and_reports_result_exit_code_in_n_0_1(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["doctor"])
        # Act
        # Assert
        # Assert
        assert result.exit_code in (0, 1)

    def test_doctor_runs_and_reports_fastmcp_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["doctor"])
        # Act
        # Assert
        # Assert
        assert "fastmcp" in result.output

    def test_doctor_runs_and_reports_autossh_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["doctor"])
        # Act
        # Assert
        # Assert
        assert "autossh" in result.output



class TestMcpShowInstallation:
    def test_text_output_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["show-installation"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_text_output_pip_install_scitex_ssh_mcp_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["show-installation"])
        # Act
        # Assert
        # Assert
        assert "pip install scitex-ssh[mcp]" in result.output

    def test_text_output_mcpservers_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["show-installation"])
        # Act
        # Assert
        # Assert
        assert "mcpServers" in result.output


    def test_json_output_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["show-installation", "--json"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_json_output_payload_install_command_pip_install_scitex_ssh_mcp_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["show-installation", "--json"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_json_output_payload_install_command_pip_install_scitex_ssh_mcp_payload_install_command_pip_install_scitex_ssh_mcp(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["show-installation", "--json"])
        # Assert
        assert result.exit_code == 0
        payload = json.loads(result.output)
        # Act
        # Assert
        assert payload["install_command"] == "pip install scitex-ssh[mcp]"


    def test_json_output_scitex_ssh_in_payload_config_mcpservers_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["show-installation", "--json"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_json_output_scitex_ssh_in_payload_config_mcpservers_scitex_ssh_in_payload_config_mcpservers(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["show-installation", "--json"])
        # Assert
        assert result.exit_code == 0
        payload = json.loads(result.output)
        # Act
        # Assert
        assert "scitex-ssh" in payload["config"]["mcpServers"]




class TestMcpListTools:
    def test_default_lists_tool_names_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["list-tools"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_default_lists_tool_names_all_tool_in_result_output_for_tool_in_tunnel_setup_tunnel_st(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["list-tools"])
        # Act
        # Assert
        # Assert
        assert all(tool in result.output for tool in ('tunnel_setup', 'tunnel_status', 'tunnel_remove'))


    def test_verbose_includes_descriptions_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["list-tools", "-v"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_verbose_includes_descriptions_set_up_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["list-tools", "-v"])
        # Act
        # Assert
        # Assert
        assert "Set up" in result.output


    def test_very_verbose_includes_params_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["list-tools", "-vv"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_very_verbose_includes_params_params_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["list-tools", "-vv"])
        # Act
        # Assert
        # Assert
        assert "params:" in result.output


    def test_json_emits_structured_payload_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["list-tools", "--json"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_json_emits_structured_payload_payload_total_3_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["list-tools", "--json"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_json_emits_structured_payload_payload_total_3_payload_total_3(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["list-tools", "--json"])
        # Assert
        assert result.exit_code == 0
        payload = json.loads(result.output)
        # Act
        # Assert
        assert payload["total"] == 3


    def test_json_emits_structured_payload_tunnel_setup_tunnel_status_tunnel_remove_names_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["list-tools", "--json"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_json_emits_structured_payload_tunnel_setup_tunnel_status_tunnel_remove_names_payload_total_3(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["list-tools", "--json"])
        # Assert
        assert result.exit_code == 0
        payload = json.loads(result.output)
        # Act
        # Assert
        assert payload["total"] == 3

    def test_json_emits_structured_payload_tunnel_setup_tunnel_status_tunnel_remove_names_tunnel_setup_tunnel_status_tunnel_remove_names(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["list-tools", "--json"])
        # Assert
        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["total"] == 3
        names = {t["name"] for t in payload["tools"]}
        # Act
        # Assert
        assert {"tunnel_setup", "tunnel_status", "tunnel_remove"} == names




class TestDeprecatedInstallationAlias:
    def test_installation_alias_errors_with_redirect_result_exit_code_equals_n_2(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["installation"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 2

    def test_installation_alias_errors_with_redirect_show_installation_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(mcp, ["installation"])
        # Act
        # Assert
        # Assert
        assert "show-installation" in result.output



# EOF
