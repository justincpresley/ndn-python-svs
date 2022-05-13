#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs
#    @Documentation: https://ndn-python-svs.readthedocs.io

# Basic Libraries
import asyncio as aio
import logging
import sys
from argparse import ArgumentParser, SUPPRESS
# NDN Imports
from ndn.app import NDNApp
from ndn.encoding import Name
# Custom Imports
sys.path.insert(0,'.')
from src.ndn.svs import SVSyncHealth, Heart, SVSyncLogger

app = NDNApp()

def parse_cmd_args() -> dict:
    # Command Line Parser
    parser = ArgumentParser(add_help=False,description="An SVS Heartbeat Node capable of syncing with others to let them know its alive.")
    requiredArgs = parser.add_argument_group("required arguments")
    optionalArgs = parser.add_argument_group("optional arguments")
    informationArgs = parser.add_argument_group("information arguments")
    # Adding all Command Line Arguments
    requiredArgs.add_argument("-n", "--nodename",action="store",dest="node_name",required=True,help="id of this node in svs")
    optionalArgs.add_argument("-gp","--groupprefix",action="store",dest="group_prefix",required=False,help="overrides config | routable group prefix to listen from")
    optionalArgs.add_argument("-v","--verbose",action="store_true",dest="verbose",default=False,required=False,help="when set, svsync info is displayed as well")
    informationArgs.add_argument("-h","--help",action="help",default=SUPPRESS,help="show this help message and exit")
    # Getting all Arguments
    argvars = parser.parse_args()
    args = {}
    args["group_prefix"] = argvars.group_prefix if argvars.group_prefix is not None else "/svs"
    args["node_id"] = argvars.node_name
    args["verbose"] = argvars.verbose
    return args

class Program:
    def __init__(self, args:dict) -> None:
        self.args = args
        self.svs:SVSyncHealth = SVSyncHealth(app, Name.from_str(self.args["group_prefix"]), Name.from_str(self.args["node_id"]), self.status_callback)
        print(f'SVS status client started | {self.args["group_prefix"]} - {self.args["node_id"]} |')
    async def run(self) -> None:
        while 1:
            try:
                self.svs.examine()
            except KeyboardInterrupt:
                sys.exit()
            await aio.sleep(0.1)
    def status_callback(self, heart:Heart) -> None:
        if heart.alive:
            print(f"[RENEW] Node {heart.nid}'s heart is noticeably alive!")
        else:
            print(f"[EXPIRE] Node {heart.nid}'s heart is ghostly silent.'")

async def start(args:dict) -> None:
    prog = Program(args)
    await prog.run()

def main() -> int:
    args = parse_cmd_args()
    args["node_id"] = Name.to_str(Name.from_str(args["node_id"]))
    args["group_prefix"] = Name.to_str(Name.from_str(args["group_prefix"]))

    SVSyncLogger.config(True if args["verbose"] else False, None, logging.INFO)

    try:
        app.run_forever(after_start=start(args))
    except (FileNotFoundError, ConnectionRefusedError):
        print('Error: could not connect to NFD for SVS.')

    return 0

if __name__ == "__main__":
    sys.exit(main())