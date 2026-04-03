# pages/5_KPI_Dashboard.py

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.kpi import (
    prepare_monthly_kpi_dataframe,
    summarize_monthly_kpis,
    summarize_asset_kpis,
)
from src.ui_helpers import (
    load_joined_monthly_actuals,
    render_global_disclaimer,
    dataframe_download_button,
)

st.set_page_config(page_title="KPI Dashboard", page_icon="📊", layout="wide")

st.title("📊 KPI Dashboard")
st.caption("Synthetic upstream JV performance reporting across production, cost, earnings, and cash flow.")

st.info(
    """
This dashboard uses entirely synthetic monthly operating and financial performance data.
It is designed to demonstrate portfolio-style KPI reporting, not real operating or financial reporting.
"""
)

raw_df = load_joined_monthly_actuals()

if raw_df.empty:
    st.warning("No monthly actuals data found in the database.")
    with st.expander("Why this might happen"):
        st.markdown(
            """
This dashboard depends on seeded synthetic `monthly_actuals` data.

If you are viewing a cloud deployment, this usually means:
- the database bootstrap completed only partially, or
- the deployed database was initialized without monthly performance data.

Recommended checks:
- verify the database seeding process includes `monthly_actuals` and `kpis`
- verify the deployed SQLite path and bootstrap flow
- verify the System Status page for table row counts
"""
        )
    render_global_disclaimer()
    st.stop()

required_cols = [
    "venture_name",
    "asset_name",
    "year_month",
    "production_bbl",
    "opex_mm",
    "capex_mm",
    "earnings_mm",
    "cashflow_mm",
]
missing_cols = [col for col in required_cols if col not in raw_df.columns]

if missing_cols:
    st.error(f"Missing required KPI columns: {missing_cols}")
    render_global_disclaimer()
    st.stop()

df = prepare_monthly_kpi_dataframe(raw_df)

st.subheader("Filters")

f1, f2, f3 = st.columns(3)

with f1:
    venture_options = ["All"] + sorted(df["venture_name"].dropna().unique().tolist())
    selected_venture = st.selectbox("Venture", venture_options)

with f2:
    asset_options = ["All"] + sorted(df["asset_name"].dropna().unique().tolist())
    selected_asset = st.selectbox("Asset", asset_options)

with f3:
    month_options = sorted(df["year_month"].dt.strftime("%Y-%m").unique().tolist())
    selected_month_range = st.select_slider(
        "Month range",
        options=month_options,
        value=(month_options[0], month_options[-1]),
    )

filtered_df = df.copy()

if selected_venture != "All":
    filtered_df = filtered_df[filtered_df["venture_name"] == selected_venture]

if selected_asset != "All":
    filtered_df = filtered_df[filtered_df["asset_name"] == selected_asset]

start_month = pd.to_datetime(selected_month_range[0])
end_month = pd.to_datetime(selected_month_range[1])

filtered_df = filtered_df[
    (filtered_df["year_month"] >= start_month) &
    (filtered_df["year_month"] <= end_month)
].copy()

if filtered_df.empty:
    st.warning("No KPI data is available for the selected filters.")
    render_global_disclaimer()
    st.stop()

summary = summarize_monthly_kpis(filtered_df)
asset_summary = summarize_asset_kpis(filtered_df)

summary = summary.sort_values("year_month").reset_index(drop=True)
asset_summary = asset_summary.reset_index(drop=True)

latest = summary.iloc[-1]
previous = summary.iloc[-2] if len(summary) > 1 else None

def delta_str(curr, prev):
    if prev is None or pd.isna(prev):
        return None
    return curr - prev

# -----------------------------
# Executive summary
# -----------------------------
st.subheader("Executive Summary")

es1, es2, es3, es4 = st.columns(4)
es1.metric("Filtered Ventures", filtered_df["venture_name"].nunique())
es2.metric("Filtered Assets", filtered_df["asset_name"].nunique())
es3.metric("Months in Scope", summary["year_month"].nunique())
es4.metric("Records in Scope", len(filtered_df))

# -----------------------------
# Headline KPIs
# -----------------------------
st.subheader("Headline Monthly KPIs")

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Production (bbl)", f"{latest['production_bbl']:,.0f}", None if previous is None else f"{delta_str(latest['production_bbl'], previous['production_bbl']):,.0f}")
m2.metric("Opex ($MM)", f"{latest['opex_mm']:,.2f}", None if previous is None else f"{delta_str(latest['opex_mm'], previous['opex_mm']):,.2f}")
m3.metric("Capex ($MM)", f"{latest['capex_mm']:,.2f}", None if previous is None else f"{delta_str(latest['capex_mm'], previous['capex_mm']):,.2f}")
m4.metric("Earnings ($MM)", f"{latest['earnings_mm']:,.2f}", None if previous is None else f"{delta_str(latest['earnings_mm'], previous['earnings_mm']):,.2f}")
m5.metric("Cash Flow ($MM)", f"{latest['cashflow_mm']:,.2f}", None if previous is None else f"{delta_str(latest['cashflow_mm'], previous['cashflow_mm']):,.2f}")

