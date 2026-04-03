# pages/10_System_Status.py

import pandas as pd
import plotly.express as px
import streamlit as st

from src.config import DB_PATH
from src.db import get_table_row_counts, read_table
from src.ui_helpers import render_global_disclaimer, dataframe_download_button

st.set_page_config(page_title="System Status", page_icon="🛠️", layout="wide")

st.title("🛠️ System Status")
st.caption("Deployment diagnostics, synthetic data completeness checks, and database health visibility.")

st.info(
    """
This page is designed to help verify that the deployed Atlas JV Planning OS environment is fully initialized,
properly seeded, and ready for interactive use.
"""
)

# -----------------------------
# Load row counts
# -----------------------------
try:
    counts_df = get_table_row_counts()
except Exception as e:
    st.error(f"Could not load database diagnostics: {e}")
    render_global_disclaimer()
    st.stop()

if counts_df.empty:
    st.warning("No diagnostic information could be generated from the database.")
    render_global_disclaimer()
    st.stop()

# -----------------------------
# Derived health logic
# -----------------------------
critical_tables = [
    "ventures",
    "assets",
    "scenarios",
    "plan_versions",
    "assumptions",
    "projects",
    "monthly_actuals",
    "kpis",
    "validation_issues",
]

counts_df["is_critical"] = counts_df["table_name"].isin(critical_tables)
counts_df["status"] = counts_df["row_count"].apply(lambda x: "Empty" if x == 0 else "Populated")

critical_df = counts_df[counts_df["is_critical"]].copy()
empty_critical_df = critical_df[critical_df["row_count"] == 0].copy()

database_ready = empty_critical_df.empty

# -----------------------------
# Top summary
# -----------------------------
m1, m2, m3, m4 = st.columns(4)
m1.metric("Tracked Tables", len(counts_df))
m2.metric("Critical Tables", len(critical_df))
m3.metric("Empty Critical Tables", len(empty_critical_df))
m4.metric("System Readiness", "Ready" if database_ready else "Incomplete")

st.markdown("### Deployment Context")
st.code(f"DB_PATH = {DB_PATH}")

if database_ready:
    st.success("The database appears complete enough for the main Atlas JV Planning OS workflow pages.")
else:
    st.warning(
        "The deployed database appears incomplete. Some workflow pages may show empty states or limited functionality."
    )

# -----------------------------
# Health visualization
# -----------------------------
st.subheader("Table Population Overview")

fig_counts = px.bar(
    counts_df.sort_values(["is_critical", "row_count"], ascending=[False, False]),
    x="table_name",
    y="row_count",
    color="status",
    pattern_shape="is_critical",
    title="Row Counts by Table",
    color_discrete_map={"Populated": "#2E8B57", "Empty": "#D62728"},
)
fig_counts.update_layout(
    xaxis_title="Table",
    yaxis_title="Row Count",
    template="plotly_white",
    height=450,
)
st.plotly_chart(fig_counts, use_container_width=True)

# -----------------------------
# Detailed diagnostics
# -----------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Row Counts",
    "Critical Gaps",
    "Recent Data Preview",
    "Recommended Actions",
])

with tab1:
    st.markdown("### Table Row Counts")
    st.dataframe(counts_df, use_container_width=True)
    dataframe_download_button(counts_df, "system_status_row_counts.csv", "Download Row Counts CSV")

with tab2:
    st.markdown("### Critical Table Gaps")

    if empty_critical_df.empty:
        st.success("No critical table gaps detected.")
    else:
        st.dataframe(empty_critical_df, use_container_width=True)

        with st.expander("Why this matters"):
            st.markdown(
                """
If a critical table is empty, one or more workflow pages may appear incomplete.

Examples:
- **monthly_actuals empty** → KPI Dashboard and Mid-Year Update cannot run properly
- **assumptions empty** → Planning Intake and plan comparisons lose value
- **projects empty** → Economics page becomes limited
- **kpis empty** → KPI storage and derived reporting are incomplete
"""
            )

with tab3:
    st.markdown("### Recent Data Preview")

    preview_table = st.selectbox(
        "Select a table to preview",
        counts_df["table_name"].tolist(),
        index=0,
    )

    try:
        preview_df = read_table(preview_table)
        if preview_df.empty:
            st.info(f"No rows available in `{preview_table}`.")
        else:
            st.dataframe(preview_df.head(20), use_container_width=True)
    except Exception as e:
        st.error(f"Could not preview `{preview_table}`: {e}")

with tab4:
    st.markdown("### Recommended Actions")

    if database_ready:
        st.markdown(
            """
The deployment appears healthy.

Recommended next checks:
- verify Planning Intake works end-to-end
- verify Economics saves results to SQLite
- verify KPI Dashboard and Mid-Year Update show populated synthetic data
- verify Planning Database comparisons are visually meaningful
"""
        )
    else:
        st.markdown(
            """
The deployment appears incomplete.

Recommended actions:
1. verify schema initialization runs on startup
2. verify database bootstrap seeds **all** critical tables
3. verify `monthly_actuals` and `kpis` are populated in cloud deployment
4. verify the deployed SQLite path is correct and writable
5. rebuild/reseed the deployment database if necessary
"""
        )

st.subheader("Interpretation Guide")
with st.expander("How to read this page"):
    st.markdown(
        """
- **Ready** means the key workflow tables needed by the app appear populated.
- **Incomplete** means one or more important tables are empty.
- A page can still render while the deployment is incomplete, but certain modules may be unavailable or unconvincing.
- This page is intended to support both debugging and reviewer transparency.
"""
    )

render_global_disclaimer()