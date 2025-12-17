import msgpack
from typing import Union, List, Dict, TypeAlias, Any
import datetime

SerializableKey = Union[str, bytes, int]

SerializableType: TypeAlias = Union[
    None,
    bool,
    int,
    float,
    str,
    bytes,
    List[Any], # List["SerializableType"],
    Dict[Any, Any], # Dict[SerializableKey, "SerializableType"],
    datetime.datetime
]




def serialize(data: SerializableType) -> bytes:
    return msgpack.packb(data, use_bin_type=True, datetime=True)

def deserialize(data: bytes, raw_str: bool = False) -> SerializableType:
    return msgpack.unpackb(data, strict_map_key=False, raw=raw_str, timestamp=3)







