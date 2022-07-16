#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs
#    @Documentation: https://ndn-python-svs.readthedocs.io

NDN_MTU = 8800

INTERVAL = 30000
INTERVAL_RANDOMNESS = 0.1
BRIEF_INTERVAL = 200
BRIEF_INTERVAL_RANDOMNESS = 0.5

PROP_INTEREST_LIFETIME = 2000
PROP_PACKET_FRESHNESS = 5000
DATA_INTEREST_LIFETIME = 2000
DATA_PACKET_FRESHNESS = 10000
SYNC_INTEREST_LIFETIME = 1000

PROP_WINDOW = 5
TRACKER_DIFFERENCE = 1000