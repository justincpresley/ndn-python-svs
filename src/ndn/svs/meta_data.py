#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs
#    @Documentation: https://ndn-python-svs.readthedocs.io

# NDN Imports
from ndn.encoding import Component, TlvModel, UintField, BytesField, DecodeError
# Custom Imports
from .tlv import SVSyncTlvTypes

# Class Type: a tlv structure for encoding
# Class Purpose:
#   hold all aspects of MetaData in a Model
class MetaDataModel(TlvModel):
    source = BytesField(SVSyncTlvTypes.META_SOURCE.value)
    tseqno = UintField(SVSyncTlvTypes.META_TOTAL.value)
    nopcks = UintField(SVSyncTlvTypes.META_NOPCKS.value)

# Class Type: a API class
# Class Purpose:
#   to make metadata model eaiser to interact with
class MetaData:
    __slots__ = ('source','tseqno','nopcks')
    def __init__(self, comp:Component=None) -> None:
        try:
            model:MetaDataModel = MetaDataModel.parse(bytes(Component.get_value(comp)))
            self.source, self.tseqno, self.nopcks = model.source, model.tseqno, model.nopcks
        except (ValueError,TypeError,IndexError,DecodeError):
            self.source, self.tseqno, self.nopcks = b'', 0, 0
    def encode(self) -> Component:
        model:MetaDataModel = MetaDataModel()
        model.source, model.tseqno, model.nopcks = self.source, self.tseqno, self.nopcks
        return Component.from_bytes(model.encode())