
import hashlib

SAFE="ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz2346789"
FULL="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

class userFriendly:
    @staticmethod
    def encode(d:bytes,to_user=False)->str:
        n=int.from_bytes(d,"big");a=SAFE if to_user else FULL;b=len(a);s=""
        while n:n,r=divmod(n,b);s=a[r]+s
        if not s:s=a[0]
        return "-".join(s[i:i+4] for i in range(0,len(s),4)) if to_user else s
    @staticmethod
    def decode(c:str)->bytes:
        a=SAFE if "-" in c else FULL;c=c.replace("-","");b=len(a);n=0
        for ch in c:n=n*b+a.index(ch)
        return n.to_bytes((n.bit_length()+7)//8,"big")



def hash3(data: bytes) -> bytes:
    return hashlib.sha3_512(data).digest()

hash = hash3


import hmac

def mix_bytes_with_int(data: bytes, n: int) -> bytes:
    assert len(data) == 64
    key = hashlib.sha3_512(str(n).encode()).digest()
    return hmac.new(key, data, hashlib.sha3_512).digest()

def xor(a: bytes, b: bytes) -> bytes:
    return bytes(a[i % len(a)] ^ b[i % len(b)] for i in range(max(len(a), len(b))))
