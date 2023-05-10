from comm import *
from ore import *
from orec import *
from tinysmpc import VirtualMachine, PrivateScalar, SharedScalar

import time
from tqdm.auto import tqdm

NB = 32
ML = 1 << NB
MR = ML - 1
ML = -ML


def cb(msg):
    msg['v'] *= 1.5
    return msg


def eval_orec_time_comm(xs, comm=True):
    s = Grpcer()
    s.start_server(cb)
    c = Grpcer()

    sim = OREC_Simulator(pn=MR+1, n_piece=2)
    ys = []
    idx = 0
    st = time.time()
    for i in tqdm(range(max(xs)+1)):
        x = random.randint(ML, MR)
        y = random.randint(ML, MR)
        res = sim.test(x, y)

        if comm:
            c.send(s, {'v': 20})
            c.send(s, {'v': x})
            c.send(s, {'v': y})

        if i == xs[idx]:
            _t = time.time()
            ys.append((_t-st)*1000)
            idx += 1
            if idx >= len(xs):
                break
    return ys


def test_compare(x, y):
    alice = VirtualMachine('alice')
    bob = VirtualMachine('bob')
    x_sh = PrivateScalar(x, alice).share([alice, bob])
    y_sh = PrivateScalar(y, bob).share([alice, bob])
    z_sh = x_sh - y_sh
    return (z_sh > 0).value


def eval_securenn_time_comm(xs, n_bit=32, comm=True):
    s = Grpcer()
    s.start_server(cb)
    c = Grpcer()

    ys = []
    idx = 0
    st = time.time()
    for i in tqdm(range(max(xs)+1)):
        x = random.randint(MR >> 1, MR)
        y = random.randint(MR >> 1, MR)
        res = test_compare(x, y)

        if comm:
            for _ in range(n_bit):
                c.send(s, {'v': 20})

        if i == xs[idx]:
            _t = time.time()
            ys.append((_t-st)*1000)
            idx += 1
            if idx >= len(xs):
                break
    return ys


n_comm = {
    'iris': 4 * 100,
    'madelon': 15 * 100 * 100,
    'adult': 49 * 100 * 100,
    'rna': 28 * 100 * 100,
}

if __name__ == '__main__':
    COMM = True

    xs = list(range(n_comm['iris']))
    ys = eval_securenn_time_comm(xs, comm=COMM)
    print(ys[-1])

    # xs = list(range(n_comm['madelon']))
    # ys = eval_securenn_time_comm(xs, comm=COMM)
    # print(ys[-1])

    # xs = list(range(n_comm['adult']))
    # ys = eval_securenn_time_comm(xs, comm=COMM)
    # print(ys[-1])

    # xs = list(range(n_comm['rna']))
    # ys = eval_securenn_time_comm(xs, comm=COMM)
    # print(ys[-1])