#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs
#    @Documentation: https://ndn-python-svs.readthedocs.io

# Basic Libraries
import logging
import sys
import time
from argparse import ArgumentParser, SUPPRESS
from typing import List, Callable, Optional
# NDN Imports
from ndn.encoding import Name
# Custom Imports
sys.path.insert(0,'.')
from src.ndn.svs import SVSync_Thread, SVSyncBase_Thread, SVSyncLogger, MissingData

def parse_cmd_args() -> dict:
    # Command Line Parser
    parser = ArgumentParser(add_help=False,description="An SVS Heartbeat Node capable of letting others know its alive.")
    requiredArgs = parser.add_argument_group("required arguments")
    optionalArgs = parser.add_argument_group("optional arguments")
    informationArgs = parser.add_argument_group("information arguments")
    # Adding all Command Line Arguments
    requiredArgs.add_argument("-n", "--nodename",action="store",dest="node_name",required=True,help="id of this node in svs")
    optionalArgs.add_argument("-gp","--groupprefix",action="store",dest="group_prefix",required=False,help="overrides config | routable group prefix to listen from")
    optionalArgs.add_argument("-i","--interval",action="store",dest="interval",type=int,default=3,required=False,help="interval at which beats are published")
    optionalArgs.add_argument("-v","--verbose",action="store_true",dest="verbose",default=False,required=False,help="when set, svsync info is displayed as well")
    informationArgs.add_argument("-h","--help",action="help",default=SUPPRESS,help="show this help message and exit")
    # Getting all Arguments
    argvars = parser.parse_args()
    args = {}
    args["group_prefix"] = argvars.group_prefix if argvars.group_prefix is not None else "/svs"
    args["node_id"] = argvars.node_name
    args["verbose"] = argvars.verbose
    args["interval"] = argvars.interval
    return args

class HeartTracker:
    class HeartInfo:
        __slots__ = ('past_beat','cycles','alive')
        def __init__(self) -> None:
            self.past_beat, self.cycles, self.alive = 0, 0, False
    def __init__(self, nn:str, hr:int, tr:int, bte:int, btr:int):
        self.hearts,self.nid,self.heartbeat_rate,self.tracker_rate,self.beats_to_expire,self.beats_to_renew = {},nn,hr,tr,bte,btr
    def reset(self, nid:str):
        try:
            heart = self.hearts[nid]
        except KeyError:
            heart = self.HeartInfo()
            self.hearts[nid] = heart
        heart.past_beat = time.perf_counter() * 1000
        if heart.alive:
            heart.cycles = 0
        else:
            heart.cycles += 1
            if heart.cycles >= self.beats_to_renew:
                heart.cycles = 0
                heart.alive = True
                print(f"Node {nid} renewed!")
    def detect(self):
        for nid in list(self.hearts):
            heart = self.hearts[nid]
            time_past = (time.perf_counter()*1000) - heart.past_beat
            if not heart.alive and time_past > self.tracker_rate:
                heart.cycles = 0
            elif time_past > self.tracker_rate:
                heart.cycles = time_past // self.tracker_rate
                if heart.cycles >= self.beats_to_expire:
                    heart.cycles = 0
                    heart.alive = False
                    print(f"Node {nid} expired!")
    def beat(self):
        try:
            time_past = (time.perf_counter()*1000) - self.hearts[self.nid].past_beat
            if time_past >= self.heartbeat_rate:
                return True
        except KeyError:
            return True
        return False

class Program:
    def __init__(self, args:dict) -> None:
        self.args = args
        self.tracker = HeartTracker(self.args["node_id"], self.args["interval"]*1000, (self.args["interval"]+1)*1000, 3, 3)
        self.svs_thread:SVSync_Thread = SVSync_Thread(Name.from_str(self.args["group_prefix"]), Name.from_str(self.args["node_id"]), self.on_missing)
        self.svs_thread.daemon = True
        self.svs_thread.start()
        self.svs_thread.wait()
        print(f'SVS beats started | {self.args["group_prefix"]} - {self.args["node_id"]} |')
    def run(self) -> None:
        while 1:
            try:
                self.tracker.detect()
                if self.tracker.beat():
                    self.svs_thread.getCore().updateMyState(self.svs_thread.getCore().getSeqno()+1)
                    self.tracker.reset(self.args["node_id"])
            except KeyboardInterrupt:
                sys.exit()
    def on_missing(self, thread:SVSyncBase_Thread) -> Callable:
        async def wrapper(missing_list:List[MissingData]) -> None:
            for i in missing_list:
                self.tracker.reset(i.nid)
        return wrapper

def main() -> int:
    args = parse_cmd_args()
    args["node_id"] = Name.to_str(Name.from_str(args["node_id"]))
    args["group_prefix"] = Name.to_str(Name.from_str(args["group_prefix"]))

    SVSyncLogger.config(True if args["verbose"] else False, None, logging.INFO)

    prog = Program(args)
    prog.run()

    return 0

if __name__ == "__main__":
    sys.exit(main())