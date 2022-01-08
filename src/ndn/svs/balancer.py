#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs
#    @Documentation: https://ndn-python-svs.readthedocs.io

# Basic Libraries
import asyncio as aio
from typing import Optional, Callable
# NDN Imports
from ndn.app import NDNApp
from ndn.encoding import Name, Component, InterestParam, BinaryStr, FormalName, SignaturePtrs, parse_data
from ndn.types import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure
# Custom Imports
from .logger import SVSyncLogger
from .meta_data import MetaData
from .security import SecurityOptions
from .state_table import StateTable
from .state_vector import StateVector
from .window import AsyncWindow

# Class Type: a ndn class
# Class Purpose:
#   manage sync interests that are sent out.
#   to hear about other sync interests
#   to find out about new data from other nodes.
class SVSyncBalancer:
    PROP_WINDOW = 5
    PROP_INTEREST_LIFETIME = 2000
    PROP_PACKET_FRESHNESS = 5000
    def __init__(self, app:NDNApp, groupPrefix:Name, nid:Name, table:StateTable, updateCallback:Callable, secOptions:SecurityOptions) -> None:
        SVSyncLogger.info("SVSyncBalancer: started svsync balancer")
        self.app, self.groupPrefix, self.nid, self.table, self.updateCallback, self.secOptions, self.busy = app, groupPrefix, nid, table, updateCallback, secOptions, False
        self.propPrefix = self.nid + self.groupPrefix + [Component.from_str("prop")]
        self.taskWindow = AsyncWindow(self.PROP_WINDOW)
        self.app.route(self.propPrefix, need_sig_ptrs=True)(self.onPropInterest)
        SVSyncLogger.info(f'SVSyncBalancer: started listening to {Name.to_str(self.propPrefix)}')
    async def balanceFromProp(self, name:Name, pckno:int) -> None:
        incoming_sv:Optional[StateVector] = await self.sendPropInterest(name, pckno)
        if not incoming_sv:
            return
        missingList = self.table.processStateVector(incoming_sv, oldData=True)
        if missingList:
            self.updateCallback(missingList)
        self.table.updateMetaData()
    async def equalize(self, incoming_md:MetaData) -> None:
        if incoming_md.tseqno <= self.table.getMetaData().tseqno or self.busy:
            return
        self.busy = True
        name = Name.from_str(bytes(incoming_md.source).decode())
        for i in range(incoming_md.nopcks):
            self.taskWindow.addTask(self.balanceFromProp, (name, i+1))
        await self.taskWindow.gather()
        SVSyncLogger.info(f'SVSyncBalancer: nmeta {bytes(self.table.getMetaData().source).decode()} - {self.table.getMetaData().tseqno} total, {self.table.getMetaData().nopcks} pcks')
        SVSyncLogger.info(f'SVSyncBalancer: ntable {self.table.getCompleteStateVector().to_str()}')
        self.busy = False
    def onPropInterest(self, int_name:FormalName, int_param:InterestParam, _app_param:Optional[BinaryStr], sig_ptrs:SignaturePtrs) -> None:
        SVSyncLogger.info(f'SVSyncBalancer: received balance {Name.to_str(int_name)}')
        aio.get_event_loop().create_task(self.onPropInterestHelper(int_name, int_param, _app_param, sig_ptrs))
    async def onPropInterestHelper(self, int_name:FormalName, int_param:InterestParam, _app_param:Optional[BinaryStr], sig_ptrs:SignaturePtrs) -> None:
        sv = bytes(self.table.getPart(Component.to_number(int_name[-1])))
        SVSyncLogger.info(f'SVSyncBalancer: sending balance {sv}')
        self.app.put_data(int_name, content=sv, signer=self.secOptions.dataSig.signer, freshness_period=self.PROP_PACKET_FRESHNESS)
    async def sendPropInterest(self, source:Name, pckno:int) -> Optional[StateVector]:
        name:Name = source + self.groupPrefix + [Component.from_str("prop")] + [Component.from_number(pckno, Component.TYPE_SEQUENCE_NUM)]
        try:
            SVSyncLogger.info(f'SVSyncBalancer: balancing by {Name.to_str(name)}')
            _, _, _, pkt = await self.app.express_interest(
                name, need_raw_packet=True, must_be_fresh=True, can_be_prefix=False, lifetime=self.PROP_INTEREST_LIFETIME)
            int_name, meta_info, content, sig_ptrs = parse_data(pkt)
            isValidated = await self.secOptions.validate(int_name, sig_ptrs)
            return StateVector(bytes(content)) if bytes(content) != b'' and isValidated else None
        except (InterestNack, InterestTimeout, InterestCanceled, ValidationFailure):
            SVSyncLogger.info(f'SVSyncBalancer: failed to get {Name.to_str(name)}')
            return None
    def isBusy(self) -> bool:
        return self.busy