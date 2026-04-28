"""scitex-ssh quickstart: query tunnel availability and version (no SSH side effects)."""

import scitex_ssh


def main():
    # 1. AVAILABLE flag — True when ssh/autossh are usable on this host.
    print("AVAILABLE:", scitex_ssh.AVAILABLE)
    assert isinstance(scitex_ssh.AVAILABLE, bool)

    # 2. get_version returns the installed package version string.
    v = scitex_ssh.get_version()
    print("version:", v)
    assert isinstance(v, str) and v.count(".") >= 2

    # 3. Public API surface includes setup/remove/status callables.
    for fn in ("setup", "remove", "status"):
        assert callable(getattr(scitex_ssh, fn)), fn
    print("setup/remove/status are callables")


if __name__ == "__main__":
    main()
