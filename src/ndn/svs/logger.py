import logging
import sys
from typing import Optional

class SVSyncLogger(object):
    _loggerName = "ndn-svs"
    _loggerLevel = logging.DEBUG
    _loggerFormat = "(%(asctime)s) %(name)s:%(levelname)s | %(message)s"
    _consoleLogging = False
    _fileForLogging = None
    _logger = None
    _configured = False

    @staticmethod
    def config(consoleLogging:bool, fileForLogging:Optional[str], level:int, format:Optional[str]=None) -> None:
        if not SVSyncLogger._configured:
            SVSyncLogger._configured = True
            SVSyncLogger._loggerLevel = level
            SVSyncLogger._consoleLogging = consoleLogging
            SVSyncLogger._fileForLogging = fileForLogging
            SVSyncLogger._loggerFormat = format if format else SVSyncLogger._loggerFormat

            SVSyncLogger._logger = logging.getLogger(SVSyncLogger._loggerName)
            SVSyncLogger._logger.setLevel(SVSyncLogger._loggerLevel)
            fm = logging.Formatter(SVSyncLogger._loggerFormat)
            if SVSyncLogger._consoleLogging:
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setFormatter(fm)
                SVSyncLogger._logger.addHandler(console_handler)
            if SVSyncLogger._fileForLogging:
                file_handler = logging.FileHandler(SVSyncLogger._fileForLogging)
                file_handler.setFormatter(fm)
                SVSyncLogger._logger.addHandler(file_handler)
            SVSyncLogger._logger.propagate = False

    @staticmethod
    def debug(msg:str) -> None:
        if SVSyncLogger._configured:
            SVSyncLogger._logger.debug(msg)
    @staticmethod
    def info(msg:str) -> None:
        if SVSyncLogger._configured:
            SVSyncLogger._logger.info(msg)
    @staticmethod
    def warning(msg:str) -> None:
        if SVSyncLogger._configured:
            SVSyncLogger._logger.warning(msg)
    @staticmethod
    def error(msg:str) -> None:
        if SVSyncLogger._configured:
            SVSyncLogger._logger.error(msg)
    @staticmethod
    def critical(msg:str) -> None:
        if SVSyncLogger._configured:
            SVSyncLogger._logger.critical(msg)