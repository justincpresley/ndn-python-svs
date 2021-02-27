# Basic Libraries
import logging
from typing import Optional, Callable
# NDN Imports
from ndn.app import NDNApp
from ndn.encoding import Name, make_data, MetaInfo, parse_data, InterestParam, BinaryStr, FormalName
from ndn.types import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure
# Custom Imports
from .state_vector import StateVector
from .svs_logic import SVS_Logic
from .svs_storage import SVS_Storage

class SVS_Socket:
    def __init__(self, app:NDNApp, groupPrefix:Name, nid:Name, updateCallback:Callable) -> None:
        logging.info(f'SVS_Socket: started svs socket')
        self.app            = app
        self.storage        = SVS_Storage()
        self.groupPrefix    = groupPrefix
        self.nid            = nid
        self.updateCallback = updateCallback
        self.dataPrefix     = self.nid + self.groupPrefix
        self.logic = SVS_Logic(self.app, self.groupPrefix, self.nid, self.updateCallback)
        self.app.route(self.dataPrefix)(self.onDataInterest)
        logging.info(f'SVS_Socket: started listening to {Name.to_str(self.dataPrefix)}')
    def onDataInterest(self, int_name:FormalName, int_param:InterestParam, _app_param:Optional[BinaryStr]) -> None:
        data_bytes = self.storage.get_data_packet(int_name, int_param.can_be_prefix)
        if data_bytes:
            _, _, content, _ = parse_data(data_bytes)
            logging.info(f'SVS_Socket: served data {bytes(content)}')
            self.app.put_data(int_name, content=bytes(content), freshness_period=500)
    async def fetchData(self, nid:Name, seqNum:int, retries:int=0) -> Optional[bytes]:
        name = nid + self.groupPrefix + Name.from_str( "/epoch-"+str(seqNum) )
        while retries+1 > 0:
            try:
                logging.info(f'SVS_Socket: fetching data {Name.to_str(name)}')
                ex_int_name, meta_info, content = await self.app.express_interest(name, must_be_fresh=True, can_be_prefix=False, lifetime=6000)
                logging.info(f'SVS_Socket: received data {bytes(content)}')
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
        name = self.dataPrefix + Name.from_str( "/epoch-"+str(self.logic.getCurrentSeqNum()+1) )
        data_packet = make_data(name, MetaInfo(freshness_period=5000), content=data)
        logging.info(f'SVS_Socket: publishing data {Name.to_str(name)}')
        self.storage.put_data_packet(name, data_packet)
        self.logic.updateState()
    def getCurrentStateVector(self) -> StateVector:
        return self.logic.getCurrentStateVector()