# Contributing to SciTeX Tunnel

Thank you for your interest in contributing to SciTeX. This guide covers the
process for reporting issues, suggesting features, and submitting code.

## Contributor License Agreement

Before your first contribution can be merged, you must agree to the
[SciTeX CLA](CLA.md). This is a one-time process. The CLA ensures that:

- You retain copyright of your work.
- The project can continue to offer dual licensing (free for researchers,
  commercial for enterprises).

See [CLA.md](CLA.md) for full details.

## Reporting Issues

- Search existing issues before opening a new one.
- Include a minimal reproducible example when reporting bugs.
- Specify your Python version, OS, and scitex-tunnel version.

## Development Setup

Clone the repo, then install in dev mode with pip.

## Branch Workflow

- main: stable releases only. Do not push directly.
- develop: integration branch. PRs target here.
- Feature branches: create from develop, name as feature/description.

## Code Style

- Follow existing conventions in the codebase.
- Use underscore prefix for internal/private modules and functions.
- Keep files under 512 lines.
- Run the full test suite before submitting.

## Pull Request Process

1. Ensure your branch is up to date with develop.
2. Write tests for new functionality.
3. Run the test suite and confirm all tests pass.
4. Open a PR targeting develop with a clear description.
5. The CLA bot will check your CLA status on your first PR.

## License

By contributing, you agree to the terms of the CLA, which includes
licensing under AGPL-3.0 (see LICENSE) and the dual-licensing
provisions described therein.
