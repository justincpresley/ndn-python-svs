import sys
import pytest
sys.path.insert(0,'.')
from src.ndn.svs.state_vector import StateVector

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