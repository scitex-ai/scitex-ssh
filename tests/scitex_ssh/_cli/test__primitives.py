#!/usr/bin/env python3
"""Tests for scitex_ssh._cli._primitives — exec/copy/attach CLI commands."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from scitex_ssh._cli._primitives import (
    _split_host_path,
    _split_opts,
    attach_cmd,
    copy_cmd,
    exec_cmd,
)


class TestSplitOpts:
    def test_none_returns_empty(self):
        # Arrange
        # Act
        # Assert
        # Arrange
        # Act
        # Assert
        assert _split_opts(None) == []

    def test_empty_string_returns_empty(self):
        # Arrange
        # Act
        # Assert
        # Arrange
        # Act
        # Assert
        assert _split_opts("") == []

    def test_shell_quoted_split(self):
        # Arrange
        # Act
        # Assert
        # Arrange
        # Act
        # Assert
        assert _split_opts("-A -o StrictHostKeyChecking=no") == [
            "-A",
            "-o",
            "StrictHostKeyChecking=no",
        ]


class TestSplitHostPath:
    def test_remote_host_path(self):
        # Arrange
        # Act
        # Assert
        # Arrange
        # Act
        # Assert
        assert _split_host_path("myhost:/tmp/file") == ("myhost", "/tmp/file")

    def test_absolute_local_path(self):
        # Arrange
        # Act
        # Assert
        # Arrange
        # Act
        # Assert
        assert _split_host_path("/tmp/file") == (None, "/tmp/file")

    def test_relative_local_path(self):
        # Arrange
        # Act
        # Assert
        # Arrange
        # Act
        # Assert
        assert _split_host_path("./file") == (None, "./file")

    def test_bare_local_filename(self):
        # No colon → local.
        # Arrange
        # Act
        # Assert
        # Arrange
        # Act
        # Assert
        assert _split_host_path("file.txt") == (None, "file.txt")

    def test_host_with_slash_treated_as_local(self):
        # A "host" containing `/` is not a real host (fallback safety net).
        # Arrange
        # Act
        # Assert
        # Arrange
        # Act
        # Assert
        assert _split_host_path("foo/bar:baz") == (None, "foo/bar:baz")


class TestExecCmd:
    def test_dry_run_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(exec_cmd, ["myhost", "uname -a", "--dry-run"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_dry_run_dry_run_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(exec_cmd, ["myhost", "uname -a", "--dry-run"])
        # Act
        # Assert
        # Assert
        assert "DRY RUN" in result.output

    def test_dry_run_myhost_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(exec_cmd, ["myhost", "uname -a", "--dry-run"])
        # Act
        # Assert
        # Assert
        assert "myhost" in result.output


    @patch("scitex_ssh.exec_remote")
    def test_invokes_exec_remote_result_exit_code_equals_n_0(self, mock_exec):
        # Arrange
        # Arrange
        mock_exec.return_value = MagicMock(stdout="ok\n", stderr="", returncode=0)
        runner = CliRunner()
        # Act
        result = runner.invoke(exec_cmd, ["myhost", "uname -a"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    @patch("scitex_ssh.exec_remote")
    def test_invokes_exec_remote_ok_in_result_output(self, mock_exec):
        # Arrange
        # Arrange
        mock_exec.return_value = MagicMock(stdout="ok\n", stderr="", returncode=0)
        runner = CliRunner()
        # Act
        result = runner.invoke(exec_cmd, ["myhost", "uname -a"])
        # Act
        # Assert
        # Assert
        assert "ok" in result.output


    @patch("scitex_ssh.exec_remote")
    def test_propagates_returncode_result_exit_code_equals_n_7(self, mock_exec):
        # Arrange
        # Arrange
        mock_exec.return_value = MagicMock(stdout="", stderr="boom\n", returncode=7)
        runner = CliRunner()
        # Act
        result = runner.invoke(exec_cmd, ["myhost", "false"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 7

    @patch("scitex_ssh.exec_remote")
    def test_propagates_returncode_boom_in_result_output(self, mock_exec):
        # Arrange
        # Arrange
        mock_exec.return_value = MagicMock(stdout="", stderr="boom\n", returncode=7)
        runner = CliRunner()
        # Act
        result = runner.invoke(exec_cmd, ["myhost", "false"])
        # Act
        # Assert
        # Assert
        assert "boom" in result.output



class TestCopyCmd:
    def test_dry_run_result_exit_code_equals_n_0(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(
            copy_cmd, ["local.txt", "myhost:/tmp/local.txt", "--dry-run"]
        )
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    def test_dry_run_dry_run_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(
            copy_cmd, ["local.txt", "myhost:/tmp/local.txt", "--dry-run"]
        )
        # Act
        # Assert
        # Assert
        assert "DRY RUN" in result.output


    def test_local_to_local_errors_result_exit_code_equals_n_2(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(copy_cmd, ["./a", "./b"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 2

    def test_local_to_local_errors_must_be_host_path_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(copy_cmd, ["./a", "./b"])
        # Act
        # Assert
        # Assert
        assert "must be HOST:PATH" in result.output


    def test_remote_to_remote_errors_result_exit_code_equals_n_2(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(copy_cmd, ["host1:/a", "host2:/b"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 2

    def test_remote_to_remote_errors_remote_to_remote_in_result_output(self):
        # Arrange
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(copy_cmd, ["host1:/a", "host2:/b"])
        # Act
        # Assert
        # Assert
        assert "remote-to-remote" in result.output


    @patch("scitex_ssh.copy_to")
    def test_copy_to_remote(self, mock_copy_to):
        # Arrange
        # Arrange
        mock_copy_to.return_value = MagicMock(stdout="", stderr="", returncode=0)
        runner = CliRunner()
        # Act
        # Act
        result = runner.invoke(copy_cmd, ["./local.txt", "myhost:/tmp/local.txt"])
        # Assert
        # Assert
        assert result.exit_code == 0
        mock_copy_to.assert_called_once()

    @patch("scitex_ssh.copy_from")
    def test_copy_from_remote(self, mock_copy_from):
        # Arrange
        # Arrange
        mock_copy_from.return_value = MagicMock(stdout="", stderr="", returncode=0)
        runner = CliRunner()
        # Act
        # Act
        result = runner.invoke(copy_cmd, ["myhost:/etc/hostname", "./hostname"])
        # Assert
        # Assert
        assert result.exit_code == 0
        mock_copy_from.assert_called_once()


class TestAttachCmd:
    @patch("scitex_ssh.attach")
    def test_attach_invokes_with_host_result_exit_code_equals_n_0(self, mock_attach):
        # Arrange
        # Arrange
        mock_attach.return_value = 0
        runner = CliRunner()
        # Act
        result = runner.invoke(attach_cmd, ["myhost"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    @patch("scitex_ssh.attach")
    def test_attach_invokes_with_host_args_0_myhost_result_exit_code_equals_n_0(self, mock_attach):
        # Arrange
        # Arrange
        mock_attach.return_value = 0
        runner = CliRunner()
        # Act
        result = runner.invoke(attach_cmd, ["myhost"])
        # Act
        # Assert
        # Assert
        assert result.exit_code == 0

    @patch("scitex_ssh.attach")
    def test_attach_invokes_with_host_args_0_myhost_args_0_myhost(self, mock_attach):
        # Arrange
        # Arrange
        mock_attach.return_value = 0
        runner = CliRunner()
        # Act
        result = runner.invoke(attach_cmd, ["myhost"])
        # Assert
        assert result.exit_code == 0
        mock_attach.assert_called_once()
        args, _ = mock_attach.call_args
        # Act
        # Assert
        assert args[0] == "myhost"




# EOF
