from argparse import ArgumentParser, SUPPRESS
import logging
from ndn.app import NDNApp
import sys
import asyncio as aio

def process_cmd_args():
    log_levels = ['CRITICAL','ERROR','WARNING','INFO','DEBUG']
    # Command Line Parser
    parser = ArgumentParser(add_help=False,description="An SVS Node")
    requiredArgs = parser.add_argument_group("required arguments")
    optionalArgs = parser.add_argument_group("optional arguments")
    # Adding All Command Line Arguments
    requiredArgs.add_argument("-gp","--groupprefix",required=True,help="group prefix to listen from")
    optionalArgs.add_argument("-lf","--logfile",help="logfile to push logging to, stdout by default")
    optionalArgs.add_argument("-ll","--loglevel",choices=log_levels,help="loglevel to record")
    optionalArgs.add_argument("-h","--help",action="help",default=SUPPRESS,help="show this help message and exit")
    # Getting All Arugments
    return vars(parser.parse_args())

def config_logging(cmdline_args):
    log_levels = {
        'CRITICAL': logging.CRITICAL,
        'ERROR': logging.ERROR,
        'WARNING': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG
    }
    log_level = cmdline_args["loglevel"] if cmdline_args["loglevel"] else "INFO"

    if not cmdline_args["logfile"]:
        logging.basicConfig(format='[%(asctime)s]%(levelname)s:%(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=log_level)
    else:
        logging.basicConfig(filename=cmdline_args["logfile"], format='[%(asctime)s]%(levelname)s:%(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=log_level)

def main() -> int:
    cmdline_args = process_cmd_args() # Process Command Line Arguments
    config_logging(cmdline_args)      # Setup Logging

    app = NDNApp()                    # Start the NDN App


    #storage = create_storage()

    #pb = PubSub(app)
    #read_handle = ReadHandle(app, storage, config)
    #write_handle = WriteCommandHandle(app, storage, pb, read_handle, config)
    #delete_handle = DeleteCommandHandle(app, storage, pb, read_handle, config)
    #tcp_bulk_insert_handle = TcpBulkInsertHandle(storage, read_handle, config)

    #svs = SVS(app, storage, read_handle, write_handle, delete_handle, tcp_bulk_insert_handle, config)
    #aio.ensure_future(svs.listen())

    try:
        app.run_forever()
    except FileNotFoundError:
        print('Error: could not connect to NFD.')
    return 0

if __name__ == "__main__":
    sys.exit(main())
