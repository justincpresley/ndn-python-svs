#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs
#    @Documentation: https://ndn-python-svs.readthedocs.io

# Basic Libraries
from typing import Optional, Callable
# NDN Imports
from ndn.encoding import Name, BinaryStr
from ndn.security import Keychain
from ndn.transport.face import Face
# Custom Imports
from .heart_tracker import HeartTracker
from .security import SecurityOptions
from .svs_shared import SVSyncHealth

# Class Type: an API thread class
# Class Purpose:
#   to push SVS to a separate thread so SVS does not become encounter a block.
#   to allow the user to interact with SVS, get health info.
#   to not worry about health stuff in the main loop.
class SVSyncHealth_Thread(Thread):
    def __init__(self, groupPrefix:Name, nid:Name, tracker:HeartTracker, securityOptions:Optional[SecurityOptions]=None, face:Optional[Face]=None, keychain:Optional[Keychain]=None) -> None:
        SVSyncLogger.info("SVSync_Thread: Created thread to push SVS to.")
        Thread.__init__(self)
        self.groupPrefix, self.nid, self.face, self.keychain, self.secOptions, self.tracker, self.svs, self.loop, self.app, self.failed = groupPrefix, nid, face, keychain, securityOptions, tracker, None, None, None, False
    async def function(self) -> None:
        self.svs = SVSyncHealth(self.app, self.groupPrefix, self.nid, self.tracker, self.secOptions)
        while 1:
            try:
                self.svs.examine()
            except KeyboardInterrupt:
                sys.exit()
            await aio.sleep(0.001)
    def wait(self) -> None:
        while self.svs is None:
            time.sleep(0.001)
            if self.failed:
                sys.exit()
    def run(self) -> None:
        def loop_task() -> None:
            self.app = NDNApp(self.face, self.keychain)
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
    def getHeart(self, nid:str) -> Optional[Heart]:
        return self.svs.getHeart(nid)
    def getSVSync(self) -> Optional[SVSyncHealth]:
        return self.svs
    def getCore(self) -> Optional[Core]:
        return self.svs.getCore() if self.svs else None