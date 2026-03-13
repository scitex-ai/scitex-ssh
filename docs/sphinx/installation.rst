Installation
============

From PyPI
---------

.. code-block:: bash

    pip install scitex-tunnel

Or as part of SciTeX:

.. code-block:: bash

    pip install scitex[tunnel]

Prerequisites
-------------

- ``autossh`` installed on the host machine (``sudo apt install autossh``)
- SSH key pair for authentication
- A bastion server with SSH access

Development
-----------

.. code-block:: bash

    pip install -e ".[dev]"
