Quickstart
==========

Setup a Tunnel
--------------

.. code-block:: bash

    scitex-tunnel setup -p 2222 -b user@bastion.example.com -s ~/.ssh/id_rsa

This creates a systemd service that maintains a persistent reverse SSH tunnel.

Check Status
------------

.. code-block:: bash

    scitex-tunnel status
    scitex-tunnel status -p 2222

Remove a Tunnel
---------------

.. code-block:: bash

    scitex-tunnel remove -p 2222

Python API
----------

.. code-block:: python

    import scitex_tunnel

    # Setup
    result = scitex_tunnel.setup(2222, "user@bastion.example.com", "~/.ssh/id_rsa")
    print(result["success"])  # True

    # Status
    result = scitex_tunnel.status(port=2222)

    # Remove
    result = scitex_tunnel.remove(2222)