m6, m7, m8 = st.columns(3)
m6.metric("Production (bopd)", f"{latest['production_bopd']:,.0f}")
m7.metric("Opex per bbl ($/bbl)", f"{latest['opex_per_bbl']:,.2f}" if pd.notna(latest["opex_per_bbl"]) else "N/A")
m8.metric("Capex Intensity ($/bbl)", f"{latest['capex_intensity']:,.2f}" if pd.notna(latest["capex_intensity"]) else "N/A")

# -----------------------------
# Trends
# -----------------------------
st.subheader("Performance Trends")

col_a, col_b = st.columns(2)

with col_a:
    fig_prod = px.line(
        summary,
        x="year_month",
        y=["production_bbl", "production_bopd"],
        title="Production Trend",
        markers=True
    )
    fig_prod.update_layout(xaxis_title="Month", yaxis_title="Production", template="plotly_white", height=420)
    st.plotly_chart(fig_prod, use_container_width=True)

with col_b:
    fig_fin = px.line(
        summary,
        x="year_month",
        y=["opex_mm", "capex_mm", "earnings_mm", "cashflow_mm"],
        title="Financial KPI Trends",
        markers=True
    )
    fig_fin.update_layout(xaxis_title="Month", yaxis_title="$MM", template="plotly_white", height=420)
    st.plotly_chart(fig_fin, use_container_width=True)

# -----------------------------
# Efficiency and cash generation
# -----------------------------
st.subheader("Efficiency and Cash Generation")

col_c, col_d = st.columns(2)

with col_c:
    fig_eff = px.line(
        summary,
        x="year_month",
        y=["opex_per_bbl", "capex_intensity"],
        title="Cost Efficiency Trend",
        markers=True
    )
    fig_eff.update_layout(xaxis_title="Month", yaxis_title="$/bbl", template="plotly_white", height=420)
    st.plotly_chart(fig_eff, use_container_width=True)

with col_d:
    fig_cash = go.Figure()
    fig_cash.add_bar(x=summary["year_month"], y=summary["cashflow_mm"], name="Cash Flow ($MM)")
    fig_cash.add_scatter(x=summary["year_month"], y=summary["earnings_mm"], mode="lines+markers", name="Earnings ($MM)")
    fig_cash.update_layout(
        title="Cash Flow vs Earnings",
        xaxis_title="Month",
        yaxis_title="$MM",
        template="plotly_white",
        height=420
    )
    st.plotly_chart(fig_cash, use_container_width=True)

# -----------------------------
# Asset comparison
# -----------------------------
st.subheader("Asset Comparison")

col_e, col_f = st.columns(2)

with col_e:
    fig_asset_cf = px.bar(
        asset_summary.sort_values("cashflow_mm", ascending=False),
        x="asset_name",
        y="cashflow_mm",
        color="venture_name",
        title="Cash Flow by Asset",
    )
    fig_asset_cf.update_layout(xaxis_title="Asset", yaxis_title="$MM", template="plotly_white", height=420)
    st.plotly_chart(fig_asset_cf, use_container_width=True)

with col_f:
    fig_scatter = px.scatter(
        asset_summary,
        x="production_bbl",
        y="cashflow_mm",
        size="capex_mm",
        color="venture_name",
        hover_name="asset_name",
        title="Portfolio View: Production vs Cash Flow",
    )
    fig_scatter.update_layout(
        xaxis_title="Production (bbl)",
        yaxis_title="Cash Flow ($MM)",
        template="plotly_white",
        height=420
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# -----------------------------
# Leaderboards
# -----------------------------
st.subheader("Asset Leaderboards")

tab1, tab2, tab3 = st.tabs(["Top Cash Flow", "Lowest Opex per bbl", "Highest Production"])

with tab1:
    st.dataframe(asset_summary.sort_values("cashflow_mm", ascending=False).reset_index(drop=True), use_container_width=True)

with tab2:
    st.dataframe(asset_summary.sort_values("opex_per_bbl", ascending=True).reset_index(drop=True), use_container_width=True)

with tab3:
    st.dataframe(asset_summary.sort_values("production_bbl", ascending=False).reset_index(drop=True), use_container_width=True)

# -----------------------------
# Detailed data
# -----------------------------
st.subheader("Detailed Monthly Data")
display_df = filtered_df.copy()
display_df["year_month"] = display_df["year_month"].dt.strftime("%Y-%m")
st.dataframe(display_df, use_container_width=True)

commentary = st.text_area(
    "Management Commentary",
    placeholder="Enter high-level monthly performance commentary here..."
)

if commentary:
    st.success("Commentary captured locally in session for demonstration.")

dataframe_download_button(display_df, "kpi_dashboard_filtered.csv", "Download KPI Data CSV")

with st.expander("How to read this dashboard"):
    st.markdown(
        """
- **Production (bbl / bopd):** operational output trend over time
- **Opex ($MM):** monthly operating expenditure
- **Capex ($MM):** monthly capital investment
- **Earnings ($MM):** synthetic profitability indicator
- **Cash Flow ($MM):** synthetic operating cash generation indicator
- **Opex per bbl:** cost efficiency proxy
- **Capex intensity:** capital spent relative to produced volumes

This dashboard is intentionally simplified and uses entirely synthetic data for portfolio demonstration.
"""
    )

render_global_disclaimer()