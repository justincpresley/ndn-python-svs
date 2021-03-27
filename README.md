---

# ndn-python-svs: State Vector Sync NDN Python library

This python library implements the [State Vector Sync (SVS) protocol](https://named-data.github.io/StateVectorSync/) to synchronise states between multiple clients over NDN for distributed realtime applications.

> This is an official implementation but considered 'experimental'. If there are any concerns or suggestions, please create [a new issue](https://github.com/justincpresley/ndn-python-svs/issues).

ndn-python-svs uses the [python-ndn](https://github.com/named-data/python-ndn) library for it's ndn client implementation.

---

## Installation

### Prerequisites

* [python-ndn](https://python-ndn.readthedocs.io/en/latest/src/installation.html) and [ndn-python-repo](https://ndn-python-repo.readthedocs.io/en/latest/src/install.html)

* [nfd](https://named-data.net/doc/NFD/0.5.0/INSTALL.html)

### From Pip

Download the python pip library [ndn-svs](https://pypi.org/project/ndn-svs/)

To import, everything is defined under `ndn.svs`. For example:
```
from ndn.svs import SVSyncShared
```

### From Source

Clone or Fork the github repository [ndn-python-svs](https://github.com/justincpresley/ndn-python-svs)

### Examples

To try out the chat demo application from source, follow the below steps.

To create a chat client, simply run this in the home directory of the repo:
```
python3 examples/chat_node.py -n NODE_NAME [-gp GROUP_PREFIX] [-h]
```
You may create as many of these as possible and all clients will sync up using SVS.

## Usage

### Group Prefix Strategy

Before you run the program, you must register the group prefix as multi-cast (even if you did not specifically define the group prefix):
```
nfdc strategy set <group-prefix> /localhost/nfd/strategy/multicast/%FD%03
```
The default (unless specified) **group prefix** is `/svs` for any build-in examples.

[More on setting different strategies (like mutli-cast) for prefixes.](https://named-data.net/doc/NFD/current/manpages/nfdc-strategy.html)

### API

The API is defined [here](https://named-data.github.io/StateVectorSync/API.html). In addition though, you may add `_Thread` to the end of any SVSync class to push SVS to a thread (SVSync normally runs on the current thread and requires a non-blocking program). The thread classes are derived from `threading.Thread` and use the same arguments as the normal classes. However, instead of passing the NDNApp as the first argument, you pass the face and keychain at the end of the parameters. Please call `wait()` after `start()` to allow the thread to fully intalize SVS. Also refer to the thread example for defining the missing data callback function. Otherwise, the thread class acts just the same as the normal class.

To make a new thread class based on a new SVS class from the SVSyncBase, make a new thread class derived from the SVSyncBase_Thread. In this new created class, you must define this function `async def function(self) -> None:`. Simply set `self.svs` to the new SVSync class.

---

## License and Authors

ndn-python-svs is an open source project that is licensed. See [`LICENSE.md`](https://github.com/justincpresley/ndn-python-svs/blob/master/LICENSE.md) for more information.

Please note: This is only a implementation in python and does not claim any credit towards the [actual design of SVS](https://named-data.github.io/StateVectorSync/).

The Names of all authors associated with this implementation project are below:

  * *Justin C Presley* (justincpresley)

Special Mentions:

  * *Xinyu Ma* (zjkmxy) helped formed the TLV structure used in SVS

---
