"""
    @Author: Justin C Presley
    @Author-Email: justincpresley@gmail.com
    @Project: NDN State Vector Sync Protocol
    @Source-Code: https://github.com/justincpresley/ndn-python-svs
    @Pip-Library: https://pypi.org/project/ndn-svs/
"""

# Basic Libraries
import sys
import pytest
# NDN Imports
from ndn.encoding import Component, Name
# Custom Imports
sys.path.insert(0,'.')
from src.ndn.svs.state_vector import StateVector, StateVectorModelTypes

def test_state_vector_ordering():
    sv1 = StateVector()
    sv1.set("c", 5)
    sv1.set("a", 6)
    sv1.set("B", 10)
    sv1.set("z", 15)
    sv1.set("x", 5225)

    sv2 = StateVector()
    sv2.set("z", 15)
    sv2.set("x", 5225)
    sv2.set("a", 6)
    sv2.set("B", 10)
    sv2.set("c", 5)

    assert sv1.to_str() == sv2.to_str()
    assert sv1.encode() == sv2.encode()

def test_state_vector_component():
    sv = StateVector()
    sv.set("c", 5)
    sv.set("a", 6)
    sv.set("B", 10)
    sv.set("z", 15)
    sv.set("x", 5225)

    svc = StateVector(sv.to_component())

    assert sv.to_str() == svc.to_str()
    assert sv.encode() == svc.encode()

def test_state_vector_get():
    sv = StateVector()
    sv.set("b", 5)
    sv.set("a", 6)

    assert sv.get("a") == 6
    assert sv.get("b") == 5

def test_state_vector_has():
    sv = StateVector()
    sv.set("b", 5)
    sv.set("a", 6)

    assert sv.has("a")
    assert sv.has("b")

def test_state_vector_set():
    sv = StateVector()
    sv.set("a", 10)
    sv.set("a", 100)

    assert sv.get("a") == 100


def test_state_vector_decode():
    # hard coded bytes of component vector based on SVS protocol
    enc_sv = b'\xCA\x03\x6F\x6E\x65\xCB\x01\x01\xCA\x03\x74\x77\x6F\xCB\x01\x02'
    enc_sv = Component.from_bytes(enc_sv, StateVectorModelTypes.VECTOR.value)

    sv = StateVector(enc_sv)
    assert sv.get("one") == 1
    assert sv.get("two") == 2


def test_state_vector_encode():
    sv = StateVector()
    sv.set("one", 1)
    sv.set("two", 2)

    enc_sv = sv.encode()
    # does this state vector's byte value equal a hard coded byte value based on the state vector's protocol
    assert enc_sv == b'\xC9\x10\xCA\x03\x6F\x6E\x65\xCB\x01\x01\xCA\x03\x74\x77\x6F\xCB\x01\x02' 

def test_state_vector_component_functionality():
    sv = StateVector()
    sv.set("one", 1)
    sv.set("two", 2)
    
    # does the state vector component act as a compoent in a name
    name = Name.from_str("/state_vector/test") + [sv.to_component()]
    assert name == Name.from_str(Name.to_str(name))
