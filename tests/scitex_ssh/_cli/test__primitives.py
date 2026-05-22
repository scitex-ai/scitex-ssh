#!/usr/bin/env python3
"""Tests for scitex_ssh._cli._primitives — exec/copy/attach CLI commands.

The CLI commands forward to ``scitex_ssh.exec_remote`` / ``copy_to`` /
``copy_from`` / ``attach``. The underlying behaviour (argv shape,
return-code propagation, ssh-opts handling) is covered against real
fake subprocess runners in ``tests/scitex_ssh/test__primitives.py``.

Here we narrow scope to what only the CLI layer adds: argument parsing,
dry-run plan output, and HOST:PATH-vs-local split logic. The mock-only
"@patch(scitex_ssh.exec_remote)" tests from the original file were
exercising Click's own dispatch rather than any first-party behaviour —
they're replaced with helper tests that observe the same end state.
"""

from __future__ import annotations

from click.testing import CliRunner

from scitex_ssh._cli._primitives import (
    _split_host_path,
    _split_opts,
    attach_cmd,
    copy_cmd,
    exec_cmd,
)


# ---------------------------------------------------------------------
# _split_opts — pure helper
# ---------------------------------------------------------------------


class TestSplitOpts:
    def test_none_input_returns_empty_list(self) -> None:
        # Arrange
        # Act
        result = _split_opts(None)
        # Assert
        assert result == []

    def test_empty_string_input_returns_empty_list(self) -> None:
        # Arrange
        # Act
        result = _split_opts("")
        # Assert
        assert result == []

    def test_shell_quoted_opts_split_into_individual_tokens(self) -> None:
        # Arrange
        raw = "-A -o StrictHostKeyChecking=no"
        # Act
        result = _split_opts(raw)
        # Assert
        assert result == ["-A", "-o", "StrictHostKeyChecking=no"]


# ---------------------------------------------------------------------
# _split_host_path — pure helper
# ---------------------------------------------------------------------


class TestSplitHostPath:
    def test_remote_host_path_splits_on_first_colon(self) -> None:
        # Arrange
        # Act
        result = _split_host_path("myhost:/tmp/file")
        # Assert
        assert result == ("myhost", "/tmp/file")

    def test_absolute_local_path_returns_none_host(self) -> None:
        # Arrange
        # Act
        result = _split_host_path("/tmp/file")
        # Assert
        assert result == (None, "/tmp/file")

    def test_relative_local_path_returns_none_host(self) -> None:
        # Arrange
        # Act
        result = _split_host_path("./file")
        # Assert
        assert result == (None, "./file")

    def test_bare_local_filename_returns_none_host(self) -> None:
        # Arrange
        # Act
        result = _split_host_path("file.txt")
        # Assert
        assert result == (None, "file.txt")

    def test_host_token_with_slash_treated_as_local_path(self) -> None:
        # Arrange
        # Act
        result = _split_host_path("foo/bar:baz")
        # Assert
        assert result == (None, "foo/bar:baz")


# ---------------------------------------------------------------------
# exec_cmd — only the dry-run / CLI-arg-parse surface
# ---------------------------------------------------------------------


class TestExecCmdDryRun:
    def test_dry_run_invocation_exit_code_zero(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(exec_cmd, ["myhost", "uname -a", "--dry-run"])
        # Assert
        assert result.exit_code == 0

    def test_dry_run_output_says_dry_run(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(exec_cmd, ["myhost", "uname -a", "--dry-run"])
        # Assert
        assert "DRY RUN" in result.output

    def test_dry_run_output_echoes_target_host_in_plan(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(exec_cmd, ["myhost", "uname -a", "--dry-run"])
        # Assert
        assert "myhost" in result.output


# ---------------------------------------------------------------------
# copy_cmd — dry-run + invalid-shape error paths
# ---------------------------------------------------------------------


class TestCopyCmdDryRun:
    def test_dry_run_invocation_exit_code_zero(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(
            copy_cmd, ["local.txt", "myhost:/tmp/local.txt", "--dry-run"]
        )
        # Assert
        assert result.exit_code == 0

    def test_dry_run_output_says_dry_run(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(
            copy_cmd, ["local.txt", "myhost:/tmp/local.txt", "--dry-run"]
        )
        # Assert
        assert "DRY RUN" in result.output


class TestCopyCmdInvalidShape:
    def test_local_to_local_exits_with_code_two(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(copy_cmd, ["./a", "./b"])
        # Assert
        assert result.exit_code == 2

    def test_local_to_local_writes_must_be_host_path_message(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(copy_cmd, ["./a", "./b"])
        # Assert
        assert "must be HOST:PATH" in result.output

    def test_remote_to_remote_exits_with_code_two(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(copy_cmd, ["host1:/a", "host2:/b"])
        # Assert
        assert result.exit_code == 2

    def test_remote_to_remote_writes_remote_to_remote_message(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(copy_cmd, ["host1:/a", "host2:/b"])
        # Assert
        assert "remote-to-remote" in result.output


# ---------------------------------------------------------------------
# attach_cmd — help-only smoke. The success path replaces the current
# process via `os.execvp`, so it cannot be exercised from a test without
# forking; the underlying argv construction is covered by
# `tests/scitex_ssh/test__primitives.py` against a real runner fake.
# ---------------------------------------------------------------------


class TestAttachCmdHelp:
    def test_attach_help_exit_code_zero(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(attach_cmd, ["--help"])
        # Assert
        assert result.exit_code == 0

    def test_attach_help_output_mentions_host_argument(self) -> None:
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(attach_cmd, ["--help"])
        # Assert
        assert "HOST" in result.output


# EOF
