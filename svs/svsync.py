# Basic Libraries
from typing import Callable
# NDN Imports
from ndn.app import NDNApp
from ndn.encoding import Name
# Custom Imports
from .svsync_base import SVSyncBase

class SVSync(SVSyncBase):
    def __init__(self, app:NDNApp, groupPrefix:Name, nid:Name, updateCallback:Callable) -> None:
        super().__init__(app, groupPrefix, groupPrefix, nid+groupPrefix, nid, updateCallback)

class SVSyncShared(SVSyncBase):
    def __init__(self, app:NDNApp, groupPrefix:Name, nid:Name, updateCallback:Callable) -> None:
        super().__init__(app, groupPrefix, groupPrefix, groupPrefix, nid, updateCallback)
