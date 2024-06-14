# coding: utf-8

import random


def get_rng(seed) -> random.Random:
    if seed < 0:
        seed = None
    return random.Random(seed)
