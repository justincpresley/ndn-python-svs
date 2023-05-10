#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs
#    @Documentation: https://ndn-python-svs.readthedocs.io

# Basic Libraries
from typing import List
import struct
# NDN Imports
from ndn.encoding import Component, TlvModel, BytesField, UintField, RepeatedField, ModelField, NameField
from ndn.encoding.name import Name
from ndn.encoding import get_tl_num_size, write_tl_num, parse_tl_num
# Custom Imports
from .tlv import SVSyncTlvTypes

# Class Type: an enumeration struct
# Class Purpose:
#   to hold info about a singular node within the vector.
class StateVectorComponentModel(TlvModel):
    nid = NameField()
    seqno = UintField(SVSyncTlvTypes.VECTOR_VALUE.value)

class StateVectorListModel(TlvModel):
    values = RepeatedField(ModelField(SVSyncTlvTypes.VECTOR_KEY.value, StateVectorComponentModel))

# Class Type: an custom tlv model class
# Class Purpose:
#   to contain all the info of a state vector.
class StateVectorModel(TlvModel):
    value = ModelField(SVSyncTlvTypes.VECTOR.value, StateVectorListModel)

# Class Type: an API class
# Class Purpose:
#   to allow an easier time to interact with the StateVectorModel class.
class StateVector:
    def __init__(self, component:Component=None) -> None:
        if component:
            self.vector = StateVectorModel.parse(component)
        else:
            self.vector = StateVectorModel()
            self.vector.value = StateVectorListModel()
            self.vector.value.values = []
    def set(self, nid:str, seqno:int) -> None:
        sort = True if not self.has(nid) else False
        nid = Name.from_str(nid)
        if sort:
            svc = StateVectorComponentModel()
            svc.seqno = seqno
            svc.nid = nid
            index = len(self.vector.value.values)
            for i, item in enumerate(self.vector.value.values):
                if self.vector.value.values[i].nid > nid:
                    index = i
                    break
            self.vector.value.values.insert(index, svc)
        else:
            for i in self.vector.value.values:
                if i.nid == nid:
                    i.seqno = seqno
                    return
    def get(self, nid:str) -> int:
        nid = Name.from_str(nid)
        for i in self.vector.value.values:
            if i.nid == nid:
                return i.seqno
        return 0
    def has(self, nid:str) -> bool:
        return ( nid in self.keys() )
    def to_str(self) -> str:
        stream = ""
        for i in self.vector.value.values:
            stream = stream + Name.to_str(i.nid) + ":" + str(i.seqno) + " "
        return stream.rstrip()
    def encode(self) -> bytes:
        return self.vector.encode()
    def keys(self) -> List[str]:
        return [Name.to_str(i.nid) for i in self.vector.value.values]
    def to_component(self) -> Component:
        return self.encode()