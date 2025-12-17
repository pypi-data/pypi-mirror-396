import os
import time
import asyncio
import hashlib
import threading
from cryptography.hazmat.primitives import hashes, constant_time, hmac as chmac
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from typing import Tuple
from hmac import compare_digest



class S1:
    def __init__(self) -> None:
        self.__V=b"KeyisB-c-s-m1"
        self.__C={}

    def __derive(self, k:bytes, kh:bool=False):
        d=hashlib.sha3_512(k).digest() if not kh else k
        if d in self.__C:return self.__C[d]
        s=hashlib.sha3_512(self.__V+b"|salt|"+k).digest()
        hk=HKDF(algorithm=hashes.SHA3_512(),length=96,salt=s,info=self.__V+b"|HKDF|")
        o=hk.derive(k);v=(o[:32],o[32:]);self.__C[d]=v;return v

    def sign(self,k:bytes)->bytes:
        ek,mk=self.__derive(k);n=os.urandom(16);t=int(time.time()).to_bytes(8,"big")
        st=hashlib.sha3_512(k[32:]+hashlib.sha3_512(k).digest()).digest()
        m=t+os.urandom(32)+st
        c=Cipher(algorithms.ChaCha20(ek,n),None).encryptor().update(m)
        h=chmac.HMAC(mk,hashes.SHA3_512());h.update(self.__V+b"|HMAC|");h.update(n);h.update(c)
        return n+c+h.finalize()

    def verify(self,k:bytes,s:bytes,ttl:int=15,kh:bool=False)->bool:
        if len(s)<80:return False
        ek,mk=self.__derive(k,kh=kh);n,ct,tg=s[:16],s[16:-64],s[-64:]
        h=chmac.HMAC(mk,hashes.SHA3_512());h.update(self.__V+b"|HMAC|");h.update(n);h.update(ct)
        try:h.verify(tg)
        except: return False
        m=Cipher(algorithms.ChaCha20(ek,n),None).decryptor().update(ct)
        if len(m)<104:return False
        ts=int.from_bytes(m[:8],"big");now=int(time.time())
        if (now-ts if now>=ts else ts-now)>ttl:return False
        st=hashlib.sha3_512(k[32:]+hashlib.sha3_512(k).digest()).digest()
        return m.endswith(st)

s1 = S1()




class S2:
    def __init__(self, V: bytes = b"KeyisB-c-s-m1"):
        self.__V = V; self.__C = {}; self.__lock = threading.Lock()
    def __norm(self, k: bytes, kh: bool) -> bytes:
        return k if kh else hashlib.sha3_512(k).digest()
    def __mix(self, base: bytes, info: bytes, l: int):
        salt = hashlib.sha3_512(self.__V + b"|salt|" + base).digest()
        hkdf = HKDF(algorithm=hashes.SHA3_512(), length=l, salt=salt, info=self.__V + b"|HKDF|" + info)
        o_hk = hkdf.derive(base)
        sh = hashlib.shake_256(); sh.update(self.__V + b"|SHAKE|" + info + base)
        return bytes(a ^ b for a, b in zip(o_hk, sh.digest(l)))
    def __derive(self, k: bytes, kh: bool = False):
        base = self.__norm(k, kh)
        with self.__lock:
            if base in self.__C: return self.__C[base]
        m = self.__mix(base, b"derive-v2", 96); ak, bl = m[:32], m[32:96]
        with self.__lock: self.__C[base] = (ak, bl)
        return ak, bl
    def sign(self, k: bytes) -> bytes:
        ak, bl = self.__derive(k, kh=False)
        n = os.urandom(12); t = int(time.time()).to_bytes(8, "big")
        base = self.__norm(k, kh=False)
        st = hashlib.sha3_512(base + base).digest()
        m = t + os.urandom(32) + st
        a = ChaCha20Poly1305(ak); aad = self.__V + b"|AEAD|v2"
        ct = a.encrypt(n, m, aad)
        b = hashlib.blake2b(digest_size=32, key=bl); b.update(n); b.update(ct); b.update(aad)
        return n + ct + b.digest()
    def verify(self, k: bytes, s: bytes, ttl: int = 15, kh: bool = False) -> bool:
        if len(s) < 12 + 16 + 8 + 32 + 32: return False
        ak, bl = self.__derive(k, kh=kh); n, ct, btag = s[:12], s[12:-32], s[-32:]
        b = hashlib.blake2b(digest_size=32, key=bl); b.update(n); b.update(ct); b.update(self.__V + b"|AEAD|v2")
        if not constant_time.bytes_eq(b.digest(), btag): return False
        a = ChaCha20Poly1305(ak); aad = self.__V + b"|AEAD|v2"
        try: m = a.decrypt(n, ct, aad)
        except Exception: return False
        if len(m) < 8 + 32 + 64: return False
        ts = int.from_bytes(m[:8], "big"); now = int(time.time())
        if (now - ts if now >= ts else ts - now) > ttl: return False
        base = self.__norm(k, kh=kh)
        st = hashlib.sha3_512(base + base).digest()
        return m.endswith(st)
    
    async def async_sign(self, k: bytes) -> bytes:
        return await asyncio.to_thread(self.sign, k)
    async def async_verify(self, k: bytes, s: bytes, ttl: int = 15, kh: bool = False) -> bool:
        return await asyncio.to_thread(self.verify, k, s, ttl, kh)

