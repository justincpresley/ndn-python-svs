import sys
import time
import asyncio as aio
import threading
from ndn.app import NDNApp
from typing import NamedTuple
from ndn.encoding import Component, Name
from enum import Enum
from ndn.encoding import *
from operator import lt, gt

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

def compare(string1, string2, less=True):
    op = lt if less else gt
    for char1, char2 in zip(string1, string2):
        ordinal1, ordinal2 = ord(char1), ord(char1)
        if ordinal1 == ordinal2:
            continue
        else:
            return op(ordinal1, ordinal2)
    return op(len(string1), len(string2))

def main():
    sv = StateVector()
    sv.set("c", 5)
    sv.set("a", 6)
    sv.set("b", 10)
    sv.set("z", 15)
    sv.set("x", 5225)

    print(sv.to_str())
    print(sv.encode())

if __name__ == "__main__":
    sys.exit(main())
