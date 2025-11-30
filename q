[1mdiff --git a/conf.py b/conf.py[m
[1mindex 262d140..a083e88 100644[m
[1m--- a/conf.py[m
[1m+++ b/conf.py[m
[36m@@ -11,5 +11,6 @@[m [mUNDLS = ['BTC', 'ETH', 'LTC', 'BNB', 'XRP'][m
 [m
 [m
 # TODO: automate[m
[31m-FRONT_EXP = '241227'[m
[31m-BACK_EXP = '250328'[m
[32m+[m[32mFRONT_EXP = '250328'[m
[32m+[m[32mBACK_EXP = '250627'[m
[32m+[m[32m#BACK_EXP = '250628'[m
[1mdiff --git a/data/basis.py b/data/basis.py[m
[1mindex 1793fa3..6eefa20 100644[m
[1m--- a/data/basis.py[m
[1m+++ b/data/basis.py[m
[36m@@ -1,7 +1,8 @@[m
 import pandas as pd[m
 [m
 from loaders.prices import CombinedPriceLoader[m
[31m-from conf import UNDLS, FRONT_EXP, BACK_EXP[m
[32m+[m[32mfrom utils.expiry_dates import get_expiries[m
[32m+[m[32mfrom conf import UNDLS[m
 [m
 [m
 class BasisTbl:[m
[36m@@ -9,7 +10,7 @@[m [mclass BasisTbl:[m
     def load(self, undl='BTC'):[m
         spot = f'{undl}USDT'[m
         futroot = f'{undl}USD'[m
[31m-        tickers = [spot, f'{futroot}_{FRONT_EXP}', f'{futroot}_{BACK_EXP}'][m
[32m+[m[32m        tickers = [spot] + [f'{futroot}_{x:%y%m%d}' for x in get_expiries()][m
         loader = CombinedPriceLoader()[m
         dfs = [][m
         for t in tickers:[m
[36m@@ -21,7 +22,7 @@[m [mclass BasisTbl:[m
         spot_px = df.loc[df['symbol'] == spot, 'price'].item()[m
         df['spot'] = spot_px[m
         df['basis'] = df['spot'] - df['price'][m
[31m-        df['basis_pct'] = df['basis'] / df['spot'][m
[32m+[m[32m        df['irr'] = ((df['price'] / df['spot']) - 1) * 100[m
 [m
         mask = df['type'] == 'fut'[m
         df.loc[mask, 'expiry'] = df.loc[mask, 'symbol'].apply([m
[36m@@ -34,7 +35,7 @@[m [mclass BasisTbl:[m
             lambda x: (x - pd.Timestamp.today()).days[m
         )[m
         df['expiry_date'] = df['expiry2'].apply(lambda x: x.date())[m
[31m-        df['basis_pct_ann'] = df['basis_pct'] * (360 / df['days_to_exp'])[m
[32m+[m[32m        df['irr'] = df['irr'] * (360 / df['days_to_exp'])[m
         return df[m
 [m
 [m
[36m@@ -58,4 +59,8 @@[m [mclass BasisSummaryTblAbs(BasisSummaryTblBase):[m
 [m
 [m
 class BasisSummaryTblPct(BasisSummaryTblBase):[m
[31m-    value = 'basis_pct_ann'[m
[32m+[m[32m    value = 'irr'[m
[32m+[m
[32m+[m
[32m+[m[32mif __name__ == '__main__':[m
[32m+[m[32m    BasisTbl().load()[m
[1mdiff --git a/loaders/prices.py b/loaders/prices.py[m
[1mindex 91cbb24..2a6088e 100644[m
[1m--- a/loaders/prices.py[m
[1m+++ b/loaders/prices.py[m
[36m@@ -9,6 +9,7 @@[m [mfrom conf import ENV[m
 [m
 class CombinedPriceLoader:[m
     def load(self, ticker):[m
[32m+[m[32m        df = pd.DataFrame()[m
         if '_' in ticker:[m
             df = FuturePriceLoader().load(ticker)[m
             df['type'] = 'fut'[m
[36m@@ -32,10 +33,15 @@[m [mclass PriceLoader:[m
 [m
 class FuturePriceLoader:[m
     def load(self, ticker):[m
[31m-        client = get_client(ENV)[m
[31m-        data = client.futures_coin_symbol_ticker(symbol=ticker)[m
[31m-        data = data[0][m
[31m-        df = pd.DataFrame.from_dict(data, orient='index').transpose()[m
[32m+[m[32m        df = pd.DataFrame()[m
[32m+[m[32m        try:[m
[32m+[m[32m            client = get_client(ENV)[m
[32m+[m[32m            data = client.futures_coin_symbol_ticker(symbol=ticker)[m
[32m+[m[32m            data = data[0][m
[32m+[m[32m            df = pd.DataFrame.from_dict(data, orient='index').transpose()[m
[32m+[m[32m        except:[m
[32m+[m[32m            logging.info(f'{ticker} not available')[m
[32m+[m[32m            data = {'symbol': ticker, 'price': np.nan}[m
         return df[m
 [m
 [m
[1mdiff --git a/viewer.py b/viewer.py[m
[1mindex 0f157ed..c6b9363 100644[m
[1m--- a/viewer.py[m
[1m+++ b/viewer.py[m
[36m@@ -16,10 +16,8 @@[m [mclass BasisViewer:[m
                 'symbol',[m
                 'price',[m
                 'spot',[m
[31m-                'basis',[m
[31m-                'basis_pct',[m
                 'days_to_exp',[m
[31m-                'basis_pct_ann',[m
[32m+[m[32m                'irr',[m
             ][m
         ][m
         df = df.set_index('symbol')[m
