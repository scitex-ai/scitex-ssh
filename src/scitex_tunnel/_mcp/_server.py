#!/usr/bin/env python3
"""MCP server for scitex-tunnel.

All tools delegate to the Python API (which delegates to shell scripts).
"""

from fastmcp import FastMCP


def create_server():
    """Create and configure the MCP server."""
    mcp = FastMCP("scitex-tunnel")

    @mcp.tool()
    def tunnel_setup(
        port: int,
        bastion_server: str | None = None,
        secret_key_path: str | None = None,
    ) -> dict:
        """Set up a persistent SSH reverse tunnel.

        Parameters
        ----------
        port : int
            The remote port to forward (e.g. 2222).
        bastion_server : str, optional
            The bastion/relay server (e.g. user@bastion.example.com).
            Falls back to SCITEX_TUNNEL_BASTION_SERVER env var.
        secret_key_path : str, optional
            Path to the SSH private key.
            Falls back to SCITEX_TUNNEL_SECRET_KEY_PATH env var.

        Returns
        -------
        dict
            Result with success, stdout, stderr keys.
        """
        import scitex_tunnel

        return scitex_tunnel.setup(port, bastion_server, secret_key_path)

    @mcp.tool()
    def tunnel_status(port: int | None = None) -> dict:
        """Check status of SSH reverse tunnels.

        Parameters
        ----------
        port : int, optional
            Specific port to check. If None, shows all tunnels.

        Returns
        -------
        dict
            Result with success, stdout, stderr keys.
        """
        import scitex_tunnel

        return scitex_tunnel.status(port)

    @mcp.tool()
    def tunnel_remove(port: int) -> dict:
        """Remove a persistent SSH reverse tunnel.

        Parameters
        ----------
        port : int
            The port of the tunnel to remove.

        Returns
        -------
        dict
            Result with success, stdout, stderr keys.
        """
        import scitex_tunnel

        return scitex_tunnel.remove(port)

    return mcp


# EOF
