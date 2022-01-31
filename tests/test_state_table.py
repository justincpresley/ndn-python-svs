#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs
#    @Documentation: https://ndn-python-svs.readthedocs.io

# Basic Libraries
import sys
from typing import List
# NDN Imports
from ndn.encoding import Name
# Custom Imports
sys.path.insert(0,'.')
from src.ndn.svs.state_table import StateTable
from src.ndn.svs.state_vector import StateVector
from src.ndn.svs.missing_data import MissingData

# File Type: pytest Testing
# Testing Classes: StateTable
# Testing Purposes:
#   to ensure proper usage of the table.

def test_state_table_update_state() -> None:
    mynid, seqno = Name.from_str("A"), 0
    st:StateTable = StateTable(mynid)
    st.updateMyState(seqno)
    seqno += 1
    st.updateMyState(seqno)
    seqno += 1
    st.updateMyState(seqno)
    seqno += 1
    st.updateMyState(seqno)
    st.updateMetaData()

    assert seqno == st.getSeqno(mynid)
    assert seqno == st.getMetaData().tseqno
    assert Name.to_str(mynid) == bytes(st.getMetaData().source).decode()

def test_state_table_metadata_change() -> None:
    mynid:Name = Name.from_str("D")
    sv, st = StateVector(), StateTable(mynid)
    sv.set("c", 4)
    sv.set("a", 6)
    sv.set("B", 10)
    sv.set(Name.to_str(mynid), 55)

    assert 0 == st.getMetaData().tseqno
    ml:List[MissingData] = st.processStateVector(sv, True)
    assert 0 == st.getMetaData().tseqno
    st.updateMetaData()
    assert 75 == st.getMetaData().tseqno
    st.updateMyState(56)
    assert 75 == st.getMetaData().tseqno
    st.updateMetaData()
    assert 76 == st.getMetaData().tseqno

def test_state_table_metadata() -> None:
    mynid:Name = Name.from_str("D")
    sv, st = StateVector(), StateTable(mynid)
    sv.set("c", 4)
    sv.set("a", 6)
    sv.set("B", 10)
    sv.set(Name.to_str(mynid), 55)
    ml:List[MissingData] = st.processStateVector(sv, True)
    st.updateMyState(56)
    st.updateMetaData()

    assert 76 == st.getMetaData().tseqno
    assert Name.to_str(mynid) == bytes(st.getMetaData().source).decode()
    assert 0 == st.getMetaData().nopcks

def test_state_table_processing_order() -> None:
    mynid:Name = Name.from_str("D")
    sv, st = StateVector(), StateTable(mynid)
    sv.set("/c", 4)
    sv.set("/a", 6)
    sv.set("/B", 10)
    sv.set(Name.to_str(mynid), 55)

    ml:List[MissingData] = st.processStateVector(sv, False)
    nsv:StateVector = st.getCompleteStateVector()

    assert nsv.to_str() == "/D:55 /B:10 /a:6 /c:4"

    sv = StateVector()
    sv.set("/Z", 44)
    ml:List[MissingData] = st.processStateVector(sv, True)
    nsv:StateVector = st.getCompleteStateVector()

    assert nsv.to_str() == "/D:55 /B:10 /a:6 /c:4 /Z:44"
