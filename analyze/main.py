import requests
import csv


url = "http://financials.morningstar.com/ajax/exportKR2CSV.html?t=%(exchange)s:%(ticker)s"
exchange = "XASX"


def create_url(ticker):
    return url % {"exchange": exchange, "ticker": ticker}


def requestcsv(session, url):
    return session.get(url).content.decode('utf-8').splitlines()


def readcsv(data):
    return csv.reader(
        data,
        delimiter=','
    )


def get_financial(session, ticker):
    filename = 'cache/%s.csv' % ticker
    try:
        with open(filename, 'r', newline='') as cached:
            return cached.readlines()
    except FileNotFoundError:
        pass
    result = requestcsv(session, create_url(ticker))
    with open(filename, 'w') as write:
        write.writelines(result)
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
        url = create_url(ticker)
        financial = get_financial(session, ticker)
        print(financial)
        
    print(tickers)

if __name__ == "__main__":
    main()
