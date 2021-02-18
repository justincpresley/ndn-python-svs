# Basic Libraries
from collections import OrderedDict
# NDN Imports
from ndn.encoding import Component

class VersionVector:
    def __init__(self, component=None):
        self.m_map = OrderedDict()
        if component:
            res = bytes(Component.get_value(component)).decode().split(" ")
            for x in res:
                temp = x.split(":")
                self.set(temp[0],int(temp[1]))
    def set(self,nid,seqNo): # returns seqNo as well
        sort = False
        if not self.has(nid):
            sort = True
        self.m_map[nid] = seqNo
        if sort:
            self.m_map = OrderedDict(sorted(self.m_map.items()))
    def get(self,nid): # seqNo returned
        return self.m_map[nid] if self.has(nid) else 0
    def has(self,nid): # bool value
        return ( nid in self.m_map.keys() )
    def to_str(self):
        stream = ""
        for key,value in self.m_map.items():
            stream = stream + key + ":" + str(value) + " "
        return stream.rstrip()
    def encode(self):
        return self.to_str().encode()
    def keys(self):
        return list(self.m_map.keys())