"""
Gather historic information from morningstart
cache it in a subdir cause it takes ages
"""
import csv
from collections import namedtuple

url = "http://financials.morningstar.com/ajax/exportKR2CSV.html?t=%(exchange)s:%(ticker)s"
exchange = "XASX"


def create_url(ticker):
    return url % {"exchange": exchange, "ticker": ticker}


def requestcsv(session, url):
    result = session.get(url).content.decode('utf-8').splitlines()
    return result


def readcsv(data):
    return csv.reader(
        data,
        delimiter=','
    )

def get_financial(session, ticker):
    filename = 'cache/%s.csv' % ticker
    try:
        with open(filename, newline='') as cached:
            return cached.readlines()
    except FileNotFoundError:
        pass
    result = requestcsv(session, create_url(ticker))
    with open(filename, 'w') as write:
        write.write("\n".join(result))
    return result
MorningData = namedtuple('MorningData', ['eps', 'dividends', 'cps'])

def financial_table(data) -> MorningData:
    csv = [row for row in readcsv(data)]
    if not csv:
        return None
    if csv == [['We’re sorry. There is no available information in our database to display.']]:
        return None
    return MorningData(
        eps=eps_row(csv), 
        dividends=dividends(csv), 
        cps=cps_row(csv)
    )

def eps_row(table):
    return table[8][1:]

def dividends(table):
    return table[9][1:]

def cps_row(table):
    return table[16][1:-1]

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
