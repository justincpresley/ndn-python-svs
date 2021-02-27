# Basic Libraries
from typing import List
from enum import Enum
# NDN Imports
from ndn.encoding import Component, TlvModel, BytesField, UintField, RepeatedField, ModelField

class StateVectorModelTypes(Enum):
    COMPONENT = 201
    KEY       = 202
    VALUE     = 203
class StateVectorComponentModel(TlvModel):
    node_id = BytesField(StateVectorModelTypes.KEY.value)
    seq_num = UintField(StateVectorModelTypes.VALUE.value)
class StateVectorModel(TlvModel):
    value   = RepeatedField(ModelField(StateVectorModelTypes.COMPONENT.value, StateVectorComponentModel))

class StateVector:
    def __init__(self, component:Component=None) -> None:
        try:
            self.vector = StateVectorModel() if not component else StateVectorModel.parse(Component.get_value(component))
        except:
            self.vector = StateVectorModel()
            component = None
        self.vector.value = [] if not component else self.vector.value
    def set(self, nid:str, seqNum:int) -> None:
        sort = True if not self.has(nid) else False
        if sort:
            svc = StateVectorComponentModel()
            svc.seq_num = seqNum
            svc.node_id = nid.encode()

            index = len(self.vector.value)
            for i in range(len(self.vector.value)):
                if bytes(self.vector.value[i].node_id).decode().lower() > nid.lower():
                    index = i
                    break
            self.vector.value.insert(index, svc)
        else:
            for i in self.vector.value:
                if bytes(i.node_id).decode() == nid:
                    i.seq_num = seqNum
                    return
    def get(self, nid:str) -> int:
        for i in self.vector.value:
            if bytes(i.node_id).decode() == nid:
                return i.seq_num
        return 0
    def has(self, nid:str) -> bool:
        return ( nid in self.keys() )
    def to_str(self) -> str:
        stream = ""
        for i in self.vector.value:
            stream = stream + bytes(i.node_id).decode() + ":" + str(i.seq_num) + " "
        return stream.rstrip()
    def encode(self) -> bytes:
        return self.vector.encode()
    def keys(self) -> List[str]:
        return [bytes(i.node_id).decode() for i in self.vector.value]
    def to_component(self) -> Component:
        return Component.from_bytes(self.encode())