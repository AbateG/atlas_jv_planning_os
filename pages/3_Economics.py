# pages/3_Economics.py

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.db import get_connection
from src.economics import (
    EconomicInputs,
    build_dcf_table,
    summarize_economics,
    build_standard_sensitivity_cases,
    build_tornado_summary,
    run_case_comparison,
    get_projects_for_economics,
    get_plan_versions,
    get_project_defaults,
    save_economic_result,
    validate_economic_inputs,
)

st.set_page_config(page_title="Economics", page_icon="📈", layout="wide")

st.title("📈 Economic Evaluation")
st.caption("Synthetic upstream JV project economics using a simplified annual discounted cash flow model.")

st.info(
    """
This module is educational and portfolio-oriented only.
All ventures, assets, projects, assumptions, and results are fictitious and based on synthetic data.
No confidential, proprietary, operational, or personally identifiable data is used.
"""
)

conn = get_connection()


def fmt_currency(x):
    return "N/A" if x is None else f"${x:,.0f}"


def fmt_pct(x):
    return "N/A" if x is None else f"{x:.1%}"


def fmt_years(x):
    return "N/A" if x is None else f"{x:.1f} years"


projects_df = get_projects_for_economics(conn)
versions_df = get_plan_versions(conn)

if projects_df.empty:
    st.warning("No projects found in the database.")
    st.stop()

if versions_df.empty:
    st.warning("No plan versions found in the database.")
    st.stop()

sel_col1, sel_col2 = st.columns([2, 2])

project_options = []
project_lookup = {}

for _, row in projects_df.iterrows():
    label = (
        f"{row['project_name']} | {row['asset_name']} | {row['venture_name']} "
        f"| Project Version {row['project_version_id']}"
    )
    project_options.append(label)
    project_lookup[label] = row.to_dict()

with sel_col1:
    selected_project_label = st.selectbox("Select project", project_options)

selected_project_row = project_lookup[selected_project_label]
selected_project_id = int(selected_project_row["project_id"])
project_version_id = int(selected_project_row["project_version_id"])

version_options = []
version_lookup = {}

for _, row in versions_df.iterrows():
    label = f"{row['version_name']} | {row['scenario_name']} | FY {row['plan_year']} | ID {row['version_id']}"
    version_options.append(label)
    version_lookup[label] = row.to_dict()

default_version_index = 0
for i, label in enumerate(version_options):
    if int(version_lookup[label]["version_id"]) == project_version_id:
        default_version_index = i
        break

with sel_col2:
    selected_version_label = st.selectbox(
        "Assumption version for economics run",
        version_options,
        index=default_version_index,
        help="Defaults to the project's own plan version. You may select another version for scenario-style testing."
    )

selected_version_row = version_lookup[selected_version_label]
selected_version_id = int(selected_version_row["version_id"])

if selected_version_id != project_version_id:
    st.warning(
        f"You are evaluating project '{selected_project_row['project_name']}' "
        f"using assumptions from plan version {selected_version_id}, "
        f"while the project belongs to version {project_version_id}. "
        "This is allowed here as a synthetic scenario test."
    )

defaults = get_project_defaults(conn, selected_project_id, selected_version_id)

st.subheader("Economic Assumptions")
st.caption(
    "Defaults are loaded from the selected project and matching asset/version assumptions where available. "
    "Project capex is sourced from projects.capex_mm and converted from MMUSD to USD for DCF calculations."
)

c1, c2, c3 = st.columns(3)

with c1:
    oil_price = st.number_input(
        "Oil price ($/bbl)",
        min_value=0.0,
        value=float(defaults["oil_price"]),
        step=1.0
    )
    production_uplift_bopd = st.number_input(
        "Production uplift (bopd)",
        min_value=0.0,
        value=float(defaults["production_uplift_bopd"]),
        step=100.0
    )
    opex_per_bbl = st.number_input(
        "Opex ($/bbl)",
        min_value=0.0,
        value=float(defaults["opex_per_bbl"]),
        step=1.0
    )

with c2:
    capex = st.number_input(
        "Capex ($)",
        min_value=0.0,
        value=float(defaults["capex"]),
        step=1_000_000.0,
        format="%.2f"
    )
    royalty_rate = st.number_input(
        "Royalty rate",
        min_value=0.0,
        max_value=1.0,
        value=float(defaults["royalty_rate"]),
        step=0.01
    )
    tax_rate = st.number_input(
        "Tax rate",
        min_value=0.0,
        max_value=1.0,
        value=float(defaults["tax_rate"]),
        step=0.01
    )

