#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs
#    @Documentation: https://ndn-python-svs.readthedocs.io

# Basic Libraries
from typing import Callable, Optional
# NDN Imports
from ndn.app import NDNApp
from ndn.encoding import Name, Component
from ndn.storage import Storage
# Custom Imports
from .security import SecurityOptions
from .svs_base import SVSyncBase

# Class Type: an API class
# Class Purpose:
#   to allow the user to interact with SVS, fetch and publish.
class SVSync(SVSyncBase):
    def __init__(self, app:NDNApp, groupPrefix:Name, nid:Name, updateCallback:Callable, storage:Optional[Storage]=None, securityOptions:Optional[SecurityOptions]=None) -> None:
        preSyncPrefix, preDataPrefix = groupPrefix + [Component.from_str("sync")], nid + groupPrefix + [Component.from_str("data")]
        super().__init__(app, preSyncPrefix, preDataPrefix, groupPrefix, nid, updateCallback, storage, securityOptions)
    def getDataName(self, nid:Name, seqno:int) -> Name:
        return ( nid + self.groupPrefix + [Component.from_str("data")] + [Component.from_str(str(seqno))] )