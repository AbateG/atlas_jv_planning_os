# pages/8_Data_Dictionary.py

import pandas as pd
import streamlit as st

from src.ui_helpers import render_global_disclaimer, dataframe_download_button

st.set_page_config(page_title="Data Dictionary", page_icon="📚", layout="wide")

st.title("📚 Data Dictionary")
st.caption("Interactive reference for the synthetic Atlas JV Planning OS data model.")

dictionary_rows = [
    ["ventures", "venture_id", "INTEGER", "Unique venture identifier"],
    ["ventures", "venture_name", "TEXT", "Fictitious venture name"],
    ["ventures", "basin", "TEXT", "Synthetic basin label"],
    ["ventures", "fluid_type", "TEXT", "High-level hydrocarbon category"],

    ["assets", "asset_id", "INTEGER", "Unique asset identifier"],
    ["assets", "venture_id", "INTEGER", "Associated venture foreign key"],
    ["assets", "asset_name", "TEXT", "Fictitious asset name"],
    ["assets", "asset_type", "TEXT", "Asset classification"],
    ["assets", "status", "TEXT", "Synthetic asset lifecycle status"],

    ["scenarios", "scenario_id", "INTEGER", "Scenario identifier"],
    ["scenarios", "scenario_name", "TEXT", "Scenario label"],
    ["scenarios", "description", "TEXT", "Scenario description"],

    ["plan_versions", "version_id", "INTEGER", "Unique plan version identifier"],
    ["plan_versions", "version_name", "TEXT", "Plan version label"],
    ["plan_versions", "plan_year", "INTEGER", "Planning year"],
    ["plan_versions", "scenario_id", "INTEGER", "Associated scenario foreign key"],
    ["plan_versions", "status", "TEXT", "Plan lifecycle status"],

    ["assumptions", "assumption_id", "INTEGER", "Assumption row identifier"],
    ["assumptions", "version_id", "INTEGER", "Associated plan version foreign key"],
    ["assumptions", "asset_id", "INTEGER", "Associated asset foreign key"],
    ["assumptions", "oil_price", "REAL", "Synthetic oil price assumption"],
    ["assumptions", "gas_price", "REAL", "Synthetic gas price assumption"],
    ["assumptions", "fx_rate", "REAL", "Synthetic FX assumption"],
    ["assumptions", "inflation_rate", "REAL", "Synthetic inflation assumption"],
    ["assumptions", "production_bopd", "REAL", "Planned production rate in bopd"],
    ["assumptions", "opex_per_bbl", "REAL", "Operating expense per barrel"],
    ["assumptions", "capex_mm", "REAL", "Capital expenditure in million USD"],
    ["assumptions", "royalty_rate", "REAL", "Synthetic royalty assumption"],
    ["assumptions", "tax_rate", "REAL", "Synthetic tax assumption"],

    ["projects", "project_id", "INTEGER", "Project identifier"],
    ["projects", "asset_id", "INTEGER", "Associated asset foreign key"],
    ["projects", "version_id", "INTEGER", "Associated plan version foreign key"],
    ["projects", "project_name", "TEXT", "Fictitious project name"],
    ["projects", "project_type", "TEXT", "Project category"],
    ["projects", "start_date", "TEXT", "Synthetic project start date"],
    ["projects", "end_date", "TEXT", "Synthetic project end date"],
    ["projects", "capex_mm", "REAL", "Project capex in million USD"],
    ["projects", "expected_uplift_bopd", "REAL", "Expected production uplift"],
    ["projects", "status", "TEXT", "Synthetic project status"],

    ["economics_results", "economics_result_id", "INTEGER", "Economic result identifier"],
    ["economics_results", "project_id", "INTEGER", "Associated project foreign key"],
    ["economics_results", "plan_version_id", "INTEGER", "Selected plan version foreign key"],
    ["economics_results", "npv", "REAL", "Calculated net present value"],
    ["economics_results", "irr", "REAL", "Calculated internal rate of return"],
    ["economics_results", "payback_period_years", "REAL", "Calculated payback period"],
    ["economics_results", "total_revenue", "REAL", "Total modelled revenue"],
    ["economics_results", "total_opex", "REAL", "Total modelled opex"],
    ["economics_results", "total_royalty", "REAL", "Total modelled royalty"],
    ["economics_results", "total_tax", "REAL", "Total modelled tax"],
    ["economics_results", "total_fcf", "REAL", "Total modelled free cash flow"],

    ["monthly_actuals", "actual_id", "INTEGER", "Monthly actual record identifier"],
    ["monthly_actuals", "asset_id", "INTEGER", "Associated asset foreign key"],
    ["monthly_actuals", "year_month", "TEXT", "Month in YYYY-MM format"],
    ["monthly_actuals", "production_bbl", "REAL", "Monthly production volume"],
    ["monthly_actuals", "opex_mm", "REAL", "Monthly operating expense in million USD"],
    ["monthly_actuals", "capex_mm", "REAL", "Monthly capex in million USD"],
    ["monthly_actuals", "earnings_mm", "REAL", "Monthly earnings in million USD"],
    ["monthly_actuals", "cashflow_mm", "REAL", "Monthly cash flow in million USD"],

    ["kpis", "kpi_id", "INTEGER", "KPI record identifier"],
    ["kpis", "asset_id", "INTEGER", "Associated asset foreign key"],
    ["kpis", "version_id", "INTEGER", "Associated plan version foreign key"],
    ["kpis", "year_month", "TEXT", "Month in YYYY-MM format"],
    ["kpis", "production_bopd", "REAL", "Derived production KPI"],
    ["kpis", "lifting_cost_per_bbl", "REAL", "Derived lifting cost KPI"],
    ["kpis", "capex_intensity", "REAL", "Derived capex intensity KPI"],
    ["kpis", "earnings_margin", "REAL", "Derived earnings margin KPI"],
    ["kpis", "cashflow_margin", "REAL", "Derived cash flow margin KPI"],

    ["validation_issues", "issue_id", "INTEGER", "Validation issue identifier"],
    ["validation_issues", "version_id", "INTEGER", "Associated plan version foreign key"],
    ["validation_issues", "asset_id", "INTEGER", "Associated asset foreign key"],
    ["validation_issues", "severity", "TEXT", "Issue severity label"],
    ["validation_issues", "issue_type", "TEXT", "Issue category"],
    ["validation_issues", "issue_message", "TEXT", "Validation issue explanation"],
]

