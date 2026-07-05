#!/usr/bin/env python3
"""Tests for scitex_ssh._tunnel_render — pure ssh tunnel argv construction.

No mocks: the renderer is a pure function of its spec, so every test asserts
directly on the rendered argv / command string. One assertion per test,
AAA-structured, per the project's test-quality rules.
"""

from __future__ import annotations

import shlex

import pytest

from scitex_ssh._tunnel_render import (
    DEFAULT_SSH_OPTS,
    Endpoint,
    TunnelSpec,
    render_argv,
    render_command,
)


def _qwen_forward() -> TunnelSpec:
    """The canonical ephemeral-node forward tunnel (qwen on a Spartan node)."""
    return TunnelSpec(
        direction="forward",
        listen=Endpoint("127.0.0.1", 4000),
        target=Endpoint("spartan-gpu-a017", 4000),
        via="spartan",
    )


def _reverse() -> TunnelSpec:
    """A persistent-style reverse tunnel: expose local 8080 on bastion:9090."""
    return TunnelSpec(
        direction="reverse",
        listen=Endpoint("", 9090),
        target=Endpoint("127.0.0.1", 8080),
        via="bastion.example.com",
    )


class TestForwardRendering:
    def test_first_arg_is_ssh(self):
        # Arrange
        spec = _qwen_forward()
        # Act
        argv = render_argv(spec)
        # Assert
        assert argv[0] == "ssh"

    def test_always_emits_dash_N(self):
        # Arrange — -N is the supervisor contract: no remote command => blocks.
        spec = _qwen_forward()
        # Act
        argv = render_argv(spec)
        # Assert
        assert "-N" in argv

    def test_forward_L_spec_shape(self):
        # Arrange
        spec = _qwen_forward()
        # Act
        argv = render_argv(spec)
        # Assert
        assert argv[argv.index("-L") + 1] == "127.0.0.1:4000:spartan-gpu-a017:4000"

    def test_destination_is_via_and_last(self):
        # Arrange
        spec = _qwen_forward()
        # Act
        argv = render_argv(spec)
        # Assert
        assert argv[-1] == "spartan"

    def test_no_proxyjump_when_jump_absent(self):
        # Arrange
        spec = _qwen_forward()
        # Act
        argv = render_argv(spec)
        # Assert
        assert "-J" not in argv

    def test_default_ssh_opt_present(self):
        # Arrange
        spec = _qwen_forward()
        # Act
        joined = " ".join(render_argv(spec))
        # Assert
        assert "ExitOnForwardFailure=yes" in joined

    def test_options_precede_destination(self):
        # Arrange
        spec = _qwen_forward()
        # Act
        argv = render_argv(spec)
        # Assert
        assert argv.index("-L") < len(argv) - 1


class TestReverseRendering:
    def test_reverse_R_spec_shape(self):
        # Arrange
        spec = _reverse()
        # Act
        argv = render_argv(spec)
        # Assert
        assert argv[argv.index("-R") + 1] == "9090:127.0.0.1:8080"

    def test_reverse_destination_is_last(self):
        # Arrange
        spec = _reverse()
        # Act
        argv = render_argv(spec)
        # Assert
        assert argv[-1] == "bastion.example.com"

    def test_reverse_includes_bind_address_when_set(self):
        # Arrange
        spec = TunnelSpec(
            direction="reverse",
            listen=Endpoint("0.0.0.0", 9090),
            target=Endpoint("127.0.0.1", 8080),
            via="bastion",
        )
        # Act
        argv = render_argv(spec)
        # Assert
        assert argv[argv.index("-R") + 1] == "0.0.0.0:9090:127.0.0.1:8080"


