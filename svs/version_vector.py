# Basic Libraries
from collections import OrderedDict
from typing import List
# NDN Imports
from ndn.encoding import Component

class VersionVector:
    def __init__(self, component:Component=None) -> None:
        self.vector = OrderedDict()
        if component:
            try:
                res = bytes(Component.get_value(component)).decode().split(" ")
                for x in res:
                    temp = x.split(":")
                    self.set(temp[0],int(temp[1]))
            except IndexError:
                pass
    def set(self, nid:str, seqNo:int) -> None:
        sort = True if not self.has(nid) else False
        self.vector[nid] = seqNo
        if sort:
            self.vector = OrderedDict(sorted(self.vector.items()))
    def get(self, nid:str) -> int:
        return self.vector[nid] if self.has(nid) else 0
    def has(self, nid:str) -> bool:
        return ( nid in self.vector.keys() )
    def to_str(self) -> str:
        stream = ""
        for key,value in self.vector.items():
            stream = stream + key + ":" + str(value) + " "
        return stream.rstrip()
    def encode(self) -> bytes:
        return self.to_str().encode()
    def keys(self) -> List[str]:
        return list(self.vector.keys())