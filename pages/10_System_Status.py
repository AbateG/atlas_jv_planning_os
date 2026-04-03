# pages/10_System_Status.py

import streamlit as st
from src.db import get_table_row_counts
from src.config import DB_PATH

st.set_page_config(page_title="System Status", page_icon="🛠️", layout="wide")

st.title("🛠️ System Status")
st.caption("Deployment diagnostics for database completeness and synthetic data availability.")

st.code(f"DB_PATH = {DB_PATH}")

counts_df = get_table_row_counts()
st.dataframe(counts_df, use_container_width=True)

empty_tables = counts_df[counts_df["row_count"] == 0]

if empty_tables.empty:
    st.success("All tracked tables contain data.")
else:
    st.warning("Some tracked tables are empty.")
    st.dataframe(empty_tables, use_container_width=True)