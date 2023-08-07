import sys
import streamlit as st
from streamlit import runtime
from streamlit.web import cli as stcli

from cryptorv.data.basis import BasisTbl, BasisSummaryTblAbs, BasisSummaryTblPct


def main():
    df = BasisSummaryTblPct().load()
    st.table(df)


if __name__ == '__main__':
    if runtime.exits():
        main()
    else:
        sys.argv = ['streamlit', 'run', 'home.py']
        sys.exit(stcli.main())
