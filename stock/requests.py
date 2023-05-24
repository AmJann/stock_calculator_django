# /exchanges/[mic]/eod/[date]

import requests
import os
import environ
from dotenv import load_dotenv
import requests

load_dotenv()
url= os.environ['STOCK_URL']
api_key = os.environ['STOCK_API_KEY']

params = {
    'access_key': api_key,
    'symbols': stock_name
}

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
    )
  
def getStocks(start_date):
    stocks = []
    for id in ResturantId:
    call_url = url + "eod/" + start_date
    response = requests.get(call_url, params=params)
        rest = response.json()
        temp = {}
        temp['opening_price'] = rest['open']
        temp['symbol'] = rest['symbol']
        temp['date'] = rest['date']

        stock.append(temp)
    
    return stocks

