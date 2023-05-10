#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs
#    @Documentation: https://ndn-python-svs.readthedocs.io

# Basic Libraries
import logging
from sys import stdout
from typing import Optional

# Class Type: a logging class
# Class Purpose:
#   to properly handle all logging within this library
class SVSyncLogger(object):
    LOGGER_NAME = "ndn-svs"
    LOGGER_LEVEL = logging.DEBUG
    LOGGER_FORMAT = "(%(asctime)s) %(name)s:%(levelname)s | %(message)s"
    CONSOLE_LOGGING = False
    LOGGER_FILE = None
    LOGGER = None
    CONFIGURED = False

    @staticmethod
    def config(console:bool, file:Optional[str], level:int, lformat:Optional[str]=None) -> None:
        if not SVSyncLogger.CONFIGURED:
            SVSyncLogger.CONFIGURED = True
            SVSyncLogger.LOGGER_LEVEL = level
            SVSyncLogger.CONSOLE_LOGGING = console
            SVSyncLogger.LOGGER_FILE = file
            SVSyncLogger.LOGGER_FORMAT = lformat if lformat else SVSyncLogger.LOGGER_FORMAT

            SVSyncLogger.LOGGER = logging.getLogger(SVSyncLogger.LOGGER_NAME)
            SVSyncLogger.LOGGER.setLevel(SVSyncLogger.LOGGER_LEVEL)
            fm = logging.Formatter(SVSyncLogger.LOGGER_FORMAT)
            if SVSyncLogger.CONSOLE_LOGGING:
                console_handler = logging.StreamHandler(stdout)
                console_handler.setFormatter(fm)
                SVSyncLogger.LOGGER.addHandler(console_handler)
            if SVSyncLogger.LOGGER_FILE:
                file_handler = logging.FileHandler(SVSyncLogger.LOGGER_FILE)
                file_handler.setFormatter(fm)
                SVSyncLogger.LOGGER.addHandler(file_handler)
            SVSyncLogger.LOGGER.propagate = False

    @staticmethod
    def debug(msg:str) -> None:
        if SVSyncLogger.CONFIGURED:
            SVSyncLogger.LOGGER.debug(msg)
    @staticmethod
    def info(msg:str) -> None:
        if SVSyncLogger.CONFIGURED:
            SVSyncLogger.LOGGER.info(msg)
    @staticmethod
    def warning(msg:str) -> None:
        if SVSyncLogger.CONFIGURED:
            SVSyncLogger.LOGGER.warning(msg)
    @staticmethod
    def error(msg:str) -> None:
        if SVSyncLogger.CONFIGURED:
            SVSyncLogger.LOGGER.error(msg)
    @staticmethod
    def critical(msg:str) -> None:
        if SVSyncLogger.CONFIGURED:
            SVSyncLogger.LOGGER.critical(msg)