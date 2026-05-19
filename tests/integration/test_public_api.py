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

    def test_version_exists_hasattr_scitex_ssh_version(self):
        # Arrange
        # Act
        # Assert
        # Arrange
        # Act
        # Assert
        assert hasattr(scitex_ssh, "__version__")

    def test_version_exists_scitex_ssh_version_is_str(self):
        # Arrange
        # Act
        # Assert
        # Arrange
        # Act
        # Assert
        assert isinstance(scitex_ssh.__version__, str)


    def test_version_format_len_parts_is_3(self):
        # Arrange
        # Arrange
        # Act
        parts = scitex_ssh.__version__.split(".")
        # Act
        # Assert
        # Assert
        assert len(parts) == 3

    def test_version_format_all_p_isdigit_for_p_in_parts(self):
        # Arrange
        # Arrange
        # Act
        parts = scitex_ssh.__version__.split(".")
        # Act
        # Assert
        # Assert
        assert all(p.isdigit() for p in parts)


    def test_get_version_scitex_ssh_get_version_scitex_ssh_version(self):
        # Arrange
        # Act
        # Assert
        # Arrange
        # Act
        # Assert
        assert scitex_ssh.get_version() == scitex_ssh.__version__

    def test_available_scitex_ssh_available_is_true(self):
        # Arrange
        # Act
        # Assert
        # Arrange
        # Act
        # Assert
        assert scitex_ssh.AVAILABLE is True


class TestScriptsDir:
    """Script directory tests."""

    def test_scripts_dir_exists(self):
        # Arrange
        # Act
        # Assert
        # Arrange
        # Act
        # Assert
        assert os.path.isdir(scitex_ssh._SCRIPTS_DIR)

    def test_setup_script_exists(self):
        # Arrange
        # Act
        # Arrange
        # Act
        path = os.path.join(scitex_ssh._SCRIPTS_DIR, "setup-autossh-service.sh")
        # Assert
        # Assert
        assert os.path.isfile(path)

    def test_remove_script_exists(self):
        # Arrange
        # Act
        # Arrange
        # Act
        path = os.path.join(scitex_ssh._SCRIPTS_DIR, "remove-autossh-service.sh")
        # Assert
        # Assert
        assert os.path.isfile(path)


