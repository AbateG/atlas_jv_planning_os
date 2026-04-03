# pages/4_Planning_Database.py

import plotly.express as px
import streamlit as st

from src.reporting import build_table_profile, build_plan_comparison, build_validation_summary
from src.ui_helpers import (
    load_table,
    load_joined_assumptions,
    render_global_disclaimer,
    dataframe_download_button,
)

st.set_page_config(page_title="Planning Database", page_icon="🗄️", layout="wide")

st.title("🗄️ Planning Database")
st.caption("Structured visibility into the synthetic planning data model, planning assumptions, validation issues, and stored outputs.")

st.info(
    """
This page is designed for transparency and traceability.
It allows users to inspect the synthetic database tables that support planning intake, economics, KPI reporting, and reforecasting.
"""
)

table_options = [
    "ventures",
    "assets",
    "scenarios",
    "plan_versions",
    "assumptions",
    "projects",
    "economics_results",
    "monthly_actuals",
    "kpis",
    "validation_issues",
]

tab1, tab2, tab3 = st.tabs(["Table Explorer", "Plan Comparison", "Data Quality Signals"])

with tab1:
    st.subheader("Table Explorer")

    table_name = st.selectbox("Select table to inspect", table_options)
    df = load_table(table_name)

    if df.empty:
        st.warning(f"No data found in `{table_name}`.")
    else:
        m1, m2, m3 = st.columns(3)
        m1.metric("Rows", len(df))
        m2.metric("Columns", len(df.columns))
        m3.metric("Null Cells", int(df.isna().sum().sum()))

        with st.expander("Column Overview"):
            st.dataframe(build_table_profile(df), use_container_width=True)

        st.markdown(f"### Preview: `{table_name}`")
        st.dataframe(df, use_container_width=True)
        dataframe_download_button(df, f"{table_name}.csv", f"Download {table_name} CSV")

with tab2:
    st.subheader("Plan Version Comparison")

    assumptions_df = load_joined_assumptions()

    if assumptions_df.empty:
        st.warning("No joined assumptions data available.")
    else:
        versions = sorted(assumptions_df["version_name"].dropna().unique().tolist())

        if len(versions) < 2:
            st.info("At least two plan versions are needed for comparison.")
        else:
            c1, c2, c3 = st.columns(3)

            with c1:
                version_a = st.selectbox("Version A", versions, index=0)

            with c2:
                version_b = st.selectbox("Version B", versions, index=1 if len(versions) > 1 else 0)

            with c3:
                compare_level = st.radio("Comparison Level", ["Venture", "Asset"], horizontal=True)

            comparison = build_plan_comparison(
                assumptions_df=assumptions_df,
                version_a=version_a,
                version_b=version_b,
                compare_level=compare_level,
            )

            st.dataframe(comparison, use_container_width=True)

            key_col = "venture_name" if compare_level == "Venture" else "asset_name"

            if not comparison.empty:
                chart_metric = st.selectbox(
                    "Metric to visualize",
                    ["production_delta", "capex_delta", "oil_price_delta", "opex_per_bbl_delta"]
                )

                fig_compare = px.bar(
                    comparison.sort_values(chart_metric, ascending=False),
                    x=key_col,
                    y=chart_metric,
                    title=f"{chart_metric.replace('_', ' ').title()} | {version_a} vs {version_b}",
                )
                fig_compare.update_layout(template="plotly_white", height=450, xaxis_title="", yaxis_title="")
                st.plotly_chart(fig_compare, use_container_width=True)

with tab3:
    st.subheader("Data Quality Signals")

    validation_df = load_table("validation_issues")
    economics_df = load_table("economics_results")
    assumptions_df = load_table("assumptions")

    q1, q2, q3 = st.columns(3)
    q1.metric("Validation Issues", 0 if validation_df.empty else len(validation_df))
    q2.metric("Economic Results Saved", 0 if economics_df.empty else len(economics_df))
    q3.metric("Assumption Rows", 0 if assumptions_df.empty else len(assumptions_df))

    severity_summary = build_validation_summary(validation_df)

    if not severity_summary.empty:
        fig_issues = px.bar(
            severity_summary,
            x="severity",
            y="issue_count",
            color="severity",
            title="Validation Issues by Severity"
        )
        fig_issues.update_layout(template="plotly_white", height=400)
        st.plotly_chart(fig_issues, use_container_width=True)

        st.markdown("### Validation Issue Details")
        st.dataframe(validation_df, use_container_width=True)
    else:
        st.info("No validation issues currently stored.")

render_global_disclaimer()