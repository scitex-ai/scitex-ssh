"""scitex-ssh quickstart: query tunnel availability and version (no SSH side effects).

Usage
-----
    python quickstart.py

Prints the tunnel availability flag, package version, and verifies that the
public setup/remove/status callables are exposed. Performs no SSH side effects,
so it is safe to run in any environment.
"""

import logging

import scitex_ssh

logger = logging.getLogger(__name__)


def main():
    # 1. AVAILABLE flag — True when ssh/autossh are usable on this host.
    logger.info("AVAILABLE: %s", scitex_ssh.AVAILABLE)
    assert isinstance(scitex_ssh.AVAILABLE, bool)

    # 2. get_version returns the installed package version string.
    v = scitex_ssh.get_version()
    logger.info("version: %s", v)
    assert isinstance(v, str) and v.count(".") >= 2

    # 3. Public API surface includes setup/remove/status callables.
    for fn in ("setup", "remove", "status"):
        assert callable(getattr(scitex_ssh, fn)), fn
    logger.info("setup/remove/status are callables")

    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    main()
