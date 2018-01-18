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
        logging.info(item)
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

"""
    This file is part of autotrader/analyzer.

    autotrader/analyzer is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    autotrader/analyzer is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with autotrader/analyzer.  If not, see <http://www.gnu.org/licenses/>.
"""
