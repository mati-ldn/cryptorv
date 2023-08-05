import pandas as pd

from loaders.prices import CombinedPriceLoader
from conf import UNDLS, FRONT_EXP, BACK_EXP


class BasisTbl:

    def load(self, undl='BTC'):
        spot = f'{undl}BUSD'
        futroot = f'{undl}USD'
        tickers = [spot, f'{futroot}_{FRONT_EXP}', f'{futroot}_{BACK_EXP}']
        loader = CombinedPriceLoader()
        dfs = []
        for t in tickers:
            df_ = loader.load(t)
            dfs.append(df_)
        df = pd.concat(dfs)
        df['price'] = df['price'].apply(float)
        df['time'] = pd.to_datetime(df['time'])
        spot_px = df.loc[df['symbol'] == spot, 'price'].item()
        df['spot'] = spot_px
        df['basis'] = df['spot'] - df['price']
        df['basis_pct'] = df['basis'] / df['spot']

        mask = df['type'] == 'fut'
        df.loc[mask, 'expiry'] = (
            df.loc[mask, 'symbol'].apply(lambda x: x.split('_')[-1])
        )
        df.loc[mask, 'expiry2'] = (
            df.loc[mask, 'expiry'].apply(lambda x: pd.to_datetime(x, format='%y%m%d'))
        )
        df['days_to_exp'] = df['expiry2'].apply(lambda x: (x - pd.Timestamp.today()).days)
        df['expiry_date'] = df['expiry2'].apply(lambda x: x.date())
        df['basis_pct_ann'] = df['basis_pct'] * (360 / df['days_to_exp'])
        return df


class BasisSummaryTblBase():
    value = ''
    def load(self):
        loader = BasisTbl()
        dfs = [loader.load(x) for x in UNDLS]
        df = pd.concat(dfs)
        df = df.dropna()
        df = df.pivot_table(index='expiry_date', columns='ps', values=self.value)
        df = df.reset_index()
        return df


class BasisSummaryTblAbs(BasisSummaryTblBase):
    value = 'basis'


class BasisSummaryTblPct(BasisSummaryTblBase):
    value = 'basis_pct_ann'
