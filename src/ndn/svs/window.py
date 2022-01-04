#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs
#    @Documentation: https://ndn-python-svs.readthedocs.io

# Basic Libraries
from queue import Queue
import asyncio as aio
from typing import Callable, Tuple

# Class Type: an async class
# Class Purpose:
#   to have a window-based method dealing with asyncio tasks
class AsyncWindow:
    class TaskItem:
        __slots__ = ('function','args')
        def __init__(self, function:Callable, args:Tuple) -> None:
            self.function, self.args = function, args
    def __init__(self, windowSize:int) -> None:
        self.maxWindow, self.currtasks, self.tasks = windowSize, [], Queue()
    def addTask(self, function:Callable, args:Tuple) -> None:
        task:TaskItem = self.TaskItem(function, args)
        self.tasks.put(task)
        self._processQueue()
    async def gather(self) -> None:
        while self.tasks.qsize() != 0 or self.currtasks:
            await aio.sleep(0.001)
    def getNumTasks(self) -> int:
        return self.tasks.qsize()
    def getWindowSize(self) -> int:
        return self.maxWindow
    async def _task(self, task:TaskItem) -> None:
        await task.function(*task.args)
        self.currtasks.remove(task)
        self._processQueue()
    def _processQueue(self) -> None:
        while self.tasks.qsize()>0 and len(self.currtasks)<self.maxWindow:
            task = self.tasks.get_nowait()
            self.currtasks.append(task)
            aio.create_task(self._task(task))