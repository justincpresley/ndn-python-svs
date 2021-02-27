# Basic Libraries
import logging
import time
from typing import Optional
# NDN Imports
from ndn.encoding import Name, parse_data, NonStrictName
from ndn.name_tree import NameTrie

class SVS_Storage:
    cache = NameTrie()
    def time_ms(self) -> int:
        return int(time.time() * 1000)
    def put_data_packet(self, name:NonStrictName, data_packet:bytes) -> None:
        _, meta_info, _, _ = parse_data(data_packet)
        expire_time_ms = self.time_ms()
        if meta_info.freshness_period:
            expire_time_ms += meta_info.freshness_period
        name = Name.normalize(name)
        self.cache[name] = (data_packet, expire_time_ms)
        logging.info(f'SVS_Storage: cache save {Name.to_str(name)}')
    def get_data_packet(self, name:NonStrictName, can_be_prefix:bool=False, must_be_fresh:bool=False) -> Optional[bytes]:
        name = Name.normalize(name)
        try:
            if not can_be_prefix:
                data, expire_time_ms = self.cache[name]
                if not must_be_fresh or expire_time_ms > self.time_ms():
                    logging.info('SVS_Storage: get from cache')
                    return data
            else:
                it = self.cache.itervalues(prefix=name, shallow=True)
                while True:
                    data, expire_time_ms = next(it)
                    if not must_be_fresh or expire_time_ms > self.time_ms():
                        logging.info('SVS_Storage: get from cache')
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
