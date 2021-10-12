Enhancements
============

There are many enhancements that have been made to ndn-python-svs that deviate it from the traditional specification.
A full list is below.

    * Ability to Create a 'Shared' version of SVSync, cache other people's data to help spread their data!
    * Thread versions of All types of SVSync! Sometimes a program can not release control to the async queue like for input.
    * State Table, an ordered state vector according to latest entries.
    * Node Balancer, a node did not get all the data from the sync interests? Request it!