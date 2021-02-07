import sys
from collections import OrderedDict

class VersionVector:
    def __init__(self):
        self.m_map = OrderedDict()
    def set(self,nid,seqNo): # returns seqNo as well
        self.m_map[nid] = seqNo
        return seqNo
    def get(self,nid): # seqNo returned
        return self.m_map[nid] if nid in self.m_map.keys() else 0
    def has(self,nid): # bool value
        return ( nid in self.m_map.keys() )
    def begin(self): # returns only nid
        return next(iter(self.m_map))
    def end(self): # returns only nid
        return next(reversed(self.m_map))
    def to_str(self):
        stream = ""
        for key,value in self.m_map.items():
            stream = stream + key + ":" + str(value) + " "
        return stream.rstrip()
    def encode(self):
        return self.to_str().encode()

def main() -> int:
    vv = VersionVector()
    vv.set("node1", 1)
    vv.set("node2", 3)
    print("|" + vv.to_str() + "|")

if __name__ == "__main__":
    sys.exit(main())
