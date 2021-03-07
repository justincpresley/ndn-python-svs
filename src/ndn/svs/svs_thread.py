# Basic Libraries
import asyncio as aio
import sys
import logging
from threading import Thread
from typing import Optional, Callable
# NDN Imports
from ndn.app import NDNApp
from ndn.encoding import Name
# Custom Imports
from .svs.svs import SVSync
from .svs_core import MissingData
from .svs_storage_base import SVSyncStorageBase

class SVSync_Thread(Thread):
    def __init__(self, groupPrefix:Name, nid:Name, updateCallback:Callable, storage:Optional[SVSyncStorageBase]=None) -> None:
        Thread.__init__(self)
        self.groupPrefix = groupPrefix
        self.nid = nid
        self.storage = storage
        self.updateCallback = updateCallback
        self.svs = None
        self.loop = None
        self.app = None
        self.failed = False
    def run(self) -> None:
        def loop_task():
            self.app = NDNApp()
            try:
                self.app.run_forever(after_start=self.function())
            except FileNotFoundError:
                logging.error(f'Error: could not connect to NFD for SVSync_Thread.')
                self.failed = True
                sys.exit()

        logging.info(f'SVSync_Thread: forming a thread to push SVSync to')
        self.loop = aio.new_event_loop()
        aio.set_event_loop(self.loop)
        self.loop.create_task(loop_task())
        self.loop.run_forever()
    async def function(self) -> None:
        self.svs = SVSync(self.app, self.groupPrefix, self.nid, self.updateCallback, self.storage)
    def getSVSync(self) -> Optional[SVSync]:
        return self.svs
    def hasFailed(self) -> None:
        return self.failed