class TestOptionalFields:
    def test_jump_renders_proxyjump_value(self):
        # Arrange
        spec = TunnelSpec(
            direction="forward",
            listen=Endpoint("127.0.0.1", 4000),
            target=Endpoint("node", 4000),
            via="spartan",
            jump="user@bastion:2222",
        )
        # Act
        argv = render_argv(spec)
        # Assert
        assert argv[argv.index("-J") + 1] == "user@bastion:2222"

    def test_jump_does_not_replace_via_destination(self):
        # Arrange
        spec = TunnelSpec(
            direction="forward",
            listen=Endpoint("127.0.0.1", 4000),
            target=Endpoint("node", 4000),
            via="spartan",
            jump="user@bastion:2222",
        )
        # Act
        argv = render_argv(spec)
        # Assert
        assert argv[-1] == "spartan"

    def test_via_user_prefixes_destination(self):
        # Arrange
        spec = TunnelSpec(
            direction="forward",
            listen=Endpoint("127.0.0.1", 4000),
            target=Endpoint("node", 4000),
            via="spartan",
            via_user="ywatanabe",
        )
        # Act
        argv = render_argv(spec)
        # Assert
        assert argv[-1] == "ywatanabe@spartan"

    def test_via_port_renders_dash_p(self):
        # Arrange
        spec = TunnelSpec(
            direction="forward",
            listen=Endpoint("127.0.0.1", 4000),
            target=Endpoint("node", 4000),
            via="spartan",
            via_port=2222,
        )
        # Act
        argv = render_argv(spec)
        # Assert
        assert argv[argv.index("-p") + 1] == "2222"

    def test_identity_renders_dash_i(self):
        # Arrange
        spec = TunnelSpec(
            direction="forward",
            listen=Endpoint("127.0.0.1", 4000),
            target=Endpoint("node", 4000),
            via="spartan",
            identity="~/.ssh/id_ed25519",
        )
        # Act
        argv = render_argv(spec)
        # Assert
        assert argv[argv.index("-i") + 1] == "~/.ssh/id_ed25519"

    def test_caller_ssh_opt_overrides_default(self):
        # Arrange
        spec = TunnelSpec(
            direction="forward",
            listen=Endpoint("127.0.0.1", 4000),
            target=Endpoint("node", 4000),
            via="spartan",
            ssh_opts={"StrictHostKeyChecking": "no"},
        )
        # Act
        joined = " ".join(render_argv(spec))
        # Assert
        assert "StrictHostKeyChecking=no" in joined

    def test_overridden_default_not_also_emitted(self):
        # Arrange
        spec = TunnelSpec(
            direction="forward",
            listen=Endpoint("127.0.0.1", 4000),
            target=Endpoint("node", 4000),
            via="spartan",
            ssh_opts={"StrictHostKeyChecking": "no"},
        )
        # Act
        joined = " ".join(render_argv(spec))
        # Assert
        assert "StrictHostKeyChecking=accept-new" not in joined

    def test_extra_argv_is_included(self):
        # Arrange
        spec = TunnelSpec(
            direction="forward",
            listen=Endpoint("127.0.0.1", 4000),
            target=Endpoint("node", 4000),
            via="spartan",
            extra_argv=("-4",),
        )
        # Act
        argv = render_argv(spec)
        # Assert
        assert "-4" in argv

    def test_extra_argv_precedes_destination(self):
        # Arrange
        spec = TunnelSpec(
            direction="forward",
            listen=Endpoint("127.0.0.1", 4000),
            target=Endpoint("node", 4000),
            via="spartan",
            extra_argv=("-4",),
        )
        # Act
        argv = render_argv(spec)
        # Assert
        assert argv.index("-4") < len(argv) - 1


class TestValidation:
    def test_rejects_unknown_direction(self):
        # Arrange
        kwargs = dict(
            direction="sideways",
            listen=Endpoint("127.0.0.1", 4000),
            target=Endpoint("node", 4000),
            via="spartan",
        )
        # Act
        ctx = pytest.raises(ValueError, match="direction")
        # Assert
        with ctx:
            TunnelSpec(**kwargs)

    def test_rejects_missing_via(self):
        # Arrange
        kwargs = dict(
            direction="forward",
            listen=Endpoint("127.0.0.1", 4000),
            target=Endpoint("node", 4000),
            via="",
        )
        # Act
        ctx = pytest.raises(ValueError, match="via")
        # Assert
        with ctx:
            TunnelSpec(**kwargs)


class TestFromDict:
    def test_from_dict_matches_constructed_spec(self):
        # Arrange
        d = {
            "direction": "forward",
            "listen": {"host": "127.0.0.1", "port": 4000},
            "target": {"host": "spartan-gpu-a017", "port": 4000},
            "via": "spartan",
        }
        # Act
        argv = render_argv(TunnelSpec.from_dict(d))
        # Assert
        assert argv == render_argv(_qwen_forward())

    def test_from_dict_missing_key_raises(self):
        # Arrange
        d = {
            "direction": "forward",
            "listen": {"host": "127.0.0.1", "port": 4000},
            "via": "spartan",
        }
        # Act
        ctx = pytest.raises(ValueError, match="target")
        # Assert
        with ctx:
            TunnelSpec.from_dict(d)

    def test_endpoint_from_host_port_sequence(self):
        # Arrange
        seq = ["h", 22]
        # Act
        ep = Endpoint.from_obj(seq)
        # Assert
        assert ep == Endpoint("h", 22)

    def test_endpoint_from_port_only_sequence(self):
        # Arrange
        seq = [9090]
        # Act
        ep = Endpoint.from_obj(seq)
        # Assert
        assert ep == Endpoint("", 9090)


class TestRenderCommand:
    def test_command_reparses_to_argv(self):
        # Arrange
        spec = _qwen_forward()
        # Act
        cmd = render_command(spec)
        # Assert
        assert shlex.split(cmd) == render_argv(spec)

    def test_command_is_single_line(self):
        # Arrange
        spec = _qwen_forward()
        # Act
        cmd = render_command(spec)
        # Assert
        assert "\n" not in cmd

    def test_default_opts_are_stable_set(self):
        # Arrange
        expected = {
            "ExitOnForwardFailure",
            "ServerAliveInterval",
            "ServerAliveCountMax",
            "StrictHostKeyChecking",
        }
        # Act
        keys = set(DEFAULT_SSH_OPTS)
        # Assert
        assert keys == expected


# EOF
