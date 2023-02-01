import requests
import pandas as pd
import numpy as np
import json as js
from datetime import datetime
from datetime import timedelta

url = "https://api.exchange.coinbase.com/products"
headers = {"Accept": "application/json"}
response = requests.get(url, headers=headers)
response_content = response.content
response_text = response.text
response_header = response.headers
# print(response_header)

df_currencies = pd.read_json(response_text)
print("Number of columns in the dataframe: %i" % (df_currencies.shape[1]))
print("Number of rows in the dataframe: %i" % (df_currencies.shape[0]))

# the number of stable pairs: 17
# print(np.sum(df_currencies.fx_stablecoin))
# choose 4 products
# MY_CURRENCIES = ['BTC-EUR','ETH-EUR','LTC-EUR','BCH-EUR']
# print(df_currencies[df_currencies.id.isin(MY_CURRENCIES)][['id', 'quote_currency', 'base_min_size', 'base_max_size']].shape)

### function to get historic data: time window 01/01/2022-06/09/2021
def get_data(currency):
    # The maximum number of data points for a single request is 300 candles.
    # each time collect 12 days data
    start_date = datetime(2022, 1, 1).isoformat()
    end_date = (datetime(2022, 1, 1) + timedelta(days=12)).isoformat()
    params = {"start": start_date, "end": end_date, "granularity": "3600"}
    response = requests.get(url + "/" + currency + "/candles", params)
    response_text = response.text
    df_history = pd.DataFrame(js.loads(response_text))

    n = (datetime(2022, 6, 1) - datetime(2022, 1, 1)).days // 12 - 1
    for i in range(n):
        start_date = (datetime(2022, 1, 1) + timedelta(days=12 * (i + 1))).isoformat()
        end_date = (datetime(2022, 1, 1) + timedelta(days=12 * (i + 2))).isoformat()
        params = {"start": start_date, "end": end_date, "granularity": "3600"}
        response = requests.get(url + "/" + currency + "/candles", params)
        response_text = response.text
        df_temp = pd.DataFrame(js.loads(response_text))
        df_history = pd.concat([df_history, df_temp], axis=0)

    start_date = end_date
    end_date = datetime(2022, 6, 1).isoformat()
    params = {"start": start_date, "end": end_date, "granularity": "3600"}
    response = requests.get(url + "/" + currency + "/candles", params)
    response_text = response.text
    df_temp = pd.DataFrame(js.loads(response_text))
    df_history = pd.concat([df_history, df_temp], axis=0)

    return df_history


currencies = df_currencies.id

df_history = get_data(currencies[0])
df_history.columns = ["time", "low", "high", "open", "close", "volume"]
df_history["id"] = [currencies[0]] * df_history.shape[0]
df_history["time"] = pd.to_datetime(df_history["time"], unit="s")
df_history.set_index("time", inplace=True)
df_history.sort_values(by="time", ascending=True, inplace=True)

for currency in currencies[1:]:
    df_temp = get_data(currency)
    if df_temp.shape[0] == 0:
        continue
    # Add column names in line with the Coinbase Pro documentation

    df_temp.columns = ["time", "low", "high", "open", "close", "volume"]
    df_temp["id"] = [currency] * df_temp.shape[0]
    df_temp["time"] = pd.to_datetime(df_temp["time"], unit="s")
    df_temp.set_index("time", inplace=True)
    df_temp.sort_values(by="time", ascending=True, inplace=True)

    df_history = pd.concat([df_history, df_temp], axis=0)

df_history.to_csv("data/" + "coinbase_data.csv")
