#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs
#    @Documentation: https://ndn-python-svs.readthedocs.io

# Class Type: an exception thats raised
# Class Purpose:
#   to let the user know that an SVS thread was not waited on.
class SVSyncUnwaitedThread(Exception):
    pass

# Class Type: an exception thats raised
# Class Purpose:
#   to let the user know that an SVS publication exceeded the maximum NDN MTU possible
class SVSyncPublicationTooLarge(Exception):
    pass