#!/usr/bin/env python3
"""Tests for scitex_ssh._tunnel_render — pure ssh tunnel argv construction.

No mocks: the renderer is a pure function of its spec, so every test asserts
directly on the rendered argv / command string.
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


class TestForwardRendering:
    def test_always_emits_dash_N_blocking(self):
        # -N is the supervisor contract: no remote command => ssh blocks.
        argv = render_argv(_qwen_forward())
        assert argv[0] == "ssh"
        assert "-N" in argv

    def test_forward_L_spec_shape(self):
        # Arrange
        spec = _qwen_forward()
        # Act
        argv = render_argv(spec)
        # Assert — -L local:target_host:target_port
        i = argv.index("-L")
        assert argv[i + 1] == "127.0.0.1:4000:spartan-gpu-a017:4000"

    def test_destination_host_is_last_and_is_via_not_jump(self):
        # The DESTINATION (via) must be the final arg; target_host resolves on
        # its network. A -J hop is NOT a substitute for a destination.
        argv = render_argv(_qwen_forward())
        assert argv[-1] == "spartan"
        assert "-J" not in argv

    def test_default_ssh_opts_present(self):
        argv = render_argv(_qwen_forward())
        joined = " ".join(argv)
        for key, val in DEFAULT_SSH_OPTS.items():
            assert f"{key}={val}" in joined

    def test_options_precede_destination(self):
        argv = render_argv(_qwen_forward())
        dest_idx = len(argv) - 1
        assert argv.index("-L") < dest_idx
        assert argv.index("-o") < dest_idx


class TestReverseRendering:
    def test_reverse_R_spec_shape(self):
        # Arrange — a persistent-style reverse tunnel: expose local 8080 on the
        # bastion's port 9090.
        spec = TunnelSpec(
            direction="reverse",
            listen=Endpoint("", 9090),
            target=Endpoint("127.0.0.1", 8080),
            via="bastion.example.com",
        )
        # Act
        argv = render_argv(spec)
        # Assert
        i = argv.index("-R")
        assert argv[i + 1] == "9090:127.0.0.1:8080"
        assert argv[-1] == "bastion.example.com"

    def test_reverse_with_bind_address(self):
        spec = TunnelSpec(
            direction="reverse",
            listen=Endpoint("0.0.0.0", 9090),
            target=Endpoint("127.0.0.1", 8080),
            via="bastion",
        )
        argv = render_argv(spec)
        i = argv.index("-R")
        assert argv[i + 1] == "0.0.0.0:9090:127.0.0.1:8080"


class TestOptionalFields:
    def test_jump_renders_proxyjump(self):
        spec = TunnelSpec(
            direction="forward",
            listen=Endpoint("127.0.0.1", 4000),
            target=Endpoint("node", 4000),
            via="spartan",
            jump="user@bastion:2222",
        )
        argv = render_argv(spec)
        j = argv.index("-J")
        assert argv[j + 1] == "user@bastion:2222"
        # via is still the destination
        assert argv[-1] == "spartan"

    def test_identity_and_via_user_and_port(self):
        spec = TunnelSpec(
            direction="forward",
            listen=Endpoint("127.0.0.1", 4000),
            target=Endpoint("node", 4000),
            via="spartan",
            via_user="ywatanabe",
            via_port=2222,
            identity="~/.ssh/id_ed25519",
        )
        argv = render_argv(spec)
        assert argv[-1] == "ywatanabe@spartan"
        assert "-p" in argv and argv[argv.index("-p") + 1] == "2222"
        assert "-i" in argv and argv[argv.index("-i") + 1] == "~/.ssh/id_ed25519"

    def test_caller_ssh_opts_override_defaults(self):
        spec = TunnelSpec(
            direction="forward",
            listen=Endpoint("127.0.0.1", 4000),
            target=Endpoint("node", 4000),
            via="spartan",
            ssh_opts={"StrictHostKeyChecking": "no", "Custom": "1"},
        )
        joined = " ".join(render_argv(spec))
        assert "StrictHostKeyChecking=no" in joined
        assert "StrictHostKeyChecking=accept-new" not in joined
        assert "Custom=1" in joined

    def test_extra_argv_before_destination(self):
        spec = TunnelSpec(
            direction="forward",
            listen=Endpoint("127.0.0.1", 4000),
            target=Endpoint("node", 4000),
            via="spartan",
            extra_argv=("-4",),
        )
        argv = render_argv(spec)
        assert "-4" in argv
        assert argv.index("-4") < len(argv) - 1


class TestValidation:
    def test_rejects_unknown_direction(self):
        with pytest.raises(ValueError, match="direction"):
            TunnelSpec(
                direction="sideways",
                listen=Endpoint("127.0.0.1", 4000),
                target=Endpoint("node", 4000),
                via="spartan",
            )

    def test_rejects_missing_via(self):
        with pytest.raises(ValueError, match="via"):
            TunnelSpec(
                direction="forward",
                listen=Endpoint("127.0.0.1", 4000),
                target=Endpoint("node", 4000),
                via="",
            )


class TestFromDict:
    def test_from_dict_roundtrips_qwen(self):
        d = {
            "direction": "forward",
            "listen": {"host": "127.0.0.1", "port": 4000},
            "target": {"host": "spartan-gpu-a017", "port": 4000},
            "via": "spartan",
        }
        spec = TunnelSpec.from_dict(d)
        assert render_argv(spec) == render_argv(_qwen_forward())

    def test_from_dict_missing_key_raises(self):
        with pytest.raises(ValueError, match="target"):
            TunnelSpec.from_dict(
                {
                    "direction": "forward",
                    "listen": {"host": "127.0.0.1", "port": 4000},
                    "via": "spartan",
                }
            )

    def test_endpoint_accepts_sequence_and_port_only(self):
        assert Endpoint.from_obj(["h", 22]) == Endpoint("h", 22)
        assert Endpoint.from_obj([9090]) == Endpoint("", 9090)


class TestRenderCommand:
    def test_command_is_shell_safe_and_reparses_to_argv(self):
        spec = _qwen_forward()
        cmd = render_command(spec)
        # shlex round-trip must reproduce the argv exactly (single safe line).
        assert shlex.split(cmd) == render_argv(spec)

    def test_command_is_single_line(self):
        assert "\n" not in render_command(_qwen_forward())


# EOF
