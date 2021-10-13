#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs/

# Basic Libraries
from time import time
from typing import Optional
# NDN Imports
from ndn.encoding import Name, parse_data, NonStrictName
from ndn.name_tree import NameTrie
# Custom Imports
from .logger import SVSyncLogger

# Class Type: a ndn class
# Class Purpose:
#   to provide a general cache class for SVS.
#   to cache data without a database.
class SVSyncStorage:
    cache = NameTrie()
    def time_ms(self) -> int:
        return int(time() * 1000)
    def put_data_packet(self, name:NonStrictName, data_packet:bytes) -> None:
        _, meta_info, _, _ = parse_data(data_packet)
        expire_time_ms = self.time_ms()
        if meta_info.freshness_period:
            expire_time_ms += meta_info.freshness_period
        name = Name.normalize(name)
        self.cache[name] = (data_packet, expire_time_ms)
        SVSyncLogger.info(f'SVSyncStorage: cache save {Name.to_str(name)}')
    def get_data_packet(self, name:NonStrictName, can_be_prefix:bool=False, must_be_fresh:bool=False) -> Optional[bytes]:
        name = Name.normalize(name)
        try:
            if not can_be_prefix:
                data, expire_time_ms = self.cache[name]
                if not must_be_fresh or expire_time_ms > self.time_ms():
                    SVSyncLogger.info('SVSyncStorage: get from cache')
                    return data
            else:
                it = self.cache.itervalues(prefix=name, shallow=True)
                while 1:
                    data, expire_time_ms = next(it)
                    if not must_be_fresh or expire_time_ms > self.time_ms():
                        SVSyncLogger.info('SVSyncStorage: get from cache')
                        return data
        except (KeyError, StopIteration):
            return None
    def remove_data_packet(self, name:NonStrictName) -> bool:
        removed = False
        name = Name.normalize(name)
        try:
            del self.cache[name]
            removed = True
        except KeyError:
            pass
        return removed