class TestSetup:
    """Tests for setup() function."""

    @patch("scitex_ssh.subprocess.run")
    def test_setup_calls_script_result_success_is_true(self, mock_run):
        # Arrange
        # Arrange
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="OK", stderr=""
        )
        # Act
        result = scitex_ssh.setup(2222, "user@bastion", "/home/user/.ssh/id_rsa")
        # Act
        # Assert
        # Assert
        assert result["success"] is True

    @patch("scitex_ssh.subprocess.run")
    def test_setup_calls_script_result_stdout_ok(self, mock_run):
        # Arrange
        # Arrange
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="OK", stderr=""
        )
        # Act
        result = scitex_ssh.setup(2222, "user@bastion", "/home/user/.ssh/id_rsa")
        # Act
        # Assert
        # Assert
        assert result["stdout"] == "OK"

    @patch("scitex_ssh.subprocess.run")
    def test_setup_calls_script_result_stderr(self, mock_run):
        # Arrange
        # Arrange
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="OK", stderr=""
        )
        # Act
        result = scitex_ssh.setup(2222, "user@bastion", "/home/user/.ssh/id_rsa")
        # Act
        # Assert
        # Assert
        assert result["stderr"] == ""


    @patch("scitex_ssh.subprocess.run")
    def test_setup_passes_args_p_in_args(self, mock_run):
        # Arrange
        # Arrange
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        scitex_ssh.setup(5098, "admin@relay.example.com", "/tmp/key")
        # Act
        args = mock_run.call_args[0][0]
        # Act
        # Assert
        # Assert
        assert "-p" in args

    @patch("scitex_ssh.subprocess.run")
    def test_setup_passes_args_n_5098_in_args(self, mock_run):
        # Arrange
        # Arrange
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        scitex_ssh.setup(5098, "admin@relay.example.com", "/tmp/key")
        # Act
        args = mock_run.call_args[0][0]
        # Act
        # Assert
        # Assert
        assert "5098" in args

    @patch("scitex_ssh.subprocess.run")
    def test_setup_passes_args_b_in_args(self, mock_run):
        # Arrange
        # Arrange
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        scitex_ssh.setup(5098, "admin@relay.example.com", "/tmp/key")
        # Act
        args = mock_run.call_args[0][0]
        # Act
        # Assert
        # Assert
        assert "-b" in args

    @patch("scitex_ssh.subprocess.run")
    def test_setup_passes_args_admin_relay_example_com_in_args(self, mock_run):
        # Arrange
        # Arrange
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        scitex_ssh.setup(5098, "admin@relay.example.com", "/tmp/key")
        # Act
        args = mock_run.call_args[0][0]
        # Act
        # Assert
        # Assert
        assert "admin@relay.example.com" in args

    @patch("scitex_ssh.subprocess.run")
    def test_setup_passes_args_s_in_args(self, mock_run):
        # Arrange
        # Arrange
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        scitex_ssh.setup(5098, "admin@relay.example.com", "/tmp/key")
        # Act
        args = mock_run.call_args[0][0]
        # Act
        # Assert
        # Assert
        assert "-s" in args

    @patch("scitex_ssh.subprocess.run")
    def test_setup_passes_args_tmp_key_in_args(self, mock_run):
        # Arrange
        # Arrange
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        scitex_ssh.setup(5098, "admin@relay.example.com", "/tmp/key")
        # Act
        args = mock_run.call_args[0][0]
        # Act
        # Assert
        # Assert
        assert "/tmp/key" in args


    @patch("scitex_ssh.subprocess.run")
    def test_setup_failure_result_success_is_false(self, mock_run):
        # Arrange
        # Arrange
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=1, stdout="", stderr="Permission denied"
        )
        # Act
        result = scitex_ssh.setup(2222, "user@bastion", "/tmp/key")
        # Act
        # Assert
        # Assert
        assert result["success"] is False

    @patch("scitex_ssh.subprocess.run")
    def test_setup_failure_result_stderr_permission_denied(self, mock_run):
        # Arrange
        # Arrange
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=1, stdout="", stderr="Permission denied"
        )
        # Act
        result = scitex_ssh.setup(2222, "user@bastion", "/tmp/key")
        # Act
        # Assert
        # Assert
        assert result["stderr"] == "Permission denied"


    @patch("scitex_ssh.subprocess.run")
    @patch.dict(
        os.environ,
        {
            "SCITEX_SSH_BASTION_SERVER": "env@bastion",
            "SCITEX_SSH_SECRET_KEY_PATH": "/env/key",
        },
    )
    def test_setup_uses_env_vars_result_success_is_true(self, mock_run):
        # Arrange
        # Arrange
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="OK", stderr=""
        )
        # Act
        result = scitex_ssh.setup(2222)
        # Act
        # Assert
        # Assert
        assert result["success"] is True

    @patch("scitex_ssh.subprocess.run")
    @patch.dict(
        os.environ,
        {
            "SCITEX_SSH_BASTION_SERVER": "env@bastion",
            "SCITEX_SSH_SECRET_KEY_PATH": "/env/key",
        },
    )
    def test_setup_uses_env_vars_env_bastion_in_args_result_success_is_true(self, mock_run):
        # Arrange
        # Arrange
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="OK", stderr=""
        )
        # Act
        result = scitex_ssh.setup(2222)
        # Act
        # Assert
        # Assert
        assert result["success"] is True

    @patch("scitex_ssh.subprocess.run")
    @patch.dict(
        os.environ,
        {
            "SCITEX_SSH_BASTION_SERVER": "env@bastion",
            "SCITEX_SSH_SECRET_KEY_PATH": "/env/key",
        },
    )
    def test_setup_uses_env_vars_env_bastion_in_args_env_bastion_in_args(self, mock_run):
        # Arrange
        # Arrange
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="OK", stderr=""
        )
        # Act
        result = scitex_ssh.setup(2222)
        # Assert
        assert result["success"] is True
        args = mock_run.call_args[0][0]
        # Act
        # Assert
        assert "env@bastion" in args


    @patch("scitex_ssh.subprocess.run")
    @patch.dict(
        os.environ,
        {
            "SCITEX_SSH_BASTION_SERVER": "env@bastion",
            "SCITEX_SSH_SECRET_KEY_PATH": "/env/key",
        },
    )
    def test_setup_uses_env_vars_env_key_in_args_result_success_is_true(self, mock_run):
        # Arrange
        # Arrange
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="OK", stderr=""
        )
        # Act
        result = scitex_ssh.setup(2222)
        # Act
        # Assert
        # Assert
        assert result["success"] is True

    @patch("scitex_ssh.subprocess.run")
    @patch.dict(
        os.environ,
        {
            "SCITEX_SSH_BASTION_SERVER": "env@bastion",
            "SCITEX_SSH_SECRET_KEY_PATH": "/env/key",
        },
    )
    def test_setup_uses_env_vars_env_key_in_args_env_key_in_args(self, mock_run):
        # Arrange
        # Arrange
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="OK", stderr=""
        )
        # Act
        result = scitex_ssh.setup(2222)
        # Assert
        assert result["success"] is True
        args = mock_run.call_args[0][0]
        # Act
        # Assert
        assert "/env/key" in args



    @patch.dict(os.environ, {}, clear=True)
    def test_setup_raises_without_bastion(self):
        # Arrange
        # Act
        # Arrange
        # Act
        import pytest

        # Assert
        # Assert
        with pytest.raises(ValueError, match="bastion_server is required"):
            scitex_ssh.setup(2222)

    @patch.dict(
        os.environ,
        {"SCITEX_SSH_BASTION_SERVER": "env@bastion"},
        clear=True,
    )
    def test_setup_raises_without_secret_key(self):
        # Arrange
        # Act
        # Arrange
        # Act
        import pytest

        # Assert
        # Assert
        with pytest.raises(ValueError, match="secret_key_path is required"):
            scitex_ssh.setup(2222)


