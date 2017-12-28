"""
Gather historic information from morningstart
cache it in a subdir cause it takes ages
"""
import csv

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
