# Basic Libraries
import logging
# NDN Imports
from ndn.app import NDNApp
from ndn.encoding import Component, Name, make_data, MetaInfo
# Custom Imports
from .svs_logic import SVS_Logic

# API of the SVS_Socket
# - fetchData()
# - publishData()

class SVS_Socket:
    def __init__(self,app,storage,groupPrefix,nid,cacheOthers=False):
        logging.info(f'SVS_Socket: started svs socket')
        self.app = app
        self.storage = storage
        self.groupPrefix = groupPrefix
        self.nid = nid
        self.cacheOthers = cacheOthers
        self.dataPrefix = self.groupPrefix + [Component.from_str("d")]
        self.listenPrefix = self.dataPrefix
        if not self.cacheOthers:
            self.listenPrefix = self.dataPrefix + self.nid
        self.logic = SVS_Logic(self.app, self.groupPrefix, self.nid)
        self.app.route(self.listenPrefix)(self.onDataInterest)
        logging.info(f'SVS_Socket: started listening to {Name.to_str(self.listenPrefix)}')
    def onDataInterest(self, int_name, int_param, _app_param):
        data_bytes = self.storage.get_data_packet(int_name, int_param.can_be_prefix)
        if data_bytes:
            logging.info(f'SVS_Socket: served data')
            self.app.put_raw_packet(data_bytes)
        return
    async def fetchData(self, nid, seqNum): # add number of retries
        name = self.dataPrefix + nid + Name.from_str( "/epoch-"+str(seqNum) )
        try:
            logging.info(f'SVS_Socket: fetching data')
            ex_int_name, meta_info, content = await self.app.express_interest(name, must_be_fresh=True, can_be_prefix=False, lifetime=6000)
            logging.info(f'SVS_Socket: received data')
            if self.cacheOthers:
                logging.info(f'SVS_Socket: publishing data')
                name = self.dataPrefix + nid + Name.from_str( "/epoch-"+str(seqNum) )
                metainfo = MetaInfo(freshness_period=500)
                data = make_data(name, metainfo, content=bytes(content))
                self.storage.put_data_packet(name, data)
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
        return None
    def publishData(self, bytes):
        logging.info(f'SVS_Socket: publishing data')
        name = self.dataPrefix + self.nid + Name.from_str( "/epoch-"+str(self.logic.getCurrentSeqNum()+1) )
        metainfo = MetaInfo(freshness_period=500)
        data = make_data(name, metainfo, content=bytes)
        self.storage.put_data_packet(name, data)
        self.logic.updateState()
