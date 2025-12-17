import hmac
import hashlib

def hkdf1(ikm: bytes, info: bytes, length: int = 32, salt: bytes = b"\x00"*64) -> bytes:
    prk = hmac.new(salt, ikm, hashlib.sha3_512).digest()
    t = b""; okm = b""; i = 1
    while len(okm) < length:
        t = hmac.new(prk, t + info + bytes([i]), hashlib.sha3_512).digest()
        okm += t; i += 1
    return okm[:length]