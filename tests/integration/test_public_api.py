#!/usr/bin/env python3
"""Integration tests for scitex_ssh public API surface.

Exercises the top-level functions exposed from scitex_ssh/__init__.py
(setup/remove/status/version) end-to-end using the production ``runner``
injection kwarg + a hand-rolled ``FakeRunner`` (see
``tests/conftest.py``) — no ``unittest.mock``, no ``monkeypatch``.

Lives in tests/integration/ (not tests/scitex_ssh/) because the
package's public API is defined in __init__.py and there is no module
basename to mirror — this is the canonical home for cross-module
surface tests per scitex-dev audit-project §3 / PS302.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

import scitex_ssh


# ---------------------------------------------------------------------
# Allowlist bypass fixture — write a real config.yaml in tmp_path and
# point the production loader at it via the `config_path` kwarg the
# bypass-aware helpers below thread through.
# ---------------------------------------------------------------------


@pytest.fixture
def allow_all_cfg(tmp_path: Path, env_save_restore) -> Path:
    """Write a tmp config that allows tunnels globally and point the
    production allowlist loader at it via ``$HOME``."""
    home = tmp_path / "home"
    cfg_dir = home / ".scitex" / "ssh"
    cfg_dir.mkdir(parents=True)
    cfg = cfg_dir / "config.yaml"
    cfg.write_text("default: {tunnels: allow}\n")
    # CONFIG_PATH is computed at import time from $HOME; re-point HOME
    # and rebind the module-level path so ``_require_allowed`` finds it.
    os.environ["HOME"] = str(home)
    from scitex_ssh import _allowlist

    _allowlist.CONFIG_PATH = cfg
    return cfg


# ---------------------------------------------------------------------
# Version + availability surface (no subprocess involved)
# ---------------------------------------------------------------------


class TestVersion:
    """Version and availability tests."""

    def test_module_exposes_version_dunder_attribute(self) -> None:
        # Arrange
        # Act
        present = hasattr(scitex_ssh, "__version__")
        # Assert
        assert present is True

    def test_version_dunder_is_string_type(self) -> None:
        # Arrange
        # Act
        v = scitex_ssh.__version__
        # Assert
        assert isinstance(v, str)

    def test_version_string_splits_into_three_dotted_parts(self) -> None:
        # Arrange
        # Act
        parts = scitex_ssh.__version__.split(".")
        # Assert
        assert len(parts) == 3

    def test_version_string_parts_are_all_digits(self) -> None:
        # Arrange
        # Act
        parts = scitex_ssh.__version__.split(".")
        # Assert
        assert all(p.isdigit() for p in parts)

    def test_get_version_helper_returns_dunder_version(self) -> None:
        # Arrange
        # Act
        result = scitex_ssh.get_version()
        # Assert
        assert result == scitex_ssh.__version__

    def test_available_module_flag_is_true(self) -> None:
        # Arrange
        # Act
        flag = scitex_ssh.AVAILABLE
        # Assert
        assert flag is True


class TestScriptsDir:
    """Script directory tests."""

    def test_scripts_dir_is_an_existing_directory(self) -> None:
        # Arrange
        # Act
        is_dir = os.path.isdir(scitex_ssh._SCRIPTS_DIR)
        # Assert
        assert is_dir is True

    def test_scripts_dir_contains_setup_autossh_service_sh(self) -> None:
        # Arrange
        path = os.path.join(scitex_ssh._SCRIPTS_DIR, "setup-autossh-service.sh")
        # Act
        is_file = os.path.isfile(path)
        # Assert
        assert is_file is True

    def test_scripts_dir_contains_remove_autossh_service_sh(self) -> None:
        # Arrange
        path = os.path.join(scitex_ssh._SCRIPTS_DIR, "remove-autossh-service.sh")
        # Act
        is_file = os.path.isfile(path)
        # Assert
        assert is_file is True


# ---------------------------------------------------------------------
# setup() — uses the bundled bash script via _run_script(runner=...)
# ---------------------------------------------------------------------


class TestSetup:
    """Tests for setup() function."""

    def test_setup_returns_success_true_when_runner_returncode_zero(
        self, fake_runner, allow_all_cfg
    ) -> None:
        # Arrange
        fake_runner.returncode = 0
        fake_runner.stdout = "OK"
        # Act
        result = scitex_ssh.setup(
            2222,
            "user@bastion",
            "/home/user/.ssh/id_rsa",
            runner=fake_runner,
        )
        # Assert
        assert result["success"] is True

    def test_setup_propagates_runner_stdout_into_result(
        self, fake_runner, allow_all_cfg
    ) -> None:
        # Arrange
        fake_runner.returncode = 0
        fake_runner.stdout = "OK"
        # Act
        result = scitex_ssh.setup(
            2222,
            "user@bastion",
            "/home/user/.ssh/id_rsa",
            runner=fake_runner,
        )
        # Assert
        assert result["stdout"] == "OK"

    def test_setup_propagates_runner_stderr_into_result(
        self, fake_runner, allow_all_cfg
    ) -> None:
        # Arrange
        fake_runner.returncode = 0
        # Act
        result = scitex_ssh.setup(
            2222,
            "user@bastion",
            "/home/user/.ssh/id_rsa",
            runner=fake_runner,
        )
        # Assert
        assert result["stderr"] == ""

    def test_setup_argv_includes_dash_p_port_flag(
        self, fake_runner, allow_all_cfg
    ) -> None:
        # Arrange
        # Act
        scitex_ssh.setup(
            5098, "admin@relay.example.com", "/tmp/key", runner=fake_runner
        )
        # Assert
        assert "-p" in fake_runner.last_cmd

    def test_setup_argv_includes_port_number_string(
        self, fake_runner, allow_all_cfg
    ) -> None:
        # Arrange
        # Act
        scitex_ssh.setup(
            5098, "admin@relay.example.com", "/tmp/key", runner=fake_runner
        )
        # Assert
        assert "5098" in fake_runner.last_cmd

    def test_setup_argv_includes_dash_b_bastion_flag(
        self, fake_runner, allow_all_cfg
    ) -> None:
        # Arrange
        # Act
        scitex_ssh.setup(
            5098, "admin@relay.example.com", "/tmp/key", runner=fake_runner
        )
        # Assert
        assert "-b" in fake_runner.last_cmd

    def test_setup_argv_includes_bastion_address(
        self, fake_runner, allow_all_cfg
    ) -> None:
        # Arrange
        # Act
        scitex_ssh.setup(
            5098, "admin@relay.example.com", "/tmp/key", runner=fake_runner
        )
        # Assert
        assert "admin@relay.example.com" in fake_runner.last_cmd

    def test_setup_argv_includes_dash_s_secret_key_flag(
        self, fake_runner, allow_all_cfg
    ) -> None:
        # Arrange
        # Act
        scitex_ssh.setup(
            5098, "admin@relay.example.com", "/tmp/key", runner=fake_runner
        )
        # Assert
        assert "-s" in fake_runner.last_cmd

    def test_setup_argv_includes_secret_key_path(
        self, fake_runner, allow_all_cfg
    ) -> None:
        # Arrange
        # Act
        scitex_ssh.setup(
            5098, "admin@relay.example.com", "/tmp/key", runner=fake_runner
        )
        # Assert
        assert "/tmp/key" in fake_runner.last_cmd

    def test_setup_marks_nonzero_returncode_as_failure(
        self, fake_runner, allow_all_cfg
    ) -> None:
        # Arrange
        fake_runner.returncode = 1
        fake_runner.stderr = "Permission denied"
        # Act
        result = scitex_ssh.setup(
            2222, "user@bastion", "/tmp/key", runner=fake_runner
        )
        # Assert
        assert result["success"] is False

    def test_setup_failure_propagates_runner_stderr_into_result(
        self, fake_runner, allow_all_cfg
    ) -> None:
        # Arrange
        fake_runner.returncode = 1
        fake_runner.stderr = "Permission denied"
        # Act
        result = scitex_ssh.setup(
            2222, "user@bastion", "/tmp/key", runner=fake_runner
        )
        # Assert
        assert result["stderr"] == "Permission denied"

    def test_setup_env_fallback_uses_bastion_from_environment(
        self, fake_runner, allow_all_cfg, env_save_restore
    ) -> None:
        # Arrange
        os.environ["SCITEX_SSH_BASTION_SERVER"] = "env@bastion"
        os.environ["SCITEX_SSH_SECRET_KEY_PATH"] = "/env/key"
        # Act
        scitex_ssh.setup(2222, runner=fake_runner)
        # Assert
        assert "env@bastion" in fake_runner.last_cmd

    def test_setup_env_fallback_uses_secret_key_from_environment(
        self, fake_runner, allow_all_cfg, env_save_restore
    ) -> None:
        # Arrange
        os.environ["SCITEX_SSH_BASTION_SERVER"] = "env@bastion"
        os.environ["SCITEX_SSH_SECRET_KEY_PATH"] = "/env/key"
        # Act
        scitex_ssh.setup(2222, runner=fake_runner)
        # Assert
        assert "/env/key" in fake_runner.last_cmd

    def test_setup_raises_valueerror_when_bastion_missing_everywhere(
        self, env_save_restore
    ) -> None:
        # Arrange
        os.environ.pop("SCITEX_SSH_BASTION_SERVER", None)
        os.environ.pop("SCITEX_SSH_SECRET_KEY_PATH", None)
        # Act
        ctx = pytest.raises(ValueError, match="bastion_server is required")
        # Assert
        with ctx:
            scitex_ssh.setup(2222)

    def test_setup_raises_valueerror_when_secret_key_missing_everywhere(
        self, env_save_restore
    ) -> None:
        # Arrange
        os.environ.pop("SCITEX_SSH_SECRET_KEY_PATH", None)
        os.environ["SCITEX_SSH_BASTION_SERVER"] = "env@bastion"
        # Act
        ctx = pytest.raises(ValueError, match="secret_key_path is required")
        # Assert
        with ctx:
            scitex_ssh.setup(2222)


# ---------------------------------------------------------------------
# remove()
# ---------------------------------------------------------------------


class TestRemove:
    """Tests for remove() function."""

    def test_remove_marks_zero_returncode_as_success(
        self, fake_runner, allow_all_cfg
    ) -> None:
        # Arrange
        fake_runner.returncode = 0
        fake_runner.stdout = "Removed"
        # Act
        result = scitex_ssh.remove(2222, runner=fake_runner)
        # Assert
        assert result["success"] is True

    def test_remove_argv_includes_dash_p_port_flag(
        self, fake_runner, allow_all_cfg
    ) -> None:
        # Arrange
        # Act
        scitex_ssh.remove(5098, runner=fake_runner)
        # Assert
        assert "-p" in fake_runner.last_cmd

    def test_remove_argv_includes_port_number_string(
        self, fake_runner, allow_all_cfg
    ) -> None:
        # Arrange
        # Act
        scitex_ssh.remove(5098, runner=fake_runner)
        # Assert
        assert "5098" in fake_runner.last_cmd


# ---------------------------------------------------------------------
# status()
# ---------------------------------------------------------------------


class TestStatus:
    """Tests for status() function."""

    def test_status_all_marks_zero_returncode_as_success(self, fake_runner) -> None:
        # Arrange
        fake_runner.returncode = 0
        fake_runner.stdout = "active"
        # Act
        result = scitex_ssh.status(runner=fake_runner)
        # Assert
        assert result["success"] is True

    def test_status_all_invokes_systemctl_list_units(self, fake_runner) -> None:
        # Arrange
        fake_runner.returncode = 0
        # Act
        scitex_ssh.status(runner=fake_runner)
        # Assert
        assert "list-units" in fake_runner.last_cmd

    def test_status_specific_port_marks_zero_returncode_as_success(
        self, fake_runner
    ) -> None:
        # Arrange
        fake_runner.returncode = 0
        fake_runner.stdout = "active"
        # Act
        result = scitex_ssh.status(port=2222, runner=fake_runner)
        # Assert
        assert result["success"] is True

    def test_status_specific_port_targets_named_service_unit(
        self, fake_runner
    ) -> None:
        # Arrange
        fake_runner.returncode = 0
        # Act
        scitex_ssh.status(port=2222, runner=fake_runner)
        # Assert
        assert "autossh-tunnel-2222.service" in fake_runner.last_cmd


# EOF
