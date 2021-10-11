#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs/

# NDN Imports
from ndn.encoding import Component
from ndn.encoding import TlvModel, UintField, BytesField, DecodeError

# Class Type: a tlv structure for encoding
# Class Purpose:
#   hold all aspects of MetaData in a Model
class MetaDataModel(TlvModel):
    source = BytesField(198)
    tseqno = UintField(199)
    nopcks = UintField(200)

# Class Type: a API class
# Class Purpose:
#   to make metadata model eaiser to interact with
class MetaData:
    __slots__ = ('source','tseqno','nopcks')
    def __init__(self, comp:Component=None) -> None:
        try:
            model = MetaDataModel.parse(bytes(Component.get_value(comp)))
            self.source = model.source
            self.tseqno = model.tseqno
            self.nopcks = model.nopcks
        except (ValueError,TypeError,IndexError,DecodeError):
            self.source = b''
            self.tseqno = 0
            self.nopcks = 0
    def encode(self) -> Component:
        model = MetaDataModel()
        model.source = self.source
        model.tseqno = self.tseqno
        model.nopcks = self.nopcks
        return Component.from_bytes(model.encode())