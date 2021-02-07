from ndn.app import NDNApp
import time
import asyncio as aio
from collections import OrderedDict

class VersionVector:
    def __init__(self):
        self.m_map = OrderedDict()
    def set(self,nid,seqNo): # returns seqNo as well
        self.m_map[nid] = seqNo
        return seqNo
    def get(self,nid): # seqNo returned
        return self.m_map[nid] if nid in self.m_map.keys() else 0
    def has(self,nid): # bool value
        return ( nid in self.m_map.keys() )
    def begin(self): # returns only nid
        return next(iter(self.m_map))
    def end(self): # returns only nid
        return next(reversed(self.m_map))
    def to_str(self):
        stream = ""
        for key,value in self.m_map.items():
            stream = stream + key + ":" + str(value) + " "
        return stream.rstrip()
    def encode(self):
        return self.to_str().encode()

class SVS_Logic:
    DEFAULT_ACK_FRESHNESS = 4000
    def __init__(self,app,syncPrefix,nid):
        self.app = app
        self.groupPrefix = syncPrefix
        self.nid = nid
        self.syncPrefix = self.groupPrefix + [Component.from_str("s")]
        self.app.route(self.syncPrefix)(self._onSyncInterest)
        print(f'SVS_Logic: started listening to {Name.to_str(self.syncPrefix)}')
        self.v_vector = VersionVector()
        print(f'SVS_Logic: starting sync interests')
        self._retxSyncInterest()
    def __del__(self):
        aio.ensure_future(self.app.unregister(prefix))
        print(f'SVS_Logic: done listening to {Name.to_str(self.syncPrefix)}')

    async def _sendSyncInterest():
        name = self.syncPrefix # + VersionVector.encode()
        try:
            data_name, meta_info, content = await app.express_interest(
                name, must_be_fresh=True, can_be_prefix=True, lifetime=1000)
        except InterestNack as e:
            pass
        except InterestTimeout:
            pass
        except InterestCanceled:
            pass
        except ValidationFailure:
            pass
        print(f'SVS_Logic: sent sync {Name.to_str(name)}')
    def _onSyncInterest(self, int_name, int_param, _app_param):
        logging.info(f'On SyncInterest: {Name.to_str(int_name)}')
    def _retxSyncInterest():
        pass