#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs
#    @Documentation: https://ndn-python-svs.readthedocs.io

# Class Type: a struct
# Class Purpose:
#   to hold a data from a subscription
class SubscriptionData:
    __slots__ = ('nid','seqno','label','data')
    def __init__(self, nid:str, seqno:int, label:str, data:bytes) -> None:
        self.nid, self.seqno, self.label, self.data = nid, seqno, label, data