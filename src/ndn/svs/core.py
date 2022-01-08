#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs
#    @Documentation: https://ndn-python-svs.readthedocs.io

# Basic Libraries
import asyncio as aio
from enum import Enum
from random import uniform
from typing import Callable, Optional, Tuple, List
# NDN Imports
from ndn.app import NDNApp
from ndn.encoding import Name, InterestParam, BinaryStr, FormalName, SignaturePtrs
from ndn.types import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure
# Custom Imports
from .balancer import SVSyncBalancer
from .state_table import StateTable
from .meta_data import MetaData
from .state_vector import StateVector
from .scheduler import AsyncScheduler
from .security import SecurityOptions
from .logger import SVSyncLogger
from .missing_data import MissingData

# Class Type: an enumeration struct
# Class Purpose:
#   to differ core states.
class SVSyncCoreState(Enum):
    STEADY     = 0
    SUPRESSION = 1

# Class Type: a ndn class
# Class Purpose:
#   manage sync interests that are sent out.
#   to hear about other sync interests
#   to find out about new data from other nodes.
class SVSyncCore:
    INTERVAL = 30000
    INTERVAL_RANDOMNESS = 0.1
    BRIEF_INTERVAL = 200
    BRIEF_INTERVAL_RANDOMNESS = 0.5
    SYNC_INTEREST_LIFETIME = 1000
    def __init__(self, app:NDNApp, syncPrefix:Name, groupPrefix:Name, nid:Name, updateCallback:Callable, secOptions:SecurityOptions) -> None:
        SVSyncLogger.info("SVSyncCore: started svsync core")
        self.app, self.nid, self.updateCallback, self.syncPrefix, self.groupPrefix, self.secOptions, self.state = app, nid, updateCallback, syncPrefix, groupPrefix, secOptions, SVSyncCoreState.STEADY
        self.table = StateTable(self.nid)
        self.balancer = SVSyncBalancer(self.app, self.groupPrefix, self.nid, self.table, self.updateCallback, self.secOptions)
        self.app.route(self.syncPrefix, need_sig_ptrs=True)(self.onSyncInterest)
        SVSyncLogger.info(f'SVSyncCore: started listening to {Name.to_str(self.syncPrefix)}')
        self.scheduler = AsyncScheduler(self.sendSyncInterest, self.INTERVAL, self.INTERVAL_RANDOMNESS)
        self.scheduler.skip_interval()
    async def asyncSendSyncInterest(self) -> None:
        name:Name = self.syncPrefix + [self.table.getMetaData().encode()] + [ self.table.getPart(0) ]
        SVSyncLogger.info(f'SVSyncCore: sync {Name.to_str(name)}')
        try:
            data_name, meta_info, content = await self.app.express_interest(
                name, signer=self.secOptions.syncSig.signer, must_be_fresh=True, can_be_prefix=True, lifetime=self.SYNC_INTEREST_LIFETIME)
        except (InterestNack, InterestTimeout, InterestCanceled, ValidationFailure):
            pass
    def sendSyncInterest(self) -> None:
        aio.get_event_loop().create_task(self.asyncSendSyncInterest())
    def onSyncInterest(self, int_name:FormalName, int_param:InterestParam, _app_param:Optional[BinaryStr], sig_ptrs:SignaturePtrs) -> None:
        aio.get_event_loop().create_task(self.onSyncInterestHelper(int_name, int_param, _app_param, sig_ptrs))
    async def onSyncInterestHelper(self, int_name:FormalName, int_param:InterestParam, _app_param:Optional[BinaryStr], sig_ptrs:SignaturePtrs) -> None:
        isValidated:bool = await self.secOptions.syncVal.validate(int_name, sig_ptrs)
        if not isValidated:
            return

        incomingVector, incomingMetadata = StateVector(int_name[-2]), MetaData(int_name[-3])
        SVSyncLogger.info("SVSyncCore: >> I: received sync")
        SVSyncLogger.info(f'SVSyncCore:       rmeta {bytes(incomingMetadata.source).decode()} - {incomingMetadata.tseqno} total, {incomingMetadata.nopcks} pcks')
        SVSyncLogger.info(f'SVSyncCore:       {incomingVector.to_str()}')

        missingList:List[MissingData] = self.table.processStateVector(incomingVector, oldData=False)
        self.table.updateMetaData()
        if missingList:
            self.updateCallback(missingList)

        supress, equalize = self.compareMetaData(incomingMetadata)
        self.state = SVSyncCoreState.SUPRESSION if supress else SVSyncCoreState.STEADY

        # reset the sync timer if STEADY
        # supress the timer if SUPPRESION
        if self.state == SVSyncCoreState.STEADY:
            self.scheduler.set_cycle()
        else:
            delay = self.BRIEF_INTERVAL + round( uniform(-self.BRIEF_INTERVAL_RANDOMNESS,self.BRIEF_INTERVAL_RANDOMNESS)*self.BRIEF_INTERVAL )
            if self.scheduler.get_time_left() > delay:
                self.scheduler.set_cycle(delay)
        SVSyncLogger.info(f'SVSyncCore: state {self.state.name}')
        SVSyncLogger.info(f'SVSyncCore: parts-{self.table.getPartCuts()} | 1stlength-{len(self.table.getPart(0))}')
        SVSyncLogger.info(f'SVSyncCore: table {self.table.getCompleteStateVector().to_str()}')

        if equalize:
            await self.balancer.equalize(incomingMetadata)
    def compareMetaData(self, incoming_md:MetaData) -> Tuple[bool, bool]:
        table_md, supress, equalize = self.table.getMetaData(), False, False
        if table_md.tseqno > incoming_md.tseqno:
            supress = True
        elif table_md.tseqno < incoming_md.tseqno:
            equalize = True
        return (supress, equalize)
    def updateMyState(self, seqno:int) -> None:
        self.table.updateMyState(seqno)
        self.table.updateMetaData()
        self.scheduler.skip_interval()
    def getSeqno(self) -> int:
        seqno = self.table.getSeqno(self.nid)
        return seqno if seqno != None else 0
    def getStateTable(self) -> StateTable:
        return self.table