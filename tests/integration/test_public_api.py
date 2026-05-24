#!/usr/bin/env python3
"""Integration tests for scitex_ssh public API surface.

Exercises the top-level functions exposed from scitex_ssh/__init__.py
(setup/remove/status/version) end-to-end against real collaborators:
a fake `bash`/`systemctl` on $PATH (subprocess_shim) and a real allowlist
config (allow_tunnels via $SCITEX_SSH_CONFIG). No mocks.

Lives in tests/integration/ (not tests/scitex_ssh/) because the package's
public API is defined in __init__.py and there is no module basename to
mirror — this is the canonical home for cross-module surface tests per
scitex-dev audit-project §3 / PS302.
"""

from __future__ import annotations

import os

import pytest

import scitex_ssh


@pytest.fixture(autouse=True)
def _isolate_tunnel_env(allow_tunnels):
    """Allow tunnels via a real config and clear inherited bastion/key env.

    `allow_tunnels` writes an allow-all config and points $SCITEX_SSH_CONFIG
    at it. Inherited SCITEX_SSH_BASTION_SERVER / SCITEX_SSH_SECRET_KEY_PATH
    from the developer's shell are stripped so tests control them explicitly.
    """
    saved = {
        k: os.environ.pop(k, None)
        for k in ("SCITEX_SSH_BASTION_SERVER", "SCITEX_SSH_SECRET_KEY_PATH")
    }
    try:
        yield
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


class TestVersion:
    """Version and availability tests."""

    def test_version_attribute_is_present(self):
        # Arrange
        # Act
        # Assert
        assert hasattr(scitex_ssh, "__version__")

    def test_version_attribute_is_a_string(self):
        # Arrange
        # Act
        # Assert
        assert isinstance(scitex_ssh.__version__, str)

    def test_version_has_three_dotted_parts(self):
        # Arrange
        # Act
        parts = scitex_ssh.__version__.split(".")
        # Assert
        assert len(parts) == 3

    def test_version_parts_are_all_numeric(self):
        # Arrange
        # Act
        parts = scitex_ssh.__version__.split(".")
        # Assert
        assert all(p.isdigit() for p in parts)

    def test_get_version_matches_dunder_version(self):
        # Arrange
        # Act
        # Assert
        assert scitex_ssh.get_version() == scitex_ssh.__version__

    def test_available_flag_is_true(self):
        # Arrange
        # Act
        # Assert
        assert scitex_ssh.AVAILABLE is True


class TestScriptsDir:
    """Script directory tests."""

    def test_scripts_dir_is_a_directory(self):
        # Arrange
        # Act
        # Assert
        assert os.path.isdir(scitex_ssh._SCRIPTS_DIR)

    def test_setup_script_file_is_present(self):
        # Arrange
        # Act
        path = os.path.join(scitex_ssh._SCRIPTS_DIR, "setup-autossh-service.sh")
        # Assert
        assert os.path.isfile(path)

    def test_remove_script_file_is_present(self):
        # Arrange
        # Act
        path = os.path.join(scitex_ssh._SCRIPTS_DIR, "remove-autossh-service.sh")
        # Assert
        assert os.path.isfile(path)


