"""
Decide how good shares are
"""
from collections import namedtuple
import logging

RateResult = namedtuple('RateResult', [
    'rating',
    'dividend_valuation',
    'eps_valuation'
])


def valuate_anuity(sequence, discount=0.9, count=1):
    suming = 0
    for item in sequence:
        if not item:
            return None
        num = float(item)
        suming += num * discount ** count
        count += 1
    return suming


def calculate_rating(data):
    eps_ann = valuate_anuity(data.eps)
    div_ann = valuate_anuity(data.dividends)
    if not (eps_ann and div_ann):
        return None

    logging.debug(data.realtime)
    price = float(data.realtime.price)
    if price == 0.0:
        return None
    return RateResult(
        rating=(min(eps_ann, div_ann)) / price,
        dividend_valuation=div_ann,
        eps_valuation=eps_ann
    )
