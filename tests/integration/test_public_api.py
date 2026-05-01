#!/usr/bin/env python3
"""Integration tests for scitex_ssh public API surface.

Exercises the top-level functions exposed from scitex_ssh/__init__.py
(setup/remove/status/version) end-to-end, with subprocess and allowlist
mocked. Lives in tests/integration/ (not tests/scitex_ssh/) because the
package's public API is defined in __init__.py and there is no module
basename to mirror — this is the canonical home for cross-module surface
tests per scitex-dev audit-project §3 / PS302.
"""

import os
import subprocess
from unittest.mock import patch

import pytest

import scitex_ssh


@pytest.fixture(autouse=True)
def _bypass_allowlist(monkeypatch):
    """Allow tunnel ops in tests regardless of host config."""
    from scitex_ssh import _allowlist

    monkeypatch.setattr(_allowlist, "is_allowed", lambda host, feature: True)


class TestVersion:
    """Version and availability tests."""

    def test_version_exists(self):
        assert hasattr(scitex_ssh, "__version__")
        assert isinstance(scitex_ssh.__version__, str)

    def test_version_format(self):
        parts = scitex_ssh.__version__.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)

    def test_get_version(self):
        assert scitex_ssh.get_version() == scitex_ssh.__version__

    def test_available(self):
        assert scitex_ssh.AVAILABLE is True


class TestScriptsDir:
    """Script directory tests."""

    def test_scripts_dir_exists(self):
        assert os.path.isdir(scitex_ssh._SCRIPTS_DIR)

    def test_setup_script_exists(self):
        path = os.path.join(scitex_ssh._SCRIPTS_DIR, "setup-autossh-service.sh")
        assert os.path.isfile(path)

    def test_remove_script_exists(self):
        path = os.path.join(scitex_ssh._SCRIPTS_DIR, "remove-autossh-service.sh")
        assert os.path.isfile(path)


class TestSetup:
    """Tests for setup() function."""

    @patch("scitex_ssh.subprocess.run")
    def test_setup_calls_script(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="OK", stderr=""
        )
        result = scitex_ssh.setup(2222, "user@bastion", "/home/user/.ssh/id_rsa")
        assert result["success"] is True
        assert result["stdout"] == "OK"
        assert result["stderr"] == ""

    @patch("scitex_ssh.subprocess.run")
    def test_setup_passes_args(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        scitex_ssh.setup(5098, "admin@relay.example.com", "/tmp/key")
        args = mock_run.call_args[0][0]
        assert "-p" in args
        assert "5098" in args
        assert "-b" in args
        assert "admin@relay.example.com" in args
        assert "-s" in args
        assert "/tmp/key" in args

    @patch("scitex_ssh.subprocess.run")
    def test_setup_failure(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=1, stdout="", stderr="Permission denied"
        )
        result = scitex_ssh.setup(2222, "user@bastion", "/tmp/key")
        assert result["success"] is False
        assert result["stderr"] == "Permission denied"

    @patch("scitex_ssh.subprocess.run")
    @patch.dict(
        os.environ,
        {
            "SCITEX_SSH_BASTION_SERVER": "env@bastion",
            "SCITEX_SSH_SECRET_KEY_PATH": "/env/key",
        },
    )
    def test_setup_uses_env_vars(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="OK", stderr=""
        )
        result = scitex_ssh.setup(2222)
        assert result["success"] is True
        args = mock_run.call_args[0][0]
        assert "env@bastion" in args
        assert "/env/key" in args

    @patch.dict(os.environ, {}, clear=True)
    def test_setup_raises_without_bastion(self):
        import pytest

        with pytest.raises(ValueError, match="bastion_server is required"):
            scitex_ssh.setup(2222)

    @patch.dict(
        os.environ,
        {"SCITEX_SSH_BASTION_SERVER": "env@bastion"},
        clear=True,
    )
    def test_setup_raises_without_secret_key(self):
        import pytest

        with pytest.raises(ValueError, match="secret_key_path is required"):
            scitex_ssh.setup(2222)


class TestRemove:
    """Tests for remove() function."""

    @patch("scitex_ssh.subprocess.run")
    def test_remove_success(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="Removed", stderr=""
        )
        result = scitex_ssh.remove(2222)
        assert result["success"] is True

    @patch("scitex_ssh.subprocess.run")
    def test_remove_passes_port(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        scitex_ssh.remove(5098)
        args = mock_run.call_args[0][0]
        assert "-p" in args
        assert "5098" in args


class TestStatus:
    """Tests for status() function."""

    @patch("scitex_ssh.subprocess.run")
    def test_status_all(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="active", stderr=""
        )
        result = scitex_ssh.status()
        assert result["success"] is True
        args = mock_run.call_args[0][0]
        assert "list-units" in args

    @patch("scitex_ssh.subprocess.run")
    def test_status_specific_port(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="active", stderr=""
        )
        result = scitex_ssh.status(port=2222)
        assert result["success"] is True
        args = mock_run.call_args[0][0]
        assert "autossh-tunnel-2222.service" in args


# EOF
