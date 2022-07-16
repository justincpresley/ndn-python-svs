#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs
#    @Documentation: https://ndn-python-svs.readthedocs.io

# Basic Libraries
from typing import Optional, Callable, List
# NDN Imports
from ndn.app import NDNApp
from ndn.encoding import Name, Component, SignatureType
# Custom Imports
from .core import Core
from .heart_tracker import HeartTracker
from .heart import Heart
from .logger import SVSyncLogger
from .missing_data import MissingData
from .security import SecurityOptions, SigningInfo, ValidatingInfo

# Class Type: an standalone API class utilizing SVS's internals
# Class Purpose:
#   to know what nodes are alive or dead with reduced network traffic
#   to have a seperate SVS type specifically to monitor the status
class SVSyncHealth:
    def __init__(self, app:NDNApp, groupPrefix:Name, nid:Name, tracker:HeartTracker, securityOptions:Optional[SecurityOptions]=None) -> None:
        SVSyncLogger.info("SVSync: started an svsync type")
        self.nid, self.tracker = Name.to_str(nid), tracker
        secOptions = securityOptions if securityOptions is not None else SecurityOptions(SigningInfo(SignatureType.DIGEST_SHA256), ValidatingInfo(ValidatingInfo.get_validator(SignatureType.DIGEST_SHA256)), SigningInfo(SignatureType.DIGEST_SHA256), [])
        self.core = Core(app, groupPrefix + [Component.from_str("sync")], groupPrefix, nid, self._missing_callback, secOptions)
    def _missing_callback(self, missing_list:List[MissingData]) -> None:
        for i in missing_list:
            if i.nid == self.nid:
                continue
            self.tracker.reset(i.nid)
    def examine(self) -> None:
        self.tracker.detect()
        if self.tracker.beat(self.nid):
            self.core.updateMyState(self.core.getSeqno()+1)
            self.tracker.reset(self.nid)
    def getHeart(self, nid:str) -> Optional[Heart]:
        return self.tracker.get(nid)
    def getCore(self) -> Core:
        return self.core