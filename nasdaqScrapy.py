from lxml import html
import requests
from time import sleep
import json
import argparse
from random import randint
import pymongo



def parse_finance_page(ticker):
    """
    Grab financial data from NASDAQ page

    Args:
      ticker (str): Stock symbol

    Returns:
      dict: Scraped data
    """
    key_stock_dict = {}
    headers = {
        "Referer": "http://www.nasdaq.com",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36"
    }
    requests.packages.urllib3.disable_warnings()
    # Retrying for failed request
    for retries in range(5):
        try:
            url = "http://www.nasdaq.com/symbol/%s" % (ticker)
            response = requests.get(url, verify=False)
            print("respose code:%d" % (response.status_code))
            if response.status_code != 200:
                raise ValueError("Invalid Response Received From Webserver")

            print("Parsing %s" % (url))
            # Adding random delay
            sleep(randint(1, 3))
            parser = html.fromstring(response.text)
            xpath_head = "//div[@id='qwidget_pageheader']//h1//text()"
            xpath_key_stock_table = '//div[@class="row overview-results relativeP"]//div[contains(@class,"table-table")]/div'
            xpath_open_price = '//b[contains(text(),"Open Price:")]/following-sibling::span/text()'
            xpath_open_date = '//b[contains(text(),"Open Date:")]/following-sibling::span/text()'
            xpath_close_price = '//b[contains(text(),"Close Price:")]/following-sibling::span/text()'
            xpath_close_date = '//b[contains(text(),"Close Date:")]/following-sibling::span/text()'
            xpath_key = './/div[@class="table-cell"]/b/text()'
            xpath_value = './/div[@class="table-cell"]/text()'

            raw_name = parser.xpath(xpath_head)
            key_stock_table = parser.xpath(xpath_key_stock_table)
            raw_open_price = parser.xpath(xpath_open_price)
            raw_open_date = parser.xpath(xpath_open_date)
            raw_close_price = parser.xpath(xpath_close_price)
            raw_close_date = parser.xpath(xpath_close_date)

            company_name = raw_name[0].replace("Common Stock Quote & Summary Data", "").strip() if raw_name else ''
            open_price = raw_open_price[0].strip() if raw_open_price else None
            open_date = raw_open_date[0].strip() if raw_open_date else None
            close_price = raw_close_price[0].strip() if raw_close_price else None
            close_date = raw_close_date[0].strip() if raw_close_date else None

            # Grabbing ans cleaning keystock data
            for i in key_stock_table:
                key = i.xpath(xpath_key)
                value = i.xpath(xpath_value)
                key = ''.join(key).strip().replace(".", "_")
                value = ' '.join(''.join(value).split())
                key_stock_dict[key] = value

            nasdaq_data = {

                "company_name": company_name,
                "ticker": ticker,
                "url": url,
                "open_price": open_price,
                "open_date": open_date,
                "close_price": close_price,
                "close_date": close_date,
                "key_stock_data": key_stock_dict
            }
            return nasdaq_data

        except Exception as e:
            print("Failed to process the request, Exception:%s" % (e))


if __name__ == "__main__":
    # argparser = argparse.ArgumentParser()
    # argparser.add_argument('ticker', help='Company stock symbol')
    # args = argparser.parse_args()
    # ticker = args.ticker
    # symbols = ['aapl', 'gluu', 'mu', 'ntap', 'msft', 'intc', 'znga', 'csco', 'siri', 'jd', 'fb', 'nvda', 'bl', 'ftnt', 'chrs', 'loco', 'catm', 'cnce', 'fizz', 'acor', 'fldm', 'sptn', 'cent', 'xent', 'adap', 'gpro', 'brks', 'sgms', 'iova', 'aaon', 'eigi', 'amzn', 'nflx', 'tsla']
    symbols = ['aapl']
    for ticker in symbols:
        print("Fetching data for %s" % (ticker))
        scraped_data = parse_finance_page(ticker)
        print("Writing scraped data to output file")
        with open('%s-summary.json' % (ticker), 'w') as fp:
            json.dump(scraped_data, fp, indent=4, ensure_ascii=False)
        myclient = pymongo.MongoClient('mongodb://localhost:27899/')
        mydb = myclient['resthub']
        mycol = mydb["stocks"]
        x = mycol.insert_one(scraped_data)
        print(x.inserted_id)