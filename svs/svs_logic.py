from ndn.app import NDNApp
from ndn.encoding import Component, Name
import time
import asyncio as aio
from random import uniform
from collections import OrderedDict
from ndn.types import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure

class VersionVector:
    def __init__(self, component=None):
        self.m_map = OrderedDict()
        if component:
            res = bytes(Component.get_value(component)).decode().split(" ")
            for x in res:
                temp = x.split(":")
                self.set(temp[0],int(temp[1]))
    def set(self,nid,seqNo): # returns seqNo as well
        sort = False
        if not self.has(nid):
            sort = True
        self.m_map[nid] = seqNo
        if sort:
            self.m_map = OrderedDict(sorted(self.m_map.items()))
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
    def __init__(self, function, interval, rand_percent):
        self.function = function
        self.default_interval = interval # milliseconds
        self.rand_percent = rand_percent
        self.interval = self.default_interval + round( uniform(-self.rand_percent,self.rand_percent)*self.default_interval )
        self.start = None
        self.run = True
        self.task = aio.get_event_loop().create_task(self._target())
    async def _target(self):
        while self.run:
            self.start = self._current_milli_time()
            while not ( self._current_milli_time()>=self.start+self.interval ):
                await aio.sleep(0.001)
            self.function()
            self.interval = self.default_interval + round( uniform(-self.rand_percent,self.rand_percent)*self.default_interval )
    def stop(self):
        self.run = False
    def make_time_left(self, delay=0):
        delay = self.default_interval+round( uniform(-self.rand_percent,self.rand_percent)*self.default_interval ) if delay==0 else delay
        self.interval = self._current_milli_time() - self.start + delay
    def reset(self, delay=0):
        delay = self.default_interval+round( uniform(-self.rand_percent,self.rand_percent)*self.default_interval ) if delay==0 else delay
        self.interval = self.interval + delay
    def skip_interval(self):
        self.interval = 0
    def time_left(self):
        return (self.start + self.interval - self._current_milli_time())
    def _current_milli_time(self):
        return round(time.time() * 1000)
class SVS_Logic:
    def __init__(self,app,groupPrefix,nid):
        print(f'SVS_Logic: started svs logic')
        self.app = app
        self.groupPrefix = groupPrefix
        self.nid = nid
        self.syncPrefix = self.groupPrefix + [Component.from_str("s")]
        self.app.route(self.syncPrefix)(self.onSyncInterest)
        print(f'SVS_Logic: started listening to {Name.to_str(self.syncPrefix)}')
        self.state_vector = VersionVector()
        self.seqNum = 0
        self.state_vector.set(Name.to_str(self.nid), self.seqNum)
        self.interval = 30000 # time in milliseconds
        self.rand_percent = 0.1
        self.lower_interval = 200 # time in milliseconds
        self.lower_rand_percent = 0.9
        self.scheduler = SVS_Scheduler(self.retxSyncInterest, self.interval, self.rand_percent)
        self.scheduler.skip_interval()
    def __del__(self):
        aio.ensure_future(self.app.unregister(self.syncPrefix))
        print(f'SVS_Logic: done listening to sync prefix')
        self.scheduler.stop()
        print(f'SVS_Logic: finished svs logic')

    async def sendSyncInterest(self):
        name = self.syncPrefix + [Component.from_bytes(self.state_vector.encode())]
        print(f'SVS_Logic: sent sync {Name.to_str(name)}')
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
    def onSyncInterest(self, int_name, int_param, _app_param):
        print(f'SVS_Logic: received sync {Name.to_str(int_name)}')
        sync_vector = VersionVector(int_name[-1])
        same_vector = True

        # check if the incoming vector is old
        for key in self.state_vector.keys():
            if not sync_vector.has(key):
                same_vector = False
            if sync_vector.get(key) < self.state_vector.get(key):
                same_vector = False

        # check if the incoming vector is new and update
        for key in sync_vector.keys():
            # get any missing keys
            if not self.state_vector.has(key):
                same_vector = False
                self.state_vector.set(key, 0)
            # update the need vector
            if sync_vector.get(key) > self.state_vector.get(key):
                same_vector = False
                self.state_vector.set(key, sync_vector.get(key))

        # reset the sync timer if incoming vector is the same
        # set the sync timer to smaller delay if incoming vector is not the same
        if same_vector:
            self.scheduler.make_time_left() # just resets the timer like its a new loop
        else:
            delay = self.lower_interval + round( uniform(-self.lower_rand_percent,self.lower_rand_percent)*self.lower_interval )
            if self.scheduler.time_left() > delay:
                self.scheduler.make_time_left(delay)
        print(f'SVS_Logic: state {self.state_vector.to_str()}')
    def retxSyncInterest(self):
        aio.get_event_loop().create_task(self.sendSyncInterest())
    def updateState(self):
        self.seqNum = self.seqNum+1
        self.state_vector.set(Name.to_str(self.nid), self.seqNum)
        self.scheduler.skip_interval()
    def getStateVector(self):
        return self.state_vector
    def getCurrentSeqNum(self):
        return self.seqNum