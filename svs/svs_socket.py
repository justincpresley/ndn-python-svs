from ndn.app import NDNApp
from ndn.encoding import Component, Name
import time
import asyncio as aio
import sys
sys.path.insert(0,'.')
from svs.svs_logic import *

# API of the SVS_Socket
# - fetchData()
# - publishData()

class SVS_Socket:
    def __init__(self,app,groupPrefix,nid):
        self.app = app
        self.groupPrefix = groupPrefix
        self.nid = nid
        self.dataPrefix = self.groupPrefix + [Component.from_str("d")]
        print(f'SVS_Socket: started svs logic')
        self.logic = SVS_Logic(self.app, self.groupPrefix, self.nid)
        self.app.route(self.dataPrefix)(self._onDataInterest)
        print(f'SVS_Socket: started listening to {Name.to_str(self.dataPrefix)}')
    def __del__(self):
        aio.ensure_future(self.app.unregister(self.dataPrefix))
        print(f'SVS_Socket: done listening to data prefix')
        del self.logic
        print(f'SVS_Socket: finished svs logic')
    def _onDataInterest(self, int_name, int_param, _app_param):
        #data_bytes = self.storage.get_data_packet(int_name, int_param.can_be_prefix)
        #if data_bytes:
        #    logging.info(f'Read handle: Found Data in Storage for {Component.to_str(int_name[-1])}')
        #    self.app.put_raw_packet(data_bytes)
        #    return
        pass
    def fetchData():
        pass
    def publishData():
        pass