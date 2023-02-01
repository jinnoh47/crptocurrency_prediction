from pkgutil import get_data
import requests
import json
import pandas as pd
import datetime as dt


# Declaring base url (Binance)
url = 'https://api.binance.com/api/v3/klines'


def get_data_binance_symbol(symbol, interval, start, end):
    """
    Pulls data from Binance api for a single symbol
    Start and end date must be a string in UTC format or timestamp in milliseconds
    Interval can take values 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1mo
    Returns dataframe with columns 'datetime', 'open', 'high', 'low', 'close', 'volume','close_time', 
    'qav', 'num_trades','taker_base_vol', 'taker_quote_vol', 'ignore'
    """
    par = {'symbol': symbol, 'interval': interval,
            'startTime': start, 'endTime': end, 'limit':1000}
    temp_data = json.loads(requests.get(url, params=par).text)       
    data = pd.DataFrame(temp_data)
    if not data.empty:
        # format columns name
        data.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume',
                        'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore']
        data.index = [dt.datetime.fromtimestamp(x/1000.0) for x in data.datetime]
        data = data.astype(float)
        data = data.drop(['close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore'], axis=1)
    start = str(int(start) + 1000*3600000)
    while (start < end):     
        par = {'symbol': symbol, 'interval': interval,
            'startTime': start, 'endTime': end, 'limit':1000}
        temp_data = json.loads(requests.get(url, params=par).text)       
        data_two = pd.DataFrame(temp_data)
        if not data_two.empty:
            # format columns name
            data_two.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume',
                            'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore']
            data_two.index = [dt.datetime.fromtimestamp(x/1000.0) for x in data_two.datetime]
            data_two = data_two.astype(float)
            data_two = data_two.drop(['close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore'], axis=1)
        start = str(int(start) + 1000*3600000)
        data = pd.concat([data, data_two], axis=0)
    return data


def get_symbol_list():
    """
    Returns a list of tickers from Binance api
    """
    data = pd.DataFrame(json.loads(requests.get(
        'https://api.binance.com/api/v3/ticker/price').text))
    symbol_list = data['symbol'].tolist()
    return symbol_list


def get_data_binance():
    """
    Pulls historical Klines for all currently listed symbols through the Binance api
    Start and end date must be a string in UTC format or timestamp in milliseconds.
    Interval can take values 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1mo
    Returns dataframe with columns 'datetime', 'open', 'high', 'low', 'close', 'volume','close_time', 
    'qav', 'num_trades','taker_base_vol', 'taker_quote_vol', 'ignore'
    """

    start = str(int(dt.datetime(2022, 1, 1).timestamp()*1000))
    end = str(int(dt.datetime(2022, 6, 1).timestamp()*1000))
    interval = '1h'

    tickers = get_symbol_list()
    tickers = [x for x in tickers if x.endswith("USD")]
    df = get_data_binance_symbol(tickers[0], interval, start, end)
    df['symbol'] = [tickers[0]] * df.shape[0]
    l = len(tickers)
    s = 1
    for symbol in tickers[1:]:
        temp_df = get_data_binance_symbol(symbol, interval, start, end)
        if not temp_df.empty:
            temp_df['symbol'] = [symbol] * temp_df.shape[0]
            df = pd.concat([df, temp_df], axis=0)
        print("Got data for", s, "/", l, "tickers")
        s = s + 1
    return df

df = get_data_binance()
df.to_csv('data/binance_data.csv')