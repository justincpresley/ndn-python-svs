# Basic Libraries
from argparse import ArgumentParser, SUPPRESS
import asyncio as aio
import sys
import time
import threading
# NDN Imports
from ndn.app import NDNApp
from ndn.encoding import Name
# Custom Imports
sys.path.insert(0,'.')
from svs.svs_socket import SVS_Socket

def process_cmd_args():
    # Command Line Parser
    parser = ArgumentParser(add_help=False,description="An SVS Chat Node capable of syncing with others.")
    requiredArgs = parser.add_argument_group("required arguments")
    optionalArgs = parser.add_argument_group("optional arguments")
    # Adding All Command Line Arguments
    requiredArgs.add_argument("-n", "--nodename",action="store",dest="node_name",required=True,help="name of this node")
    optionalArgs.add_argument("-gp","--groupprefix",action="store",dest="group_prefix",required=False,default="/svs",help="group prefix to listen from")
    optionalArgs.add_argument("-h","--help",action="help",default=SUPPRESS,help="show this help message and exit")
    # Getting All Arguments
    args = {}
    if parser.parse_args().group_prefix[-1] == "/":
        parser.parse_args().group_prefix = parser.parse_args().group_prefix[:-1]
    if parser.parse_args().group_prefix[0] != "/":
        parser.parse_args().group_prefix = "/" + parser.parse_args().group_prefix
    if parser.parse_args().node_name[-1] == "/":
        parser.parse_args().node_name = parser.parse_args().node_name[:-1]
    if parser.parse_args().node_name[0] != "/":
        parser.parse_args().node_name = "/" + parser.parse_args().node_name
    args["group_prefix"] = Name.from_str(parser.parse_args().group_prefix)
    args["node_name"] = Name.from_str(parser.parse_args().node_name)
    return args

class SVS_Thread(threading.Thread):
    def __init__(self, group_prefix, node_name):
        threading.Thread.__init__(self)
        self.group_prefix = group_prefix
        self.nid = node_name
        self.svs = None
        self.loop = None
        self.app = None
        self.failed = False
    def run(self):
        def loop_task():
            self.app = NDNApp()
            try:
                self.app.run_forever(after_start=self.function())
            except FileNotFoundError:
                print(f'Error: could not connect to NFD for SVS.')
                self.failed = True
                quit()

        self.loop = aio.new_event_loop()
        aio.set_event_loop(self.loop)
        self.loop.create_task(loop_task())
        self.loop.run_forever()
    async def function(self):
        self.svs = SVS_Socket(self.app, self.group_prefix, self.nid)
    def get_svs(self):
        return self.svs
    def get_loop(self):
        return self.loop
    def get_app(self):
        return self.app
    def has_failed(self):
        return self.failed
class Program:
    def __init__(self, cmdline_args):
        self.args = cmdline_args
        self.svs_thread = SVS_Thread(self.args["group_prefix"],self.args["node_name"])
        self.svs_thread.daemon = True
        self.svs_thread.start()
        while self.svs_thread.get_svs() == None:
            time.sleep(0.001)
            if self.svs_thread.has_failed():
                quit()
        self.svs = self.svs_thread.get_svs()
        print(f'SVS chat client started | {Name.to_str(self.args["group_prefix"])} - {Name.to_str(self.args["node_name"])} |')
    def run(self):
        while True:
            try:
                time.sleep(5)
                print("Main thread Executed")
            except:
                quit()

def main() -> int:
    cmdline_args = process_cmd_args()
    prog = Program(cmdline_args)
    prog.run()

if __name__ == "__main__":
    sys.exit(main())
