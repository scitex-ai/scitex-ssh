# Changelog

All notable changes to `scitex-ssh` are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.2.0] - 2026-07-12

### Added

- `probe_remote()` primitive: single-ssh-round-trip reachability +
  capability preflight (`command -v <name>` checks), policy-free like
  `sync_dir`. Exposed as `scitex-ssh probe HOST [--requires TOOL ...]
  [--json]`.
- `tunnel render-argv` — pure `ssh -L`/`-R` argv renderer (no side
  effects), for callers that want the exact tunnel command without
  invoking it.
- `tunnel forward --discovery` — discovery-driven forward tunnel setup.

### Changed

- **`exec_remote`/`probe_remote`/`copy_to`/`copy_from`/`sync_dir` now
  default every ssh/scp/rsync invocation to `-o ControlMaster=no -o
  ControlPath=none -o ClearAllForwardings=yes`**, unless the caller's
  `ssh_opts` already sets `ControlMaster`/`ControlPath` explicitly.
  These are one-shot automation calls, not interactive sessions, and
  should not silently inherit a host's interactive-session baggage:
  ControlMaster multiplexing assumes a writable `~/.ssh/` for the
  control socket (containers often mount it read-only for *new*
  sockets while reusing pre-existing ones, which made failures look
  host-specific when they were really just "which socket already
  existed"), and `Local`/`RemoteForward` entries in `~/.ssh/config` are
  typically scoped to one human's session — concurrent automated
  callers hitting the same alias will port-conflict on fixed ports
  regardless of ControlMaster. A caller who deliberately wants either
  can still opt in via their own `ssh_opts`. `attach()` (interactive by
  design) and the persistent autossh tunnel daemon are unaffected.
  `sync_dir` now always passes `-e` to rsync (previously omitted when
  `ssh_opts` was empty).
- Reverse autossh tunnel unit hardened against a dead-forward-after-blip
  failure mode: adds `ServerAliveInterval`/`ServerAliveCountMax`/
  `ExitOnForwardFailure` so a network blip doesn't leave the forward
  silently dead while systemd reports the unit as running.

## [1.1.0] - 2026-07-03

### Added

- `sync_dir()` primitive: one-way rsync-over-ssh directory sync
  (`rsync -a --partial`) with caller-supplied exclude globs, optional
  `--delete`, extra rsync flags, and `ssh_opts` wired via `-e`.
  Policy-free by design — callers own excludes and any post-sync step.
  Exposed as `scitex-ssh sync SRC DEST` (push/pull inferred from which
  side is `HOST:PATH`). Enables cross-machine sync of per-user dirs such
  as `~/.scitex/scholar/library` without shipping a live index database.
- `_allowlist`: honour the `$SCITEX_SSH_CONFIG` environment variable as a
  config-path override (resolved per-call via the new `config_path()`),
  matching the precedence chain already advertised in the CLI `--help` and
  the skills docs. Closes a doc-vs-code gap.

### Changed

- Test suite de-mocked end to end (no `unittest.mock` / `patch` /
  `MagicMock` / `monkeypatch`): ssh/scp/bash/systemctl collaborators are
  exercised through real fake binaries on `$PATH`, the allowlist through a
  real config file, env-var fallbacks through a save/restore fixture. Tests
  now satisfy the test-quality rules (one assertion per test, AAA markers,
  descriptive names). Shared `subprocess_shim` / `env_save_restore` /
  `allow_tunnels` / `deny_tunnels` fixtures live in `tests/conftest.py`.

## [1.0.0]

- Initial CHANGELOG entry — see git log for prior history.
