from ndn.app import NDNApp
from ndn.encoding import Component, Name, parse_data, NonStrictName
from ndn.encoding.tlv_var import parse_tl_num
from ndn.name_tree import NameTrie
from typing import List, Optional
import time
import asyncio as aio
import sys
sys.path.insert(0,'.')
from svs.svs_logic import *

# API of the SVS_Socket
# - fetchData()
# - publishData()

class SVS_Storage:
    cache = NameTrie()

    def __init__(self):
        print(f'SVS_Storage: started svs storage')
        aio.get_event_loop().create_task(self._periodic_write_back())

    ###### wrappers around key-value store
    async def _periodic_write_back(self):
        self._write_back()
        await aio.sleep(10)
        aio.get_event_loop().create_task(self._periodic_write_back())

    @staticmethod
    def _get_name_bytes_wo_tl(name: NonStrictName) -> bytes:
        # remove name's TL as key to support efficient prefix search
        name = Name.to_bytes(name)
        offset = 0
        offset += parse_tl_num(name, offset)[1]
        offset += parse_tl_num(name, offset)[1]
        return name[offset:]

    @staticmethod
    def _time_ms():
        return int(time.time() * 1000)

    def _write_back(self):
        keys = []
        values = []
        expire_time_mss = []
        for name, (data, expire_time_ms) in self.cache.iteritems(prefix=[], shallow=True):
            keys.append(self._get_name_bytes_wo_tl(name))
            values.append(data)
            expire_time_mss.append(expire_time_ms)
        if len(keys) > 0:
            self._put_batch(keys, values, expire_time_mss)
            logging.info(f'Cache write back {len(keys)} items')
        self.cache = NameTrie()

    def put_data_packet(self, name: NonStrictName, data: bytes):
        """
        Insert a data packet named ``name`` with value ``data``.
        This method will parse ``data`` to get its freshnessPeriod, and compute its expiration time\
            by adding the freshnessPeriod to the current time.

        :param name: NonStrictName. The name of the data packet.
        :param data: bytes. The value of the data packet.
        """
        _, meta_info, _, _ = parse_data(data)
        expire_time_ms = self._time_ms()
        if meta_info.freshness_period:
            expire_time_ms += meta_info.freshness_period

        # write data packet and freshness_period to cache
        name = Name.normalize(name)
        self.cache[name] = (data, expire_time_ms)
        logging.info(f'Cache save: {Name.to_str(name)}')

    def get_data_packet(self, name: NonStrictName, can_be_prefix: bool=False,
                        must_be_fresh: bool=False) -> Optional[bytes]:
        name = Name.normalize(name)
        # cache lookup
        try:
            if not can_be_prefix:
                data, expire_time_ms = self.cache[name]
                if not must_be_fresh or expire_time_ms > self._time_ms():
                    logging.info('get from cache')
                    return data
            else:
                it = self.cache.itervalues(prefix=name, shallow=True)
                while True:
                    data, expire_time_ms = next(it)
                    if not must_be_fresh or expire_time_ms > self._time_ms():
                        logging.info('get from cache')
                        return data
        # not in cache, lookup in storage
        except (KeyError, StopIteration):
            key = self._get_name_bytes_wo_tl(name)
            return self._get(key, can_be_prefix, must_be_fresh)

    def remove_data_packet(self, name: NonStrictName) -> bool:
        removed = False
        name = Name.normalize(name)
        try:
            del self.cache[name]
            removed = True
        except KeyError:
            pass
        if self._remove(self._get_name_bytes_wo_tl(name)):
            removed = True
        return removed
class SVS_Socket:
    def __init__(self,app,groupPrefix,nid):
        print(f'SVS_Socket: started svs socket')
        self.app = app
        self.groupPrefix = groupPrefix
        self.nid = nid
        self.dataPrefix = self.groupPrefix + [Component.from_str("d")]

        self.logic = SVS_Logic(self.app, self.groupPrefix, self.nid)
        self.storage = SVS_Storage()

        self.app.route(self.dataPrefix)(self.onDataInterest)
        print(f'SVS_Socket: started listening to {Name.to_str(self.dataPrefix)}')
    def __del__(self):
        aio.ensure_future(self.app.unregister(self.dataPrefix))
        print(f'SVS_Socket: done listening to data prefix')
        del self.logic
        print(f'SVS_Socket: finished svs socket')

    def onDataInterest(self, int_name, int_param, _app_param):
        data_bytes = self.storage.get_data_packet(int_name, int_param.can_be_prefix)
        if data_bytes:
            print(f'Read handle: Found Data in Storage for {Component.to_str(int_name[-1])}')
            self.app.put_raw_packet(data_bytes)
            return

    async def fetchData(self, nid, seqNum):
        try:
            name = self.dataPrefix + nid + [Component.from_str("seqNum="+string(seqNum))]
            print(f'SVS_Socket: sending data interest')
            ex_int_name, meta_info, content = await self.app.express_interest(name, must_be_fresh=True, can_be_prefix=False, lifetime=3000)
            return bytes(content) if content else None
        except InterestNack as e:
            pass
        except InterestTimeout:
            pass
        except InterestCanceled:
            pass
        except ValidationFailure:
            pass
        except Exception as e:
            pass
        return None

    def publishData(bytes):
        self.logic.updateState()