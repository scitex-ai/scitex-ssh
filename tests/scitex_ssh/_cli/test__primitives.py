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
        assert _split_opts(None) == []

    def test_empty_string_returns_empty(self):
        assert _split_opts("") == []

    def test_shell_quoted_split(self):
        assert _split_opts("-A -o StrictHostKeyChecking=no") == [
            "-A",
            "-o",
            "StrictHostKeyChecking=no",
        ]


class TestSplitHostPath:
    def test_remote_host_path(self):
        assert _split_host_path("myhost:/tmp/file") == ("myhost", "/tmp/file")

    def test_absolute_local_path(self):
        assert _split_host_path("/tmp/file") == (None, "/tmp/file")

    def test_relative_local_path(self):
        assert _split_host_path("./file") == (None, "./file")

    def test_bare_local_filename(self):
        # No colon → local.
        assert _split_host_path("file.txt") == (None, "file.txt")

    def test_host_with_slash_treated_as_local(self):
        # A "host" containing `/` is not a real host (fallback safety net).
        assert _split_host_path("foo/bar:baz") == (None, "foo/bar:baz")


class TestExecCmd:
    def test_dry_run(self):
        runner = CliRunner()
        result = runner.invoke(exec_cmd, ["myhost", "uname -a", "--dry-run"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.output
        assert "myhost" in result.output

    @patch("scitex_ssh.exec_remote")
    def test_invokes_exec_remote(self, mock_exec):
        mock_exec.return_value = MagicMock(stdout="ok\n", stderr="", returncode=0)
        runner = CliRunner()
        result = runner.invoke(exec_cmd, ["myhost", "uname -a"])
        assert result.exit_code == 0
        assert "ok" in result.output
        mock_exec.assert_called_once()

    @patch("scitex_ssh.exec_remote")
    def test_propagates_returncode(self, mock_exec):
        mock_exec.return_value = MagicMock(stdout="", stderr="boom\n", returncode=7)
        runner = CliRunner()
        result = runner.invoke(exec_cmd, ["myhost", "false"])
        assert result.exit_code == 7
        assert "boom" in result.output


class TestCopyCmd:
    def test_dry_run(self):
        runner = CliRunner()
        result = runner.invoke(
            copy_cmd, ["local.txt", "myhost:/tmp/local.txt", "--dry-run"]
        )
        assert result.exit_code == 0
        assert "DRY RUN" in result.output

    def test_local_to_local_errors(self):
        runner = CliRunner()
        result = runner.invoke(copy_cmd, ["./a", "./b"])
        assert result.exit_code == 2
        assert "must be HOST:PATH" in result.output

    def test_remote_to_remote_errors(self):
        runner = CliRunner()
        result = runner.invoke(copy_cmd, ["host1:/a", "host2:/b"])
        assert result.exit_code == 2
        assert "remote-to-remote" in result.output

    @patch("scitex_ssh.copy_to")
    def test_copy_to_remote(self, mock_copy_to):
        mock_copy_to.return_value = MagicMock(stdout="", stderr="", returncode=0)
        runner = CliRunner()
        result = runner.invoke(copy_cmd, ["./local.txt", "myhost:/tmp/local.txt"])
        assert result.exit_code == 0
        mock_copy_to.assert_called_once()

    @patch("scitex_ssh.copy_from")
    def test_copy_from_remote(self, mock_copy_from):
        mock_copy_from.return_value = MagicMock(stdout="", stderr="", returncode=0)
        runner = CliRunner()
        result = runner.invoke(copy_cmd, ["myhost:/etc/hostname", "./hostname"])
        assert result.exit_code == 0
        mock_copy_from.assert_called_once()


class TestAttachCmd:
    @patch("scitex_ssh.attach")
    def test_attach_invokes_with_host(self, mock_attach):
        mock_attach.return_value = 0
        runner = CliRunner()
        result = runner.invoke(attach_cmd, ["myhost"])
        assert result.exit_code == 0
        mock_attach.assert_called_once()
        args, _ = mock_attach.call_args
        assert args[0] == "myhost"


# EOF
