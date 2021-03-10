# Basic Libraries
from argparse import ArgumentParser, SUPPRESS
import asyncio as aio
import sys
import time
import logging
import threading
from typing import Optional, List
# NDN Imports
from ndn.app import NDNApp
from ndn.encoding import Name
# Custom Imports
sys.path.insert(0,'.')
from src.ndn.svs.svs import SVSync
from src.ndn.svs.svs_shared import SVSyncShared
from src.ndn.svs.svs_core import MissingData

app = NDNApp()

def parse_cmd_args() -> dict:
    # Command Line Parser
    parser = ArgumentParser(add_help=False,description="An SVS Chat Node capable of syncing with others.")
    requiredArgs = parser.add_argument_group("required arguments")
    optionalArgs = parser.add_argument_group("optional arguments")
    informationArgs = parser.add_argument_group("information arguments")
    # Adding all Command Line Arguments
    requiredArgs.add_argument("-n", "--nodename",action="store",dest="node_name",required=True,help="id of this node in svs")
    optionalArgs.add_argument("-gp","--groupprefix",action="store",dest="group_prefix",required=False,help="overrides config | routable group prefix to listen from")
    informationArgs.add_argument("-h","--help",action="help",default=SUPPRESS,help="show this help message and exit")
    # Getting all Arguments
    vars = parser.parse_args()
    args = {}
    args["group_prefix"] = vars.group_prefix if vars.group_prefix!=None else "/svs"
    args["node_id"] = vars.node_name
    return args

class Program:
    def __init__(self, args:dict) -> None:
        self.args = args
        self.svs = SVSyncShared(app, Name.from_str(self.args["group_prefix"]), Name.from_str(self.args["node_id"]), self.missing_callback, True)
        print(f'SVS client started | {self.args["group_prefix"]} - {self.args["node_id"]} |')
    async def run(self) -> None:
        num = 0
        while True:
            num = num+1
            try:
                await aio.sleep(8)
                print("YOU: "+str(num))
                self.svs.publishData(str(num).encode())
            except KeyboardInterrupt:
                sys.exit()
    def missing_callback(self, missing_list:List[MissingData]) -> None:
        aio.ensure_future(self.on_missing_data(missing_list))
    async def on_missing_data(self, missing_list:List[MissingData]) -> None:
        for i in missing_list:
            nid = Name.from_str(i.nid)
            while i.lowSeqNum <= i.highSeqNum:
                content_str = await self.svs.fetchData(nid, i.lowSeqNum)
                if content_str != None:
                    content_str = i.nid + ": " + content_str.decode();
                    sys.stdout.write("\033[K")
                    sys.stdout.flush()
                    print(content_str)
                i.lowSeqNum = i.lowSeqNum + 1

async def main() -> int:
    args = parse_cmd_args()
    args["node_id"] = Name.to_str(Name.from_str(args["node_id"]))
    args["group_prefix"] = Name.to_str(Name.from_str(args["group_prefix"]))

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', \
        filename=args["node_id"][1:].replace("/","_")+".log", \
        filemode='w+', level=logging.INFO)

    prog = Program(args)
    await prog.run()

if __name__ == "__main__":
    try:
        app.run_forever(after_start=main())
    except FileNotFoundError:
        print('Error: could not connect to NFD for SVS.')
