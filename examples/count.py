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
from typing import List, Optional
# NDN Imports
from ndn.app import NDNApp
from ndn.encoding import Name
# Custom Imports
sys.path.insert(0,'.')
from src.ndn.svs import SVSync, SVSyncLogger, MissingData

app = NDNApp()

def parse_cmd_args() -> dict:
    # Command Line Parser
    parser = ArgumentParser(add_help=False,description="An SVS Integer Counting Node capable of syncing with others.")
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
        self.svs:SVSync = SVSync(app, Name.from_str(self.args["group_prefix"]), Name.from_str(self.args["node_id"]), self.missing_callback)
        print(f'SVS client started | {self.args["group_prefix"]} - {self.args["node_id"]} |')
    async def run(self) -> None:
        # wait 10ms before publishing data to ensure proper asyncio setup
        await aio.sleep(0.01)
        num:int = 0
        while 1:
            num = num+1
            try:
                print("YOU: "+str(num))
                self.svs.publishData(str(num).encode())
            except KeyboardInterrupt:
                sys.exit()
            await aio.sleep(5)
    def missing_callback(self, missing_list:List[MissingData]) -> None:
        aio.ensure_future(self.on_missing_data(missing_list))
    async def on_missing_data(self, missing_list:List[MissingData]) -> None:
        for i in missing_list:
            nid:Name = Name.from_str(i.nid)
            while i.lowSeqNum <= i.highSeqNum:
                content_str:Optional[bytes] = await self.svs.fetchData(nid, i.lowSeqNum, 3)
                if content_str:
                    output_str:str = i.nid + ": " + content_str.decode()
                    sys.stdout.write("\033[K")
                    sys.stdout.flush()
                    print(output_str)
                i.lowSeqNum = i.lowSeqNum + 1

async def start_count(args:dict) -> None:
    prog = Program(args)
    await prog.run()

def main() -> int:
    args = parse_cmd_args()
    args["node_id"] = Name.to_str(Name.from_str(args["node_id"]))
    args["group_prefix"] = Name.to_str(Name.from_str(args["group_prefix"]))

    SVSyncLogger.config(True if args["verbose"] else False, None, logging.INFO)

    try:
        app.run_forever(after_start=start_count(args))
    except (FileNotFoundError, ConnectionRefusedError):
        print('Error: could not connect to NFD for SVS.')

    return 0

if __name__ == "__main__":
    sys.exit(main())