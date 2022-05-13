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
from .constants import TRACKER_RATE, BEAT_RATE, BEATS_TO_RENEW, BEATS_TO_EXPIRE
from .heart import Heart
from .logger import SVSyncLogger

# Class Type: a class
# Class Purpose:
#   to keep track of the last send update of all nodes
#   to keep track of the status of all nodes
class HeartTracker:
    def __init__(self, nid:str, callback:Callable) -> None:
        self.hearts, self.nid, self.callback = {}, nid, callback
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
            if heart.cycles >= BEATS_TO_RENEW:
                heart.cycles = 0
                heart.alive = True
                self.callback(heart)
                SVSyncLogger.info(f"HeartTracker: Node {nid} renewed!")
    def detect(self) -> None:
        for nid in list(self.hearts):
            heart = self.hearts[nid]
            time_past = (time.perf_counter()*1000) - heart.last_beat
            if not heart.alive and time_past > TRACKER_RATE:
                heart.cycles = 0
            elif time_past > TRACKER_RATE:
                heart.cycles = time_past // TRACKER_RATE
                if heart.cycles >= BEATS_TO_EXPIRE:
                    heart.cycles = 0
                    heart.alive = False
                    self.updateCallback(heart)
                    SVSyncLogger.info(f"HeartTracker: Node {nid} expired!")
    def beat(self) -> bool:
        try:
            time_past = (time.perf_counter()*1000) - self.hearts[self.nid].last_beat
            if time_past >= BEAT_RATE:
                return True
        except KeyError:
            return True
        return False
    def get(self, nid:str) -> Optional[Heart]:
        try:
            return self.hearts[nid]
        except KeyError:
            return None