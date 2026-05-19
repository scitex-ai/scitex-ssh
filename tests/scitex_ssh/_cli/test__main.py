#!/usr/bin/env python3
"""Tests for scitex_ssh._cli._main — top-level Click group, tunnel subgroup,
deprecation aliases."""

from unittest.mock import patch

from click.testing import CliRunner

from scitex_ssh._cli._main import (
    CategorizedGroup,
    _default_host,
    _get_version,
    main,
)


class TestRootGroup:
    """Root `main` group: --version / --help-recursive / no-arg behavior."""

    def test_main_is_categorized_group(self):
        # Arrange
        # Act
        # Assert
        # Arrange
        # Act
        # Assert
        assert isinstance(main, CategorizedGroup)

    def test_help_lists_categories_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["--help"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_help_lists_categories_ssh_primitives_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["--help"])
        # Act
        # Assert
        # Assert
        assert "SSH Primitives" in result.output

    def test_help_lists_categories_tunnel_management_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["--help"])
        # Act
        # Assert
        # Assert
        assert "Tunnel Management" in result.output

    def test_help_lists_categories_integration_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["--help"])
        # Act
        # Assert
        # Assert
        assert "Integration" in result.output


    def test_version_flag_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["-V"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_version_flag_scitex_ssh_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["-V"])
        # Act
        # Assert
        # Assert
        assert "scitex-ssh" in result.output


    def test_help_recursive_flag_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["--help-recursive"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_help_recursive_flag_all_token_in_result_output_for_token_in_exec_copy_attach_tun(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["--help-recursive"])
        # Act
        # Assert
        # Assert
        assert all(token in result.output for token in ['exec', 'copy', 'attach', 'tunnel', 'mcp'])


    def test_no_subcommand_prints_help_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, [])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_no_subcommand_prints_help_usage_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, [])
        # Act
        # Assert
        # Assert
        assert "Usage" in result.output



