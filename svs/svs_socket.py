# Basic Libraries
import sys
# NDN Imports
from ndn.app import NDNApp
from ndn.encoding import Component, Name
# Custom Imports
sys.path.insert(0,'.')
from svs.svs_logic import *
from svs.svs_storage import *

# API of the SVS_Socket
# - fetchData()
# - publishData()

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
    def onDataInterest(self, int_name, int_param, _app_param):
        pass
    def fetchData(self, nid, seqNum):
        pass
    def publishData(self, bytes):
        pass