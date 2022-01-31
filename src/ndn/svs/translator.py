#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs
#    @Documentation: https://ndn-python-svs.readthedocs.io

# Basic Libraries
from typing import Optional
# NDN Imports
from ndn.app import NDNApp
from ndn.encoding import Name, Component, InterestParam, BinaryStr, FormalName, SignaturePtrs, parse_data
from ndn.types import InterestNack, InterestTimeout, InterestCanceled, ValidationFailure
# Custom Imports
from .plot_container import PlotContainer

# Class Type: a ndn class
# Class Purpose:
#   manage plot interests that are sent out.
#   to fetch and serve plots
class SVSyncTranslator:
    TRANSLATIONS_IN_PACKET = 85
    PLOT_INTEREST_LIFETIME = 2000
    PLOT_PACKET_FRESHNESS = 11000
    def __init__(self, app:NDNApp, groupPrefix:Name, nid:Name, storage:Storage, secOptions:SecurityOptions) -> None:
        SVSyncLogger.info("SVSyncTranslator: started svsync translator")
        self.app, self.groupPrefix, self.nid, self.storage, self.secOptions = app, groupPrefix, nid, storage, secOptions
        self.container, self.plotPrefix, self.nidstr = PlotContainer(self.nid, self.TRANSLATIONS_IN_PACKET), nid + groupPrefix + [Component.from_str("plot")], Name.to_str(nid)
        self.app.route(self.plotPrefix, need_sig_ptrs=True)(self.onPlotInterest)
        SVSyncLogger.info(f'SVSyncTranslator: started listening to {Name.to_str(self.plotPrefix)}')
    def roundPlotno(plotno:int) -> int:
        return (plotno//self.TRANSLATIONS_IN_PACKET) if (plotno%self.TRANSLATIONS_IN_PACKET)>0 else (plotno//self.TRANSLATIONS_IN_PACKET)+1
    def onPlotInterest(self, int_name:FormalName, int_param:InterestParam, _app_param:Optional[BinaryStr], sig_ptrs:SignaturePtrs) -> None:
        #nid, plotno = self.parsePlotName(int_name)
        # check storage
        data_pkt = self.storage.get_packet(int_name, int_param.can_be_prefix)
        if data_pkt:
            SVSyncLogger.info(f'SVSyncTranslator: served plot {Name.to_str(int_name)}')
            self.app.put_raw_packet(data_pkt)
        # check storage for next up and provide forwarding hint
        #rounded_name = self.getPlotName(nid, self.roundPlotno(plotno))
        #data_pkt = self.storage.get_packet(rounded_name, int_param.can_be_prefix)
        #if data_pkt:
            #SVSyncLogger.info(f'SVSyncTranslator: forwarding plot {Name.to_str(int_name)}')
            #self.app.put_data(int_name, content=Name.to_bytes(rounded_name), content_type=ContentType.LINK)
    def provideTranslation(seqno:int, label:str) -> None:
        self.container.add(self.nidstr, seqno, label)
        name = self.getPlotName(self.nidstr, seqno)
        data_packet = make_data(name, MetaInfo(freshness_period=self.PLOT_PACKET_FRESHNESS), content=self.container.encode(), signer=self.secOptions.dataSig.signer)
        SVSyncLogger.info(f'SVSyncTranslator: providing plot {Name.to_str(name)}')
        self.storage.put_packet(name, data_packet)
    def getTranslation(nid:str, seqno:int) -> Optional[str]:
        return self.container.find(nid, seqno)
    def getPlotName(self, nid:Name, plotno:int) -> Name:
        return ( nid + self.groupPrefix + [Component.from_str("plot")] + [Component.from_str(str(seqno))] )
    def parsePlotName(self, int_name:FormalName) -> Tuple[Name,int]:
        raise NotImplementedError
    async def _fetch(self, nid:Name, seqno:int, retries:int=0) -> Tuple[Optional[bytes], Optional[BinaryStr]]:
        name = self.getPlotName(nid, seqno)
        while retries+1 > 0:
            try:
                SVSyncLogger.info(f'SVSyncTranslator: fetching plot {Name.to_str(name)}')
                _, _, _, pkt = await self.app.express_interest(name, need_raw_packet=True, must_be_fresh=True, can_be_prefix=False, lifetime=self.PLOT_INTEREST_LIFETIME)
                ex_int_name, meta_info, content, sig_ptrs = parse_data(pkt)
                isValidated = await self.secOptions.validate(ex_int_name, sig_ptrs)
                if not isValidated:
                    return (None, None)
                SVSyncLogger.info(f'SVSyncTranslator: received plot {bytes(content)}')
                return (bytes(content), pkt) if content else (None, pkt)
            except InterestNack as e:
                SVSyncLogger.warning(f'SVSyncTranslator: nacked with reason={e.reason}')
            except InterestTimeout:
                SVSyncLogger.warning("SVSyncTranslator: timeout")
            except InterestCanceled:
                SVSyncLogger.warning("SVSyncTranslator: canceled")
            except ValidationFailure:
                SVSyncLogger.warning("SVSyncTranslator: data failed to validate")
            except Exception as e:
                SVSyncLogger.warning(f'SVSyncTranslator: unknown error has occured: {e}')

            retries = retries - 1
            if retries+1 > 0:
                SVSyncLogger.info("SVSyncTranslator: retrying fetching plot")
        return (None, None)
    async def fetchPlot(self, nid:Name, seqno:int, retries:int=0) -> Optional[bytes]:
        data, _ = await self._fetch(nid, seqno, retries)
        if data:
            return data
        else:
            data, _ = await self._fetch(nid, self.roundPlotno(seqno), retries)
            return data