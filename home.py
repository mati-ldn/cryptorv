import sys
import streamlit as st
from streamlit.web import cli as stcli

from cryptorv.data.basis import BasisTbl, BasisSummaryTblAbs, BasisSummaryTblPct


df = BasisSummaryTblPct().load()
st.table(df)


if __name__ == '__main__':
    sys.argv = ['streamlit', 'run', 'home.py']
    sys.exit(stcli.main())
