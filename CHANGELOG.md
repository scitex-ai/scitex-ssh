# Changelog

All notable changes to `scitex-ssh` are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

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
