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
from ndn.encoding import Component, get_tl_num_size, write_tl_num, parse_tl_num, pack_uint_bytes
# Custom Imports
from .tlv import SVSyncTlvTypes

# Class Type: a struct
# Class Purpose:
#   to hold info about a singular node within the vector.
class StateVectorEntry:
    __slots__ = ('nid','seqno')
    def __init__(self, nid:str, seqno:int) -> None:
        self.nid, self.seqno = nid, seqno
    def encode(self) -> bytearray:
        bseqno, bnid = pack_uint_bytes(self.seqno), self.nid.encode()
        # nid
        size = len(bnid) + get_tl_num_size(len(bnid)) + get_tl_num_size(SVSyncTlvTypes.VECTOR_ENTRY.value)
        temp1 = bytearray(size)
        pos = write_tl_num(SVSyncTlvTypes.VECTOR_ENTRY.value, temp1)
        pos += write_tl_num(len(bnid), temp1, pos)
        temp1[pos:pos + len(bnid)] = bnid
        # seqno
        size = len(bseqno) + get_tl_num_size(len(bseqno)) + get_tl_num_size(SVSyncTlvTypes.SEQNO.value)
        temp2 = bytearray(size)
        pos = write_tl_num(SVSyncTlvTypes.SEQNO.value, temp2)
        pos += write_tl_num(len(bseqno), temp2, pos)
        temp2[pos:pos + len(bseqno)] = bseqno
        return temp1+temp2

# Class Type: an custom tlv model class
# Class Purpose:
#   to contain all the info of a state vector.
class StateVectorModel:
    def __init__(self, value:List[StateVectorEntry]) -> None:
        self.value:List[StateVectorEntry] = value
    def encode(self) -> bytearray:
        length, component_wires = 0, []
        for v in self.value:
            ba = v.encode()
            length += len(ba)
            component_wires.append(ba)
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
            ret.value.append(StateVectorEntry(bytes(entry).decode(), seqno))
        return ret

# Class Type: a class
# Class Purpose:
#   to allow an easier time to interact with the StateVectorModel class.
class StateVector:
    def __init__(self, component:Component=None) -> None:
        self.vector, self.wire = StateVectorModel([]), None
        if component:
            temp_vector:Optional[StateVectorModel] = StateVectorModel.parse(component)
            if temp_vector != None:
                self.vector = temp_vector
    def set(self, nid:str, seqno:int, oldData:bool=False) -> None:
        index, self.wire = self.index(nid), None
        if index == None:
            svc:StateVectorEntry = StateVectorEntry(nid, seqno)
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
            if i.nid == nid:
                return i.seqno
        return None
    def has(self, nid:str) -> bool:
        return False if self.get(nid) == None else True
    def index(self, nid:str) -> Optional[int]:
        for index, value in enumerate(self.vector.value):
            if value.nid == nid:
                return index
        return None
    def to_str(self) -> str:
        return " ".join([( i.nid + ":" + str(i.seqno) ) for i in self.vector.value])
    def encode(self) -> bytes:
        if self.wire == None:
            self.wire = self.vector.encode()
        return self.wire
    def keys(self) -> List[str]:
        return [i.nid for i in self.vector.value]
    def list(self) -> List[StateVectorEntry]:
        return self.vector.value
    def to_component(self) -> Component:
        return self.encode()
    def length(self) -> int:
        return len(self.encode())
    def partition(self, start:int, end:int) -> Component:
        return StateVectorModel(self.vector.value[start:end]).encode()
    def entry(self, index:int) -> Optional[StateVectorEntry]:
        try:
            return self.vector.value[index]
        except (IndexError, ValueError):
            return None
    def total(self) -> int:
        return sum(i.seqno for i in self.vector.value)
    def entry_lengths(self) -> List[int]:
        return [len(i.encode()) for i in self.vector.value]