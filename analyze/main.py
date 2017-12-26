import requests
import csv


url = "http://financials.morningstar.com/ajax/exportKR2CSV.html?t=%(exchange)s:%(ticker)s"
exchange = "XASX"


def create_url(ticker):
    return url % {"exchange": exchange, "ticker": ticker}


def main():
    companies_csv = requests.get(
        'http://www.asx.com.au/asx/research/ASXListedCompanies.csv'
    )
    parsed = csv.reader(
        companies_csv.content.decode('utf-8').splitlines(),
        delimiter=','
    )
    print(parsed)
    nohead = [row for row in parsed][3:]
    symbols = [row[1] for row in nohead]
    session = requests.Session()
    for symbol in symbols:
        url = create_url(symbol)
        financial = session.get(url)
        print(financial.text)
        
    print(symbols)

if __name__ == "__main__":
    main()
