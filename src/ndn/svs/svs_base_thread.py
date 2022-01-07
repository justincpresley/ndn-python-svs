#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs
#    @Documentation: https://ndn-python-svs.readthedocs.io

# Basic Libraries
import asyncio as aio
import sys
import time
from threading import Thread
from typing import Optional, List, Callable
# NDN Imports
from ndn.app import NDNApp
from ndn.encoding import Name, BinaryStr
from ndn.security import Keychain
from ndn.transport.stream_socket import Face
from ndn.storage import Storage, DiskStorage
# Custom Imports
from .core import SVSyncCore
from .logger import SVSyncLogger
from .missing_data import MissingData
from .security import SecurityOptions
from .svs_base import SVSyncBase

# Class Type: an abstract API thread class
# Class Purpose:
#   to push SVS to a separate thread so SVS does not become encounter a block.
#   to derive different SVSync_Thread classes from.
#   to allow the user to interact with SVS, fetch and publish.
class SVSyncBase_Thread(Thread):
    class SVSyncUnwaitedThread(Exception):
        pass
    def __init__(self, groupPrefix:Name, nid:Name, updateCallback:Callable, storage:Optional[Storage]=None, securityOptions:Optional[SecurityOptions]=None, face:Optional[Face]=None, keychain:Optional[Keychain]=None) -> None:
        SVSyncLogger.info("SVSync_Thread: Created thread to push SVS to.")
        Thread.__init__(self)
        self.groupPrefix, self.nid, self.updateCallback, self.storage, self.face, self.keychain, self.secOptions, self.svs, self.loop, self.app, self.failed = groupPrefix, nid, updateCallback, storage, face, keychain, securityOptions, None, None, None, False
    def wait(self) -> None:
        while self.svs is None:
            time.sleep(0.001)
            if self.failed:
                sys.exit()
    def run(self) -> None:
        def loop_task() -> None:
            self.app = NDNApp(self.face, self.keychain)
            if issubclass(type(self.storage), DiskStorage):
                self.storage.initialize()
            try:
                self.app.run_forever(after_start=self.function())
            except (FileNotFoundError, ConnectionRefusedError):
                print("Error: could not connect to NFD for SVS.")
                self.failed = True
                sys.exit()

        self.loop = aio.new_event_loop()
        aio.set_event_loop(self.loop)
        self.loop.create_task(loop_task())
        self.loop.run_forever()
    async def function(self) -> None:
        raise NotImplementedError
    def missing_callback(self, missing_list:List[MissingData]) -> None:
        aio.get_event_loop().create_task(self.updateCallback(self)(missing_list))
    def getSVSync(self) -> Optional[SVSyncBase]:
        return self.svs
    async def fetchData(self, nid:Name, seqno:int, retries:int=0) -> Optional[bytes]:
        try:
            data = await self.svs.fetchData(nid, seqno, retries)
            return data
        except AttributeError:
            raise self.SVSyncUnwaitedThread("A SVSync Thread needs to be waited on before doing operations.")
    async def fetchDataPacket(self, nid:Name, seqno:int, retries:int=0) -> Optional[BinaryStr]:
        try:
            pck = await self.svs.fetchDataPacket(nid, seqno, retries)
            return pck
        except AttributeError:
            raise self.SVSyncUnwaitedThread("A SVSync Thread needs to be waited on before doing operations.")
    def publishData(self, data:bytes) -> None:
        try:
            self.svs.publishData(data)
        except AttributeError:
            raise self.SVSyncUnwaitedThread("A SVSync Thread needs to be waited on before doing operations.")
    def getCore(self) -> Optional[SVSyncCore]:
        return self.svs.getCore() if self.svs else None