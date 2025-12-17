

from typing import Union,List
from Crypto.Hash import KMAC256
from cryptography.hazmat.primitives.ciphers.aead import AESGCM,ChaCha20Poly1305

class M1:
    B=Union[bytes,List[bytes]]
    @staticmethod
    def _n(v:B)->bytes:
        if isinstance(v,bytes):return v
        if isinstance(v,list):return b''.join(v)
        raise TypeError
    @staticmethod
    def _km(k:bytes,c:bytes,m:bytes,l:int)->bytes:
        h=KMAC256.new(key=k,custom=c,mac_len=l);h.update(m);return h.digest()
    @classmethod
    def _m(cls,k:bytes,n1:bytes,n2:bytes):
        s=cls._km(k,k,n1+n2,32)
        ad=cls._km(k,s,k,16)
        kc=cls._km(k,n1,s,32);ka=cls._km(k,n2,s,32)
        nc=cls._km(k,kc+s,n1,12);na=cls._km(k,ka+s,n2,12)
        return kc,ka,nc,na,ad
    @classmethod
    def encrypt(cls,n1:B,n2:B,data:B,key:B)->bytes:
        n1,n2,d,k=cls._n(n1),cls._n(n2),cls._n(data),cls._n(key)
        kc,ka,nc,na,ad=cls._m(k,n1,n2)
        return AESGCM(ka).encrypt(na,ChaCha20Poly1305(kc).encrypt(nc,d,ad),ad)
    @classmethod
    def decrypt(cls,n1:B,n2:B,enc:B,key:B)->bytes:
        n1,n2,e,k=cls._n(n1),cls._n(n2),cls._n(enc),cls._n(key)
        kc,ka,nc,na,ad=cls._m(k,n1,n2)
        return ChaCha20Poly1305(kc).decrypt(nc,AESGCM(ka).decrypt(na,e,ad),ad)
    @classmethod
    def fastEncrypt(cls,data:B,key:B)->bytes:
        d,k=cls._n(data),cls._n(key)
        n1=cls._km(k,k,k,16)
        n2=cls._km(k,n1,k,16)
        return cls.encrypt(n1,n2,d,k)
    @classmethod
    def fastDecrypt(cls,enc:B,key:B)->bytes:
        e,k=cls._n(enc),cls._n(key)
        n1=cls._km(k,k,k,16)
        n2=cls._km(k,n1,k,16)
        return cls.decrypt(n1,n2,e,k)
    
        
m1 = M1()