#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs
#    @Documentation: https://ndn-python-svs.readthedocs.io

# Basic Libraries
from typing import Optional, Callable
# NDN Imports
from ndn.encoding import Name, BinaryStr
from ndn.security import Keychain
from ndn.transport.stream_socket import Face
from ndn.storage import Storage
# Custom Imports
from .security import SecurityOptions
from .svs_base_thread import SVSyncBase_Thread
from .svs_shared import SVSyncShared

# Class Type: an API thread class
# Class Purpose:
#   to push SVS to a separate thread so SVS does not become encounter a block.
#   to allow the user to interact with SVS, fetch and publish.
#   to allow caching other node's data in case one node goes down.
class SVSyncShared_Thread(SVSyncBase_Thread):
    def __init__(self, groupPrefix:Name, nid:Name, updateCallback:Callable, cacheOthers:bool, storage:Optional[Storage]=None, securityOptions:Optional[SecurityOptions]=None, face:Optional[Face]=None, keychain:Optional[Keychain]=None) -> None:
        super().__init__(groupPrefix, nid, updateCallback, storage, securityOptions, face, keychain)
        self.cacheOthers = cacheOthers
    async def function(self) -> None:
        self.svs = SVSyncShared(self.app, self.groupPrefix, self.nid, self.missing_callback, self.cacheOthers, self.storage, self.secOptions)
    def serveDataPacket(datapkt:BinaryStr) -> None:
        try:
            self.svs.serveDataPacket(datapkt)
        except AttributeError:
            raise self.SVSyncUnwaitedThread("A SVSync Thread needs to be waited on before doing operations.")