class TestRemove:
    """Tests for remove() function."""

    @patch("scitex_ssh.subprocess.run")
    def test_remove_success_result_success_is_true(self, mock_run):
        # Arrange
        # Arrange
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="Removed", stderr=""
        )
        # Act
        # Act
        result = scitex_ssh.remove(2222)
        # Assert
        # Assert
        assert result["success"] is True

    @patch("scitex_ssh.subprocess.run")
    def test_remove_passes_port_p_in_args(self, mock_run):
        # Arrange
        # Arrange
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        scitex_ssh.remove(5098)
        # Act
        args = mock_run.call_args[0][0]
        # Act
        # Assert
        # Assert
        assert "-p" in args

    @patch("scitex_ssh.subprocess.run")
    def test_remove_passes_port_n_5098_in_args(self, mock_run):
        # Arrange
        # Arrange
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )
        scitex_ssh.remove(5098)
        # Act
        args = mock_run.call_args[0][0]
        # Act
        # Assert
        # Assert
        assert "5098" in args



class TestStatus:
    """Tests for status() function."""

    @patch("scitex_ssh.subprocess.run")
    def test_status_all_result_success_is_true(self, mock_run):
        # Arrange
        # Arrange
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="active", stderr=""
        )
        # Act
        result = scitex_ssh.status()
        # Act
        # Assert
        # Assert
        assert result["success"] is True

    @patch("scitex_ssh.subprocess.run")
    def test_status_all_list_units_in_args_result_success_is_true(self, mock_run):
        # Arrange
        # Arrange
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="active", stderr=""
        )
        # Act
        result = scitex_ssh.status()
        # Act
        # Assert
        # Assert
        assert result["success"] is True

    @patch("scitex_ssh.subprocess.run")
    def test_status_all_list_units_in_args_list_units_in_args(self, mock_run):
        # Arrange
        # Arrange
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="active", stderr=""
        )
        # Act
        result = scitex_ssh.status()
        # Assert
        assert result["success"] is True
        args = mock_run.call_args[0][0]
        # Act
        # Assert
        assert "list-units" in args



    @patch("scitex_ssh.subprocess.run")
    def test_status_specific_port_result_success_is_true(self, mock_run):
        # Arrange
        # Arrange
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="active", stderr=""
        )
        # Act
        result = scitex_ssh.status(port=2222)
        # Act
        # Assert
        # Assert
        assert result["success"] is True

    @patch("scitex_ssh.subprocess.run")
    def test_status_specific_port_autossh_tunnel_2222_service_in_args_result_success_is_true(self, mock_run):
        # Arrange
        # Arrange
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="active", stderr=""
        )
        # Act
        result = scitex_ssh.status(port=2222)
        # Act
        # Assert
        # Assert
        assert result["success"] is True

    @patch("scitex_ssh.subprocess.run")
    def test_status_specific_port_autossh_tunnel_2222_service_in_args_autossh_tunnel_2222_service_in_args(self, mock_run):
        # Arrange
        # Arrange
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="active", stderr=""
        )
        # Act
        result = scitex_ssh.status(port=2222)
        # Assert
        assert result["success"] is True
        args = mock_run.call_args[0][0]
        # Act
        # Assert
        assert "autossh-tunnel-2222.service" in args




# EOF
