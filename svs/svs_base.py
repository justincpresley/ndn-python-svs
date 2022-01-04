#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs
#    @Documentation: https://ndn-python-svs.readthedocs.io

# Basic Libraries
import logging
from typing import Optional, Callable
# NDN Imports
from ndn.app import NDNApp
from ndn.encoding import Name, MetaInfo, InterestParam, BinaryStr, FormalName, SignatureType
from ndn.encoding import make_data, parse_data
from ndn.types import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure
from ndn.storage import Storage, MemoryStorage
# Custom Imports
from .core import SVSyncCore
from .security import SecurityOptions, SigningInfo, ValidatingInfo

# Class Type: an abstract API class
# Class Purpose:
#   to derive different SVSync from.
#   to allow the user to interact with SVS, fetch and publish.
class SVSyncBase():
    def __init__(self, app:NDNApp, syncPrefix:Name, dataPrefix:Name, nid:Name, updateCallback:Callable, storage:Optional[Storage]=None, securityOptions:Optional[SecurityOptions]=None) -> None:
        logging.info(f'SVSync: started svsync')
        self.app = app
        self.storage = MemoryStorage() if not storage else storage
        self.syncPrefix = syncPrefix
        self.dataPrefix = dataPrefix
        self.nid = nid
        self.updateCallback = updateCallback
        self.secOptions = securityOptions if securityOptions is not None else SecurityOptions(SigningInfo(SignatureType.DIGEST_SHA256), ValidatingInfo(ValidatingInfo.get_validator(SignatureType.DIGEST_SHA256)), SigningInfo(SignatureType.DIGEST_SHA256), [])
        self.core = SVSyncCore(self.app, self.syncPrefix, self.nid, self.updateCallback, self.secOptions)
        self.app.route(self.dataPrefix)(self.onDataInterest)
        logging.info(f'SVSync: started listening to {Name.to_str(self.dataPrefix)}')
    def onDataInterest(self, int_name:FormalName, int_param:InterestParam, _app_param:Optional[BinaryStr]) -> None:
        data_pkt = self.storage.get_packet(int_name, int_param.can_be_prefix)
        if data_pkt:
            logging.info(f'SVSync: served data {Name.to_str(int_name)}')
            self.app.put_raw_packet(data_pkt)
    async def fetchData(self, nid:Name, seqno:int, retries:int=0) -> Optional[bytes]:
        name = self.getDataName(nid, seqno)
        while retries+1 > 0:
            try:
                logging.info(f'SVSync: fetching data {Name.to_str(name)}')
                _, _, _, pkt = await self.app.express_interest(name, need_raw_packet=True, must_be_fresh=True, can_be_prefix=False, lifetime=6000)
                ex_int_name, meta_info, content, sig_ptrs = parse_data(pkt)
                isValidated = await self.secOptions.validate(ex_int_name, sig_ptrs)
                if not isValidated:
                    return None
                logging.info(f'SVSync: received data {bytes(content)}')
                return bytes(content) if content else None
            except InterestNack as e:
                logging.warning(f'SVSync: nacked with reason={e.reason}')
            except InterestTimeout:
                logging.warning(f'SVSync: timeout')
            except InterestCanceled:
                logging.warning(f'SVSync: canceled')
            except ValidationFailure:
                logging.warning(f'SVSync: data failed to validate')
            except Exception as e:
                logging.warning(f'SVSync: unknown error has occured: {e}')

            retries = retries - 1
            if retries+1 > 0:
                logging.info(f'SVSync: retrying fetching data')
        return None
    def publishData(self, data:bytes) -> None:
        name = self.getDataName(self.nid, self.core.getSeqno()+1)
        data_packet = make_data(name, MetaInfo(freshness_period=5000), content=data, signer=self.secOptions.dataSig.signer)
        logging.info(f'SVSync: publishing data {Name.to_str(name)}')
        self.storage.put_packet(name, data_packet)
        self.core.updateStateVector(self.core.getSeqno()+1)
    def getCore(self) -> SVSyncCore:
        return self.core
    def getDataName(self, nid:Name, seqno:int) -> Name:
        raise NotImplementedError