# pages/6_Mid_Year_Update.py

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.forecasting import (
    prepare_mid_year_actuals,
    filter_mid_year_df,
    split_ytd_h2,
    apply_h2_adjustments,
    combine_ytd_and_reforecast,
    build_summary_table,
    build_reforecast_compare_table,
    build_monthly_compare_table,
    make_display_df,
)
from src.ui_helpers import (
    load_joined_monthly_actuals,
    render_global_disclaimer,
    dataframe_download_button,
)

st.set_page_config(page_title="Mid-Year Update", page_icon="🔄", layout="wide")

st.title("🔄 Mid-Year Update / Reforecast")
st.caption("Synthetic YTD actuals plus revised H2 assumptions to simulate a simplified full-year reforecast process.")

st.info(
    """
This module simulates a simplified mid-year reforecast workflow using synthetic monthly performance data.
It is designed to demonstrate planning update logic, not real forecasting or financial guidance.
"""
)

raw_df = load_joined_monthly_actuals()

if raw_df.empty:
    st.warning("No monthly actuals data available.")
    with st.expander("Why this might happen"):
        st.markdown(
            """
The Mid-Year Update module requires seeded synthetic `monthly_actuals`.

If this is a deployed environment, the database may be incomplete.
Recommended checks:
- verify the database bootstrap process
- verify `monthly_actuals` has been seeded
- review the System Status page for table row counts
"""
        )
    render_global_disclaimer()
    st.stop()

try:
    df = prepare_mid_year_actuals(raw_df)
except ValueError as e:
    st.error(str(e))
    render_global_disclaimer()
    st.stop()

# -----------------------------
# Filters
# -----------------------------
f1, f2 = st.columns(2)

with f1:
    venture_options = ["All"] + sorted(df["venture_name"].dropna().unique().tolist())
    selected_venture = st.selectbox("Venture", venture_options)

with f2:
    asset_options = ["All"] + sorted(df["asset_name"].dropna().unique().tolist())
    selected_asset = st.selectbox("Asset", asset_options)

filtered_df = filter_mid_year_df(df, selected_venture, selected_asset)

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    render_global_disclaimer()
    st.stop()

# -----------------------------
# Reforecast controls
# -----------------------------
st.subheader("Reforecast Controls")

c1, c2, c3, c4 = st.columns(4)
with c1:
    cutoff_month = st.slider("YTD Cutoff Month", 3, 9, 6, 1)
with c2:
    production_factor = st.slider("H2 Production Adjustment", 0.80, 1.20, 1.00, 0.01)
with c3:
    opex_factor = st.slider("H2 Opex Adjustment", 0.80, 1.20, 1.00, 0.01)
with c4:
    capex_factor = st.slider("H2 Capex Adjustment", 0.80, 1.20, 1.00, 0.01)

c5, c6 = st.columns(2)
with c5:
    earnings_factor = st.slider("H2 Earnings Adjustment", 0.80, 1.20, 1.00, 0.01)
with c6:
    cashflow_factor = st.slider("H2 Cash Flow Adjustment", 0.80, 1.20, 1.00, 0.01)

# -----------------------------
# Reforecast build
# -----------------------------
ytd_df, h2_df = split_ytd_h2(filtered_df, cutoff_month)

reforecast_h2 = apply_h2_adjustments(
    h2_df,
    production_factor=production_factor,
    opex_factor=opex_factor,
    capex_factor=capex_factor,
    earnings_factor=earnings_factor,
    cashflow_factor=cashflow_factor,
)

original_fy = filtered_df.copy()
reforecast_fy = combine_ytd_and_reforecast(ytd_df, reforecast_h2)

summary_table = build_summary_table(
    ytd_df=ytd_df,
    original_h2=h2_df,
    reforecast_h2=reforecast_h2,
    original_fy=original_fy,
    reforecast_fy=reforecast_fy,
    cutoff_month=cutoff_month,
)

compare_table = build_reforecast_compare_table(original_fy, reforecast_fy)
monthly_compare = build_monthly_compare_table(original_fy, reforecast_fy)

headline_lookup = {row["metric"]: row for _, row in compare_table.iterrows()}

# -----------------------------
# Executive context
# -----------------------------
st.subheader("Executive Reforecast Summary")

