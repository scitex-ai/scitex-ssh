# Changelog

All notable changes to `scitex-ssh` are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.1.0] - 2026-07-03

### Added

- `sync_dir()` primitive: one-way rsync-over-ssh directory sync
  (`rsync -a --partial`) with caller-supplied exclude globs, optional
  `--delete`, extra rsync flags, and `ssh_opts` wired via `-e`.
  Policy-free by design — callers own excludes and any post-sync step.
  Exposed as `scitex-ssh sync SRC DEST` (push/pull inferred from which
  side is `HOST:PATH`). Enables cross-machine sync of per-user dirs such
  as `~/.scitex/scholar/library` without shipping a live sqlite index.
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
