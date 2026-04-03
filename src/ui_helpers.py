import streamlit as st
import pandas as pd

from src.db import read_table, run_query


@st.cache_data
def load_table(table_name: str) -> pd.DataFrame:
    return read_table(table_name)


@st.cache_data
def load_joined_assumptions() -> pd.DataFrame:
    query = """
    SELECT
        a.assumption_id,
        pv.version_name,
        pv.plan_year,
        s.scenario_name,
        v.venture_name,
        ast.asset_name,
        ast.asset_type,
        a.oil_price,
        a.gas_price,
        a.fx_rate,
        a.inflation_rate,
        a.production_bopd,
        a.opex_per_bbl,
        a.capex_mm,
        a.royalty_rate,
        a.tax_rate,
        a.created_at
    FROM assumptions a
    JOIN plan_versions pv ON a.version_id = pv.version_id
    JOIN scenarios s ON pv.scenario_id = s.scenario_id
    JOIN assets ast ON a.asset_id = ast.asset_id
    JOIN ventures v ON ast.venture_id = v.venture_id
    ORDER BY pv.version_id, ast.asset_id
    """
    return run_query(query)


@st.cache_data
def load_joined_monthly_actuals() -> pd.DataFrame:
    query = """
    SELECT
        ma.actual_id,
        ma.year_month,
        v.venture_name,
        ast.asset_name,
        ast.asset_type,
        ma.production_bbl,
        ma.opex_mm,
        ma.capex_mm,
        ma.earnings_mm,
        ma.cashflow_mm
    FROM monthly_actuals ma
    JOIN assets ast ON ma.asset_id = ast.asset_id
    JOIN ventures v ON ast.venture_id = v.venture_id
    ORDER BY ma.year_month, ast.asset_id
    """
    return run_query(query)


@st.cache_data
def load_joined_projects_economics() -> pd.DataFrame:
    query = """
    SELECT
        p.project_id,
        p.project_name,
        p.project_type,
        p.start_date,
        p.end_date,
        p.capex_mm,
        p.expected_uplift_bopd,
        p.status,
        pv.version_name,
        v.venture_name,
        ast.asset_name,
        er.discount_rate,
        er.npv_mm,
        er.irr,
        er.payback_years,
        er.scenario_name
    FROM projects p
    JOIN assets ast ON p.asset_id = ast.asset_id
    JOIN ventures v ON ast.venture_id = v.venture_id
    JOIN plan_versions pv ON p.version_id = pv.version_id
    LEFT JOIN economics_results er ON p.project_id = er.project_id
    ORDER BY p.project_id
    """
    return run_query(query)


@st.cache_data
def load_joined_kpis() -> pd.DataFrame:
    query = """
    SELECT
        k.kpi_id,
        k.year_month,
        pv.version_name,
        v.venture_name,
        ast.asset_name,
        k.production_bopd,
        k.lifting_cost_per_bbl,
        k.capex_intensity,
        k.earnings_margin,
        k.cashflow_margin
    FROM kpis k
    JOIN assets ast ON k.asset_id = ast.asset_id
    JOIN ventures v ON ast.venture_id = v.venture_id
    JOIN plan_versions pv ON k.version_id = pv.version_id
    ORDER BY k.year_month, ast.asset_id
    """
    return run_query(query)


@st.cache_data
def load_joined_validation_issues() -> pd.DataFrame:
    query = """
    SELECT
        vi.issue_id,
        vi.version_id,
        pv.version_name,
        vi.asset_id,
        v.venture_name,
        ast.asset_name,
        vi.severity,
        vi.issue_type,
        vi.issue_message,
        vi.created_at
    FROM validation_issues vi
    JOIN plan_versions pv ON vi.version_id = pv.version_id
    JOIN assets ast ON vi.asset_id = ast.asset_id
    JOIN ventures v ON ast.venture_id = v.venture_id
    ORDER BY vi.version_id, vi.asset_id
    """
    return run_query(query)


def render_global_disclaimer():
    st.caption(
        "Disclaimer: All entities, names, figures, and scenarios are fictitious and "
        "synthetically generated for educational and portfolio purposes only."
    )


def dataframe_download_button(df: pd.DataFrame, filename: str, label: str = "Download CSV"):
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=label,
        data=csv,
        file_name=filename,
        mime="text/csv"
    )


def fmt_currency(x):
    if x is None:
        return "N/A"
    return f"${x:,.0f}"


def fmt_pct(x):
    if x is None:
        return "N/A"
    return f"{x:.1%}"


def fmt_years(x):
    if x is None:
        return "N/A"
    return f"{x:.1f} years"