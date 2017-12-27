import requests
import csv
import json
from pprint import pprint
from collections import namedtuple
from jinja2 import Template
import logging
import argparse

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


Realtime = namedtuple('Realtime', ['price', 'eps', 'name', 'url'])
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


def find_realtime_stock(session, ticker):
    response = session.get('https://finance.google.com/finance?q=ASX:%s&output=json' % ticker)
    son = json.loads(response.content[6:-2].decode('unicode_escape'))
    return Realtime(price=son['l'], eps=son['eps'], name=son['name'], url=son['f_reuters_url'])

def float_or_zero(string):
    return float(string) if string else 0

def valuate_anuity(sequence, discount=0.9, count=1):
    suming = 0
    for item in sequence:
        num = float_or_zero(item)
        suming += num * discount ** count
    return suming


def calculate_rating(data):
    cur_eps = float_or_zero(data.realtime.eps)
    eps_ann = valuate_anuity(data.eps) + cur_eps
    div_ann = valuate_anuity(data.dividends)
    price = float(data.realtime.price)
    if price == 0.0:
        return None
    return RateResult(
        rating=(min(eps_ann, div_ann) + cur_eps) / price ,
        dividend_valuation=div_ann,
        eps_valuation=eps_ann
    )


PresentRow = namedtuple('PresentRow', ['ticker', 'name', 'eps', 'price', 'rating', 'url'])
ViewRow = namedtuple('ViewRow', [
    'ticker',
    'percent_eps',
    'percent_dividend',
    'percent_earnings',
    'price',
    'eps',
    'dividend',
    'earnings',
    'url'
])


def create_view_row(result):
    price = float(result.price)

    def ratio(num):
        return (num/price)*100

    logging.debug('converting %s' % result.ticker)
    return ViewRow(
        ticker=result.ticker,
        percent_eps=ratio(float(result.eps)),
        percent_dividend=ratio(result.rating.dividend_valuation),
        percent_earnings=ratio(result.rating.eps_valuation),
        price=price,
        eps=result.eps,
        dividend=result.rating.dividend_valuation,
        earnings=result.rating.eps_valuation,
        url=result.url
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

        rating = calculate_rating(data)

        if rating:
            result.append(PresentRow(
                ticker=ticker,
                eps=data.realtime.eps,
                price=data.realtime.price,
                name=data.realtime.name,
                rating=rating,
                url=data.realtime.url
            ))

    sorted_results = sorted(result, key=lambda it: -it.rating.rating)
    jinja_results = [create_view_row(row) for row in sorted_results]
    with open('template.html') as template:
        print(Template(''.join(template.readlines())).render(results=jinja_results))


if __name__ == "__main__":
    main()
