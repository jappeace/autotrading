"""
Gather realtime(ish) info from asx
"""
from bs4 import BeautifulSoup
from collections import namedtuple
from datetime import datetime, timedelta

Realtime = namedtuple('Realtime', [
    'ticker',
    'price',
    'high',
    'low',
    'volume',
    'timestamp'
])


def chunks(array, chunksize):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(array), chunksize):
        yield array[i:i + chunksize]


def find_realtime_stocks(session, *tickers):
    url = 'http://www.asx.com.au/asx/markets/equityPrices.do?by=asxCodes&asxCodes=%s'
    chunked = chunks(tickers, 10)
    result = {}
    for chunk in chunked:
        formated_uri = url % '+'.join(chunk)
        response = session.get(formated_uri)
        soup = BeautifulSoup(response.text)
        rows = soup.select('.datatable tr')[1:]
        for row in rows:
            ticker = row.select('.row a')[0].get_text()
            colls = row.select('td')
            price = colls[0].get_text().strip()
            if not price:
                continue
            result[ticker] = Realtime(
                ticker=ticker,
                price=price,
                high=colls[6].get_text().strip(),
                low=colls[7].get_text().strip(),
                volume=colls[8].get_text().strip(),
                # api is 20 minutes old
                timestamp=datetime.now() - timedelta(minutes=20)
            )
    return result

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
