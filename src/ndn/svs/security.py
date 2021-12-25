#    @Author: Justin C Presley
#    @Author-Email: justincpresley@gmail.com
#    @Project: NDN State Vector Sync Protocol
#    @Source-Code: https://github.com/justincpresley/ndn-python-svs
#    @Pip-Library: https://pypi.org/project/ndn-svs
#    @Documentation: https://ndn-python-svs.readthedocs.io

# Basic Libraries
from Cryptodome.Hash import SHA256, HMAC
from Cryptodome.PublicKey import ECC, RSA
from Cryptodome.Signature import DSS, pkcs1_15
from typing import Union, Optional, Dict
# NDN Imports
from ndn.encoding import FormalName, SignaturePtrs, Name, SignatureType
from ndn.security import Sha256WithEcdsaSigner, Sha256WithRsaSigner, HmacSha256Signer, DigestSha256Signer, sha256_digest_checker
from ndn.types import Validator
# Custom Imports
from .logger import SVSyncLogger

# Class Type: a struct
# Class Purpose:
#   to hold all signature information including the signer and info used to make the signer
class SigningInfo:
    __slots__ = ('signer','type','keyName','privKey')
    def __init__(self, stype:SignatureType, keyName:Optional[str]=None, privKey:Optional[bytes]=None) -> None:
        self.type, self.signer, self.keyName, self.privKey = stype, None, "", b''

        if self.type != SignatureType.DIGEST_SHA256 and self.type != SignatureType.NOT_SIGNED:
            if privKey is None or privKey == b'':
                raise KeyError("Private Key has to be Defined in Signing Info with this Type.")
            if keyName is None or keyName == "":
                raise KeyError("Key Name has to be Defined in Signing Info with this Type.")
            self.keyName = keyName
            self.privKey = privKey

        if self.type == SignatureType.SHA256_WITH_ECDSA:
            self.signer = Sha256WithEcdsaSigner(Name.from_str(self.keyName), self.privKey)
        elif self.type == SignatureType.SHA256_WITH_RSA:
            self.signer = Sha256WithRsaSigner(Name.from_str(self.keyName), self.privKey)
        elif self.type == SignatureType.HMAC_WITH_SHA256:
            self.signer = HmacSha256Signer(Name.from_str(self.keyName), self.privKey)
        elif self.type == SignatureType.DIGEST_SHA256:
            self.signer = DigestSha256Signer()

