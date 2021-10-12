Configuration
=============

Group Prefix Strategy
---------------------

Before you run the program (assuming you have NFD running), you must register the group prefix as multi-cast (even if you did not specifically define the group prefix):

.. code-block:: bash

    $ nfdc strategy set <group-prefix> /localhost/nfd/strategy/multicast/%FD%04

The default (unless specified) **group prefix** is `/svs` for any build-in examples.

More on setting different strategies (like mutli-cast) for prefixes found here_.


.. _here: https://named-data.net/doc/NFD/current/manpages/nfdc-strategy.html