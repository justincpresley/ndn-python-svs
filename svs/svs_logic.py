from ndn.app import NDNApp
from ndn.encoding import Component, Name
import time
import asyncio as aio
from collections import OrderedDict
from ndn.types import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure

class VersionVector:
    def __init__(self, component=None):
        self.m_map = OrderedDict()
        if component:
            res = component.tobytes().decode()
            res = res[res.find('/'):]
            lst = res.split(" ")
            for x in lst:
                temp = x.split(":")
                self.set(temp[0],int(temp[1]))
    def set(self,nid,seqNo): # returns seqNo as well
        self.m_map[nid] = seqNo
    def get(self,nid): # seqNo returned
        return self.m_map[nid] if self.has(nid) else 0
    def has(self,nid): # bool value
        return ( nid in self.m_map.keys() )
    def to_str(self):
        stream = ""
        for key,value in self.m_map.items():
            stream = stream + key + ":" + str(value) + " "
        return stream.rstrip()
    def encode(self):
        return self.to_str().encode()
    def keys(self):
        return list(self.m_map.keys())
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
                await aio.sleep(0.001)
            self.function()
            self.interval = self.default_interval
    def stop(self):
        self.run = False
    def reset(self):
        self.interval = self.interval + self.default_interval
    def skip_interval(self):
        self.interval = 0
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
        self.state_vector = VersionVector()
        self.need_vector = VersionVector()
        self.seqNum = 0
        self.state_vector.set(Name.to_str(self.nid), self.seqNum)
        self.need_vector.set(Name.to_str(self.nid), 0)
        print(f'SVS_Logic: starting sync interests')
        self.interval = 30000 # time in milliseconds
        self.scheduler = SVS_Scheduler(self.retxSyncInterest, self.interval)
        self.scheduler.skip_interval()
    def __del__(self):
        aio.ensure_future(self.app.unregister(self.syncPrefix))
        print(f'SVS_Logic: done listening to {Name.to_str(self.syncPrefix)}')
        self.scheduler.stop()
        print(f'SVS_Logic: finished sync interests')

    async def sendSyncInterest(self):
        name = self.syncPrefix + [Component.from_bytes(self.state_vector.encode())]
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
        print(f'SVS_Logic: received sync {Name.to_str(int_name)}')
        sync_vector = VersionVector(int_name[-1])
        # get any missing keys
        for key in sync_vector.keys():
            if not self.state_vector.has(key):
                self.state_vector.set(key, 0)
                self.need_vector.set(key, 0)
        # update the need vector
        for key in sync_vector.keys():
            if sync_vector.get(key) > self.state_vector.get(key):
                self.need_vector.set(key, sync_vector.get(key) - self.state_vector.get(key))
    def retxSyncInterest(self):
        aio.get_event_loop().create_task(self.sendSyncInterest())
