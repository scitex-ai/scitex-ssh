#!/usr/bin/env python3
"""Tests for scitex_ssh._tunnel_forward — discovery-driven forward tunnel spec.

No mocks: discovery files are written to a real tmp_path and read back. The
process-replacing exec_forward is not unit-tested (it overlays the process);
resolution + rendering + error paths are, which is where the logic lives.
"""

from __future__ import annotations

import json

import pytest

from scitex_ssh._tunnel_forward import (
    DiscoveryError,
    forward_command,
    load_discovery,
    resolve_forward_spec,
)
from scitex_ssh._tunnel_render import render_argv, render_command

_DISCOVERY = {
    "node": "spartan-gpgpu014",
    "litellm_port": 4000,
    "vllm_port": 8765,
    "model": "qwen36-35b-a3b",
    "key": "sk-clew-local",
    "updated_at": "2026-07-05T17:00:00Z",
}


def _write_discovery(tmp_path, data=None) -> str:
    """Write a discovery JSON file and return its path."""
    p = tmp_path / "qwen-endpoint.json"
    p.write_text(json.dumps(_DISCOVERY if data is None else data))
    return str(p)


class TestResolveForwardSpec:
    def test_direction_is_forward(self, tmp_path):
        # Arrange
        path = _write_discovery(tmp_path)
        # Act
        spec = resolve_forward_spec(path)
        # Assert
        assert spec.direction == "forward"

    def test_target_host_is_discovery_node(self, tmp_path):
        # Arrange
        path = _write_discovery(tmp_path)
        # Act
        spec = resolve_forward_spec(path)
        # Assert
        assert spec.target.host == "spartan-gpgpu014"

    def test_target_port_from_litellm_field(self, tmp_path):
        # Arrange
        path = _write_discovery(tmp_path)
        # Act
        spec = resolve_forward_spec(path)
        # Assert
        assert spec.target.port == 4000

    def test_local_port_defaults_to_remote(self, tmp_path):
        # Arrange
        path = _write_discovery(tmp_path)
        # Act
        spec = resolve_forward_spec(path)
        # Assert
        assert spec.listen.port == 4000

    def test_via_is_destination_and_last_arg(self, tmp_path):
        # Arrange
        path = _write_discovery(tmp_path)
        # Act
        argv = render_argv(resolve_forward_spec(path, via="spartan"))
        # Assert
        assert argv[-1] == "spartan"

    def test_remote_port_override_wins(self, tmp_path):
        # Arrange
        path = _write_discovery(tmp_path)
        # Act
        spec = resolve_forward_spec(path, remote_port=9999)
        # Assert
        assert spec.target.port == 9999

    def test_vllm_port_field_selects_vllm_port(self, tmp_path):
        # Arrange
        path = _write_discovery(tmp_path)
        # Act
        spec = resolve_forward_spec(path, port_field="vllm_port")
        # Assert
        assert spec.target.port == 8765

    def test_custom_local_port_is_used(self, tmp_path):
        # Arrange
        path = _write_discovery(tmp_path)
        # Act
        spec = resolve_forward_spec(path, local_port=4100)
        # Assert
        assert spec.listen.port == 4100

    def test_forward_command_matches_render_command(self, tmp_path):
        # Arrange
        path = _write_discovery(tmp_path)
        spec = resolve_forward_spec(path)
        # Act
        cmd = forward_command(spec)
        # Assert
        assert cmd == render_command(spec)


class TestDiscoveryErrors:
    def test_missing_file_raises(self, tmp_path):
        # Arrange
        missing = str(tmp_path / "nope.json")
        # Act
        ctx = pytest.raises(DiscoveryError, match="unreadable")
        # Assert
        with ctx:
            load_discovery(missing)

    def test_invalid_json_raises(self, tmp_path):
        # Arrange
        p = tmp_path / "bad.json"
        p.write_text("{not json")
        # Act
        ctx = pytest.raises(DiscoveryError, match="not valid JSON")
        # Assert
        with ctx:
            load_discovery(str(p))

    def test_non_object_json_raises(self, tmp_path):
        # Arrange
        p = tmp_path / "arr.json"
        p.write_text("[1, 2, 3]")
        # Act
        ctx = pytest.raises(DiscoveryError, match="JSON object")
        # Assert
        with ctx:
            load_discovery(str(p))

    def test_missing_node_raises(self, tmp_path):
        # Arrange
        path = _write_discovery(tmp_path, {"litellm_port": 4000})
        # Act
        ctx = pytest.raises(DiscoveryError, match="node")
        # Assert
        with ctx:
            resolve_forward_spec(path)

    def test_missing_port_field_raises(self, tmp_path):
        # Arrange
        path = _write_discovery(tmp_path, {"node": "n"})
        # Act
        ctx = pytest.raises(DiscoveryError, match="port field")
        # Assert
        with ctx:
            resolve_forward_spec(path)

    def test_unknown_port_field_raises(self, tmp_path):
        # Arrange
        path = _write_discovery(tmp_path)
        # Act
        ctx = pytest.raises(DiscoveryError, match="unknown port_field")
        # Assert
        with ctx:
            resolve_forward_spec(path, port_field="bogus_port")


# EOF
