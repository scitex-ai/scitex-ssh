#!/usr/bin/env python3
"""MCP server for scitex-ssh.

All tools delegate to the Python API (which delegates to shell scripts).
"""

from fastmcp import FastMCP


def create_server():
    """Create and configure the MCP server."""
    mcp = FastMCP("scitex-ssh")

    @mcp.tool()
    def tunnel_setup(
        port: int,
        bastion_server: str | None = None,
        secret_key_path: str | None = None,
    ) -> dict:
        """Install an `autossh`-backed `autossh-tunnel-<port>.service` systemd unit that opens a reverse SSH tunnel (local → bastion:port) and auto-reconnects on drop. One call replaces writing the unit file, enabling it, starting it, and testing reconnect. Drop-in replacement for hand-crafted `autossh -M 0 -NR port:localhost:22 user@host`, `/etc/systemd/system/autossh-tunnel-*.service` files, `sshuttle`, and `tmux` + `ssh -R` reconnect loops. Use whenever the user asks to "set up a reverse tunnel", "expose this machine through a bastion", "open port X on the jump host", "autossh systemd service for port X", "make this NAT-ed box reachable", or mentions bastion, jump host, HPC login node, NAT traversal.

        Parameters
        ----------
        port : int
            The remote port to forward (e.g. 2222).
        bastion_server : str, optional
            The bastion/relay server (e.g. user@bastion.example.com).
            Falls back to SCITEX_SSH_BASTION_SERVER env var.
        secret_key_path : str, optional
            Path to the SSH private key.
            Falls back to SCITEX_SSH_SECRET_KEY_PATH env var.

        Returns
        -------
        dict
            Result with success, stdout, stderr keys.
        """
        import scitex_ssh

        return scitex_ssh.setup(port, bastion_server, secret_key_path)

    @mcp.tool()
    def tunnel_status(port: int | None = None) -> dict:
        """Report live state of autossh reverse-tunnel systemd units — active/inactive, PID, restart count, last journal lines — for one specific port or every installed tunnel. Drop-in replacement for `systemctl status autossh-tunnel-<port>.service` + `journalctl -u autossh-tunnel-*`. Use when the user asks "is my tunnel up?", "why can't I reach port 2222?", "list all reverse tunnels", "check tunnel health", or is debugging a dropped connection.

        Parameters
        ----------
        port : int, optional
            Specific port to check. If None, shows all tunnels.

        Returns
        -------
        dict
            Result with success, stdout, stderr keys.
        """
        import scitex_ssh

        return scitex_ssh.status(port)

    @mcp.tool()
    def tunnel_remove(port: int) -> dict:
        """Tear down an autossh reverse-tunnel unit — stop + disable + delete `autossh-tunnel-<port>.service` + `systemctl daemon-reload`. Drop-in replacement for running `systemctl stop/disable` + `rm /etc/systemd/system/autossh-tunnel-<port>.service` + `daemon-reload` by hand. Use when the user asks to "remove the tunnel", "delete reverse tunnel on port X", "stop autossh", "decommission this tunnel", or is cleaning up old bastion routes.

        Parameters
        ----------
        port : int
            The port of the tunnel to remove.

        Returns
        -------
        dict
            Result with success, stdout, stderr keys.
        """
        import scitex_ssh

        return scitex_ssh.remove(port)

    return mcp


# EOF