class TestSetup:
    """Tests for setup() function — real bash script invocation."""

    def test_setup_reports_success_on_zero_exit(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("bash", rc=0, stdout="OK")
        # Act
        result = scitex_ssh.setup(2222, "user@bastion", "/home/user/.ssh/id_rsa")
        # Assert
        assert result["success"] is True

    def test_setup_captures_script_stdout(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("bash", rc=0, stdout="OK")
        # Act
        result = scitex_ssh.setup(2222, "user@bastion", "/home/user/.ssh/id_rsa")
        # Assert
        assert result["stdout"] == "OK"

    def test_setup_captures_empty_stderr_on_success(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("bash", rc=0, stdout="OK")
        # Act
        result = scitex_ssh.setup(2222, "user@bastion", "/home/user/.ssh/id_rsa")
        # Assert
        assert result["stderr"] == ""

    def test_setup_passes_port_flag_to_script(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("bash", rc=0)
        # Act
        scitex_ssh.setup(5098, "admin@relay.example.com", "/tmp/key")
        # Assert
        assert "-p" in subprocess_shim.argv("bash")

    def test_setup_passes_port_value_to_script(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("bash", rc=0)
        # Act
        scitex_ssh.setup(5098, "admin@relay.example.com", "/tmp/key")
        # Assert
        assert "5098" in subprocess_shim.argv("bash")

    def test_setup_passes_bastion_flag_to_script(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("bash", rc=0)
        # Act
        scitex_ssh.setup(5098, "admin@relay.example.com", "/tmp/key")
        # Assert
        assert "-b" in subprocess_shim.argv("bash")

    def test_setup_passes_bastion_value_to_script(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("bash", rc=0)
        # Act
        scitex_ssh.setup(5098, "admin@relay.example.com", "/tmp/key")
        # Assert
        assert "admin@relay.example.com" in subprocess_shim.argv("bash")

    def test_setup_passes_secret_key_flag_to_script(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("bash", rc=0)
        # Act
        scitex_ssh.setup(5098, "admin@relay.example.com", "/tmp/key")
        # Assert
        assert "-s" in subprocess_shim.argv("bash")

    def test_setup_passes_secret_key_value_to_script(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("bash", rc=0)
        # Act
        scitex_ssh.setup(5098, "admin@relay.example.com", "/tmp/key")
        # Assert
        assert "/tmp/key" in subprocess_shim.argv("bash")

    def test_setup_reports_failure_on_nonzero_exit(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("bash", rc=1, stderr="Permission denied")
        # Act
        result = scitex_ssh.setup(2222, "user@bastion", "/tmp/key")
        # Assert
        assert result["success"] is False

    def test_setup_captures_script_stderr_on_failure(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("bash", rc=1, stderr="Permission denied")
        # Act
        result = scitex_ssh.setup(2222, "user@bastion", "/tmp/key")
        # Assert
        assert result["stderr"] == "Permission denied"

    def test_setup_uses_env_var_bastion_when_arg_omitted(
        self, subprocess_shim, env_save_restore
    ):
        # Arrange
        subprocess_shim.install("bash", rc=0, stdout="OK")
        env_save_restore("SCITEX_SSH_BASTION_SERVER", "env@bastion")
        env_save_restore("SCITEX_SSH_SECRET_KEY_PATH", "/env/key")
        # Act
        scitex_ssh.setup(2222)
        # Assert
        assert "env@bastion" in subprocess_shim.argv("bash")

    def test_setup_uses_env_var_secret_key_when_arg_omitted(
        self, subprocess_shim, env_save_restore
    ):
        # Arrange
        subprocess_shim.install("bash", rc=0, stdout="OK")
        env_save_restore("SCITEX_SSH_BASTION_SERVER", "env@bastion")
        env_save_restore("SCITEX_SSH_SECRET_KEY_PATH", "/env/key")
        # Act
        scitex_ssh.setup(2222)
        # Assert
        assert "/env/key" in subprocess_shim.argv("bash")

    def test_setup_with_env_var_fallback_reports_success(
        self, subprocess_shim, env_save_restore
    ):
        # Arrange
        subprocess_shim.install("bash", rc=0, stdout="OK")
        env_save_restore("SCITEX_SSH_BASTION_SERVER", "env@bastion")
        env_save_restore("SCITEX_SSH_SECRET_KEY_PATH", "/env/key")
        # Act
        result = scitex_ssh.setup(2222)
        # Assert
        assert result["success"] is True

    def test_setup_raises_when_bastion_missing(self):
        # Arrange — _isolate_tunnel_env cleared the env vars
        # Act
        ctx = pytest.raises(ValueError, match="bastion_server is required")
        # Assert
        with ctx:
            scitex_ssh.setup(2222)

    def test_setup_raises_when_secret_key_missing(self, env_save_restore):
        # Arrange — bastion present, secret key absent
        env_save_restore("SCITEX_SSH_BASTION_SERVER", "env@bastion")
        # Act
        ctx = pytest.raises(ValueError, match="secret_key_path is required")
        # Assert
        with ctx:
            scitex_ssh.setup(2222)


class TestRemove:
    """Tests for remove() function — real bash script invocation."""

    def test_remove_reports_success_on_zero_exit(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("bash", rc=0, stdout="Removed")
        # Act
        result = scitex_ssh.remove(2222)
        # Assert
        assert result["success"] is True

    def test_remove_passes_port_flag_to_script(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("bash", rc=0)
        # Act
        scitex_ssh.remove(5098)
        # Assert
        assert "-p" in subprocess_shim.argv("bash")

    def test_remove_passes_port_value_to_script(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("bash", rc=0)
        # Act
        scitex_ssh.remove(5098)
        # Assert
        assert "5098" in subprocess_shim.argv("bash")


class TestStatus:
    """Tests for status() function — real systemctl invocation."""

    def test_status_all_reports_success(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("systemctl", rc=0, stdout="active")
        # Act
        result = scitex_ssh.status()
        # Assert
        assert result["success"] is True

    def test_status_all_uses_list_units(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("systemctl", rc=0, stdout="active")
        # Act
        scitex_ssh.status()
        # Assert
        assert "list-units" in subprocess_shim.argv("systemctl")

    def test_status_specific_port_reports_success(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("systemctl", rc=0, stdout="active")
        # Act
        result = scitex_ssh.status(port=2222)
        # Assert
        assert result["success"] is True

    def test_status_specific_port_targets_that_unit(self, subprocess_shim):
        # Arrange
        subprocess_shim.install("systemctl", rc=0, stdout="active")
        # Act
        scitex_ssh.status(port=2222)
        # Assert
        assert "autossh-tunnel-2222.service" in subprocess_shim.argv("systemctl")


# EOF
