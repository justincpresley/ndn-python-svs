#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs
#    @Documentation: https://ndn-python-svs.readthedocs.io

# Basic Libraries
from typing import Optional, Callable, Tuple
# NDN Imports
from ndn.app import NDNApp
from ndn.encoding import Name, MetaInfo, InterestParam, BinaryStr, FormalName, SignatureType, make_data, parse_data
from ndn.types import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure
from ndn.storage import Storage, MemoryStorage
# Custom Imports
from .constants import NDN_MTU, DATA_INTEREST_LIFETIME, DATA_PACKET_FRESHNESS
from .core import Core
from .exceptions import SVSyncPublicationTooLarge
from .logger import SVSyncLogger
from .security import SecurityOptions, SigningInfo, ValidatingInfo

# Class Type: an abstract API class
# Class Purpose:
#   to derive different SVSync from.
#   to allow the user to interact with SVS, fetch and publish.
class SVSyncBase:
    def __init__(self, app:NDNApp, syncPrefix:Name, dataPrefix:Name, groupPrefix:Name, nid:Name, updateCallback:Callable, storage:Optional[Storage]=None, securityOptions:Optional[SecurityOptions]=None) -> None:
        SVSyncLogger.info("SVSync: started an svsync type")
        self.app, self.syncPrefix, self.dataPrefix, self.groupPrefix, self.nid, self.updateCallback = app, syncPrefix, dataPrefix, groupPrefix, nid, updateCallback
        self.storage = MemoryStorage() if not storage else storage
        self.secOptions = securityOptions if securityOptions is not None else SecurityOptions(SigningInfo(SignatureType.DIGEST_SHA256), ValidatingInfo(ValidatingInfo.get_validator(SignatureType.DIGEST_SHA256)), SigningInfo(SignatureType.DIGEST_SHA256), [])
        self.app.route(self.dataPrefix)(self.onDataInterest)
        self.core = Core(self.app, self.syncPrefix, self.groupPrefix, self.nid, self.updateCallback, self.secOptions)
        SVSyncLogger.info(f'SVSync: started listening to {Name.to_str(self.dataPrefix)}')
    def onDataInterest(self, int_name:FormalName, int_param:InterestParam, _app_param:Optional[BinaryStr]) -> None:
        data_pkt = self.storage.get_packet(int_name, int_param.can_be_prefix)
        if data_pkt:
            SVSyncLogger.info(f'SVSync: served data {Name.to_str(int_name)}')
            self.app.put_raw_packet(data_pkt)
    async def fetchData(self, nid:Name, seqno:int, retries:int=0) -> Optional[bytes]:
        name = self.getDataName(nid, seqno)
        while retries+1 > 0:
            try:
                SVSyncLogger.info(f'SVSync: fetching data {Name.to_str(name)}')
                _, _, _, pkt = await self.app.express_interest(name, need_raw_packet=True, must_be_fresh=True, can_be_prefix=True, lifetime=DATA_INTEREST_LIFETIME)
                ex_int_name, meta_info, content, sig_ptrs = parse_data(pkt)
                isValidated = await self.secOptions.validate(ex_int_name, sig_ptrs)
                if not isValidated:
                    return None
                SVSyncLogger.info(f'SVSync: received data {bytes(content)}')
                return bytes(content) if content else None
            except InterestNack as e:
                SVSyncLogger.warning(f'SVSync: nacked with reason={e.reason} {Name.to_str(name)}')
            except InterestTimeout:
                SVSyncLogger.warning(f'SVSync: timeout {Name.to_str(name)}')
            except InterestCanceled:
                SVSyncLogger.warning(f'SVSync: canceled {Name.to_str(name)}')
            except ValidationFailure:
                SVSyncLogger.warning(f'SVSync: data failed to validate {Name.to_str(name)}')
            except Exception as e:
                SVSyncLogger.warning(f'SVSync: unknown error has occured: {e}')

            retries = retries - 1
            if retries+1 > 0:
                SVSyncLogger.info("SVSync: retrying fetching data")
        return None
    def publishData(self, data:bytes) -> None:
        segno = self.core.getSeqno()+1
        name = self.getDataName(self.nid, segno)
        data_packet = make_data(name, MetaInfo(freshness_period=DATA_PACKET_FRESHNESS), content=data, signer=self.secOptions.dataSig.signer)
        if len(data_packet) > NDN_MTU:
            raise SVSyncPublicationTooLarge(f"A SVSync Publication can not be over NDN's MTU ({self.NDN_MTU}).")
        SVSyncLogger.info(f'SVSync: publishing data {Name.to_str(name)}')
        self.storage.put_packet(name, data_packet)
        self.core.updateMyState(segno)
    def getCore(self) -> Core:
        return self.core
    def getDataName(self, nid:Name, seqno:int) -> Name:
        raise NotImplementedError