#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs
#    @Documentation: https://ndn-python-svs.readthedocs.io

# Class Type: a struct
# Class Purpose:
#   to hold the health status of a node.
class Heart:
    __slots__ = ('nid','last_beat','cycles','alive')
    def __init__(self, nid:str) -> None:
        self.nid, self.last_beat, self.cycles, self.alive = nid, 0, 0, False