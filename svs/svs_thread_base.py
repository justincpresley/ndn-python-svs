#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs
#    @Documentation: https://ndn-python-svs.readthedocs.io

# Basic Libraries
import asyncio as aio
import sys
import logging
import time
from threading import Thread
from typing import Optional, List, Callable
# NDN Imports
from ndn.app import NDNApp
# from ndn.transport.stream_socket import Face
from ndn.transport.face import Face
from ndn.encoding import Name
from ndn.security import Keychain
from ndn.storage import Storage, DiskStorage
# Custom Imports
from .svs_base import SVSyncBase
from .core import MissingData, SVSyncCore
from .security import SecurityOptions

# Class Type: an abstract API thread class
# Class Purpose:
#   to push SVS to a separate thread so SVS does not become encounter a block.
#   to derive different SVSync_Thread classes from.
#   to allow the user to interact with SVS, fetch and publish.
class SVSyncBase_Thread(Thread):
    def __init__(self, groupPrefix:Name, nid:Name, updateCallback:Callable, storage:Optional[Storage]=None, securityOptions:Optional[SecurityOptions]=None, face:Optional[Face]=None, keychain:Optional[Keychain]=None) -> None:
        logging.info(f'SVSync_Thread: Created thread to push SVS to.')
        Thread.__init__(self)
        self.groupPrefix = groupPrefix
        self.nid = nid
        self.updateCallback = updateCallback
        self.storage = storage
        self.face = face
        self.keychain = keychain
        self.secOptions = securityOptions
        self.svs = None
        self.loop = None
        self.app = None
        self.failed = False
    def wait(self):
        while self.svs is None:
            time.sleep(0.001)
            if self.failed:
                sys.exit()
    def run(self) -> None:
        def loop_task():
            self.app = NDNApp(self.face, self.keychain)
            if issubclass(type(self.storage), DiskStorage):
                self.storage.initialize()
            try:
                self.app.run_forever(after_start=self.function())
            except (FileNotFoundError, ConnectionRefusedError):
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
    async def fetchData(self, nid:Name, seqno:int, retries:int=0) -> Optional[bytes]:
        return await self.svs.fetchData(nid, seqno, retries)
    def publishData(self, data:bytes) -> None:
        self.svs.publishData(data)
    def getCore(self) -> SVSyncCore:
        return self.svs.getCore()
