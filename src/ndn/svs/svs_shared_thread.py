# Basic Libraries
from typing import Optional, Callable
# NDN Imports
from ndn.encoding import Name
# Custom Imports
from .svs_thread import SVSync_Thread
from .svs_shared import SVSyncShared

class SVSyncShared_Thread(SVSync_Thread):
    def __init__(self, groupPrefix:Name, nid:Name, updateCallback:Callable, cacheOthers:bool, storage:Optional[SVSyncStorageBase]=None) -> None:
        super().__init__(groupPrefix, nid, updateCallback, storage)
        self.cacheOthers = cacheOthers
    async def function(self) -> None:
        self.svs = SVSyncShared(self.app, self.groupPrefix, self.nid, self.updateCallback, self.cacheOthers, self.storage)