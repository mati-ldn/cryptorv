import pandas as pd

from loaders.prices import CombinedPriceLoader
from utils.expiry_dates import get_expiries
from conf import UNDLS


class BasisTbl:

    def load(self, undl='BTC'):
        spot = f'{undl}USDT'
        futroot = f'{undl}USD'
        tickers = [spot] + [f'{futroot}_{x:%y%m%d}' for x in get_expiries()]
        loader = CombinedPriceLoader()
        dfs = []
        for t in tickers:
            df_ = loader.load(t)
            dfs.append(df_)
        df = pd.concat(dfs)
        df = df.dropna()
        df['undl'] = undl
        df['price'] = df['price'].apply(float)
        # df['time'] = pd.to_datetime(df['time'])
        spot_px = df.loc[df['symbol'] == spot, 'price'].item()
        df['spot'] = spot_px
        df['basis'] = df['spot'] - df['price']
        df['irr'] = (df['price'] / df['spot']) - 1

        mask = df['type'] == 'fut'
        df.loc[mask, 'expiry'] = df.loc[mask, 'symbol'].apply(
            lambda x: x.split('_')[-1]
        )
        df.loc[mask, 'expiry2'] = df.loc[mask, 'expiry'].apply(
            lambda x: pd.to_datetime(x, format='%y%m%d')
        )
        df['days_to_exp'] = df['expiry2'].apply(
            lambda x: (x - pd.Timestamp.today()).days
        )
        df['expiry_date'] = df['expiry2'].apply(lambda x: x.date())
        df['irr'] = df['irr'] * (360 / df['days_to_exp'])
        return df


class BasisSummaryTblBase:
    value = ''

    def load(self):
        loader = BasisTbl()
        dfs = [loader.load(x) for x in UNDLS]
        df = pd.concat(dfs)
        df = df.dropna()
        df = df.pivot_table(index='expiry', columns='undl', values=self.value)
        df = df.reset_index()
        return df


class BasisSummaryTblAbs(BasisSummaryTblBase):
    value = 'basis'


class BasisSummaryTblPct(BasisSummaryTblBase):
    value = 'irr'


if __name__ == '__main__':
    BasisSummaryTblPct().load()
