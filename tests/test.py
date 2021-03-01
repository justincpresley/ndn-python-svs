import sys
sys.path.insert(0,'.')
from svs.state_vector import StateVector

def main():
    sv = StateVector()
    sv.set("c", 5)
    sv.set("a", 6)
    sv.set("B", 10)
    sv.set("z", 15)
    sv.set("x", 5225)

    print(sv.to_str())
    print(sv.encode())

if __name__ == "__main__":
    sys.exit(main())
