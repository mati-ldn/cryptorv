import pandas as pd

from client import get_client
from conf import ENV


class HistoryLoader:
    def load(self, undl='BTC'):
        ticker = f'{undl}USDT'
        client = get_client(ENV)
        timestamp = client._get_earliest_valid_timestamp('BTCUSDT', '1d')
        bars = client.get_historical_klines(ticker, '1d', timestamp, limit=1000)
        for line in bars:
            del line[5:]
        df = pd.DataFrame(bars, columns=['date', 'open', 'high', 'low', 'close'])
        df.set_index('date', inplace=True)
        df = df.applymap(float)
        df.index = pd.to_datetime(df.index, unit='ms')
        return df['close'].reset_index()


class HistoryFutureLoader(HistoryLoader):
    def load(self, undl='BTC', contract='CURRENT_QUARTER'):
        pair = f'{undl}USD'
        client = get_client(ENV)
        bars = client.futures_coin_continous_klines(pair=pair,
                                             contractType=contract,
                                             interval='1d')
        for line in bars:
            del line[5:]
        df = pd.DataFrame(bars, columns=['date', 'open', 'high', 'low', 'close'])
        df.set_index('date', inplace=True)
        df = df.applymap(float)
        df.index = pd.to_datetime(df.index, unit='ms')
        return df['close'].reset_index()


class HistoryBasisLoader:
    def load(self, undl='BTC', contract='CURRENT_QUARTER'):
        client = get_client(ENV)
        df_spot = HistoryLoader().load(undl)
        df_spot = df_spot.rename({'close': 'spot'}, axis=1)
        df_fut = HistoryFutureLoader().load(undl, contract=contract)
        df_fut = df_fut.rename({'close': 'fut'}, axis=1)
        df = df_spot.merge(df_fut, on='date')
        df['basis'] = df['spot'] - df['fut']
        return df


if __name__ == '__main__':
    loader = HistoryBasisLoader()
    df = loader.load()
    print(df.tail())