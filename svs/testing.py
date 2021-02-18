import sys
import time
import asyncio as aio
import threading
from ndn.app import NDNApp
sys.path.insert(0,'.')
from svs.svs_logic import SVS_Logic

class SVS_Thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.svs = None
        self.loop = None
        self.app = None
    def run(self):
        def loop_task():
            self.app = NDNApp()
            try:
                self.app.run_forever(after_start=self.function())
            except FileNotFoundError:
                print(f'Error: could not connect to NFD for SVS.')
                exit()
            self.loop.stop()

        self.loop = aio.new_event_loop()
        aio.set_event_loop(self.loop)
        self.loop.create_task(loop_task())
        self.loop.run_forever()
    async def function(self):
        self.svs = SVS_Logic(self.app, Name.from_str("/svs"), Name.from_str("/Austin"))

class Main_Thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.svs = None
        self.loop = None
        self.app = None
    def run(self):
        def loop_task():
            self.app = NDNApp()
            try:
                self.app.run_forever(after_start=self.function())
            except FileNotFoundError:
                print(f'Error: could not connect to NFD for Main Thread.')
                exit()
            self.loop.stop()

        self.loop = aio.new_event_loop()
        aio.set_event_loop(self.loop)
        self.loop.create_task(loop_task())
        self.loop.run_forever()
    async def function(self):
        while True:
            time.sleep(1)
            print("Main thread Executed")

def main():
    svs_thread = SVS_Thread()
    main_thread = Main_Thread()
    svs_thread.start()
    main_thread.start()

if __name__ == "__main__":
    sys.exit(main())
