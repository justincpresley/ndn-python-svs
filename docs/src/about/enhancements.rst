Enhancements
============

There are many enhancements that have been made to ndn-python-svs that deviate it from the traditional specification.
A full list is below.

    * **Shared type of SVSync**: cache other people's data to help spread their data!
    * **Thread versions of all types of SVSync**: sometimes a program can not release control to the async queue like for input.
    * **State Table of ordered latest data entries**: be sure to get the latest data entry updates.
    * **Node Balancer**: a node did not get all the data from the sync interests? Request it!
    * **Sliding Window**: asynchronously send interests when balancing a node's state or fetching data.