#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs/

# Basic Libraries
import sys
import pytest
# NDN Imports
from ndn.encoding import Component, Name
# Custom Imports
sys.path.insert(0,'.')
from src.ndn.svs.meta_data import MetaData

# File Type: pytest Testing
# Testing Classes: MetaData
# Testing Purposes:
#   to ensure encode and component compatibility.

def test_meta_data_encode():
    md = MetaData(None)
    md.source = b'/node1/data'
    md.tseqno = 512
    md.nopcks = 3

    enc_md = md.encode()
    assert enc_md == b'\x08\x14\xc6\x0b/node1/data\xc7\x02\x02\x00\xc8\x01\x03'

def test_meta_data_past_component():
    md = MetaData(None)
    md.source = b'/node1/data'
    md.tseqno = 512
    md.nopcks = 3

    new_md = MetaData(md.encode())
    assert new_md.nopcks == md.nopcks
    assert new_md.tseqno == md.tseqno
    assert new_md.source == md.source