#!/usr/bin/env python3
"""Tests for scitex_ssh._allowlist — real config file via $SCITEX_SSH_CONFIG.

No mocks: each test writes a real YAML config to tmp_path and points the
allowlist at it with the $SCITEX_SSH_CONFIG env var (the documented
override). The production `_load()` reads that real file.
"""

from __future__ import annotations

import pytest

from scitex_ssh._allowlist import PolicyError, is_allowed, require


@pytest.fixture
def cfg(tmp_path, env_save_restore):
    """Point the allowlist at a tmp config; return its path (not yet written)."""
    path = tmp_path / "config.yaml"
    env_save_restore("SCITEX_SSH_CONFIG", str(path))
    return path


def test_missing_config_file_does_not_exist(cfg):
    # Arrange — fixture set the env var but wrote no file
    # Act
    exists = cfg.exists()
    # Assert
    assert exists is False


def test_missing_config_denies_unknown_host(cfg):
    # Arrange — no config file written
    # Act
    allowed = is_allowed("anyhost", "tunnels")
    # Assert
    assert allowed is False


def test_missing_config_require_raises_policyerror(cfg):
    # Arrange — no config file written
    # Act
    ctx = pytest.raises(PolicyError)
    # Assert
    with ctx:
        require("anyhost", "tunnels")


def test_host_explicitly_allowed_is_allowed_returns_true(cfg):
    # Arrange
    cfg.write_text("default: {tunnels: deny}\nhosts:\n  mba: {tunnels: allow}\n")
    # Act
    allowed = is_allowed("mba", "tunnels")
    # Assert
    assert allowed is True


def test_host_explicitly_allowed_require_does_not_raise(cfg):
    # Arrange
    cfg.write_text("default: {tunnels: deny}\nhosts:\n  mba: {tunnels: allow}\n")
    raised = False
    # Act
    try:
        require("mba", "tunnels")
    except PolicyError:
        raised = True
    # Assert
    assert raised is False


def test_host_explicitly_denied_is_allowed_returns_false(cfg):
    # Arrange
    cfg.write_text("default: {tunnels: allow}\nhosts:\n  spartan: {tunnels: deny}\n")
    # Act
    allowed = is_allowed("spartan", "tunnels")
    # Assert
    assert allowed is False


def test_host_explicitly_denied_require_raises_policyerror(cfg):
    # Arrange
    cfg.write_text("default: {tunnels: allow}\nhosts:\n  spartan: {tunnels: deny}\n")
    # Act
    ctx = pytest.raises(PolicyError)
    # Assert
    with ctx:
        require("spartan", "tunnels")


def test_default_allow_permits_unlisted_host(cfg):
    # Arrange
    cfg.write_text("default: {tunnels: allow}\n")
    # Act
    allowed = is_allowed("randomhost", "tunnels")
    # Assert
    assert allowed is True


def test_default_deny_denies_unlisted_host(cfg):
    # Arrange
    cfg.write_text("default: {tunnels: deny}\n")
    # Act
    allowed = is_allowed("randomhost", "tunnels")
    # Assert
    assert allowed is False


def test_default_deny_require_raises_policyerror_for_unlisted_host(cfg):
    # Arrange
    cfg.write_text("default: {tunnels: deny}\n")
    # Act
    ctx = pytest.raises(PolicyError)
    # Assert
    with ctx:
        require("randomhost", "tunnels")


# EOF
