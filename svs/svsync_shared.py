# Basic Libraries
from typing import Callable, Optional
import logging
# NDN Imports
from ndn.app import NDNApp
from ndn.encoding import Name, Component, make_data, MetaInfo, parse_data, InterestParam, BinaryStr, FormalName
from ndn.types import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure
# Custom Imports
from .svsync_base import SVSyncBase
from .svsync_storage_base import SVSyncStorageBase

class SVSyncShared(SVSyncBase):
    def __init__(self, app:NDNApp, groupPrefix:Name, nid:Name, updateCallback:Callable, cacheOthers:bool, storage:Optional[SVSyncStorageBase]=None) -> None:
        self.cacheOthers = cacheOthers
        preDataPrefix = groupPrefix + [Component.from_str("d")]
        if not self.cacheOthers:
            preDataPrefix = preDataPrefix + nid
        super().__init__(app, groupPrefix, groupPrefix+[Component.from_str("s")], preDataPrefix, nid, updateCallback, storage)
        self.dataPrefix = groupPrefix + [Component.from_str("d")]
    async def fetchData(self, nid:Name, seqNum:int, retries:int=0) -> Optional[bytes]:
        name = self.dataPrefix + nid + Name.from_str( "/epoch-"+str(seqNum) )
        while retries+1 > 0:
            try:
                logging.info(f'SVS_Socket: fetching data {Name.to_str(name)}')
                ex_int_name, meta_info, content = await self.app.express_interest(name, must_be_fresh=True, can_be_prefix=False, lifetime=6000)
                logging.info(f'SVS_Socket: received data {bytes(content)}')
                if content and self.cacheOthers:
                    data_packet = make_data(name, MetaInfo(freshness_period=5000), content=bytes(content))
                    logging.info(f'SVS_Socket: publishing others data {Name.to_str(name)}')
                    self.storage.put_data_packet(name, data_packet)
                return bytes(content) if content else None
            except InterestNack as e:
                logging.warning(f'SVS_Socket: nacked with reason={e.reason}')
            except InterestTimeout:
                logging.warning(f'SVS_Socket: timeout')
            except InterestCanceled:
                logging.warning(f'SVS_Socket: canceled')
            except ValidationFailure:
                logging.warning(f'SVS_Socket: data failed to validate')
            except Exception as e:
                logging.warning(f'SVS_Socket: unknown error has occured: {e}')

            retries = retries - 1
            if retries+1 > 0:
                logging.warning(f'SVS_Socket: retrying fetching data')
        return None
    def publishData(self, data:bytes) -> None:
        name = self.dataPrefix + self.nid + Name.from_str( "/epoch-"+str(self.core.getSeqNum()+1) )
        data_packet = make_data(name, MetaInfo(freshness_period=5000), content=data)
        logging.info(f'SVSync: publishing data {Name.to_str(name)}')
        self.storage.put_data_packet(name, data_packet)
        self.core.updateStateVector(self.core.getSeqNum()+1)