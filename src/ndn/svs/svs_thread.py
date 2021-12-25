#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs
#    @Documentation: https://ndn-python-svs.readthedocs.io

# Basic Libraries
from typing import Optional, Callable
# NDN Imports
from ndn.encoding import Name
from ndn.security import Keychain
from ndn.transport.stream_socket import Face
from ndn.storage import Storage
# Custom Imports
from .security import SecurityOptions
from .svs import SVSync
from .svs_base_thread import SVSyncBase_Thread

# Class Type: an API thread class
# Class Purpose:
#   to push SVS to a separate thread so SVS does not become encounter a block.
#   to allow the user to interact with SVS, fetch and publish.
class SVSync_Thread(SVSyncBase_Thread):
    def __init__(self, groupPrefix:Name, nid:Name, updateCallback:Callable, storage:Optional[Storage]=None, securityOptions:Optional[SecurityOptions]=None, face:Optional[Face]=None, keychain:Optional[Keychain]=None) -> None:
        super().__init__(groupPrefix, nid, updateCallback, storage, securityOptions, face, keychain)
    async def function(self) -> None:
        self.svs = SVSync(self.app, self.groupPrefix, self.nid, self.missing_callback, self.storage, self.secOptions)