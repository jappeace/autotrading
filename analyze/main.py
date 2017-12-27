import requests
import csv
import json
from pprint import pprint
from collections import namedtuple
from jinja2 import Template
import logging
import argparse
from datetime import datetime


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


ShareData = namedtuple('ShareData', [
    'ticker',
    'realtime',
    'eps',
    'dividends'
])
RateResult = namedtuple('RateResult', [
    'rating',
    'dividend_valuation',
    'eps_valuation'
])

def chunks(array, chunksize):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(array), chunksize):
        yield array[i:i + chunksize]

Realtime = namedtuple('Realtime', [
    'ticker',
    'price',
    'high',
    'low',
    'volume',
    'timestamp'
])

def find_realtime_stock(session, ticker):
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=%(ticker)s.AX&interval=1min&apikey=%(key)s'
    api_key = ""
    with open('key') as keyfile:
        api_key = keyfile.readline()
    formated_uri = url % {
        'ticker': ticker,
        'key': api_key
    }
    logging.debug(formated_uri)
    response = session.get(formated_uri)
    son = json.loads(response.text)
    dict_key = "Time Series (1min)"
    if dict_key not in son:
        return None
    series = son[dict_key]
    collected = [(datetime.strptime(time, "%Y-%m-%d %H:%M:%S"), data) for time, data in series.items()]
    sort = sorted(collected, key=lambda a: a[0])

    latest = sort[-1]
    logging.debug(latest)
    return Realtime(
        timestamp=latest[0],
        ticker=ticker,
        price=latest[1]['4. close'],
        high=latest[1]['2. high'],
        low=latest[1]['3. low'],
        volume=latest[1]['5. volume'],
    )

def float_or_zero(string):
    return float(string) if string else 0

def valuate_anuity(sequence, discount=0.9, count=1):
    suming = 0
    for item in sequence:
        num = float_or_zero(item)
        suming += num * discount ** count
    return suming


def calculate_rating(data):
    eps_ann = valuate_anuity(data.eps)
    div_ann = valuate_anuity(data.dividends)
    price = float(data.realtime.price)
    if price == 0.0:
        return None
    return RateResult(
        rating=(min(eps_ann, div_ann)) / price,
        dividend_valuation=div_ann,
        eps_valuation=eps_ann
    )


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
        parsed = readcsv(
            requestcsv(
                session,
                'http://www.asx.com.au/asx/research/ASXListedCompanies.csv'
            )
        )
        nohead = [row for row in parsed][3:]
        tickers = [row[1] for row in nohead]

    result = []
    for ticker in tickers:
        logging.info('doing %s' % ticker)
        financial = get_financial(session, ticker)
        csv = [row for row in readcsv(financial)]
        if not csv:
            continue
        if csv == [['We’re sorry. There is no available information in our database to display.']]:
            continue

        try:
            data = ShareData(
                ticker=ticker,
                realtime=find_realtime_stock(session, ticker),
                eps=reversed(csv[8][1:-1]),
                dividends=reversed(csv[9][1:-1])
            )
        except json.decoder.JSONDecodeError:
            continue

        if not data.realtime:
            continue

        rating = calculate_rating(data)

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
