# src/economics.py

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

import numpy as np
import numpy_financial as npf
import pandas as pd


@dataclass
class EconomicInputs:
    project_id: int
    project_name: str

    oil_price: float
    production_uplift_bopd: float
    opex_per_bbl: float
    capex: float
    royalty_rate: float
    tax_rate: float
    discount_rate: float
    project_life: int
    annual_decline_rate: float

    asset_id: Optional[int] = None
    asset_name: Optional[str] = None
    venture_name: Optional[str] = None
    plan_version_id: Optional[int] = None
    project_version_id: Optional[int] = None
    scenario_name: Optional[str] = None


@dataclass
class EconomicOutputs:
    npv: float
    irr: Optional[float]
    payback_period_years: Optional[float]
    total_revenue: float
    total_opex: float
    total_royalty: float
    total_tax: float
    total_fcf: float


def validate_economic_inputs(inputs: EconomicInputs) -> List[str]:
    issues = []

    if inputs.oil_price < 0:
        issues.append("Oil price must be non-negative.")
    if inputs.production_uplift_bopd < 0:
        issues.append("Production uplift must be non-negative.")
    if inputs.opex_per_bbl < 0:
        issues.append("Opex per bbl must be non-negative.")
    if inputs.capex < 0:
        issues.append("Capex must be non-negative.")
    if not (0 <= inputs.royalty_rate <= 1):
        issues.append("Royalty rate must be between 0 and 1.")
    if not (0 <= inputs.tax_rate <= 1):
        issues.append("Tax rate must be between 0 and 1.")
    if not (0 <= inputs.discount_rate <= 1):
        issues.append("Discount rate must be between 0 and 1.")
    if inputs.project_life <= 0:
        issues.append("Project life must be greater than 0.")
    if not (0 <= inputs.annual_decline_rate <= 1):
        issues.append("Annual decline rate must be between 0 and 1.")

    return issues


def build_dcf_table(inputs: EconomicInputs) -> pd.DataFrame:
    issues = validate_economic_inputs(inputs)
    if issues:
        raise ValueError("Invalid economic inputs: " + " | ".join(issues))

    rows = [{
        "year": 0,
        "production_bbl": 0.0,
        "oil_price": inputs.oil_price,
        "revenue": 0.0,
        "opex": 0.0,
        "royalty": 0.0,
        "pre_tax_cf": 0.0,
        "tax": 0.0,
        "free_cash_flow": -inputs.capex,
        "discount_factor": 1.0,
        "discounted_fcf": -inputs.capex,
    }]

    base_annual_bbl = inputs.production_uplift_bopd * 365.0

    for year in range(1, inputs.project_life + 1):
        annual_production = base_annual_bbl * ((1 - inputs.annual_decline_rate) ** (year - 1))
        revenue = annual_production * inputs.oil_price
        opex = annual_production * inputs.opex_per_bbl
        royalty = revenue * inputs.royalty_rate
        pre_tax_cf = revenue - opex - royalty
        tax = max(pre_tax_cf, 0.0) * inputs.tax_rate
        free_cash_flow = pre_tax_cf - tax
        discount_factor = 1 / ((1 + inputs.discount_rate) ** year)
        discounted_fcf = free_cash_flow * discount_factor

        rows.append({
            "year": year,
            "production_bbl": annual_production,
            "oil_price": inputs.oil_price,
            "revenue": revenue,
            "opex": opex,
            "royalty": royalty,
            "pre_tax_cf": pre_tax_cf,
            "tax": tax,
            "free_cash_flow": free_cash_flow,
            "discount_factor": discount_factor,
            "discounted_fcf": discounted_fcf,
        })

    df = pd.DataFrame(rows)
    df["cumulative_fcf"] = df["free_cash_flow"].cumsum()
    df["discounted_cumulative_fcf"] = df["discounted_fcf"].cumsum()
    return df


def calculate_irr(cash_flows: List[float]) -> Optional[float]:
    try:
        irr = npf.irr(cash_flows)
        if irr is None or np.isnan(irr) or np.isinf(irr):
            return None
        return float(irr)
    except Exception:
        return None


def calculate_payback_period(dcf_df: pd.DataFrame) -> Optional[float]:
    df = dcf_df.copy()

    if "cumulative_fcf" not in df.columns:
        df["cumulative_fcf"] = df["free_cash_flow"].cumsum()

    crossing = df[df["cumulative_fcf"] >= 0]
    if crossing.empty:
        return None

    first_cross_idx = crossing.index[0]
    first_cross_row = df.loc[first_cross_idx]

    if first_cross_row["year"] == 0:
        return 0.0

    prev_row = df.loc[first_cross_idx - 1]
    prev_cum = prev_row["cumulative_fcf"]
    curr_cum = first_cross_row["cumulative_fcf"]

    delta = curr_cum - prev_cum
    if delta == 0:
        return float(first_cross_row["year"])

    fraction = (0 - prev_cum) / delta
    fraction = max(0.0, min(1.0, fraction))

    return float(prev_row["year"] + fraction)


