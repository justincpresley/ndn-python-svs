# Basic Libraries
import asyncio as aio
import sys
import logging
import time
from threading import Thread
from typing import Optional, List, Callable
# NDN Imports
from ndn.app import NDNApp
from ndn.transport.stream_socket import Face
from ndn.encoding import Name
from ndn.security import Keychain
from ndn_python_repo import Storage
# Custom Imports
from .svs_base import SVSyncBase
from .svs_core import MissingData, SVSyncCore

class SVSyncBase_Thread(Thread):
    def __init__(self, groupPrefix:Name, nid:Name, updateCallback:Callable, storage:Optional[Storage]=None, face:Optional[Face]=None, keychain:Optional[Keychain]=None) -> None:
        logging.info(f'SVSync_Thread: Created thread to push SVS to.')
        Thread.__init__(self)
        self.groupPrefix = groupPrefix
        self.nid = nid
        self.updateCallback = updateCallback
        self.storage = storage
        self.face = face
        self.keychain = keychain
        self.svs = None
        self.loop = None
        self.app = None
        self.failed = False
    def wait(self):
        while self.svs == None:
            time.sleep(0.001)
            if self.failed:
                sys.exit()
    def run(self) -> None:
        def loop_task():
            self.app = NDNApp(self.face, self.keychain)
            try:
                self.app.run_forever(after_start=self.function())
            except FileNotFoundError:
                print(f'Error: could not connect to NFD for SVS.')
                self.failed = True
                sys.exit()

        self.loop = aio.new_event_loop()
        aio.set_event_loop(self.loop)
        self.loop.create_task(loop_task())
        self.loop.run_forever()
    async def function(self) -> None:
        raise NotImplementedError
    def missing_callback(self, missing_list:List[MissingData]) -> None:
        aio.ensure_future(self.updateCallback(self)(missing_list))
    def getSVSync(self) -> SVSyncBase:
        return self.svs
    async def fetchData(self, nid:Name, seqNum:int, retries:int=0) -> Optional[bytes]:
        await self.svs.fetchData(nid, seqNum, retries)
    def publishData(self, data:bytes) -> None:
        self.svs.publishData(data)
    def getCore(self) -> SVSyncCore:
        return self.svs.getCore()