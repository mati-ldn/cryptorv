import pandas as pd
import sys
import streamlit as st
from streamlit import runtime
from streamlit.web import cli as stcli
import plotly.express as px

from viewer import BasisViewer
from formatters import table_heatmap, table_format
from conf import UNDLS


def main():
    cols = st.columns([4, 1])
    with cols[0]:
        st.title(':classical_building: Crypto RV')
    with cols[1]:
        if st.button("🔄 Refresh"):
            st.rerun()
        timestamp = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        st.write(timestamp)

    st.subheader('Implied Repo Matrix')
    vw = BasisViewer('BTC')
    df = vw.all_undl()
    st.dataframe(table_heatmap(df, col_format='{:.1%}'))

    tabs = st.tabs(UNDLS)
    for i in range(len(UNDLS)):
        with tabs[i]:
            undl = UNDLS[i]
            vw = BasisViewer(undl)
            try:
                df = vw.basis_tbl()
                st.dataframe(table_format(df, custom_formats={'irr': '{:.1%}'}))
            except Exception as e:
                st.error(f'{e}')

            df = vw.timeseries()
            cols = st.columns(2)
            with cols[0]:
                fig = px.line(
                    df,
                    x='date',
                    y=['spot', 'fut'],
                    title='Spot vs Futures Price',
                )
                st.plotly_chart(fig)
            with cols[1]:
                fig = px.line(df, x='date', y=['basis'], title='$ basis')
                st.plotly_chart(fig)


if __name__ == '__main__':
    if runtime.exists():
        main()
    else:
        sys.argv = ['streamlit', 'run', 'home.py']
        sys.exit(stcli.main())
