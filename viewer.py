import pandas as pd

from data.basis import BasisTbl, BasisSummaryTblAbs, BasisSummaryTblPct
from loaders.history import HistoryLoader, HistoryBasisLoader


class BasisViewer:

    def __init__(self, undl='BTC'):
        self.undl = undl

    def basis_tbl(self):
        df = BasisTbl().load(self.undl)
        df = df[
            [
                'symbol',
                'price',
                'spot',
                'days_to_exp',
                'irr',
            ]
        ]
        df = df.set_index('symbol')
        df = df.iloc[1:]
        return df

    def timeseries(self):
        df = HistoryBasisLoader().load(self.undl)
        return df

    def all_undl(self):
        df = BasisSummaryTblPct().load()
        df = df.set_index('expiry_date')
        df.index = [str(i) for i in df.index]
        df = df.apply(pd.to_numeric)
        return df


if __name__ == '__main__':
    print(BasisViewer().basis_tbl())
