"""
Dumps a bunch of html to std out with a table that valuates shares based on
profit or dividend / price.
Should give a good idea of what's intersting to buy (and not overvalued)
"""

import requests
import json
from collections import namedtuple
from jinja2 import Template
import logging
import argparse
from lib import morningstar, rate, realtime

ShareData = namedtuple('ShareData', [
    'ticker',
    'realtime',
    'eps',
    'dividends'
])

PresentRow = namedtuple('PresentRow', ['ticker', 'realtime', 'rating'])
ViewRow = namedtuple('ViewRow', [
    'ticker',
    'percent_dividend',
    'percent_earnings',
    'price',
    'time',
    'dividend',
    'earnings',
    'url',
    'high',
    'low',
    'volume'
])


def create_view_row(result):
    price = float(result.realtime.price)

    def ratio(num):
        return (num/price)*100

    logging.debug('converting %s' % result.ticker)
    return ViewRow(
        ticker=result.ticker,
        percent_dividend=ratio(result.rating.dividend_valuation),
        percent_earnings=ratio(result.rating.eps_valuation),
        price=price,
        time=result.realtime.timestamp,
        dividend=result.rating.dividend_valuation,
        earnings=result.rating.eps_valuation,
        url="http://stocks.us.reuters.com/stocks/ratios.asp?rpc=66&symbol=%s.AX" % result.ticker,
        high=result.realtime.high,
        low=result.realtime.low,
        volume=result.realtime.volume,
    )

def main():
    logging.basicConfig(filename='progress.log', level=logging.DEBUG)
    session = requests.Session()

    parser  = argparse.ArgumentParser(
        description='Valuates shares on the ASX, probably quite naivly'
    )
    parser.add_argument('tickers', nargs='*')
    args = parser.parse_args()

    tickers = args.tickers
    if not args.tickers:
        parsed = morningstar.readcsv(
            morningstar.requestcsv(
                session,
                'http://www.asx.com.au/asx/research/ASXListedCompanies.csv'
            )
        )
        nohead = [row for row in parsed][3:]
        tickers = [row[1] for row in nohead]

    result = []
    realtimes = realtime.find_realtime_stocks(session, *tickers)
    for ticker in tickers:
        logging.info('doing %s' % ticker)
        financial = morningstar.get_financial(session, ticker)
        csv = [row for row in morningstar.readcsv(financial)]
        if not csv:
            continue
        if csv == [['We’re sorry. There is no available information in our database to display.']]:
            continue

        try:
            data = ShareData(
                ticker=ticker,
                realtime=realtimes.get(ticker),
                eps=reversed(csv[8][1:]),
                dividends=reversed(csv[9][1:])
            )
        except json.decoder.JSONDecodeError:
            continue

        if not data.realtime:
            continue
        rating = rate.calculate_rating(data)

        if rating:
            result.append(PresentRow(
                ticker=ticker,
                realtime=data.realtime,
                rating=rating,
            ))

    sorted_results = sorted(result, key=lambda it: -it.rating.rating)
    jinja_results = [create_view_row(row) for row in sorted_results]
    with open('template.html') as template:
        print(Template(''.join(template.readlines())).render(results=jinja_results))


if __name__ == "__main__":
    main()
