#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs
#    @Documentation: https://ndn-python-svs.readthedocs.io

# Class Type: a struct
# Class Purpose:
#   to hold the range of missing data for a specific node.
class MissingData:
    __slots__ = ('nid','lowSeqNum','highSeqNum')
    def __init__(self, nid:str, lowSeqNum:int, highSeqNum:int) -> None:
        self.nid, self.lowSeqNum, self.highSeqNum = nid, lowSeqNum, highSeqNum