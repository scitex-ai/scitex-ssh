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
        assert isinstance(main, CategorizedGroup)

    def test_help_lists_categories(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        # Categorized output groups commands by section header.
        assert "SSH Primitives" in result.output
        assert "Tunnel Management" in result.output
        assert "Integration" in result.output

    def test_version_flag(self):
        runner = CliRunner()
        result = runner.invoke(main, ["-V"])
        assert result.exit_code == 0
        assert "scitex-ssh" in result.output

    def test_help_recursive_flag(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--help-recursive"])
        assert result.exit_code == 0
        # All major leaf commands should appear at least once.
        for token in ["exec", "copy", "attach", "tunnel", "mcp"]:
            assert token in result.output

    def test_no_subcommand_prints_help(self):
        runner = CliRunner()
        result = runner.invoke(main, [])
        assert result.exit_code == 0
        assert "Usage" in result.output


class TestTunnelSubgroup:
    """`scitex-ssh tunnel {setup,remove,status}` — including --dry-run."""

    def test_tunnel_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["tunnel", "--help"])
        assert result.exit_code == 0
        for sub in ("setup", "remove", "status"):
            assert sub in result.output

    def test_tunnel_setup_dry_run(self):
        runner = CliRunner()
        result = runner.invoke(
            main,
            ["tunnel", "setup", "-p", "8080", "-b", "user@host", "--dry-run"],
        )
        assert result.exit_code == 0
        assert "DRY RUN" in result.output
        assert "8080" in result.output

    def test_tunnel_remove_dry_run(self):
        runner = CliRunner()
        result = runner.invoke(main, ["tunnel", "remove", "-p", "8080", "--dry-run"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.output

    @patch("scitex_ssh.setup")
    def test_tunnel_setup_success(self, mock_setup):
        mock_setup.return_value = {
            "success": True,
            "stdout": "service started",
            "stderr": "",
        }
        runner = CliRunner()
        result = runner.invoke(
            main,
            ["tunnel", "setup", "-p", "2222", "-b", "user@host", "-s", "/dev/null"],
        )
        assert result.exit_code == 0
        assert "successfully" in result.output

    @patch("scitex_ssh.setup")
    def test_tunnel_setup_failure_exits_nonzero(self, mock_setup):
        mock_setup.return_value = {
            "success": False,
            "stdout": "",
            "stderr": "permission denied",
        }
        runner = CliRunner()
        result = runner.invoke(
            main,
            ["tunnel", "setup", "-p", "2222", "-b", "user@host", "-s", "/dev/null"],
        )
        assert result.exit_code != 0

    @patch("scitex_ssh.setup")
    def test_tunnel_setup_policy_error_exits_two(self, mock_setup):
        from scitex_ssh._allowlist import PolicyError

        mock_setup.side_effect = PolicyError("not on the allowlist")
        runner = CliRunner()
        result = runner.invoke(
            main,
            ["tunnel", "setup", "-p", "2222", "-b", "user@host", "-s", "/dev/null"],
        )
        assert result.exit_code == 2
        assert "not on the allowlist" in result.output

    @patch("scitex_ssh.remove")
    def test_tunnel_remove_success(self, mock_remove):
        mock_remove.return_value = {
            "success": True,
            "stdout": "removed",
            "stderr": "",
        }
        runner = CliRunner()
        result = runner.invoke(main, ["tunnel", "remove", "-p", "2222"])
        assert result.exit_code == 0
        assert "removed" in result.output.lower()

    @patch("scitex_ssh.status")
    def test_tunnel_status_invocation(self, mock_status):
        mock_status.return_value = {
            "success": True,
            "stdout": "active tunnels",
            "stderr": "",
        }
        runner = CliRunner()
        result = runner.invoke(main, ["tunnel", "status"])
        assert result.exit_code == 0
        assert "active tunnels" in result.output

    @patch("scitex_ssh.status")
    def test_tunnel_status_json(self, mock_status):
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
        result = runner.invoke(main, ["tunnel", "check-status", "-p", "8080", "--json"])
        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["port"] == 8080
        assert payload["stdout"] == "active"


class TestDeprecatedAliases:
    """Hidden top-level aliases warn but still delegate correctly."""

    @patch("scitex_ssh.setup")
    def test_setup_tunnel_deprecated(self, mock_setup):
        mock_setup.return_value = {"success": True, "stdout": "", "stderr": ""}
        runner = CliRunner()
        result = runner.invoke(
            main,
            ["setup-tunnel", "-p", "2222", "-b", "user@host", "-s", "/dev/null"],
        )
        assert result.exit_code == 0
        assert "deprecated" in result.output

    @patch("scitex_ssh.remove")
    def test_remove_tunnel_deprecated(self, mock_remove):
        mock_remove.return_value = {"success": True, "stdout": "", "stderr": ""}
        runner = CliRunner()
        result = runner.invoke(main, ["remove-tunnel", "-p", "2222"])
        assert result.exit_code == 0
        assert "deprecated" in result.output

    @patch("scitex_ssh.status")
    def test_show_status_deprecated(self, mock_status):
        mock_status.return_value = {"success": True, "stdout": "ok", "stderr": ""}
        runner = CliRunner()
        result = runner.invoke(main, ["show-status"])
        assert result.exit_code == 0
        assert "deprecated" in result.output


class TestHelpers:
    """Internal helpers — _get_version, _default_host."""

    def test_get_version_returns_str(self):
        v = _get_version()
        assert isinstance(v, str)
        assert v  # non-empty

    def test_default_host_returns_short_hostname(self):
        h = _default_host()
        assert isinstance(h, str)
        assert "." not in h  # short form, dot-stripped


# EOF