dict_df = pd.DataFrame(dictionary_rows, columns=["Table", "Field", "Type", "Description"])

st.subheader("Dictionary Explorer")

c1, c2 = st.columns(2)
with c1:
    table_filter = st.selectbox("Filter by table", ["All"] + sorted(dict_df["Table"].unique().tolist()))
with c2:
    search_text = st.text_input("Search field or description")

filtered_df = dict_df.copy()

if table_filter != "All":
    filtered_df = filtered_df[filtered_df["Table"] == table_filter]

if search_text:
    mask = (
        filtered_df["Field"].str.contains(search_text, case=False, na=False) |
        filtered_df["Description"].str.contains(search_text, case=False, na=False) |
        filtered_df["Table"].str.contains(search_text, case=False, na=False)
    )
    filtered_df = filtered_df[mask]

m1, m2, m3 = st.columns(3)
m1.metric("Tables", dict_df["Table"].nunique())
m2.metric("Fields", len(filtered_df))
m3.metric("Filtered Tables", filtered_df["Table"].nunique())

st.dataframe(filtered_df, use_container_width=True)
dataframe_download_button(filtered_df, "atlas_data_dictionary.csv", "Download Data Dictionary CSV")

st.subheader("Entity Relationship Summary")
st.markdown(
    """
- **ventures → assets**: one venture can contain many assets  
- **scenarios → plan_versions**: one scenario can contain many plan versions  
- **plan_versions + assets → assumptions**: one row per asset per version  
- **assets + plan_versions → projects**: projects are linked to both asset and version  
- **projects + plan_versions → economics_results**: stored economics outputs  
- **assets → monthly_actuals**: monthly actual performance by asset  
- **assets + versions → kpis**: derived KPI storage  
- **plan_versions + assets → validation_issues**: data quality and rule checks  
"""
)

with st.expander("How to use this page"):
    st.markdown(
        """
Use this page to quickly understand:

- what each table represents
- what each field means
- how planning assumptions connect to economics and KPI reporting
- where validation and derived outputs are stored
"""
    )

render_global_disclaimer()