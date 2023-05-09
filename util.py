from loguru import logger
import random
from string import digits
from datetime import datetime


def get_random_key(n=16):
    return ''.join(random.choice(digits) for _ in range(n))


def get_size_relation(x, y):
    return 0 if x == y else (-1 if x < y else 1)