with c3:
    discount_rate = st.number_input(
        "Discount rate",
        min_value=0.0,
        max_value=1.0,
        value=float(defaults["discount_rate"]),
        step=0.01
    )
    project_life = st.number_input(
        "Project life (years)",
        min_value=1,
        max_value=50,
        value=int(defaults["project_life"]),
        step=1
    )
    annual_decline_rate = st.number_input(
        "Annual decline rate",
        min_value=0.0,
        max_value=1.0,
        value=float(defaults["annual_decline_rate"]),
        step=0.01
    )

with st.expander("Loaded planning context"):
    st.write({
        "project_id": defaults["project_id"],
        "project_name": defaults["project_name"],
        "asset_id": defaults["asset_id"],
        "asset_name": defaults["asset_name"],
        "venture_name": defaults["venture_name"],
        "project_version_id": defaults["project_version_id"],
        "selected_plan_version_id": defaults["plan_version_id"],
        "gas_price": defaults["gas_price"],
        "fx_rate": defaults["fx_rate"],
        "inflation_rate": defaults["inflation_rate"],
        "base_production_bopd": defaults["base_production_bopd"],
    })

inputs = EconomicInputs(
    project_id=defaults["project_id"],
    project_name=defaults["project_name"],
    asset_id=defaults.get("asset_id"),
    asset_name=defaults.get("asset_name"),
    venture_name=defaults.get("venture_name"),
    plan_version_id=selected_version_id,
    project_version_id=defaults.get("project_version_id"),
    scenario_name=selected_version_row.get("scenario_name"),
    oil_price=oil_price,
    production_uplift_bopd=production_uplift_bopd,
    opex_per_bbl=opex_per_bbl,
    capex=capex,
    royalty_rate=royalty_rate,
    tax_rate=tax_rate,
    discount_rate=discount_rate,
    project_life=int(project_life),
    annual_decline_rate=annual_decline_rate,
)

issues = validate_economic_inputs(inputs)
if issues:
    for issue in issues:
        st.error(issue)
    st.stop()

run_model = st.button("Run Economic Evaluation", type="primary", use_container_width=True)