def summarize_economics(dcf_df: pd.DataFrame) -> EconomicOutputs:
    cash_flows = dcf_df["free_cash_flow"].tolist()

    return EconomicOutputs(
        npv=float(dcf_df["discounted_fcf"].sum()),
        irr=calculate_irr(cash_flows),
        payback_period_years=calculate_payback_period(dcf_df),
        total_revenue=float(dcf_df["revenue"].sum()),
        total_opex=float(dcf_df["opex"].sum()),
        total_royalty=float(dcf_df["royalty"].sum()),
        total_tax=float(dcf_df["tax"].sum()),
        total_fcf=float(dcf_df["free_cash_flow"].sum()),
    )


def build_standard_sensitivity_cases(base_inputs: EconomicInputs) -> pd.DataFrame:
    sensitivity_config = {
        "oil_price": [0.8, 0.9, 1.0, 1.1, 1.2],
        "production_uplift_bopd": [0.8, 0.9, 1.0, 1.1, 1.2],
        "opex_per_bbl": [0.8, 0.9, 1.0, 1.1, 1.2],
        "capex": [0.8, 0.9, 1.0, 1.1, 1.2],
        "discount_rate": [0.8, 0.9, 1.0, 1.1, 1.2],
    }

    rows = []
    base_dict = asdict(base_inputs)

    for variable, multipliers in sensitivity_config.items():
        base_value = base_dict[variable]

        for mult in multipliers:
            test_inputs = EconomicInputs(**base_dict)
            setattr(test_inputs, variable, base_value * mult)

            dcf_df = build_dcf_table(test_inputs)
            summary = summarize_economics(dcf_df)

            rows.append({
                "variable": variable,
                "base_value": base_value,
                "multiplier": mult,
                "test_value": getattr(test_inputs, variable),
                "npv": summary.npv,
                "irr": summary.irr,
                "payback_period_years": summary.payback_period_years,
            })

    return pd.DataFrame(rows)


def build_tornado_summary(base_inputs: EconomicInputs) -> pd.DataFrame:
    base_npv = summarize_economics(build_dcf_table(base_inputs)).npv

    variables = [
        "oil_price",
        "production_uplift_bopd",
        "opex_per_bbl",
        "capex",
        "discount_rate",
    ]

    base_dict = asdict(base_inputs)
    rows = []

    for variable in variables:
        base_value = base_dict[variable]

        low_inputs = EconomicInputs(**base_dict)
        high_inputs = EconomicInputs(**base_dict)

        setattr(low_inputs, variable, base_value * 0.8)
        setattr(high_inputs, variable, base_value * 1.2)

        low_npv = summarize_economics(build_dcf_table(low_inputs)).npv
        high_npv = summarize_economics(build_dcf_table(high_inputs)).npv

        rows.append({
            "variable": variable,
            "base_npv": base_npv,
            "low_npv": low_npv,
            "high_npv": high_npv,
            "downside_impact": low_npv - base_npv,
            "upside_impact": high_npv - base_npv,
            "swing": abs(high_npv - low_npv),
        })

    return pd.DataFrame(rows).sort_values("swing", ascending=False).reset_index(drop=True)


def run_case_comparison(base_inputs: EconomicInputs) -> pd.DataFrame:
    base_dict = asdict(base_inputs)

    cases = {
        "Downside": {
            "oil_price": base_inputs.oil_price * 0.9,
            "production_uplift_bopd": base_inputs.production_uplift_bopd * 0.9,
            "opex_per_bbl": base_inputs.opex_per_bbl * 1.1,
            "capex": base_inputs.capex * 1.1,
        },
        "Base": {},
        "Upside": {
            "oil_price": base_inputs.oil_price * 1.1,
            "production_uplift_bopd": base_inputs.production_uplift_bopd * 1.1,
            "opex_per_bbl": base_inputs.opex_per_bbl * 0.9,
            "capex": base_inputs.capex * 0.9,
        },
    }

    rows = []

    for case_name, overrides in cases.items():
        case_inputs = EconomicInputs(**base_dict)
        for key, val in overrides.items():
            setattr(case_inputs, key, val)

        summary = summarize_economics(build_dcf_table(case_inputs))
        rows.append({
            "case": case_name,
            "npv": summary.npv,
            "irr": summary.irr,
            "payback_period_years": summary.payback_period_years,
            "total_fcf": summary.total_fcf,
        })

    return pd.DataFrame(rows)


def get_projects_for_economics(conn: sqlite3.Connection) -> pd.DataFrame:
    query = """
    SELECT
        p.project_id,
        p.project_name,
        p.project_type,
        p.asset_id,
        p.version_id AS project_version_id,
        p.capex_mm,
        p.expected_uplift_bopd,
        p.status AS project_status,
        a.asset_name,
        a.asset_type,
        v.venture_name
    FROM projects p
    LEFT JOIN assets a
        ON p.asset_id = a.asset_id
    LEFT JOIN ventures v
        ON a.venture_id = v.venture_id
    ORDER BY p.project_name
    """
    return pd.read_sql_query(query, conn)


