# Basic Libraries
import logging
from Cryptodome.Hash import SHA256, HMAC
from Cryptodome.PublicKey import ECC, RSA
from Cryptodome.Signature import DSS, pkcs1_15
from typing import Union, Optional
from enum import Enum
# NDN Imports
from ndn.types import Validator
from ndn.encoding import FormalName, SignaturePtrs, Name, MetaInfo, SignatureType, parse_data, make_data
from ndn.security import Sha256WithEcdsaSigner, Sha256WithRsaSigner, HmacSha256Signer, DigestSha256Signer, sha256_digest_checker

class SVSyncSecurity:
    def __init__(self, type:Optional[SignatureType]=None, key_name:Optional[Name]=None, priv_key:Optional[bytes]=None, pub_key:Optional[bytes]=None):
        self.type = type if type!=None else SignatureType.DIGEST_SHA256
        self.key_name = Name.to_str(key_name) if key_name!=None else None
        self.priv_key = priv_key
        self.pub_key = pub_key
        self.signer = None
        self.validator = None
        self.no_signature = False
        self.determine()
    def determine(self):
        if self.type:
            if self.type == SignatureType.SHA256_WITH_ECDSA:
                self.signer = Sha256WithEcdsaSigner(self.key_name, self.priv_key)
                self.validator = self.ecdsa_checker(Name.from_str(self.key_name), self.pub_key)
            elif self.type == SignatureType.SHA256_WITH_RSA:
                self.signer = Sha256WithRsaSigner(self.key_name, self.priv_key)
                self.validator = self.rsa_checker(Name.from_str(self.key_name), self.pub_key)
            elif self.type == SignatureType.HMAC_WITH_SHA256:
                self.signer = HmacSha256Signer(self.key_name, self.priv_key)
                self.validator = self.hmac_checker(Name.from_str(self.key_name), self.pub_key)
            elif self.type == SignatureType.DIGEST_SHA256:
                self.signer = DigestSha256Signer()
                self.validator = self.digest_checker()
            else:
                self.no_signature = True
        else:
            self.signer = DigestSha256Signer()
            self.validator = self.digest_checker()
    def digest_checker(self):
        return sha256_digest_checker
    def ecdsa_checker(self, key_name:FormalName, key_bits:Union[bytes, str]) -> Validator:
        async def wrapper(name:FormalName, sig:SignaturePtrs) -> bool:
            nonlocal key_bits
            sig_info = sig.signature_info
            covered_part = sig.signature_covered_part
            sig_value = sig.signature_value_buf
            if sig_info and sig_info.signature_type == SignatureType.SHA256_WITH_ECDSA:
                if sig_info.key_locator.name != key_name:
                    return False
                # Import known key
                pub_key = ECC.import_key(key_bits)
                verifier = DSS.new(pub_key, 'fips-186-3', 'der')
                sha256_algo = SHA256.new()
                if not covered_part or not sig_value:
                    ret = False
                else:
                    # Compute the hash
                    for blk in covered_part:
                        sha256_algo.update(blk)
                    try:
                        # Verify the signature
                        verifier.verify(sha256_algo, bytes(sig_value))
                        return True
                    except ValueError:
                        return False
                logging.debug('Digest check %s -> %s' % (Name.to_str(name), ret))
                return ret
            else:
                # True means pass for all other types, which can be used by union_checker
                # If you want to force a specific signature type, return False
                return False
        return wrapper
    def rsa_checker(self, key_name:FormalName, key_bits:Union[bytes, str]) -> Validator:
        async def wrapper(name:FormalName, sig:SignaturePtrs) -> bool:
            nonlocal key_bits
            sig_info = sig.signature_info
            covered_part = sig.signature_covered_part
            sig_value = sig.signature_value_buf
            if sig_info and sig_info.signature_type == SignatureType.SHA256_WITH_RSA:
                if sig_info.key_locator.name != key_name:
                    return False
                # Import known key
                pub_key = RSA.import_key(key_bits)
                verifier = pkcs1_15.new(pub_key)
                sha256_algo = SHA256.new()
                if not covered_part or not sig_value:
                    ret = False
                else:
                    # Compute the hash
                    for blk in covered_part:
                        sha256_algo.update(blk)
                    try:
                        # Verify the signature
                        verifier.verify(sha256_algo, bytes(sig_value))
                        return True
                    except ValueError:
                        return False
                logging.debug('Digest check %s -> %s' % (Name.to_str(name), ret))
                return ret
            else:
                # True means pass for all other types, which can be used by union_checker
                # If you want to force a specific signature type, return False
                return False
        return wrapper
    def hmac_checker(self, key_name:FormalName, secret:bytes) -> Validator:
        async def wrapper(name:FormalName, sig:SignaturePtrs) -> bool:
            nonlocal secret
            sig_info = sig.signature_info
            covered_part = sig.signature_covered_part
            sig_value = sig.signature_value_buf
            if sig_info and sig_info.signature_type == SignatureType.HMAC_WITH_SHA256:
                if sig_info.key_locator.name != key_name:
                    return False
                # Import known key
                hmac_algo = HMAC.new(secret, digestmod=SHA256)
                if not covered_part or not sig_value:
                    ret = False
                else:
                    # Compute the hash
                    for blk in covered_part:
                        hmac_algo.update(blk)
                    try:
                        # Verify the signature
                        hmac_algo.verify(sig_value)
                        return True
                    except ValueError:
                        return False
                logging.debug('Digest check %s -> %s' % (Name.to_str(name), ret))
                return ret
            else:
                # True means pass for all other types, which can be used by union_checker
                # If you want to force a specific signature type, return False
                return False
        return wrapper