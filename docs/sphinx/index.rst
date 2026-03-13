.. SciTeX Tunnel documentation master file

SciTeX Tunnel - Persistent SSH Reverse Tunnel
==============================================

**SciTeX Tunnel** manages persistent SSH reverse tunnels for NAT traversal, powered by autossh and systemd. It provides three interfaces: Python API, CLI, and MCP server for AI agents.

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/scitex_tunnel

Key Features
------------

- **Persistent Tunnels**: autossh-based reverse SSH tunnels that auto-restart on failure
- **systemd Integration**: Each tunnel runs as a managed systemd service
- **Three Interfaces**: Python API, CLI, and MCP server for AI agents
- **Simple API**: Three operations - setup, status, remove

Quick Example
-------------

Python API:

.. code-block:: python

    import scitex_tunnel

    # Set up a tunnel
    result = scitex_tunnel.setup(2222, "user@bastion.example.com", "~/.ssh/id_rsa")

    # Check status
    result = scitex_tunnel.status()

    # Remove
    result = scitex_tunnel.remove(2222)

CLI:

.. code-block:: bash

    scitex-tunnel setup -p 2222 -b user@bastion.example.com -s ~/.ssh/id_rsa
    scitex-tunnel status
    scitex-tunnel remove -p 2222

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
