from typing import List, Tuple

NumTuple = Tuple[int, ...]

_cache: dict[str, List[Tuple[NumTuple, NumTuple]]] = {}

def _normalize(a: NumTuple, b: NumTuple) -> Tuple[NumTuple, NumTuple]:
    la, lb = len(a), len(b)
    l = max(la, lb)
    a_ext = a + (0,) * (l - la)
    b_ext = b + (10**9,) * (l - lb)
    return a_ext, b_ext

def in_range(pos: str, ranges: str) -> bool:
    if ranges not in _cache:
        parsed: List[Tuple[NumTuple, NumTuple]] = []
        for part in ranges.split(";"):
            if "-" in part:
                a, b = part.split("-", 1)
                a_t = tuple(map(int, a.split(".")))
                b_t = tuple(map(int, b.split(".")))
                parsed.append(_normalize(a_t, b_t))
            else:
                t = tuple(map(int, part.split(".")))
                parsed.append(_normalize(t, t))
        _cache[ranges] = parsed

    p = tuple(map(int, pos.split(".")))
    for start, end in _cache[ranges]:
        l = len(end)
        p_ext = p + (0,) * (l - len(p))
        if start <= p_ext <= end:
            return True
    return False
