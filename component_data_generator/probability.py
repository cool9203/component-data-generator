# coding: utf-8

import random

import utils

from ._types import _logger_level, _normal_variate_mu, _normal_variate_sigma, _probability_seed
from .util import get_rng

logger = utils.get_logger(
    logger_name=__name__,
    log_level=_logger_level.upper(),
    log_fmt=_logger_level,
)

rng = get_rng(_probability_seed)


def seed(seed):
    global rng
    rng = get_rng(seed)


def get_result(p) -> bool:
    _p = rng.random()
    logger.debug(f"p: {p}, _p: {_p}")
    if p >= _p:
        return True
    return False


def area_probability(
    used_area: float,
    max_area: float,
) -> bool:
    p = (max_area - used_area) / max_area
    return get_result(p)


def base_probability() -> bool:
    p = rng.random()
    return get_result(p)


def get_gauss_int(a, b, mu=_normal_variate_mu, sigma=_normal_variate_sigma) -> int:
    assert a != b
    if a > b:
        (a, b) = (b, a)

    num = int(rng.normalvariate(mu=mu + (abs(a - b) / 2), sigma=sigma) + a)
    while num < a or num > b:
        num = int(rng.normalvariate(mu=mu + (abs(a - b) / 2), sigma=sigma) + a)
    return num
