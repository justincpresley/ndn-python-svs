#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs
#    @Documentation: https://ndn-python-svs.readthedocs.io

# Basic Libraries
import asyncio as aio
import logging
from enum import Enum
from random import uniform
from typing import Callable, Optional
# NDN Imports
from ndn.app import NDNApp
from ndn.encoding import Name, InterestParam, BinaryStr, FormalName, SignaturePtrs
from ndn.types import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure
# Custom Imports
from .state_vector import StateVector
from .scheduler import AsyncScheduler
from .security import SecurityOptions

# Class Type: a struct
# Class Purpose:
#   to hold the range of missing data for a specific node.
class MissingData:
    __slots__ = ('nid','lowSeqno','highSeqno')
    def __init__(self, nid:str, lowSeqno:int, highSeqno:int) -> None:
        self.nid        = nid
        self.lowSeqno   = lowSeqno
        self.highSeqno  = highSeqno

# Class Type: an enumeration struct
# Class Purpose:
#   to differ core states.
class SVSyncCore_State(Enum):
    STEADY     = 0
    SUPRESSION = 1

# Class Type: a ndn class
# Class Purpose:
#   manage sync interests that are sent out.
#   to hear about other sync interests
#   to find out about new data from other nodes.
class SVSyncCore:
    def __init__(self, app:NDNApp, syncPrefix:Name, nid:Name, updateCallback:Callable, secOptions:SecurityOptions) -> None:
        logging.info(f'SVSyncCore: started svsync core')
        self.state = SVSyncCore_State.STEADY
        self.app = app
        self.nid = nid
        self.updateCallback = updateCallback
        self.syncPrefix = syncPrefix
        self.secOptions = secOptions
        self.vector = StateVector()
        self.seqno = 0
        self.interval = 30000 # time in milliseconds
        self.randomPercent = 0.1
        self.briefInterval = 200 # time in milliseconds
        self.briefRandomPercent = 0.5
        self.app.route(self.syncPrefix, need_sig_ptrs=True)(self.onSyncInterest)
        logging.info(f'SVSyncCore: started listening to {Name.to_str(self.syncPrefix)}')
        self.scheduler = AsyncScheduler(self.sendSyncInterest, self.interval, self.randomPercent)
        self.scheduler.skip_interval()
    async def asyncSendSyncInterest(self) -> None:
        name = self.syncPrefix + [ self.vector.to_component() ]
        logging.info(f'SVSyncCore: sent sync {Name.to_str(name)}')
        try:
            data_name, meta_info, content = await self.app.express_interest(
                name, signer=self.secOptions.syncSig.signer, must_be_fresh=True, can_be_prefix=True, lifetime=1000)
        except (InterestNack, InterestTimeout, InterestCanceled, ValidationFailure) as e:
            pass
    def sendSyncInterest(self) -> None:
        aio.get_event_loop().create_task(self.asyncSendSyncInterest())
    def mergeStateVector(self, otherVector:StateVector) -> None:
        myVectorNew = False
        otherVectorNew = False
        missingList = []

        # check if other vector has a newer state
        for key in otherVector.keys():
            mySeq = self.vector.get(key)
            otherSeq = otherVector.get(key)

            if mySeq < otherSeq:
                otherVectorNew = True
                temp = MissingData(key, mySeq+1, otherSeq)
                self.vector.set(key, otherSeq)
                missingList.append(temp)

        # callback if missing data found
        if missingList:
            self.updateCallback(missingList)

        # check if my vector has a newer state
        for key in self.vector.keys():
            mySeq = self.vector.get(key)
            otherSeq = otherVector.get(key)
            if otherVector.get(key) < self.vector.get(key):
                myVectorNew = True

        # return bools
        return (myVectorNew, otherVectorNew)
    def onSyncInterest(self, int_name:FormalName, int_param:InterestParam, _app_param:Optional[BinaryStr], sig_ptrs:SignaturePtrs) -> None:
        logging.info(f'SVSyncCore: received sync {Name.to_str(int_name)}')
        aio.get_event_loop().create_task(self.onSyncInterestHelper(int_name, int_param, _app_param, sig_ptrs))
    async def onSyncInterestHelper(self, int_name:FormalName, int_param:InterestParam, _app_param:Optional[BinaryStr], sig_ptrs:SignaturePtrs) -> None:
        isValidated = await self.secOptions.syncVal.validate(int_name, sig_ptrs)
        if not isValidated:
            return

        incomingVector = StateVector(int_name[-2])

        myVectorNew, incomingVectorNew = self.mergeStateVector(incomingVector)
        self.state = SVSyncCore_State.SUPRESSION if myVectorNew else SVSyncCore_State.STEADY

        # reset the sync timer if STEADY
        # supress the timer if SUPPRESION
        if self.state == SVSyncCore_State.STEADY:
            self.scheduler.set_cycle()
        else:
            delay = self.briefInterval + round( uniform(-self.briefRandomPercent,self.briefRandomPercent)*self.briefInterval )
            if self.scheduler.get_time_left() > delay:
                self.scheduler.set_cycle(delay)
        logging.info(f'SVSyncCore: state {self.state.name}')
        logging.info(f'SVSyncCore: vector {self.vector.to_str()}')
    def updateStateVector(self, seqno:int, nid:Name=None) -> None:
        if not nid:
            nid = self.nid
        if Name.to_str(nid) == Name.to_str(self.nid):
            self.seqno = seqno
        self.vector.set(Name.to_str(nid), seqno)
        self.scheduler.skip_interval()
    def getSeqno(self) -> int:
        return self.seqno
    def getStateVector(self) -> StateVector:
        return self.vector