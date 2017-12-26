import requests
import csv
from pprint import pprint


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


def main():
    session = requests.Session()
    parsed = readcsv(
        requestcsv(
            session,
            'http://www.asx.com.au/asx/research/ASXListedCompanies.csv'
        )
    )
    nohead = [row for row in parsed][3:]
    tickers = [row[1] for row in nohead]
    for ticker in tickers:
        financial = get_financial(session, ticker)
        csv = [row for row in readcsv(financial)]
        if not csv:
            continue
        if csv == [['We’re sorry. There is no available information in our database to display.']]:
            continue
        print(ticker)
        pprint(csv[8])
        pprint(csv[9])
        
    print(tickers)

if __name__ == "__main__":
    main()
