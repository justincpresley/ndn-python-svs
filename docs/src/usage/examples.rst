Examples
========

For the basic example, we will be having all nodes fall under one NFD.
This means we can eliminate routing for a quick run.

**1. Edit NFD config to see things happen**

.. code-block:: bash

    cs_max_packets 0

**2. Start / Restart NFD**

**3. Configure Repo Prefix Strategy**

.. code-block:: bash

    $ nfdc strategy set /<repo-prefix>/group /localhost/nfd/strategy/multicast/%FD%04

**4. Run the following on 2 or more terminals.**

.. code-block:: bash

    $ cd ndn-python-svs # inside root directory
    $ python3 examples/chat.py -n <node-name> [-gp <group-prefix>] [-h]

- *group-prefix* : The registered-multicast group prefix for all under the SVS group. All should be ran with the same prefix. (example: /svs)
- *node_name* : A unique, per node, name. Always unique, create new on restart. (example: node1)

**5. Chat!**

You should be able to chat away! See how the chat room operates when a node is down or see how it handles lots of data.

**6. Investigate**

Now that you see the overview of what happens, take a closer look at the mechanisms behind the StateVectorSync Protocol!

Instead of ``examples/chat.py`` try ``examples/count.py``. This should be automatic (no input required) and will allow you
to see the insides of the StateVectorSync Protocol.