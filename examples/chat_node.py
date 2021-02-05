from argparse import ArgumentParser, SUPPRESS
import sys

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
    args = parser.parse_args()
    if args.group_prefix[-1] == "/":
        args.group_prefix = args.group_prefix[:-1]
    if args.group_prefix[0] != "/":
        args.group_prefix = "/" + args.group_prefix
    return args

class Program:
    def __init__(self, cmdline_args):
        pass
    def run(self):
        pass

def main() -> int:
    cmdline_args = process_cmd_args() # Process Command Line Arguments
    program = Program(cmdline_args)
    program.run()

if __name__ == "__main__":
    sys.exit(main())
