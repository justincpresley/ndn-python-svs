#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs
#    @Documentation: https://ndn-python-svs.readthedocs.io

# Basic Libraries
from enum import Enum

# Class Type: an enumeration struct
# Class Purpose:
#   to differ tlv model types.
class SVSyncTlvTypes(Enum):
    VECTOR       = 201
    VECTOR_KEY   = 202
    VECTOR_VALUE = 204
