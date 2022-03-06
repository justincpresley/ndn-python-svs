Enhancements
============

There are many enhancements that have been made to ndn-python-svs that deviate it from the traditional specification.
A full list is below.

    * **Unique Types**: tons of types to suit an environment specifically, check types in spec for more info.
    * **Thread versions**: sometimes a program can not release control to the async queue like for input.
    * **State Table**: be sure to get the latest data entry updates via ordered entries.
    * **Node Balancer**: a node did not get all the data from the sync interests? Request it!
    * **Sliding Window**: asynchronously send interests when balancing a node's state or fetching data.