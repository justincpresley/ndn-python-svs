# Basic Libraries
from typing import Callable, Optional
# NDN Imports
from ndn.app import NDNApp
from ndn.encoding import Name
# Custom Imports
from .svs_base import SVSyncBase
from .svs_storage_base import SVSyncStorageBase

class SVSync(SVSyncBase):
    def __init__(self, app:NDNApp, groupPrefix:Name, nid:Name, updateCallback:Callable, storage:Optional[SVSyncStorageBase]=None) -> None:
        super().__init__(app, groupPrefix, groupPrefix, nid+groupPrefix, nid, updateCallback, storage)