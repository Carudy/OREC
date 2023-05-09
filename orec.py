from ore import *


def concat_ore(a, b):
    ret = (a << (MAX_BITS >> 1)) | b
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
        self.pv = 0
        self.kr = 0
        self.pn = pn

    def encode_and_genkey(self):
        # encode
        self.verfy_nums = [self.prg.randint(0, 1000), self.prg.randint(0, 1000)]
        y = self.verfy_nums[self.idx]

        e = self.ore.encode(scale_val(self.x, pn=self.pn)).encoding
        self.er = e & ((1 << (MAX_BITS >> 1)) - 1)
        self.el = e >> (MAX_BITS >> 1)

        z = self.ore.encode(scale_val(y, pn=self.pn)).encoding
        self.zr = z & ((1 << (MAX_BITS >> 1)) - 1)
        self.zl = z >> (MAX_BITS >> 1)

        # gen key
        self.ks = [random.randint(0, 3) % 4 for _ in range(4)]
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
    def __init__(self) -> None:
        self.es = [[None, None], [None, None]]
        self.ks = [[None, None], [None, None]]
        self.res = [[None, None], [None, None]]

    def receive_req(self, round, idx, xl, xr, ks):
        self.es[round][idx] = [xl, xr]
        self.ks[round][idx] = ks

    def calc_cmp(self):
        for round in range(2):
            ret = []
            for i in range(2):
                a = concat_ore(self.es[round][0][i], self.es[round][0][i ^ 1])
                for j in range(2):
                    b = concat_ore(self.es[round][1][j],
                                   self.es[round][1][j ^ 1])
                    ret.append(ORE.compare(a, b))
            for i in range(2):
                self.res[round][i] = ret[:]
                for j in range(4):
                    self.res[round][i][j] ^= self.ks[round][i ^ 1][j]


class OREC_Simulator:
    def __init__(self, pn=0):
        self.A = OREC_Client(idx=0, pn=pn)
        self.B = OREC_Client(idx=1, pn=pn)
        self.C = OREC_ThirdParty()

    def test(self, x, y):
        self.A.x = x
        self.B.x = y

        # A negotiate with B
        self.A.k0 = self.B.k0 = get_random_key()
        self.A.p = self.B.p = random.randint(0, 3)
        self.A.pv = self.B.pv = random.randint(0, 3)
        self.A.prg.seed(self.A.k0)
        self.B.prg.seed(self.B.k0)
        self.A.ore.key = self.A.k0
        self.B.ore.key = self.B.k0

        # local computation
        self.A.encode_and_genkey()
        self.B.encode_and_genkey()

        # send first to C
        if self.A.p < 2:
            self.C.receive_req(0, 0, self.A.el, self.A.er, self.A.ks)
        else:
            self.C.receive_req(0, 0, self.A.er, self.A.el, self.A.ks)
        if self.B.p & 1 == 0:
            self.C.receive_req(0, 1, self.B.el, self.B.er, self.B.ks)
        else:
            self.C.receive_req(0, 1, self.B.er, self.B.el, self.B.ks)
        # send second to C
        if self.A.p < 2:
            self.C.receive_req(1, 0, self.A.zl, self.A.zr, self.A.ks)
        else:
            self.C.receive_req(1, 0, self.A.zr, self.A.zl, self.A.ks)
        if self.B.p & 1 == 0:
            self.C.receive_req(1, 1, self.B.zl, self.B.zr, self.B.ks)
        else:
            self.C.receive_req(1, 1, self.B.zr, self.B.zl, self.B.ks)
        self.C.calc_cmp()

        # get ans
        ra = self.A.get_res((self.C.res[0][0], self.C.res[1][0]))
        rb = self.B.get_res((self.C.res[0][1], self.C.res[1][1]))
        if ra != rb:
            logger.info('Diff res!')
        return ra