s2 = S2()







class S3:
    def __init__(self, V: bytes = b"KeyisB-c-s-s3"):
        self.__V = V
        self.__C = {}
        self.__lock = threading.Lock()

    def __derive(self, k: bytes) -> Tuple[bytes, bytes]:
        base = hashlib.sha3_512(k).digest()
        with self.__lock:
            if base in self.__C:
                return self.__C[base]
        hkdf = HKDF(algorithm=hashes.SHA3_512(), length=96,
                     salt=hashlib.sha3_512(self.__V + b"|salt|" + base).digest(),
                     info=self.__V + b"|HKDF|derive-v2")
        m = hkdf.derive(base)
        ak, bl = m[:32], m[32:96]
        with self.__lock:
            self.__C[base] = (ak, bl)
        return ak, bl

    def sign(self, k: bytes, msg: bytes, aad: bytes = b"S2|v2") -> bytes:
        ak, bl = self.__derive(k)
        n = os.urandom(12)
        base = hashlib.sha3_512(k).digest()
        st = hashlib.sha3_512(base + base).digest()
        m = int(time.time()).to_bytes(8, "big") + os.urandom(32) + st + msg
        a = ChaCha20Poly1305(ak)
        ct = a.encrypt(n, m, aad)
        b = hashlib.blake2b(digest_size=32, key=bl)
        b.update(n); b.update(ct); b.update(aad)
        return n + ct + b.digest()

    def verify(self, k: bytes, s: bytes, ttl: int = 900, aad: bytes = b"S2|v2"):
        if len(s) < 12 + 16 + 8 + 32 + 32:
            return (False, b"")
        ak, bl = self.__derive(k)
        n, ct, btag = s[:12], s[12:-32], s[-32:]
        b = hashlib.blake2b(digest_size=32, key=bl)
        b.update(n); b.update(ct); b.update(aad)
        if not compare_digest(b.digest(), btag):
            return (False, b"")
        a = ChaCha20Poly1305(ak)
        try:
            m = a.decrypt(n, ct, aad)
        except Exception:
            return (False, b"")
        ts = int.from_bytes(m[:8], "big")
        now = int(time.time())
        if abs(now - ts) > ttl:
            return (False, b"")
        return (True, m[8+32+64:])

    @staticmethod
    def blake2b(key: bytes, data: bytes) -> bytes:
        b = hashlib.blake2b(digest_size=64, key=key)
        b.update(data)
        return b.digest()

s3 = S3()