e1, e2, e3, e4 = st.columns(4)
e1.metric("Venture Scope", selected_venture)
e2.metric("Asset Scope", selected_asset)
e3.metric("YTD Cutoff", f"Month {cutoff_month}")
e4.metric("Months in Scope", filtered_df["year_label"].nunique())

# -----------------------------
# Headline impacts
# -----------------------------
st.subheader("Headline Reforecast Impact")

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("FY Production (bbl)", f"{headline_lookup['production_bbl']['reforecast_fy']:,.0f}", f"{headline_lookup['production_bbl']['delta']:,.0f}")
m2.metric("FY Opex ($MM)", f"{headline_lookup['opex_mm']['reforecast_fy']:,.2f}", f"{headline_lookup['opex_mm']['delta']:,.2f}")
m3.metric("FY Capex ($MM)", f"{headline_lookup['capex_mm']['reforecast_fy']:,.2f}", f"{headline_lookup['capex_mm']['delta']:,.2f}")
m4.metric("FY Earnings ($MM)", f"{headline_lookup['earnings_mm']['reforecast_fy']:,.2f}", f"{headline_lookup['earnings_mm']['delta']:,.2f}")
m5.metric("FY Cash Flow ($MM)", f"{headline_lookup['cashflow_mm']['reforecast_fy']:,.2f}", f"{headline_lookup['cashflow_mm']['delta']:,.2f}")

# -----------------------------
# Tables
# -----------------------------
st.subheader("Period Summary")
st.dataframe(summary_table, use_container_width=True)

st.subheader("Original vs Reforecast")
st.dataframe(compare_table, use_container_width=True)

# -----------------------------
# Charts
# -----------------------------
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    fig_compare = px.bar(
        compare_table,
        x="metric",
        y=["original_fy", "reforecast_fy"],
        barmode="group",
        title="Original Full-Year vs Reforecast"
    )
    fig_compare.update_layout(template="plotly_white", height=420, xaxis_title="", yaxis_title="")
    st.plotly_chart(fig_compare, use_container_width=True)

with chart_col2:
    fig_monthly = go.Figure()
    fig_monthly.add_scatter(
        x=monthly_compare["year_label"],
        y=monthly_compare["original_cashflow_mm"],
        mode="lines+markers",
        name="Original Cash Flow"
    )
    fig_monthly.add_scatter(
        x=monthly_compare["year_label"],
        y=monthly_compare["reforecast_cashflow_mm"],
        mode="lines+markers",
        name="Reforecast Cash Flow"
    )
    fig_monthly.update_layout(
        title="Monthly Cash Flow: Original vs Reforecast",
        xaxis_title="Month",
        yaxis_title="$MM",
        template="plotly_white",
        height=420,
    )
    st.plotly_chart(fig_monthly, use_container_width=True)

# -----------------------------
# Detail tabs
# -----------------------------
st.subheader("YTD Actuals and Reforecast Detail")

detail_tab1, detail_tab2, detail_tab3 = st.tabs(["YTD Actuals", "Original H2", "Reforecast H2"])

with detail_tab1:
    if ytd_df.empty:
        st.info("No YTD rows available for the selected cutoff/filter combination.")
    else:
        st.dataframe(make_display_df(ytd_df), use_container_width=True)

with detail_tab2:
    if h2_df.empty:
        st.info("No original H2 rows available for the selected cutoff/filter combination.")
    else:
        st.dataframe(make_display_df(h2_df), use_container_width=True)

with detail_tab3:
    if reforecast_h2.empty:
        st.info("No reforecast H2 rows available for the selected cutoff/filter combination.")
    else:
        st.dataframe(make_display_df(reforecast_h2), use_container_width=True)

commentary = st.text_area(
    "Reforecast Commentary",
    placeholder="Summarize key changes versus original plan, major assumptions, and expected full-year outcome..."
)

if commentary:
    st.success("Reforecast commentary captured locally in session for demonstration.")

dataframe_download_button(compare_table, "mid_year_update_summary.csv", "Download Reforecast Summary CSV")

with st.expander("How to interpret this module"):
    st.markdown(
        """
- **YTD Actuals** represent locked-in synthetic actual performance up to the selected cutoff month
- **Original H2** represents the original synthetic remaining-year outlook
- **Reforecast H2** applies user-selected adjustment factors to simulate a revised outlook
- **Original vs Reforecast** highlights how the revised H2 assumptions change the full-year view

This module is intentionally simplified for educational and portfolio purposes.
"""
    )

render_global_disclaimer()