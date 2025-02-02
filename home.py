import pandas as pd
import sys
import streamlit as st
from streamlit import runtime
from streamlit.web import cli as stcli

from viewer import BasisViewer
from formatters import table_heatmap, table_format


def main():
    st.title(':dollar: Crypto RV')
    st.subheader('App to monitor cash-future basis')

    vw = BasisViewer()

    df = vw.basis_tbl()
    st.dataframe(table_format(df, custom_formats={'irr': '{:.1%}'}))



    df = vw.timeseries()
    cols = st.columns(2)
    with cols[0]:
        st.line_chart(df, x='date', y=['spot', 'fut'])
    with cols[1]:
        st.line_chart(df, x='date', y='basis')

    st.subheader('All Undl')
    df = vw.all_undl()
    st.dataframe(table_heatmap(df, col_format='{:.1%}'))


if __name__ == '__main__':
    if runtime.exists():
        main()
    else:
        sys.argv = ['streamlit', 'run', 'home.py']
        sys.exit(stcli.main())
