#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs/

# Basic Libraries
import sys
# NDN Imports
from ndn.encoding import Component, Name
# Custom Imports
sys.path.insert(0,'.')
from src.ndn.svs.state_vector import StateVector, StateVectorModelTypes

# File Type: pytest Testing
# Testing Classes: StateVector
# Testing Purposes:
#   to ensure Component compatibility.
#   to ensure defined SVS protocol compatibility.
#   to test that all API functions from StateVector work as intended.

def test_state_vector_ordering():
    sv1 = StateVector()
    sv1.set("c", 5)
    sv1.set("a", 6)
    sv1.set("B", 10)

    assert sv1.to_str() == "B:10 a:6 c:5"

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
    assert sv.get("c") == None

def test_state_vector_decode():
    # hard coded bytes of component vector based on SVS protocol
    enc_sv = b'\xCA\x03\x6F\x6E\x65\xCB\x01\x01\xCA\x03\x74\x77\x6F\xCB\x01\x02'
    enc_sv = Component.from_bytes(enc_sv, StateVectorModelTypes.VECTOR.value)

    sv = StateVector(enc_sv)
    assert sv.get("one") == 1
    assert sv.get("two") == 2

def test_state_vector_encode():
    sv = StateVector(None)
    sv.set("one", 1)
    sv.set("two", 2)

    enc_sv = sv.encode()
    # does this state vector's byte value equal a hard coded byte value based on the state vector's protocol
    assert enc_sv == b'\xc9\x10\xca\x03two\xcb\x01\x02\xca\x03one\xcb\x01\x01'

def test_state_vector_component_functionality():
    sv = StateVector()
    sv.set("one", 1)
    sv.set("two", 2)

    # does the state vector component act as a compoent in a name
    name = Name.from_str("/state_vector/test") + [sv.to_component()]
    assert name == Name.from_str(Name.to_str(name))

def test_state_vector_total():
    sv = StateVector(None)
    sv.set("c", 5)
    sv.set("a", 6)
    sv.set("B", 10)
    sv.set("z", 15)
    sv.set("x", 5225)

    assert sv.total() == 5261

def test_state_vector_partition():
    sv = StateVector(None)
    sv.set("c", 5)
    sv.set("a", 6)
    sv.set("B", 10)
    sv.set("z", 15)
    sv.set("x", 5225)

    nsv = StateVector(sv.partition(0,0))
    osv = StateVector(None)

    assert osv.to_str() == nsv.to_str()