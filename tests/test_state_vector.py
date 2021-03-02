import sys
import pytest
sys.path.insert(0,'.')
from svs.state_vector import StateVector

def state_vector_ordering():
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

    return sv1.to_str() == sv2.to_str()

def state_vector_component():
    sv = StateVector()
    sv.set("c", 5)
    sv.set("a", 6)
    sv.set("B", 10)
    sv.set("z", 15)
    sv.set("x", 5225)

    return StateVector(sv.to_component()).encode() == sv.encode()

def test_state_vector_ordering():
    assert state_vector_ordering() == True

def test_state_vector_component():
    assert state_vector_component() == True
