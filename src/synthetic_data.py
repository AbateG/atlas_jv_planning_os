"""
ATLAS JV PLANNING OS - SYNTHETIC DATA GENERATOR
===============================================
All data produced by this module is 100% fictitious.

No real company, asset, employee, or proprietary dataset is used.
All outputs are generated programmatically for educational and
portfolio demonstration purposes only.

Ranges are calibrated only to generalized, publicly known industry
concepts at a high level and are not tied to any confidential source.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from faker import Faker

SEED = 42
np.random.seed(SEED)
fake = Faker()
Faker.seed(SEED)


def generate_ventures() -> pd.DataFrame:
    ventures = [
        {
            "venture_name": "Orinoquia Energy S.A.",
            "basin": "Eastern Heavy Oil Basin",
            "fluid_type": "Heavy Oil",
        },
        {
            "venture_name": "Llanocrudo Holdings C.A.",
            "basin": "Central Plains Basin",
            "fluid_type": "Medium Oil",
        },
        {
            "venture_name": "Costanera Operaciones S.A.",
            "basin": "Western Mature Basin",
            "fluid_type": "Conventional Oil",
        },
        {
            "venture_name": "Deltaflux Energy C.A.",
            "basin": "Offshore Gas-Condensate Basin",
            "fluid_type": "Condensate",
        },
    ]
    return pd.DataFrame(ventures)


def generate_assets(ventures_df: pd.DataFrame) -> pd.DataFrame:
    asset_templates = {
        "Heavy Oil": [
            ("Junin Norte", "Producing Field"),
            ("Morichal Este", "Producing Field"),
        ],
        "Medium Oil": [
            ("Palmar Centro", "Producing Field"),
            ("Guarico Sur", "Producing Field"),
        ],
        "Conventional Oil": [
            ("Lago Oeste", "Mature Field"),
            ("Cabimas Norte", "Mature Field"),
        ],
        "Condensate": [
            ("Perla Azul", "Offshore Block"),
            ("Delta Norte", "Offshore Block"),
        ],
    }

    rows = []
    for venture_id, row in enumerate(ventures_df.to_dict("records"), start=1):
        fluid_type = row["fluid_type"]
        for asset_name, asset_type in asset_templates[fluid_type]:
            rows.append(
                {
                    "venture_id": venture_id,
                    "asset_name": asset_name,
                    "asset_type": asset_type,
                    "status": "Active",
                }
            )

    return pd.DataFrame(rows)


def generate_scenarios() -> pd.DataFrame:
    scenarios = [
        {"scenario_name": "Base", "description": "Base planning case"},
        {"scenario_name": "High", "description": "Upside case with stronger price and delivery"},
        {"scenario_name": "Low", "description": "Downside case with weaker price and delivery"},
    ]
    return pd.DataFrame(scenarios)


def generate_plan_versions() -> pd.DataFrame:
    versions = [
        {"version_name": "BP2026_Base_v1", "plan_year": 2026, "scenario_id": 1, "status": "Approved"},
        {"version_name": "BP2026_Base_v2", "plan_year": 2026, "scenario_id": 1, "status": "Draft"},
        {"version_name": "BP2026_High_v1", "plan_year": 2026, "scenario_id": 2, "status": "Draft"},
        {"version_name": "BP2026_Low_v1", "plan_year": 2026, "scenario_id": 3, "status": "Draft"},
    ]
    return pd.DataFrame(versions)


def _asset_profile(asset_name: str) -> dict:
    if asset_name in ["Junin Norte", "Morichal Este"]:
        return {
            "prod_range": (18000, 42000),
            "opex_range": (9, 18),
            "capex_range": (35, 120),
        }
    elif asset_name in ["Palmar Centro", "Guarico Sur"]:
        return {
            "prod_range": (9000, 22000),
            "opex_range": (6, 12),
            "capex_range": (20, 70),
        }
    elif asset_name in ["Lago Oeste", "Cabimas Norte"]:
        return {
            "prod_range": (4000, 12000),
            "opex_range": (10, 20),
            "capex_range": (10, 40),
        }
    else:
        return {
            "prod_range": (3000, 10000),
            "opex_range": (7, 15),
            "capex_range": (25, 80),
        }


def generate_assumptions(assets_df: pd.DataFrame, plan_versions_df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    # Stable base assumptions by asset
    asset_base_map = {}

    for asset_id, asset in enumerate(assets_df.to_dict("records"), start=1):
        profile = _asset_profile(asset["asset_name"])
        asset_base_map[asset_id] = {
            "base_prod": np.random.uniform(*profile["prod_range"]),
            "base_opex": np.random.uniform(*profile["opex_range"]),
            "base_capex": np.random.uniform(*profile["capex_range"]),
            "base_oil_price": np.random.uniform(58, 72),
            "base_gas_price": np.random.uniform(2.8, 4.0),
            "base_fx": np.random.uniform(30, 45),
            "base_inflation": np.random.uniform(0.02, 0.08),
            "base_royalty": np.random.uniform(0.12, 0.25),
            "base_tax": np.random.uniform(0.25, 0.38),
        }

    for version_id, version in enumerate(plan_versions_df.to_dict("records"), start=1):
        version_name = version["version_name"]
        scenario_id = version["scenario_id"]

        for asset_id, asset in enumerate(assets_df.to_dict("records"), start=1):
            base = asset_base_map[asset_id]

            oil_price = base["base_oil_price"]
            gas_price = base["base_gas_price"]
            production_bopd = base["base_prod"]
            opex_per_bbl = base["base_opex"]
            capex_mm = base["base_capex"]
            fx_rate = base["base_fx"]
            inflation_rate = base["base_inflation"]
            royalty_rate = base["base_royalty"]
            tax_rate = base["base_tax"]

            if version_name == "BP2026_Base_v2":
                # Moderate, believable deltas reflecting realistic planning refresh
                oil_price *= np.random.uniform(1.02, 1.05)  # +2% to +5%
                gas_price *= np.random.uniform(0.99, 1.03)  # -1% to +3%
                production_bopd *= np.random.uniform(1.01, 1.03)  # +1% to +3%
                opex_per_bbl *= np.random.uniform(1.01, 1.04)  # +1% to +4%
                capex_mm *= np.random.uniform(0.98, 1.02)  # -2% to +2%
                inflation_rate *= np.random.uniform(1.00, 1.02)  # Slight inflation adjustment

            elif scenario_id == 2:  # High
                oil_price *= np.random.uniform(1.10, 1.20)
                gas_price *= np.random.uniform(1.10, 1.20)
                production_bopd *= np.random.uniform(1.05, 1.15)
                opex_per_bbl *= np.random.uniform(0.95, 1.02)
                capex_mm *= np.random.uniform(1.00, 1.15)

            elif scenario_id == 3:  # Low
                oil_price *= np.random.uniform(0.75, 0.90)
                gas_price *= np.random.uniform(0.75, 0.90)
                production_bopd *= np.random.uniform(0.85, 0.97)
                opex_per_bbl *= np.random.uniform(1.00, 1.12)
                capex_mm *= np.random.uniform(0.85, 1.00)

            rows.append(
                {
                    "version_id": version_id,
                    "asset_id": asset_id,
                    "oil_price": round(oil_price, 2),
                    "gas_price": round(gas_price, 2),
                    "fx_rate": round(fx_rate, 2),
                    "inflation_rate": round(inflation_rate, 4),
                    "production_bopd": round(production_bopd, 2),
                    "opex_per_bbl": round(opex_per_bbl, 2),
                    "capex_mm": round(capex_mm, 2),
                    "royalty_rate": round(royalty_rate, 4),
                    "tax_rate": round(tax_rate, 4),
                }
            )

    return pd.DataFrame(rows)


def generate_projects(assets_df: pd.DataFrame, plan_versions_df: pd.DataFrame) -> pd.DataFrame:
    project_types = [
        "Well Workover",
        "Artificial Lift Upgrade",
        "Flowline Replacement",
        "Debottlenecking",
        "Well Reactivation",
        "Facility Upgrade",
    ]

    rows = []
    project_counter = 1

    for version_id, _ in enumerate(plan_versions_df.to_dict("records"), start=1):
        for asset_id, asset in enumerate(assets_df.to_dict("records"), start=1):
            for _ in range(2):
                start_month = np.random.randint(1, 10)
                duration_months = np.random.randint(2, 5)
                end_month = min(start_month + duration_months, 12)

                rows.append(
                    {
                        "asset_id": asset_id,
                        "version_id": version_id,
                        "project_name": f"{asset['asset_name']} Project {project_counter}",
                        "project_type": np.random.choice(project_types),
                        "start_date": f"2026-{start_month:02d}-01",
                        "end_date": f"2026-{end_month:02d}-28",
                        "capex_mm": round(np.random.uniform(1.5, 18.0), 2),
                        "expected_uplift_bopd": round(np.random.uniform(100, 2500), 2),
                        "status": np.random.choice(["Planned", "Under Review", "Approved"], p=[0.5, 0.2, 0.3]),
                    }
                )
                project_counter += 1

    return pd.DataFrame(rows)


def generate_economics_results(projects_df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for project_id, project in enumerate(projects_df.to_dict("records"), start=1):
        capex_usd = project["capex_mm"] * 1_000_000
        uplift = project["expected_uplift_bopd"]

        annual_revenue = uplift * 365 * np.random.uniform(55, 75)
        annual_opex = uplift * 365 * np.random.uniform(8, 18)
        annual_royalty = annual_revenue * np.random.uniform(0.10, 0.20)
        annual_tax = max(annual_revenue - annual_opex - annual_royalty, 0) * np.random.uniform(0.25, 0.35)
        annual_fcf = annual_revenue - annual_opex - annual_royalty - annual_tax

        npv = annual_fcf * np.random.uniform(2.0, 4.0) - capex_usd
        irr = np.random.uniform(0.12, 0.45)
        payback = np.random.uniform(1.2, 4.8)

        rows.append(
            {
                "project_id": project_id,
                "plan_version_id": project["version_id"],
                "npv": round(npv, 2),
                "irr": round(irr, 4),
                "payback_period_years": round(payback, 2),
                "total_revenue": round(annual_revenue * 5, 2),
                "total_opex": round(annual_opex * 5, 2),
                "total_royalty": round(annual_royalty * 5, 2),
                "total_tax": round(annual_tax * 5, 2),
                "total_fcf": round(annual_fcf * 5, 2),
                "oil_price": round(np.random.uniform(58, 75), 2),
                "production_uplift_bopd": round(uplift, 2),
                "opex_per_bbl": round(np.random.uniform(8, 18), 2),
                "capex": round(capex_usd, 2),
                "royalty_rate": round(np.random.uniform(0.10, 0.20), 4),
                "tax_rate": round(np.random.uniform(0.25, 0.35), 4),
                "discount_rate": 0.10,
                "project_life": 10,
                "annual_decline_rate": 0.12,
            }
        )

    return pd.DataFrame(rows)


def generate_monthly_actuals(assets_df: pd.DataFrame, year: int = 2026) -> pd.DataFrame:
    rows = []

    for asset_id, asset in enumerate(assets_df.to_dict("records"), start=1):
        profile = _asset_profile(asset["asset_name"])
        base_prod_bopd = np.random.uniform(*profile["prod_range"])
        opex_per_bbl = np.random.uniform(*profile["opex_range"])

        for month in range(1, 13):
            days = 30
            monthly_prod_bbl = base_prod_bopd * np.random.uniform(0.90, 1.10) * days
            realized_price = np.random.uniform(52, 78)
            revenue_mm = monthly_prod_bbl * realized_price / 1_000_000
            opex_mm = monthly_prod_bbl * opex_per_bbl * np.random.uniform(0.95, 1.08) / 1_000_000
            capex_mm = np.random.uniform(0.5, 8.0)
            earnings_mm = revenue_mm - opex_mm - capex_mm * np.random.uniform(0.15, 0.35)
            cashflow_mm = revenue_mm - opex_mm - capex_mm

            rows.append(
                {
                    "asset_id": asset_id,
                    "year_month": f"{year}-{month:02d}",
                    "production_bbl": round(monthly_prod_bbl, 2),
                    "opex_mm": round(opex_mm, 2),
                    "capex_mm": round(capex_mm, 2),
                    "earnings_mm": round(earnings_mm, 2),
                    "cashflow_mm": round(cashflow_mm, 2),
                }
            )

    return pd.DataFrame(rows)


def generate_kpis(monthly_actuals_df: pd.DataFrame, default_version_id: int = 1) -> pd.DataFrame:
    rows = []

    for row in monthly_actuals_df.to_dict("records"):
        production_bbl = row["production_bbl"]
        opex_mm = row["opex_mm"]
        capex_mm = row["capex_mm"]
        earnings_mm = row["earnings_mm"]
        cashflow_mm = row["cashflow_mm"]

        production_bopd = production_bbl / 30
        lifting_cost_per_bbl = (opex_mm * 1_000_000 / production_bbl) if production_bbl > 0 else 0
        capex_intensity = (capex_mm * 1_000_000 / production_bbl) if production_bbl > 0 else 0

        # derive an implied revenue estimate for ratio metrics
        implied_revenue_mm = max(earnings_mm + opex_mm + capex_mm * 0.2, 0.01)
        earnings_margin = earnings_mm / implied_revenue_mm
        cashflow_margin = cashflow_mm / implied_revenue_mm

        rows.append(
            {
                "asset_id": row["asset_id"],
                "version_id": default_version_id,
                "year_month": row["year_month"],
                "production_bopd": round(production_bopd, 2),
                "lifting_cost_per_bbl": round(lifting_cost_per_bbl, 2),
                "capex_intensity": round(capex_intensity, 2),
                "earnings_margin": round(earnings_margin, 4),
                "cashflow_margin": round(cashflow_margin, 4),
            }
        )

    return pd.DataFrame(rows)


def generate_validation_issues(assumptions_df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for assumption in assumptions_df.to_dict("records"):
        issues = []

        if assumption["production_bopd"] <= 0:
            issues.append(("Error", "Production", "Production must be greater than zero."))

        if assumption["opex_per_bbl"] < 0:
            issues.append(("Error", "Opex", "Opex per barrel cannot be negative."))

        if assumption["capex_mm"] < 0:
            issues.append(("Error", "Capex", "Capex cannot be negative."))

        if assumption["oil_price"] < 35 or assumption["oil_price"] > 100:
            issues.append(("Warning", "Oil Price", "Oil price is outside typical synthetic planning range."))

        if assumption["royalty_rate"] < 0 or assumption["royalty_rate"] > 1:
            issues.append(("Error", "Royalty", "Royalty rate must be between 0 and 1."))

        if assumption["tax_rate"] < 0 or assumption["tax_rate"] > 1:
            issues.append(("Error", "Tax", "Tax rate must be between 0 and 1."))

        if assumption["capex_mm"] > 80 and assumption["production_bopd"] < 5000:
            issues.append(
                ("Warning", "Capex-Production Consistency", "High capex with relatively low production should be reviewed.")
            )

        for severity, issue_type, issue_message in issues:
            rows.append(
                {
                    "version_id": assumption["version_id"],
                    "asset_id": assumption["asset_id"],
                    "severity": severity,
                    "issue_type": issue_type,
                    "issue_message": issue_message,
                }
            )

    return pd.DataFrame(rows)


def generate_all_data() -> dict[str, pd.DataFrame]:
    ventures_df = generate_ventures()
    assets_df = generate_assets(ventures_df)
    scenarios_df = generate_scenarios()
    plan_versions_df = generate_plan_versions()
    assumptions_df = generate_assumptions(assets_df, plan_versions_df)
    projects_df = generate_projects(assets_df, plan_versions_df)
    economics_results_df = generate_economics_results(projects_df)
    monthly_actuals_df = generate_monthly_actuals(assets_df)
    kpis_df = generate_kpis(monthly_actuals_df, default_version_id=1)
    validation_issues_df = generate_validation_issues(assumptions_df)

    return {
        "ventures": ventures_df,
        "assets": assets_df,
        "scenarios": scenarios_df,
        "plan_versions": plan_versions_df,
        "assumptions": assumptions_df,
        "projects": projects_df,
        "economics_results": economics_results_df,
        "monthly_actuals": monthly_actuals_df,
        "kpis": kpis_df,
        "validation_issues": validation_issues_df,
    }