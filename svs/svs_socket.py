# Basic Libraries
import logging
# NDN Imports
from ndn.app import NDNApp
from ndn.encoding import Component, Name
# Custom Imports
from .svs_logic import SVS_Logic

# API of the SVS_Socket
# - fetchData()
# - publishData()

class SVS_Socket:
    def __init__(self,app,storage,groupPrefix,nid,cacheOthers):
        logging.info(f'SVS_Socket: started svs socket')
        self.app = app
        self.storage = storage
        self.groupPrefix = groupPrefix
        self.nid = nid
        self.cacheOthers = cacheOthers
        self.dataPrefix = self.groupPrefix + [Component.from_str("d")]
        self.listenPrefix = self.dataPrefix
        if not self.cacheOthers:
            self.listenPrefix = self.dataPrefix + self.nid
        self.logic = SVS_Logic(self.app, self.groupPrefix, self.nid)
        self.app.route(self.listenPrefix)(self.onDataInterest)
        logging.info(f'SVS_Socket: started listening to {Name.to_str(self.listenPrefix)}')
    def onDataInterest(self, int_name, int_param, _app_param):
        pass
    def fetchData(self, nid, seqNum):
        pass
    def publishData(self, bytes):
        #name = self.dataPrefix + self.nid + Name.from_str( "/epoch-"+str(self.logic.getCurrentSeqNum()+1) )
        #data = form a data packet
        #self.storage.put_data_packet(name, data)
        self.logic.updateState()