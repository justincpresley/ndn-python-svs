from collections import OrderedDict

class VersionVector:
    def __init__(self):
        self.m_map = OrderedDict()
    def set(NodeID nid, SeqNo seqNo): # returns seqNo as well
        self.m_map[nid] = seqNo
        return seqNo
    def get(NodeID nid): # seqNo returned
        return self.m_map[nid] if nid in self.m_map.keys() else 0
    def has(NodeID nid): # bool value
        return ( nid in self.m_map.keys() )
    def begin(): # returns only nid
        return next(iter(self.m_map))
    def end(): # returns only nid
        return next(reversed(self.m_map))
    def toStr():
        pass
    def encode():
        pass

  #VersionVector() = default;
  #VersionVector(const VersionVector&) = default;
  #VersionVector(const ndn::Block& encoded);
