#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs
#    @Documentation: https://ndn-python-svs.readthedocs.io

from __future__ import annotations

# Basic Libraries
from struct import unpack_from
from typing import List, Optional
# NDN Imports
from ndn.encoding import Component, TlvModel, BytesField, UintField
from ndn.encoding import get_tl_num_size, write_tl_num, parse_tl_num
# Custom Imports
from .tlv import SVSyncTlvTypes

# Class Type: a struct
# Class Purpose:
#   to hold info about a singular node within the vector.
class StateVectorComponentModel(TlvModel):
    nid = BytesField(SVSyncTlvTypes.VECTOR_ENTRY.value)
    seqno = UintField(SVSyncTlvTypes.SEQNO.value)

# Class Type: an custom tlv model class
# Class Purpose:
#   to contain all the info of a state vector.
class StateVectorModel:
    def __init__(self, value:List[StateVectorComponentModel]) -> None:
        self.value:List[StateVectorComponentModel] = value
    def encode(self) -> bytearray:
        component_wires = [v.encode() for v in self.value]
        length = sum(len(w) for w in component_wires)
        buf_len = length + get_tl_num_size(length) + get_tl_num_size(SVSyncTlvTypes.VECTOR.value)
        ret = bytearray(buf_len)
        pos = write_tl_num(SVSyncTlvTypes.VECTOR.value, ret)
        pos += write_tl_num(length, ret, pos)
        for w in component_wires:
            ret[pos:pos + len(w)] = w
            pos += len(w)
        return ret
    @staticmethod
    def parse(buf:Component) -> Optional[StateVectorModel]:
        # Verify the Type
        typ, pos = parse_tl_num(buf)
        if typ != SVSyncTlvTypes.VECTOR.value:
            return None
        # Check the length
        length, l = parse_tl_num(buf, pos)
        pos += l
        if pos + length != len(buf):
            return None
        # Decode components
        ret:StateVectorModel = StateVectorModel([])
        ret.value = []
        while pos < len(buf):
            # Entry ID
            typ, l = parse_tl_num(buf, pos)
            pos += l
            if typ != SVSyncTlvTypes.VECTOR_ENTRY.value:
                return None
            length, l = parse_tl_num(buf, pos)
            pos += l
            entry = buf[pos:pos + length]
            pos += length
            # Seqno
            typ, l = parse_tl_num(buf, pos)
            pos += l
            if typ != SVSyncTlvTypes.SEQNO.value:
                return None
            length, l = parse_tl_num(buf, pos)
            pos += l
            if length == 1:
                seqno = unpack_from('!B', buf, pos)[0]
            elif length == 2:
                seqno = unpack_from('!H', buf, pos)[0]
            elif length == 4:
                seqno = unpack_from('!I', buf, pos)[0]
            elif length == 8:
                seqno = unpack_from('!Q', buf, pos)[0]
            else:
                return None
            pos += length
            # Append the component
            comp:StateVectorComponentModel = StateVectorComponentModel()
            comp.nid = entry
            comp.seqno = seqno
            ret.value.append(comp)
        return ret

# Class Type: a class
# Class Purpose:
#   to allow an easier time to interact with the StateVectorModel class.
class StateVector:
    def __init__(self, component:Component=None) -> None:
        self.vector:StateVectorModel = StateVectorModel([])
        self.wire:Optional[bytes] = None
        if component:
            temp_vector:Optional[StateVectorModel] = StateVectorModel.parse(component)
            if temp_vector != None:
                for i in temp_vector.value:
                    self.set(bytes(i.nid).decode(), i.seqno, True)
    def set(self, nid:str, seqno:int, oldData:bool=False) -> None:
        self.wire = None
        index:Optional[int] = self.index(nid)
        if index == None:
            svc:StateVectorComponentModel = StateVectorComponentModel()
            svc.seqno = seqno
            svc.nid = nid.encode()
            if not oldData:
                self.vector.value.insert(0,svc)
            else:
                self.vector.value.append(svc)
        else:
            self.vector.value[index].seqno = seqno
            if not oldData:
                self.vector.value.insert(0, self.vector.value.pop(index))
    def get(self, nid:str) -> Optional[int]:
        for i in self.vector.value:
            if bytes(i.nid).decode() == nid:
                return i.seqno
        return None
    def has(self, nid:str) -> bool:
        return False if self.index(nid) == None else True
    def index(self, nid:str) -> Optional[int]:
        for index, value in enumerate(self.vector.value):
            if bytes(value.nid).decode() == nid:
                return index
        return None
    def to_str(self) -> str:
        return " ".join([( bytes(i.nid).decode() + ":" + str(i.seqno) ) for i in self.vector.value])
    def encode(self) -> bytes:
        if self.wire == None:
            self.wire = self.vector.encode()
        return self.wire
    def keys(self) -> List[str]:
        return [bytes(i.nid).decode() for i in self.vector.value]
    def list(self) -> List[StateVectorComponentModel]:
        return self.vector.value
    def to_component(self) -> Component:
        return self.encode()
    def length(self) -> int:
        return len(self.encode())
    def partition(self, start:int, end:int) -> Component:
        return StateVectorModel(self.vector.value[start:end]).encode()
    def entry(self, index:int) -> Optional[StateVectorComponentModel]:
        try:
            return self.vector.value[index]
        except (IndexError, ValueError):
            return None
    def total(self) -> int:
        return sum(i.seqno for i in self.vector.value)
    def entry_lengths(self) -> List[int]:
        return [len(i.encode()) for i in self.vector.value]