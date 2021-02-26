import sys
import time
import asyncio as aio
import threading
from ndn.app import NDNApp
from typing import NamedTuple
from ndn.encoding import Component, Name
from enum import Enum
from ndn.encoding import *

sys.path.insert(0,'.')
from svs.state_vector import StateVector

"""
StateVector = VERSION-VECTOR-TYPE TLV-LENGTH
              *StateVectorComponent

StateVectorComponent = NodeID SeqNo
NodeID = VERSION-VECTOR-KEY-TYPE TLV-LENGTH *OCTET
SeqNo = VERSION-VECTOR-VALUE-TYPE TLV-LENGTH NonNegativeInteger
VERSION-VECTOR-TYPE = 201
VERSION-VECTOR-KEY-TYPE = 202
VERSION-VECTOR-VALUE-TYPE = 203
"""

"""
StateVector = *StateVectorComponent
StateVectorComponent = VERSION-VECTOR-COMPONENT-TYPE TLV-LENGTH NodeID SeqNo
NodeID = VERSION-VECTOR-KEY-TYPE TLV-LENGTH *OCTET
SeqNo = VERSION-VECTOR-VALUE-TYPE TLV-LENGTH NonNegativeInteger
VERSION-VECTOR-COMPONENT-TYPE = 201
VERSION-VECTOR-KEY-TYPE = 202
VERSION-VECTOR-VALUE-TYPE = 203

"""

def main():
    sv = StateVector()
    print(sv.to_str())

    name = Name.from_str("/svs") + [Component.from_bytes(sv.encode())]
    print( Name.to_str(name) )
    sv = StateVector(name[-1])
    print(sv.to_str())
    print(sv.encode())

if __name__ == "__main__":
    sys.exit(main())
