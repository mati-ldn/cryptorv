import pandas as pd
from client import BinanceDataFetcher
from conf import ENV


class HistoryLoader:
    def load(self, undl='BTC'):
        fetcher = BinanceDataFetcher()
        df = fetcher.get_klines(base=undl, quote='USDT', interval='1d', limit=1000)
        return df[['timestamp', 'close']].rename(columns={'timestamp': 'date'})


class HistoryFutureLoader(HistoryLoader):
    def load(self, undl='BTC', contract='CURRENT_QUARTER'):
        fetcher = BinanceDataFetcher()
        df = fetcher.get_futures_klines(
            base=undl, 
            quote='USDT', 
            interval='1d', 
            limit=1000,
            contract_type=contract
        )
        return df[['timestamp', 'close']].rename(columns={'timestamp': 'date'})


class HistoryBasisLoader:
    def load(self, undl='BTC', contract='CURRENT_QUARTER'):
        df_spot = HistoryLoader().load(undl)
        df_spot = df_spot.rename({'close': 'spot'}, axis=1)
        df_fut = HistoryFutureLoader().load(undl, contract=contract)
        df_fut = df_fut.rename({'close': 'fut'}, axis=1)
        df = df_spot.merge(df_fut, on='date')
        df['basis'] = df['spot'] - df['fut']
        return df


if __name__ == '__main__':
    loader = HistoryLoader()  # Changed to HistoryLoader since futures isn't implemented yet
    df = loader.load()
    print(df.tail())

    fetcher = BinanceDataFetcher()
    perpetual_data = fetcher.get_futures_klines('BTC')
    quarterly_data = fetcher.get_futures_klines('BTC', contract_type='CURRENT_QUARTER')
