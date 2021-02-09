# ndn-python-svs: State Vector Sync NDN Python library

This python library implements the State Vector Sync (SVS) protocol to synchronise states between multiple clients over NDN for distributed realtime applications that is originally implemented and designed in c++ [here](https://github.com/named-data/ndn-svs).

**This is NOT an official implementation and consider 'experimental'**.

ndn-python-svs uses the [python-ndn](https://github.com/named-data/python-ndn) library for it's implementation.

## Installation

### Prerequisites

* [python-ndn](https://python-ndn.readthedocs.io/en/latest/src/installation.html)

* [nfd](https://named-data.net/doc/NFD/0.5.0/INSTALL.html)

### Examples

To try out the chat demo application, follow the below steps.

To create a chat client, simply run this in the home directory:
```
python3 examples/chat_node.py -n NODE_NAME [-h] [-gp GROUP_PREFIX]
```
You may create as many of these as possible and all clients will sync up using SVS.


Before you run the program, you must register the group prefix as multi-cast (even if you did not specifically define the group prefix):
```
nfdc strategy set <group-prefix> /localhost/nfd/strategy/multicast/%FD%03
```
The default group prefix is ['/svs'] for our examples.
More on setting different strategies (like mutli-cast) for different prefixes can be found [here](https://named-data.net/doc/NFD/current/manpages/nfdc-strategy.html).


## License and Authors

ndn-python-svs is an open source project that is licensed. See [`LICENSE.md`](LICENSE.md) for more information.

Please note: This is only a reimplementation in python and does not claim any credit towards the actual design of SVS.

The Names of all authors associated with this reimplementation project are below:

  * *Justin Presley*