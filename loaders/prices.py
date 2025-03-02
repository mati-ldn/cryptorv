import logging

import pandas as pd
import numpy as np

from client import BinanceDataFetcher
from conf import ENV


class CombinedPriceLoader:
    def __init__(self):
        self.fetcher = BinanceDataFetcher()

    def load(self, ticker):
        df = pd.DataFrame()
        if '_' in ticker:
            df = FuturePriceLoader(self.fetcher).load(ticker)
            df['type'] = 'fut'
        else:
            df = PriceLoader(self.fetcher).load(ticker)
            df['type'] = 'spot'
        return df


class PriceLoader:
    def __init__(self, fetcher):
        self.fetcher = fetcher

    def load(self, ticker):
        try:
            if 'USD' in ticker:
                base = ticker.replace('USD', '')
                quote = 'USD'
            else:
                base = ticker[:-4]
                quote = ticker[-4:]
            
            price = self.fetcher.get_current_price(base, quote)
            data = {'symbol': ticker, 'price': price}
        except Exception as e:
            logging.info(f'{ticker} not available: {str(e)}')
            data = {'symbol': ticker, 'price': np.nan}
        
        return pd.DataFrame([data])


class FuturePriceLoader:
    def __init__(self, fetcher):
        self.fetcher = fetcher

    def load(self, ticker):
        try:
            base = ticker.split('USD_')[0]
            data = {'symbol': ticker}
            
            futures_data = self.fetcher.client.futures_coin_symbol_ticker(symbol=ticker)[0]
            data['price'] = float(futures_data['price'])
            
            return pd.DataFrame([data])
        except Exception as e:
            logging.info(f'{ticker} not available: {str(e)}')
            return pd.DataFrame([{'symbol': ticker, 'price': np.nan}])


if __name__ == '__main__':
    tickers = ['BTCBUST', 'BTCUSD_240329', 'BTCUSD_240628']
    loader = CombinedPriceLoader()
    dfs = []
    for t in tickers:
        df_ = loader.load(t)
        dfs.append(df_)
    df = pd.concat(dfs)
