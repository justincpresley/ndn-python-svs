import sys
from ndn.encoding import SignatureType, Name
sys.path.insert(0,'.')
from src.ndn.svs.svs_security import SVSyncSecurity

def main() -> int:
    typess = SignatureType.SHA256_WITH_ECDSA
    key_name = Name.from_str("/svs")
    sec = SVSyncSecurity(typess, key_name, None, b'')
    print("PASSED")

if __name__ == "__main__":
    sys.exit(main())