# Class Type: a struct with some methods
# Class Purpose:
#   to hold a validator for a specific signature
#   to have a class to generate a basic validator for a certain type
class ValidatingInfo:
    __slots__ = ('validator')
    def __init__(self, validator:Optional[Validator]) -> None:
        self.validator  = validator
    async def validate(self, name:FormalName, sig_ptrs:SignaturePtrs) -> bool:
        if self.validator:
            return await self.validator(name, sig_ptrs)
        return True

    @staticmethod
    def get_validator(stype:SignatureType, keyName:Optional[str]=None, pubKey:Optional[bytes]=None):
        if stype != SignatureType.DIGEST_SHA256 and stype != SignatureType.NOT_SIGNED:
            if pubKey is None or pubKey == b'':
                raise KeyError("Public Key has to be Defined when Generating a Validator with this Type.")
            if keyName is None or keyName == "":
                raise KeyError("Key Name has to be Defined when Generating a Validator with this Type.")
        if stype == SignatureType.SHA256_WITH_ECDSA:
            return ValidatingInfo._ecdsa_checker(Name.from_str(keyName), pubKey)
        if stype == SignatureType.SHA256_WITH_RSA:
            return ValidatingInfo._rsa_checker(Name.from_str(keyName), pubKey)
        if stype == SignatureType.HMAC_WITH_SHA256:
            return ValidatingInfo._hmac_checker(Name.from_str(keyName), pubKey)
        if stype == SignatureType.DIGEST_SHA256:
            return ValidatingInfo._digest_checker()
        return None
    @staticmethod
    def _ecdsa_checker(key_name:FormalName, key_bits:Union[bytes, str]) -> Validator:
        async def wrapper(name:FormalName, sig:SignaturePtrs) -> bool:
            nonlocal key_bits
            sig_info = sig.signature_info
            covered_part = sig.signature_covered_part
            sig_value = sig.signature_value_buf
            if sig_info and sig_info.signature_type == SignatureType.SHA256_WITH_ECDSA:
                if sig_info.key_locator.name != key_name:
                    return False
                pub_key = ECC.import_key(key_bits)
                verifier = DSS.new(pub_key, 'fips-186-3', 'der')
                sha256_algo = SHA256.new()
                if not covered_part or not sig_value:
                    ret = False
                else:
                    for blk in covered_part:
                        sha256_algo.update(blk)
                    try:
                        verifier.verify(sha256_algo, bytes(sig_value))
                        return True
                    except ValueError:
                        return False
                SVSyncLogger.debug(f'Digest check {Name.to_str(name)} -> {ret}')
                return ret
            return False
        return wrapper
    @staticmethod
    def _rsa_checker(key_name:FormalName, key_bits:Union[bytes, str]) -> Validator:
        async def wrapper(name:FormalName, sig:SignaturePtrs) -> bool:
            nonlocal key_bits
            sig_info = sig.signature_info
            covered_part = sig.signature_covered_part
            sig_value = sig.signature_value_buf
            if sig_info and sig_info.signature_type == SignatureType.SHA256_WITH_RSA:
                if sig_info.key_locator.name != key_name:
                    return False
                pub_key = RSA.import_key(key_bits)
                verifier = pkcs1_15.new(pub_key)
                sha256_algo = SHA256.new()
                if not covered_part or not sig_value:
                    ret = False
                else:
                    for blk in covered_part:
                        sha256_algo.update(blk)
                    try:
                        verifier.verify(sha256_algo, bytes(sig_value))
                        return True
                    except ValueError:
                        return False
                SVSyncLogger.debug(f'Digest check {Name.to_str(name)} -> {ret}')
                return ret
            return False
        return wrapper
    @staticmethod
    def _hmac_checker(key_name:FormalName, secret:bytes) -> Validator:
        async def wrapper(name:FormalName, sig:SignaturePtrs) -> bool:
            nonlocal secret
            sig_info = sig.signature_info
            covered_part = sig.signature_covered_part
            sig_value = sig.signature_value_buf
            if sig_info and sig_info.signature_type == SignatureType.HMAC_WITH_SHA256:
                if sig_info.key_locator.name != key_name:
                    return False
                hmac_algo = HMAC.new(secret, digestmod=SHA256)
                if not covered_part or not sig_value:
                    ret = False
                else:
                    for blk in covered_part:
                        hmac_algo.update(blk)
                    try:
                        hmac_algo.verify(sig_value)
                        return True
                    except ValueError:
                        return False
                SVSyncLogger.debug(f'Digest check {Name.to_str(name)} -> {ret}')
                return ret
            return False
        return wrapper
    @staticmethod
    def _digest_checker() -> Validator:
        return sha256_digest_checker

# Class Type: a security class
# Class Purpose:
#   to hold all signing and validating info used in SVS
class SecurityOptions:
    __slots__ = ('syncSig','syncVal','dataSig','dataValDict')
    # It is not neccessary to include digest or nosignature validators in the dataValidatingInfoDict.
    def __init__(self, syncSigningInfo:SigningInfo, syncValidatingInfo:ValidatingInfo, dataSigningInfo:SigningInfo, dataValidatingInfoDict:Dict[str, ValidatingInfo]) -> None:
        self.syncSig, self.syncVal, self.dataSig, self.dataValDict = syncSigningInfo, syncValidatingInfo, dataSigningInfo, dataValidatingInfoDict
    async def validate(self, name:FormalName, sig_ptrs:SignaturePtrs):
        val = None
        if sig_ptrs.signature_info.signature_type is None:
            return True
        if sig_ptrs.signature_info.signature_type == 1:
            val = ValidatingInfo(ValidatingInfo.get_validator(SignatureType.DIGEST_SHA256))
        else:
            try:
                keyname = Name.to_str(sig_ptrs.signature_info.key_locator.name)
                for key in self.dataValDict:
                    if key == keyname:
                        val = self.dataValDict[keyname]
            except AttributeError:
                val = None
        if val:
            return await val.validate(name, sig_ptrs)
        return True # We do not have the key for this keyname (cant error check it)