class TestTunnelSubgroup:
    """`scitex-ssh tunnel {setup,remove,status}` — including --dry-run."""

    def test_tunnel_help_result_exit_code_equals_n_0_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["tunnel", "--help"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_tunnel_help_result_exit_code_equals_n_0_all_sub_in_result_output_for_sub_in_setup_remove_status(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["tunnel", "--help"])
        # Act
        # Assert
        # Assert
        assert all(sub in result.output for sub in ('setup', 'remove', 'status'))


    def test_tunnel_setup_dry_run_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(
            main,
            ["tunnel", "setup", "-p", "8080", "-b", "user@host", "--dry-run"],
        )
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_tunnel_setup_dry_run_dry_run_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(
            main,
            ["tunnel", "setup", "-p", "8080", "-b", "user@host", "--dry-run"],
        )
        # Act
        # Assert
        # Assert
        assert "DRY RUN" in result.output

    def test_tunnel_setup_dry_run_n_8080_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(
            main,
            ["tunnel", "setup", "-p", "8080", "-b", "user@host", "--dry-run"],
        )
        # Act
        # Assert
        # Assert
        assert "8080" in result.output


    def test_tunnel_remove_dry_run_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["tunnel", "remove", "-p", "8080", "--dry-run"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_tunnel_remove_dry_run_dry_run_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["tunnel", "remove", "-p", "8080", "--dry-run"])
        # Act
        # Assert
        # Assert
        assert "DRY RUN" in result.output


    @patch("scitex_ssh.setup")
    def test_tunnel_setup_success_result_exit_code_equals_n_0(self, mock_setup):
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
            ["tunnel", "setup", "-p", "2222", "-b", "user@host", "-s", "/dev/null"],
        )
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    @patch("scitex_ssh.setup")
    def test_tunnel_setup_success_successfully_in_result_output(self, mock_setup):
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
            ["tunnel", "setup", "-p", "2222", "-b", "user@host", "-s", "/dev/null"],
        )
        # Act
        # Assert
        # Assert
        assert "successfully" in result.output


    @patch("scitex_ssh.setup")
    def test_tunnel_setup_failure_exits_nonzero(self, mock_setup):
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
            ["tunnel", "setup", "-p", "2222", "-b", "user@host", "-s", "/dev/null"],
        )
        # Assert
        # Assert
        assert result.exit_code != 0

    @patch("scitex_ssh.setup")
    def test_tunnel_setup_policy_error_exits_two_result_exit_code_equals_n_2(self, mock_setup):
        # Arrange
        # Arrange
        from scitex_ssh._allowlist import PolicyError
        mock_setup.side_effect = PolicyError("not on the allowlist")
        runner = CliRunner()
        # Act
        result = runner.invoke(
            main,
            ["tunnel", "setup", "-p", "2222", "-b", "user@host", "-s", "/dev/null"],
        )
        # Act
        # Assert
        # Assert
        assert result.exit_code == 2

    @patch("scitex_ssh.setup")
    def test_tunnel_setup_policy_error_exits_two_not_on_the_allowlist_in_result_output(self, mock_setup):
        # Arrange
        # Arrange
        from scitex_ssh._allowlist import PolicyError
        mock_setup.side_effect = PolicyError("not on the allowlist")
        runner = CliRunner()
        # Act
        result = runner.invoke(
            main,
            ["tunnel", "setup", "-p", "2222", "-b", "user@host", "-s", "/dev/null"],
        )
        # Act
        # Assert
        # Assert
        assert "not on the allowlist" in result.output


    @patch("scitex_ssh.remove")
    def test_tunnel_remove_success_result_exit_code_equals_n_0(self, mock_remove):
        # Arrange
        # Arrange
        mock_remove.return_value = {
            "success": True,
            "stdout": "removed",
            "stderr": "",
        }
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["tunnel", "remove", "-p", "2222"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    @patch("scitex_ssh.remove")
    def test_tunnel_remove_success_removed_in_result_output_lower(self, mock_remove):
        # Arrange
        # Arrange
        mock_remove.return_value = {
            "success": True,
            "stdout": "removed",
            "stderr": "",
        }
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["tunnel", "remove", "-p", "2222"])
        # Act
        # Assert
        # Assert
        assert "removed" in result.output.lower()


    @patch("scitex_ssh.status")
    def test_tunnel_status_invocation_result_exit_code_equals_n_0(self, mock_status):
        # Arrange
        # Arrange
        mock_status.return_value = {
            "success": True,
            "stdout": "active tunnels",
            "stderr": "",
        }
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["tunnel", "status"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    @patch("scitex_ssh.status")
    def test_tunnel_status_invocation_active_tunnels_in_result_output(self, mock_status):
        # Arrange
        # Arrange
        mock_status.return_value = {
            "success": True,
            "stdout": "active tunnels",
            "stderr": "",
        }
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["tunnel", "status"])
        # Act
        # Assert
        # Assert
        assert "active tunnels" in result.output


    @patch("scitex_ssh.status")
    def test_tunnel_status_json_result_exit_code_equals_n_0(self, mock_status):
        # Arrange
        # Arrange
        import json
        mock_status.return_value = {
            "success": True,
            "stdout": "active",
            "stderr": "",
        }
        runner = CliRunner()
        # Use canonical `check-status` rather than deprecated `status` —
        # the deprecated alias writes a deprecation warning to stderr
        # which CliRunner merges into result.output, breaking json.loads.
        # Act
        result = runner.invoke(main, ["tunnel", "check-status", "-p", "8080", "--json"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    @patch("scitex_ssh.status")
    def test_tunnel_status_json_payload_port_8080_result_exit_code_equals_n_0(self, mock_status):
        # Arrange
        # Arrange
        import json
        mock_status.return_value = {
            "success": True,
            "stdout": "active",
            "stderr": "",
        }
        runner = CliRunner()
        # Use canonical `check-status` rather than deprecated `status` —
        # the deprecated alias writes a deprecation warning to stderr
        # which CliRunner merges into result.output, breaking json.loads.
        # Act
        result = runner.invoke(main, ["tunnel", "check-status", "-p", "8080", "--json"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    @patch("scitex_ssh.status")
    def test_tunnel_status_json_payload_port_8080_payload_port_8080(self, mock_status):
        # Arrange
        # Arrange
        import json
        mock_status.return_value = {
            "success": True,
            "stdout": "active",
            "stderr": "",
        }
        runner = CliRunner()
        # Use canonical `check-status` rather than deprecated `status` —
        # the deprecated alias writes a deprecation warning to stderr
        # which CliRunner merges into result.output, breaking json.loads.
        # Act
        result = runner.invoke(main, ["tunnel", "check-status", "-p", "8080", "--json"])
        # Assert
        assert result.exit_code == 0
        payload = json.loads(result.output)
        # Act
        # Assert
        assert payload["port"] == 8080


    @patch("scitex_ssh.status")
    def test_tunnel_status_json_payload_stdout_active_result_exit_code_equals_n_0(self, mock_status):
        # Arrange
        # Arrange
        import json
        mock_status.return_value = {
            "success": True,
            "stdout": "active",
            "stderr": "",
        }
        runner = CliRunner()
        # Use canonical `check-status` rather than deprecated `status` —
        # the deprecated alias writes a deprecation warning to stderr
        # which CliRunner merges into result.output, breaking json.loads.
        # Act
        result = runner.invoke(main, ["tunnel", "check-status", "-p", "8080", "--json"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    @patch("scitex_ssh.status")
    def test_tunnel_status_json_payload_stdout_active_payload_stdout_active(self, mock_status):
        # Arrange
        # Arrange
        import json
        mock_status.return_value = {
            "success": True,
            "stdout": "active",
            "stderr": "",
        }
        runner = CliRunner()
        # Use canonical `check-status` rather than deprecated `status` —
        # the deprecated alias writes a deprecation warning to stderr
        # which CliRunner merges into result.output, breaking json.loads.
        # Act
        result = runner.invoke(main, ["tunnel", "check-status", "-p", "8080", "--json"])
        # Assert
        assert result.exit_code == 0
        payload = json.loads(result.output)
        # Act
        # Assert
        assert payload["stdout"] == "active"




class TestDeprecatedAliases:
    """Hidden top-level aliases warn but still delegate correctly."""

    @patch("scitex_ssh.setup")
    def test_setup_tunnel_deprecated_result_exit_code_equals_n_0(self, mock_setup):
        # Arrange
        # Arrange
        mock_setup.return_value = {"success": True, "stdout": "", "stderr": ""}
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
    def test_setup_tunnel_deprecated_deprecated_in_result_output(self, mock_setup):
        # Arrange
        # Arrange
        mock_setup.return_value = {"success": True, "stdout": "", "stderr": ""}
        runner = CliRunner()
        # Act
        result = runner.invoke(
            main,
            ["setup-tunnel", "-p", "2222", "-b", "user@host", "-s", "/dev/null"],
        )
        # Act
        # Assert
        # Assert
        assert "deprecated" in result.output


    @patch("scitex_ssh.remove")
    def test_remove_tunnel_deprecated_result_exit_code_equals_n_0(self, mock_remove):
        # Arrange
        # Arrange
        mock_remove.return_value = {"success": True, "stdout": "", "stderr": ""}
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["remove-tunnel", "-p", "2222"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    @patch("scitex_ssh.remove")
    def test_remove_tunnel_deprecated_deprecated_in_result_output(self, mock_remove):
        # Arrange
        # Arrange
        mock_remove.return_value = {"success": True, "stdout": "", "stderr": ""}
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["remove-tunnel", "-p", "2222"])
        # Act
        # Assert
        # Assert
        assert "deprecated" in result.output


    @patch("scitex_ssh.status")
    def test_show_status_deprecated_result_exit_code_equals_n_0(self, mock_status):
        # Arrange
        # Arrange
        mock_status.return_value = {"success": True, "stdout": "ok", "stderr": ""}
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["show-status"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    @patch("scitex_ssh.status")
    def test_show_status_deprecated_deprecated_in_result_output(self, mock_status):
        # Arrange
        # Arrange
        mock_status.return_value = {"success": True, "stdout": "ok", "stderr": ""}
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["show-status"])
        # Act
        # Assert
        # Assert
        assert "deprecated" in result.output



class TestHelpers:
    """Internal helpers — _get_version, _default_host."""

    def test_get_version_returns_str_v_is_str(self):
        # Arrange
        # Arrange
        # Act
        v = _get_version()
        # Act
        # Assert
        # Assert
        assert isinstance(v, str)

    def test_get_version_returns_str_v(self):
        # Arrange
        # Arrange
        # Act
        v = _get_version()
        # Act
        # Assert
        # Assert
        assert v  # non-empty


    def test_default_host_returns_short_hostname_h_is_str(self):
        # Arrange
        # Arrange
        # Act
        h = _default_host()
        # Act
        # Assert
        # Assert
        assert isinstance(h, str)

    def test_default_host_returns_short_hostname_not_in_h(self):
        # Arrange
        # Arrange
        # Act
        h = _default_host()
        # Act
        # Assert
        # Assert
        assert "." not in h  # short form, dot-stripped



# EOF
