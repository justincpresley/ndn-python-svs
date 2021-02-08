from ndn.app import NDNApp
from ndn.encoding import Component, Name
import time
import asyncio as aio
from collections import OrderedDict
from ndn.types import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure

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
class SVS_Scheduler:
    def __init__(self, function, interval):
        self.function = function
        self.default_interval = interval # milliseconds
        self.interval = self.default_interval
        self.start = None
        self.run = True
        self.task = aio.ensure_future(self._target())
    async def _target(self):
        while self.run:
            self.start = self._current_milli_time()
            while not ( self._current_milli_time()>=self.start+self.interval ):
                await aio.sleep(0)
            self.function()
            self.interval = self.default_interval
    def stop(self):
        self.run = False
    def reset(self):
        self.interval = self.interval + self.default_interval
    def skip(self):
        self.interval = 0
    def get_task(self):
        return self.task
    def _current_milli_time(self):
        return round(time.time() * 1000)
class SVS_Logic:
    def __init__(self,app,groupPrefix,nid):
        self.app = app
        self.groupPrefix = groupPrefix
        self.nid = nid
        self.syncPrefix = self.groupPrefix + [Component.from_str("s")]
        self.app.route(self.syncPrefix)(self.onSyncInterest)
        print(f'SVS_Logic: started listening to {Name.to_str(self.syncPrefix)}')
        self.v_vector = VersionVector()
        print(f'SVS_Logic: starting sync interests')
        self.interval = 30000 # time in milliseconds
        self.scheduler = SVS_Scheduler(self.retxSyncInterest, self.interval)
        self.scheduler_task = self.scheduler.get_task()
    def __del__(self):
        aio.ensure_future(self.app.unregister(self.syncPrefix))
        print(f'SVS_Logic: done listening to {Name.to_str(self.syncPrefix)}')
        self.scheduler.stop()
        print(f'SVS_Logic: finished sync interests')
    def get_scheduler_task(self):
        return self.scheduler_task
    async def sendSyncInterest(self):
        name = self.syncPrefix + [Component.from_bytes(self.v_vector.encode())]
        try:
            data_name, meta_info, content = await self.app.express_interest(
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
    def onSyncInterest(self, int_name, int_param, _app_param):
        print(f'On SyncInterest: {Name.to_str(int_name)}')
    def retxSyncInterest(self):
        aio.get_event_loop().create_task(self.sendSyncInterest())
