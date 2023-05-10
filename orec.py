from ore import *

import itertools
import numpy as np


def concat_ore(pieces, piece_bit):
    ret = pieces[0]
    for i in pieces[1:]:
        ret = (ret << piece_bit) | i
    return OREncoding(ret)


class OREC_Client:
    def __init__(self, idx, pn=0, n_piece=2) -> None:
        self.idx = idx
        self.x = 0
        self.verfy_nums = [0, 0]
        self.k0 = '123'
        self.ks = ['0'] * 4
        self.ore = ORE()
        self.prg = random.Random()
        self.p = 0
        self.kr = 0
        self.pn = pn
        self.n_piece = n_piece

    def split_encoding(self, encoding):
        res = []
        piece_bit = int(MAX_BITS / self.n_piece)
        for _ in range(self.n_piece-1):
            now = encoding & ((1 << (piece_bit)) - 1)
            res.append(now)
            encoding >>= piece_bit
        res.append(encoding)
        return res[::-1]

    def encode_and_genkey(self):
        # encode
        self.verfy_nums = [self.prg.randint(0, 1000), self.prg.randint(0, 1000)]
        veri = self.verfy_nums[self.idx]

        e = self.ore.encode(scale_val(self.x, pn=self.pn)).encoding
        self.es = self.split_encoding(e)

        z = self.ore.encode(scale_val(veri, pn=self.pn)).encoding
        self.zs = self.split_encoding(z)

        # gen key
        n_pob = np.math.factorial(self.n_piece) ** 2
        self.ks = [random.randint(0, 3) for _ in range(n_pob)]
        if self.idx == 0:
            self.ks[self.p] = self.prg.randint(0, 3) 
            self.kr = self.prg.randint(0, 3)
        else:
            self.kr = self.prg.randint(0, 3)
            self.ks[self.p] = self.prg.randint(0, 3)

    def get_res(self, rs):
        verify_res = self.kr ^ rs[1][self.p]
        tar_res = get_size_relation(*self.verfy_nums)
        if verify_res != tar_res:
            logger.info(f'Verfiy error!: self: {self.idx} res: {verify_res} {tar_res}')
        self.res = self.kr ^ rs[0][self.p]
        return self.res


class OREC_ThirdParty:
    def __init__(self, n_piece=2) -> None:
        self.n_piece = n_piece
        self.es = [[None, None], [None, None]]
        self.ks = [[None, None], [None, None]]
        self.res = [[None, None], [None, None]]

    def receive_req(self, round, idx, x_pieces, ks):
        self.es[round][idx] = x_pieces
        self.ks[round][idx] = ks

    def calc_cmp(self):
        for round in range(2):
            ret = []
            for p0 in itertools.permutations(self.es[round][0]):
                a = concat_ore(p0, piece_bit=int(MAX_BITS / self.n_piece))
                for p1 in itertools.permutations(self.es[round][1]):
                    b = concat_ore(p1, piece_bit=int(MAX_BITS / self.n_piece))
                    ret.append(ORE.compare(a, b))
            # encryption
            for i in range(2):
                self.res[round][i] = ret[:]
                for j in range(len(self.res[round][i])):
                    self.res[round][i][j] ^= self.ks[round][i ^ 1][j]


class OREC_Simulator:
    def __init__(self, pn=0, n_piece=2):
        self.A = OREC_Client(idx=0, pn=pn, n_piece=n_piece)
        self.B = OREC_Client(idx=1, pn=pn, n_piece=n_piece)
        self.C = OREC_ThirdParty(n_piece=n_piece)

    def trans_p_es(self, ea, eb, p):
        top = self.rel[p]
        r0 = [0] * len(top[0])
        r1 = [0] * len(top[0])
        for i, j in enumerate(top[0]):
            r0[j] = ea[i]
        for i, j in enumerate(top[1]):
            r1[j] = eb[i]
        return (r0, r1)

    def test(self, x, y):
        self.A.x = x
        self.B.x = y

        # A negotiate with B
        n_pos = np.math.factorial(self.A.n_piece) ** 2
        self.A.p = self.B.p = random.randint(0, n_pos-1)
        self.A.prg.seed(self.A.k0)
        self.B.prg.seed(self.B.k0)
        self.A.ore.key = self.A.k0
        self.B.ore.key = self.B.k0

        # calc pos-p relation
        _a = list(range(self.A.n_piece))
        pa = list(itertools.permutations(_a))
        rel = itertools.product(pa, pa)
        self.rel = {i: j for i, j in enumerate(rel)}

        # local computation
        self.A.encode_and_genkey()
        self.B.encode_and_genkey()

        # send first to C
        _ea, _eb = self.trans_p_es(self.A.es, self.B.es, self.A.p)
        self.C.receive_req(0, 0, _ea, self.A.ks)
        self.C.receive_req(0, 1, _eb, self.B.ks)

        # send second to C
        _za, _zb = self.trans_p_es(self.A.zs, self.B.zs, self.A.p)
        self.C.receive_req(1, 0, _za, self.A.ks)
        self.C.receive_req(1, 1, _zb, self.B.ks)

        self.C.calc_cmp()

        # get ans
        ra = self.A.get_res((self.C.res[0][0], self.C.res[1][0]))
        rb = self.B.get_res((self.C.res[0][1], self.C.res[1][1]))
        if ra != rb:
            logger.info('Diff res!')
        return ra