def get_plan_versions(conn: sqlite3.Connection) -> pd.DataFrame:
    query = """
    SELECT
        pv.version_id,
        pv.version_name,
        pv.plan_year,
        pv.scenario_id,
        s.scenario_name,
        pv.status
    FROM plan_versions pv
    LEFT JOIN scenarios s
        ON pv.scenario_id = s.scenario_id
    ORDER BY pv.version_id DESC
    """
    return pd.read_sql_query(query, conn)


def get_project_defaults(
    conn: sqlite3.Connection,
    project_id: int,
    plan_version_id: Optional[int] = None
) -> Dict:
    project_query = """
    SELECT
        p.project_id,
        p.project_name,
        p.asset_id,
        p.version_id AS project_version_id,
        p.capex_mm,
        p.expected_uplift_bopd,
        a.asset_name,
        v.venture_name
    FROM projects p
    LEFT JOIN assets a
        ON p.asset_id = a.asset_id
    LEFT JOIN ventures v
        ON a.venture_id = v.venture_id
    WHERE p.project_id = ?
    """
    project_df = pd.read_sql_query(project_query, conn, params=[project_id])

    if project_df.empty:
        raise ValueError(f"Project {project_id} not found.")

    row = project_df.iloc[0].to_dict()
    effective_version_id = plan_version_id if plan_version_id is not None else row["project_version_id"]

    assumptions_query = """
    SELECT
        version_id,
        asset_id,
        oil_price,
        gas_price,
        fx_rate,
        inflation_rate,
        production_bopd,
        opex_per_bbl,
        capex_mm,
        royalty_rate,
        tax_rate
    FROM assumptions
    WHERE version_id = ? AND asset_id = ?
    """
    assumptions_df = pd.read_sql_query(
        assumptions_query,
        conn,
        params=[effective_version_id, row["asset_id"]],
    )

    assumption_row = assumptions_df.iloc[0].to_dict() if not assumptions_df.empty else {}

    defaults = {
        "project_id": int(row["project_id"]),
        "project_name": row["project_name"],
        "asset_id": int(row["asset_id"]),
        "asset_name": row.get("asset_name"),
        "venture_name": row.get("venture_name"),
        "plan_version_id": int(effective_version_id) if effective_version_id is not None else None,
        "project_version_id": int(row["project_version_id"]) if row.get("project_version_id") is not None else None,
        "oil_price": float(assumption_row.get("oil_price", 75.0)),
        "production_uplift_bopd": float(row.get("expected_uplift_bopd", 2500.0)),
        "opex_per_bbl": float(assumption_row.get("opex_per_bbl", 18.0)),
        "capex": float(row.get("capex_mm", 75.0)) * 1_000_000,
        "royalty_rate": float(assumption_row.get("royalty_rate", 0.10)),
        "tax_rate": float(assumption_row.get("tax_rate", 0.30)),
        "discount_rate": 0.10,
        "project_life": 10,
        "annual_decline_rate": 0.12,
        "gas_price": float(assumption_row.get("gas_price", 0.0)) if assumption_row else 0.0,
        "fx_rate": float(assumption_row.get("fx_rate", 1.0)) if assumption_row else 1.0,
        "inflation_rate": float(assumption_row.get("inflation_rate", 0.02)) if assumption_row else 0.02,
        "base_production_bopd": float(assumption_row.get("production_bopd", 0.0)) if assumption_row else 0.0,
    }

    return defaults


def save_economic_result(
    conn: sqlite3.Connection,
    project_id: int,
    plan_version_id: Optional[int],
    summary: EconomicOutputs,
    input_assumptions: EconomicInputs,
) -> None:
    cursor = conn.cursor()

    if plan_version_id is not None:
        cursor.execute(
            """
            DELETE FROM economics_results
            WHERE project_id = ? AND plan_version_id = ?
            """,
            (project_id, plan_version_id),
        )

    cursor.execute(
        """
        INSERT INTO economics_results (
            project_id,
            plan_version_id,
            npv,
            irr,
            payback_period_years,
            total_revenue,
            total_opex,
            total_royalty,
            total_tax,
            total_fcf,
            oil_price,
            production_uplift_bopd,
            opex_per_bbl,
            capex,
            royalty_rate,
            tax_rate,
            discount_rate,
            project_life,
            annual_decline_rate
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            project_id,
            plan_version_id,
            summary.npv,
            summary.irr,
            summary.payback_period_years,
            summary.total_revenue,
            summary.total_opex,
            summary.total_royalty,
            summary.total_tax,
            summary.total_fcf,
            input_assumptions.oil_price,
            input_assumptions.production_uplift_bopd,
            input_assumptions.opex_per_bbl,
            input_assumptions.capex,
            input_assumptions.royalty_rate,
            input_assumptions.tax_rate,
            input_assumptions.discount_rate,
            input_assumptions.project_life,
            input_assumptions.annual_decline_rate,
        ),
    )

    conn.commit()