#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs
#    @Documentation: https://ndn-python-svs.readthedocs.io

# Basic Libraries
import time
from typing import Optional, Callable
# Custom Imports
from .constants import TRACKER_DIFFERENCE
from .heart import Heart
from .logger import SVSyncLogger

# Class Type: a class
# Class Purpose:
#   to keep track of the last send update of all nodes
#   to keep track of the status of all nodes
class HeartTracker:
    def __init__(self, callback:Callable, beat_rate:int, beats_to_renew:int, beats_to_expire:int) -> None:
        self.hearts, self.callback, self.rate, self.track, self.btr, self.bte = {}, callback, beat_rate, beat_rate+TRACKER_DIFFERENCE, beats_to_renew, beats_to_expire
    def reset(self, nid:str) -> None:
        try:
            heart = self.hearts[nid]
        except KeyError:
            heart = Heart(nid)
            self.hearts[nid] = heart
        heart.last_beat = time.perf_counter() * 1000
        if heart.alive:
            heart.cycles = 0
        else:
            heart.cycles += 1
            if heart.cycles >= self.btr:
                heart.cycles = 0
                heart.alive = True
                self.callback(heart)
                SVSyncLogger.info(f"HeartTracker: Node {nid} renewed!")
    def detect(self) -> None:
        for nid in list(self.hearts):
            heart = self.hearts[nid]
            time_past = (time.perf_counter()*1000) - heart.last_beat
            if not heart.alive and time_past > self.track:
                heart.cycles = 0
            elif time_past > self.track:
                heart.cycles = time_past // self.track
                if heart.cycles >= self.bte:
                    heart.cycles = 0
                    heart.alive = False
                    self.updateCallback(heart)
                    SVSyncLogger.info(f"HeartTracker: Node {nid} expired!")
    def beat(self, nid:str) -> bool:
        try:
            time_past = (time.perf_counter()*1000) - self.hearts[nid].last_beat
            if time_past >= self.rate:
                return True
        except KeyError:
            return True
        return False
    def get(self, nid:str) -> Optional[Heart]:
        try:
            return self.hearts[nid]
        except KeyError:
            return None