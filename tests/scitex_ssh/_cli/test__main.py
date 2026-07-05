#!/usr/bin/env python3
"""Tests for scitex_ssh._cli._main — top-level Click group, tunnel subgroup,
deprecation aliases.

No mocks. Tunnel setup/remove/status run the real production functions
against a fake `bash`/`systemctl` on $PATH (subprocess_shim) plus a real
allowlist config (allow_tunnels). PolicyError is exercised with a real
deny config rather than a forced side effect.
"""

from __future__ import annotations

import json

from click.testing import CliRunner

from scitex_ssh._cli._main import (
    CategorizedGroup,
    _default_host,
    _get_version,
    main,
)


class TestRootGroup:
    """Root `main` group: --version / --help-recursive / no-arg behavior."""

    def test_main_is_a_categorized_group(self):
        # Arrange
        # Act
        # Assert
        assert isinstance(main, CategorizedGroup)

    def test_help_exits_zero(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["--help"])
        # Assert
        assert result.exit_code == 0

    def test_help_lists_ssh_primitives_category(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["--help"])
        # Assert
        assert "SSH Primitives" in result.output

    def test_help_lists_tunnel_management_category(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["--help"])
        # Assert
        assert "Tunnel Management" in result.output

    def test_help_lists_integration_category(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["--help"])
        # Assert
        assert "Integration" in result.output

    def test_version_flag_exits_zero(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["-V"])
        # Assert
        assert result.exit_code == 0

    def test_version_flag_prints_package_name(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["-V"])
        # Assert
        assert "scitex-ssh" in result.output

    def test_help_recursive_flag_exits_zero(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["--help-recursive"])
        # Assert
        assert result.exit_code == 0

    def test_help_recursive_lists_every_top_level_command(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["--help-recursive"])
        # Assert
        assert all(
            token in result.output
            for token in ["exec", "copy", "attach", "tunnel", "mcp"]
        )

    def test_no_subcommand_exits_zero(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, [])
        # Assert
        assert result.exit_code == 0

    def test_no_subcommand_prints_usage(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, [])
        # Assert
        assert "Usage" in result.output


