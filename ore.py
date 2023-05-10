import nacl.encoding
import nacl.hash

from util import *

MAX_BITS = 64 + 12
MINN = -(1 << MAX_BITS)
MAXN = -MINN - 1
SCALE_BIT = 8
SCALE = 1 << SCALE_BIT
HALF_SCALE = 1 << (SCALE_BIT >> 1)


def scale_val(x, pn=0, scale=SCALE):
    res = int((x+pn) * scale)
    if abs(res) >= MAXN:
        raise Exception('Beyond MAXN!')
    return res


def bin_enc(x, nb=MAX_BITS):
    res = bin(abs(x))[2:]
    n = len(res)
    # if x < 0:
    #     return '0' + '1' * (nb - n - 1) + ''.join(['1' if i == '0' else '0' for i in res])
    # return '1' + '0' * (nb - n - 1) + res
    return '0' * (nb - n) + res


class OREncoding:
    def __init__(self, x) -> None:
        self.encoding = x

    def __eq__(self, __o) -> bool:
        return self.encoding == __o.encoding

    def __lt__(self, __o):
        return ORE.compare(self, __o) == -1

    def __gt__(self, __o):
        return ORE.compare(self, __o) == 1

    def __ge__(self, __o):
        return ORE.compare(self, __o) != -1

    def __str__(self) -> str:
        return str(self.encoding)


class ORE:
    def __init__(self, key='111'):
        self.key = key
        self.hasher = nacl.hash.blake2b
        self.prg = random.Random(datetime.now())

    def encode(self, x: int, nb=MAX_BITS):
        res = 0
        s = bin_enc(x)
        n = len(s)
        for i in range(MAX_BITS-1, MAX_BITS-nb-1, -1):
            t = int(f'{self.key}{i}{s[:i]}{"0" * (n-i)}')
            self.prg.seed(t)
            res = (res << 2) | (
                (self.prg.randint(1, 123580) + int(s[i])) & 0b11)
        return OREncoding(res)

    @staticmethod
    def compare(x: OREncoding, y: OREncoding):
        if x == y:
            return 0
        _x = x.encoding
        _y = y.encoding
        for _ in range(MAX_BITS):
            a = _x & 0b11
            b = _y & 0b11
            if a != b:
                return 1 if (a & 0b11) == ((b+1) & 0b11) else -1
            _x >>= 2
            _y >>= 2
