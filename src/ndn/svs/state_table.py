#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs
#    @Documentation: https://ndn-python-svs.readthedocs.io

# Basic Libraries
from typing import List, Optional
# NDN Imports
from ndn.encoding import Component, Name
# Custom Imports
from .constants import NDN_MTU
from .meta_data import MetaData
from .missing_data import MissingData
from .state_vector import StateVector, StateVectorEntry

# Class Type: a class
# Class Purpose:
#   to allow an easier time to form sync interest and handle all states
class StateTable:
    def __init__(self, mynid:Name) -> None:
        self.table, self.meta, self.parts, self.nidstr = StateVector(), MetaData(), [[0,0]], Name.to_str(mynid)
        self.meta.source = self.nidstr.encode()
    def processStateVector(self, incoming_sv:StateVector, oldData:bool) -> List[MissingData]:
        listOrder:List[StateVectorEntry] = incoming_sv.list() if oldData else reversed(incoming_sv.list())
        missingList:List[MissingData] = []
        for i in listOrder:
            tableSeqno:int = self.table.get(i.nid) if self.table.get(i.nid) else 0
            if tableSeqno < i.seqno:
                tableSeqno = tableSeqno + 1
                temp:MissingData = MissingData(i.nid, tableSeqno, i.seqno)
                self.table.set(i.nid, i.seqno, oldData)
                missingList.append(temp)
        return missingList
    def updateMetaData(self) -> None:
        self.meta.tseqno = self.table.total()
        self.calculateParts()
        self.meta.nopcks = len(self.parts) - 1
    def updateMyState(self, seqno:int) -> None:
        self.table.set(self.nidstr, seqno)
    def getPart(self, no:int) -> Component:
        try:
            return self.table.partition(self.parts[no][0],self.parts[no][1])
        except (IndexError, ValueError):
            return bytearray()
    def getMetaData(self) -> MetaData:
        return self.meta
    def getCompleteStateVector(self) -> StateVector:
        return self.table
    def calculateParts(self) -> None:
        mainlist, templist, part, total = [], [], 0, 0
        templist.insert(0, 0)
        for index, value in enumerate(self.table.entry_lengths()):
            if total + value > self.getPartMaximum(part):
                templist.insert(1, index)
                part = part + 1
                total = value
                mainlist.append(templist)
                templist = []
                templist.insert(0, index)
            else:
                total = total + value
        if templist:
            templist.insert(1, len(self.table.entry_lengths()))
            mainlist.append(templist)
        self.parts = mainlist
    def getPartMaximum(self, part:int) -> int:
        return (NDN_MTU - 1500) # optimize this part for each packet (including interest)
    def getPartCuts(self) -> list:
        return self.parts
    def getSeqno(self, nid:Name) -> Optional[int]:
        return self.table.get(Name.to_str(nid))