class TestTunnelSubgroup:
    """`scitex-ssh tunnel {setup,remove,status}` — including --dry-run."""

    def test_tunnel_help_exits_zero(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["tunnel", "--help"])
        # Assert
        assert result.exit_code == 0

    def test_tunnel_help_lists_subcommands(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["tunnel", "--help"])
        # Assert
        assert all(sub in result.output for sub in ("setup", "remove", "status"))

    def test_tunnel_setup_dry_run_exits_zero(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(
            main, ["tunnel", "setup", "-p", "8080", "-b", "user@host", "--dry-run"]
        )
        # Assert
        assert result.exit_code == 0

    def test_tunnel_setup_dry_run_announces_dry_run(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(
            main, ["tunnel", "setup", "-p", "8080", "-b", "user@host", "--dry-run"]
        )
        # Assert
        assert "DRY RUN" in result.output

    def test_tunnel_setup_dry_run_mentions_port(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(
            main, ["tunnel", "setup", "-p", "8080", "-b", "user@host", "--dry-run"]
        )
        # Assert
        assert "8080" in result.output

    def test_tunnel_remove_dry_run_exits_zero(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["tunnel", "remove", "-p", "8080", "--dry-run"])
        # Assert
        assert result.exit_code == 0

    def test_tunnel_remove_dry_run_announces_dry_run(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["tunnel", "remove", "-p", "8080", "--dry-run"])
        # Assert
        assert "DRY RUN" in result.output

    def test_tunnel_setup_success_exits_zero(self, subprocess_shim, allow_tunnels):
        # Arrange
        subprocess_shim.install("bash", rc=0, stdout="service started")
        runner = CliRunner()
        # Act
        result = runner.invoke(
            main,
            ["tunnel", "setup", "-p", "2222", "-b", "user@host", "-s", "/dev/null"],
        )
        # Assert
        assert result.exit_code == 0

    def test_tunnel_setup_success_reports_success(self, subprocess_shim, allow_tunnels):
        # Arrange
        subprocess_shim.install("bash", rc=0, stdout="service started")
        runner = CliRunner()
        # Act
        result = runner.invoke(
            main,
            ["tunnel", "setup", "-p", "2222", "-b", "user@host", "-s", "/dev/null"],
        )
        # Assert
        assert "successfully" in result.output

    def test_tunnel_setup_nonzero_script_exit_fails(
        self, subprocess_shim, allow_tunnels
    ):
        # Arrange
        subprocess_shim.install("bash", rc=1, stderr="permission denied")
        runner = CliRunner()
        # Act
        result = runner.invoke(
            main,
            ["tunnel", "setup", "-p", "2222", "-b", "user@host", "-s", "/dev/null"],
        )
        # Assert
        assert result.exit_code != 0

    def test_tunnel_setup_denied_host_exits_two(self, deny_tunnels):
        # Arrange — real allowlist config that denies tunnels for every host
        runner = CliRunner()
        # Act
        result = runner.invoke(
            main,
            ["tunnel", "setup", "-p", "2222", "-b", "user@host", "-s", "/dev/null"],
        )
        # Assert — PolicyError → exit 2
        assert result.exit_code == 2

    def test_tunnel_setup_denied_host_reports_policy_error(self, deny_tunnels):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(
            main,
            ["tunnel", "setup", "-p", "2222", "-b", "user@host", "-s", "/dev/null"],
        )
        # Assert
        assert "not allowed" in result.output

    def test_tunnel_remove_success_exits_zero(self, subprocess_shim, allow_tunnels):
        # Arrange
        subprocess_shim.install("bash", rc=0, stdout="removed")
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["tunnel", "remove", "-p", "2222"])
        # Assert
        assert result.exit_code == 0

    def test_tunnel_remove_success_reports_removed(
        self, subprocess_shim, allow_tunnels
    ):
        # Arrange
        subprocess_shim.install("bash", rc=0, stdout="removed")
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["tunnel", "remove", "-p", "2222"])
        # Assert
        assert "removed" in result.output.lower()

    def test_tunnel_status_exits_zero(self, subprocess_shim):
        # Arrange — status is not allowlist-gated
        subprocess_shim.install("systemctl", rc=0, stdout="active tunnels")
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["tunnel", "check-status"])
        # Assert
        assert result.exit_code == 0

    def test_tunnel_status_streams_systemctl_stdout(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("systemctl", rc=0, stdout="active tunnels")
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["tunnel", "check-status"])
        # Assert
        assert "active tunnels" in result.output

    def test_tunnel_status_json_exits_zero(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("systemctl", rc=0, stdout="active")
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["tunnel", "check-status", "-p", "8080", "--json"])
        # Assert
        assert result.exit_code == 0

    def test_tunnel_status_json_payload_carries_port(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("systemctl", rc=0, stdout="active")
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["tunnel", "check-status", "-p", "8080", "--json"])
        # Assert
        assert json.loads(result.output)["port"] == 8080

    def test_tunnel_status_json_payload_carries_stdout(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("systemctl", rc=0, stdout="active")
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["tunnel", "check-status", "-p", "8080", "--json"])
        # Assert
        assert json.loads(result.output)["stdout"] == "active"


