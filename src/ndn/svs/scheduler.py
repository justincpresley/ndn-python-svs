#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs/

# Basic Libraries
from typing import Callable
import asyncio as aio
from random import uniform
from time import time
# Custom Imports
from .logger import SVSyncLogger

# Class Type: an async class
# Class Purpose:
#   to call a specific function based on an interval.
class AsyncScheduler:
    def __init__(self, function:Callable, interval:int, randomPercent:float) -> None:
        SVSyncLogger.info(f'AsyncScheduler: started scheduler for an async function')
        self.function, self.defaultInterval, self.randomPercent, self.startTime, self.stop = function, interval, randomPercent, None, False
        self.interval = self.defaultInterval + round( uniform(-self.randomPercent,self.randomPercent)*self.defaultInterval )
        self.task = aio.get_event_loop().create_task(self.target())
    async def target(self) -> None:
        while not self.stop:
            self.startTime = self.get_current_milli_time()
            while not ( self.get_current_milli_time() >= (self.startTime+self.interval) ):
                await aio.sleep(0.001)
            self.function()
            self.interval = self.defaultInterval + round( uniform(-self.randomPercent,self.randomPercent)*self.defaultInterval )
    def set_cycle(self, delay:int=0, add_to:bool=False) -> None:
        delay = self.defaultInterval+round( uniform(-self.randomPercent,self.randomPercent)*self.defaultInterval ) if delay==0 else delay
        self.interval = (self.interval + delay) if add_to else (self.get_current_milli_time() - self.startTime + delay)
    def skip_interval(self) -> None:
        self.interval = 0
    def stop(self) -> None:
        self.stop = True
        self.skip_interval()
    def get_time_left(self) -> int:
        return (self.startTime + self.interval - self.get_current_milli_time())
    def get_current_milli_time(self) -> int:
        return round(time() * 1000)