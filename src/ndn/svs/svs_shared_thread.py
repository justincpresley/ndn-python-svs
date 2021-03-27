#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs/

# Basic Libraries
from typing import Optional, Callable
# NDN Imports
from ndn.app import NDNApp
from ndn.transport.stream_socket import Face
from ndn.encoding import Name
from ndn.security import Keychain
from ndn_python_repo import Storage
# Custom Imports
from .svs_thread_base import SVSyncBase_Thread
from .svs_shared import SVSyncShared
from .security import SecurityOptions

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