class TestDeprecatedAliases:
    """Hidden top-level aliases warn but still delegate correctly."""

    def test_setup_tunnel_deprecated_exits_zero(self, subprocess_shim, allow_tunnels):
        # Arrange
        subprocess_shim.install("bash", rc=0, stdout="")
        runner = CliRunner()
        # Act
        result = runner.invoke(
            main,
            ["setup-tunnel", "-p", "2222", "-b", "user@host", "-s", "/dev/null"],
        )
        # Assert
        assert result.exit_code == 0

    def test_setup_tunnel_deprecated_warns_deprecated(
        self, subprocess_shim, allow_tunnels
    ):
        # Arrange
        subprocess_shim.install("bash", rc=0, stdout="")
        runner = CliRunner()
        # Act
        result = runner.invoke(
            main,
            ["setup-tunnel", "-p", "2222", "-b", "user@host", "-s", "/dev/null"],
        )
        # Assert
        assert "deprecated" in result.output

    def test_remove_tunnel_deprecated_exits_zero(self, subprocess_shim, allow_tunnels):
        # Arrange
        subprocess_shim.install("bash", rc=0, stdout="")
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["remove-tunnel", "-p", "2222"])
        # Assert
        assert result.exit_code == 0

    def test_remove_tunnel_deprecated_warns_deprecated(
        self, subprocess_shim, allow_tunnels
    ):
        # Arrange
        subprocess_shim.install("bash", rc=0, stdout="")
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["remove-tunnel", "-p", "2222"])
        # Assert
        assert "deprecated" in result.output

    def test_show_status_deprecated_exits_zero(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("systemctl", rc=0, stdout="ok")
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["show-status"])
        # Assert
        assert result.exit_code == 0

    def test_show_status_deprecated_warns_deprecated(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("systemctl", rc=0, stdout="ok")
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["show-status"])
        # Assert
        assert "deprecated" in result.output


class TestHelpers:
    """Internal helpers — _get_version, _default_host."""

    def test_get_version_returns_a_string(self):
        # Arrange
        # Act
        version = _get_version()
        # Assert
        assert isinstance(version, str)

    def test_get_version_returns_a_nonempty_string(self):
        # Arrange
        # Act
        version = _get_version()
        # Assert
        assert version

    def test_default_host_returns_a_string(self):
        # Arrange
        # Act
        host = _default_host()
        # Assert
        assert isinstance(host, str)

    def test_default_host_strips_domain_to_short_form(self):
        # Arrange
        # Act
        host = _default_host()
        # Assert
        assert "." not in host


class TestTunnelRenderArgv:
    """`tunnel render-argv`: pure JSON-spec -> ssh command rendering."""

    _QWEN = (
        '{"direction":"forward",'
        '"listen":{"host":"127.0.0.1","port":4000},'
        '"target":{"host":"spartan-gpu-a017","port":4000},'
        '"via":"spartan"}'
    )

    def test_renders_shell_string_by_default(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(main, ["tunnel", "render-argv", "--profile", self._QWEN])
        # Assert
        assert result.exit_code == 0
        out = result.output.strip()
        assert out.startswith("ssh -N ")
        assert "-L 127.0.0.1:4000:spartan-gpu-a017:4000" in out
        assert out.endswith(" spartan")

    def test_as_json_emits_argv_array(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(
            main, ["tunnel", "render-argv", "--profile", self._QWEN, "--as-json"]
        )
        # Assert
        assert result.exit_code == 0
        argv = json.loads(result.output)
        assert argv[0] == "ssh"
        assert argv[-1] == "spartan"
        assert "-L" in argv

    def test_reads_profile_from_stdin(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(
            main, ["tunnel", "render-argv", "--profile", "-"], input=self._QWEN
        )
        # Assert
        assert result.exit_code == 0
        assert "spartan-gpu-a017" in result.output

    def test_invalid_json_exits_2(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(
            main, ["tunnel", "render-argv", "--profile", "{not json"]
        )
        # Assert
        assert result.exit_code == 2
        assert "not valid JSON" in result.output

    def test_missing_required_key_exits_2(self):
        # Arrange
        runner = CliRunner()
        bad = '{"direction":"forward","listen":{"port":4000},"via":"spartan"}'
        # Act
        result = runner.invoke(main, ["tunnel", "render-argv", "--profile", bad])
        # Assert
        assert result.exit_code == 2
        assert "invalid tunnel profile" in result.output


# EOF
