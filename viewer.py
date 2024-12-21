import pandas as pd

from data.basis import BasisTbl, BasisSummaryTblAbs, BasisSummaryTblPct
from loaders.history import HistoryLoader, HistoryBasisLoader


class BasisViewer:

    def __init__():
        pass

    def basis_tbl():
        df = BasisTbl().load()
        df = df[['symbol', 'price', 'spot', 'basis', 'basis_pct', 'days_to_exp', 'basis_pct_ann']]
        df = df.set_index('symbol')
        df = df.iloc[1:]
        return df
    
    def timeseries():
        df = HistoryBasisLoader().load('BTC')
        return df

    def all_undl():
        df = BasisSummaryTblPct().load()
        df = df.set_index('expiry_date')
        df.index = [str(i) for i in df.index]
        df = df.apply(pd.to_numeric)
        return df


if __name__ == '__main__':
    print(BasisViewer().basis_tbl())
