from argparse import ArgumentParser, SUPPRESS
import sys
from ndn.app import NDNApp
from ndn.encoding import Name
import asyncio as aio
sys.path.insert(0,'.')
from svs.svs_logic import *

def process_cmd_args():
    # Command Line Parser
    parser = ArgumentParser(add_help=False,description="An SVS Chat Node capable of syncing with others by using the API.")
    requiredArgs = parser.add_argument_group("required arguments")
    optionalArgs = parser.add_argument_group("optional arguments")
    # Adding All Command Line Arguments
    requiredArgs.add_argument("-n", "--nodename",action="store",dest="node_name",required=True,help="name of this node")
    optionalArgs.add_argument("-gp","--groupprefix",action="store",dest="group_prefix",required=False,default="/ndn/svs",help="group prefix to listen from")
    optionalArgs.add_argument("-h","--help",action="help",default=SUPPRESS,help="show this help message and exit")
    # Getting All Arugments
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

class Program:
    def __init__(self, app, cmdline_args):
        self.args = cmdline_args
        self.app = app
        self.logic = None
        print(f'SVS chat client stared | {Name.to_str(self.args["group_prefix"])} - {Name.to_str(self.args["node_name"])} |')
    async def run(self):
        self.logic = SVS_Logic(self.app, self.args["group_prefix"], self.args["node_name"])
        while True:
            await aio.sleep(1)

def main() -> int:
    cmdline_args = process_cmd_args()
    app = NDNApp()
    prog = Program(app, cmdline_args)
    try:
        app.run_forever(after_start=prog.run())
    except FileNotFoundError:
        print('Error: could not connect to NFD.')
    except KeyboardInterrupt:
        print('Error: interrupted')
    finally:
        app.shutdown()
if __name__ == "__main__":
    main()
