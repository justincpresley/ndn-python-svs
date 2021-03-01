import sys
sys.path.insert(0,'.')
from svs.state_vector import StateVector

def main() -> int:
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

    assert sv1.encode() == sv2.encode()
    assert sv1.to_str() == sv2.to_str()

    sv1.set("c", 10)
    assert sv1.to_str() != sv2.to_str()
    assert sv1.get("c") == 10
    sv1.set("c", 5)

    component = sv1.to_component()

    svc = StateVector(component)
    assert sv1.to_str() == svc.to_str()

if __name__ == "__main__":
    sys.exit(main())
