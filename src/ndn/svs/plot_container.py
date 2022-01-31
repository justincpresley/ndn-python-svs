#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs
#    @Documentation: https://ndn-python-svs.readthedocs.io

from __future__ import annotations

# Basic Libraries
from typing import Optional
# Custom Imports
from .plot import Plot

# Class Type: a struct
# Class Purpose:
#   to hold a mapping of nids to their plots
class PlotContainer:
    def __init__(self, nid:str, transInPkt:int) -> None:
        self.plots, self.nid, self.myplot, self.transInPkt = {}, nid, Plot(), transInPkt
    def find(self, nid:str, seqno:int) -> Optional[str]:
        try:
            return self.plots[nid].find(seqno)
        except KeyError:
            return None
    def add(self, nid:str, seqno:int, label:str) -> None:
        try:
            self.plots[nid].add(seqno, label)
        except KeyError:
            self.plots[nid] = Plot()
            self.plots[nid].add(seqno, label)
        if nid == self.nid:
            if len(self.myplot.getDict()) == transInPkt:
                self.myplot = Plot()
            self.myplot.add(seqno, label)
    def clear(self) -> None:
        self.plots.clear()
    def getDict(self) -> dict:
        return self.plots
    def getSeqnos(self) -> list:
        return self.plots.keys()
    def getEntries(self) -> List:
        return self.plots.values()
    def getNodeID(self) -> Optional[str]:
        return self.nid
    def incorporate(self, nid:str, val:Plot) -> None:
        try:
            self.plots[nid].incorporate(val)
        except KeyError:
            self.plots[nid] = val
    def encode(self) -> bytes:
        return self.myplot.encode()