if run_model:
    dcf_df = build_dcf_table(inputs)
    summary = summarize_economics(dcf_df)
    sensitivity_df = build_standard_sensitivity_cases(inputs)
    tornado_df = build_tornado_summary(inputs)
    case_compare_df = run_case_comparison(inputs)

    st.subheader("Project Context")
    meta1, meta2, meta3, meta4 = st.columns(4)
    meta1.metric("Project", inputs.project_name)
    meta2.metric("Asset", inputs.asset_name or "N/A")
    meta3.metric("Venture", inputs.venture_name or "N/A")
    meta4.metric("Scenario", inputs.scenario_name or "N/A")

    st.subheader("Headline Economics")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("NPV", fmt_currency(summary.npv))
    m2.metric("IRR", fmt_pct(summary.irr))
    m3.metric("Payback", fmt_years(summary.payback_period_years))
    m4.metric("Total FCF", fmt_currency(summary.total_fcf))

    m5, m6, m7, m8 = st.columns(4)
    m5.metric("Total Revenue", fmt_currency(summary.total_revenue))
    m6.metric("Total Opex", fmt_currency(summary.total_opex))
    m7.metric("Total Royalty", fmt_currency(summary.total_royalty))
    m8.metric("Total Tax", fmt_currency(summary.total_tax))

    st.subheader("Case Comparison")
    st.dataframe(case_compare_df, use_container_width=True)

    fig_cases = px.bar(
        case_compare_df,
        x="case",
        y="npv",
        color="case",
        title="NPV by Standard Scenario Case"
    )
    fig_cases.update_layout(template="plotly_white", height=400, showlegend=False)
    st.plotly_chart(fig_cases, use_container_width=True)

    st.subheader("Annual Cash Flow Profile")
    fig_cf = go.Figure()
    fig_cf.add_bar(x=dcf_df["year"], y=dcf_df["free_cash_flow"], name="Free Cash Flow")
    fig_cf.add_scatter(x=dcf_df["year"], y=dcf_df["cumulative_fcf"], mode="lines+markers", name="Cumulative FCF")
    fig_cf.add_scatter(
        x=dcf_df["year"],
        y=dcf_df["discounted_cumulative_fcf"],
        mode="lines",
        name="Discounted Cumulative FCF",
        line=dict(dash="dash")
    )
    fig_cf.update_layout(
        xaxis_title="Year",
        yaxis_title="USD",
        template="plotly_white",
        height=450
    )
    st.plotly_chart(fig_cf, use_container_width=True)

    left_col, right_col = st.columns(2)

    with left_col:
        fig_prod = px.line(
            dcf_df[dcf_df["year"] > 0],
            x="year",
            y="production_bbl",
            markers=True,
            title="Annual Production Profile"
        )
        fig_prod.update_layout(template="plotly_white", height=400)
        st.plotly_chart(fig_prod, use_container_width=True)

    with right_col:
        comp_df = dcf_df[dcf_df["year"] > 0][["year", "revenue", "opex", "royalty", "tax"]].melt(
            id_vars="year",
            var_name="component",
            value_name="value"
        )
        fig_components = px.bar(
            comp_df,
            x="year",
            y="value",
            color="component",
            barmode="group",
            title="Revenue and Cost Components"
        )
        fig_components.update_layout(template="plotly_white", height=400)
        st.plotly_chart(fig_components, use_container_width=True)

    st.subheader("Annual DCF Table")
    st.dataframe(dcf_df, use_container_width=True)

    st.subheader("Sensitivity Analysis")

    tornado_plot_df = tornado_df.copy()
    tornado_plot_df["variable_label"] = tornado_plot_df["variable"].str.replace("_", " ").str.title()

    fig_tornado = go.Figure()
    fig_tornado.add_bar(
        y=tornado_plot_df["variable_label"],
        x=tornado_plot_df["downside_impact"],
        orientation="h",
        name="Low Case Impact"
    )
    fig_tornado.add_bar(
        y=tornado_plot_df["variable_label"],
        x=tornado_plot_df["upside_impact"],
        orientation="h",
        name="High Case Impact"
    )
    fig_tornado.update_layout(
        title="Tornado View: NPV Impact vs Base Case",
        xaxis_title="Change in NPV ($)",
        yaxis_title="Variable",
        barmode="overlay",
        template="plotly_white",
        height=450
    )
    st.plotly_chart(fig_tornado, use_container_width=True)

    st.dataframe(sensitivity_df, use_container_width=True)

    csv_data = dcf_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download DCF Table as CSV",
        data=csv_data,
        file_name=f"atlas_economics_project_{inputs.project_id}_version_{inputs.plan_version_id}.csv",
        mime="text/csv",
        use_container_width=True
    )

    st.subheader("Methodology")
    st.markdown(
        """
**Model structure**
- Year 0 contains upfront capex as a negative free cash flow.
- Annual production is estimated from project uplift in bopd multiplied by 365 days.
- Production declines each year using the selected annual decline rate.
- Revenue = annual production × oil price.
- Opex = annual production × opex per bbl.
- Royalty = revenue × royalty rate.
- Pre-tax cash flow = revenue − opex − royalty.
- Tax = max(pre-tax cash flow, 0) × tax rate.
- Free cash flow = pre-tax cash flow − tax.
- NPV is calculated using the selected discount rate.
- IRR is calculated from the annual free cash flow series when mathematically available.
- Payback period is estimated from cumulative free cash flow using interpolation within the crossing year.

**Data linkage**
- Project capex and uplift defaults are sourced from the synthetic `projects` table.
- Price/cost/fiscal defaults are sourced from the synthetic `assumptions` table for the selected plan version and asset.
- This creates a simplified linkage between planning assumptions and economic evaluation.

**Important limitations**
- This is a simplified educational DCF model, not a reserves-certified field development model.
- It excludes financing, depreciation, working interest complexity, gas monetization logic, abandonment, inflation/escalation roll-forward, and detailed fiscal regime mechanics.
- All entities, scenarios, assumptions, and outputs are fictitious and synthetic.
"""
    )

    if st.button("Save Results to Database", use_container_width=True):
        try:
            save_economic_result(
                conn=conn,
                project_id=inputs.project_id,
                plan_version_id=inputs.plan_version_id,
                summary=summary,
                input_assumptions=inputs,
            )
            st.success("Economic results saved to SQLite.")
        except Exception as e:
            st.error(f"Could not save economic results: {e}")