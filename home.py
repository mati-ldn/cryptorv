import pandas as pd
import sys
import streamlit as st
from streamlit import runtime
from streamlit.web import cli as stcli

from cryptorv.data.basis import BasisTbl, BasisSummaryTblAbs, BasisSummaryTblPct
from cryptorv.loaders.history import HistoryLoader, HistoryBasisLoader
from cryptorv.formatters import table_heatmap, table_format


def main():
    st.title(':dollar: Crypto RV')
    st.subheader('App to monitor cash-future basis')

    df = BasisTbl().load()
    df = df[['symbol', 'price', 'spot', 'basis', 'basis_pct', 'days_to_exp', 'basis_pct_ann']]
    df = df.set_index('symbol')
    df = df.iloc[1:]
    # st.table(df)
    st.table(table_format(df))

    df = HistoryBasisLoader().load('BTC')
    cols = st.columns(2)
    with cols[0]:
        st.line_chart(df, x='date', y=['spot', 'fut'])
    with cols[1]:
        st.line_chart(df, x='date', y='basis')

    # st.subheader('All Undl')
    # df = BasisSummaryTblPct().load()
    # df = df.set_index('expiry_date')
    # df.index = [str(i) for i in df.index]
    # df = df.apply(pd.to_numeric)
    # st.table(table_format(df))

if __name__ == '__main__':
    if runtime.exists():
        main()
    else:
        sys.argv = ['streamlit', 'run', 'home.py']
        sys.exit(stcli.main())
