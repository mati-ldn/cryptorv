import logging

import pandas as pd
import numpy as np

from client import get_client
from conf import ENV


class CombinedPriceLoader:
    def load(self, ticker):
        if '_' in ticker:
            df = FuturePriceLoader().load(ticker)
            df['type'] = 'fut'
        else:
            df = PriceLoader().load(ticker)
            df['type'] = 'spot'
        return df


class PriceLoader:
    def load(self, ticker):
        client = get_client(ENV)
        try:
            data = client.get_symbol_ticker(symbol=ticker)
        except:
            logging.info(f'{ticker} not available')
            data = {'symbol': ticker, 'price': np.nan}
        df = pd.DataFrame.from_dict(data, orient='index').transpose()
        return df


class FuturePriceLoader:
    def load(self, ticker):
        client = get_client(ENV)
        data = client.futures_coin_symbol_ticker(symbol=ticker)
        data = data[0]
        df = pd.DataFrame.from_dict(data, orient='index').transpose()
        return df


if __name__ == '__main__':
    tickers = ['BTCBUSD', 'BTCUSD_240329', 'BTCUSD_240628']
    loader = CombinedPriceLoader()
    dfs = []
    for t in tickers:
        df_ = loader.load(t)
        dfs.append(df_)
    df = pd.concat(dfs)