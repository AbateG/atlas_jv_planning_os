# src/kpi.py

import pandas as pd


def prepare_monthly_kpi_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["year_month"] = pd.to_datetime(out["year_month"])
    out["days_in_month"] = out["year_month"].dt.days_in_month
    out["production_bopd"] = out["production_bbl"] / out["days_in_month"]
    out["opex_per_bbl"] = out["opex_mm"] * 1_000_000 / out["production_bbl"].replace(0, pd.NA)
    out["capex_intensity"] = out["capex_mm"] * 1_000_000 / out["production_bbl"].replace(0, pd.NA)
    return out


def summarize_monthly_kpis(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("year_month", as_index=False)
        .agg(
            production_bbl=("production_bbl", "sum"),
            opex_mm=("opex_mm", "sum"),
            capex_mm=("capex_mm", "sum"),
            earnings_mm=("earnings_mm", "sum"),
            cashflow_mm=("cashflow_mm", "sum"),
        )
        .sort_values("year_month")
    )

    summary["days_in_month"] = summary["year_month"].dt.days_in_month
    summary["production_bopd"] = summary["production_bbl"] / summary["days_in_month"]
    summary["opex_per_bbl"] = summary["opex_mm"] * 1_000_000 / summary["production_bbl"].replace(0, pd.NA)
    summary["capex_intensity"] = summary["capex_mm"] * 1_000_000 / summary["production_bbl"].replace(0, pd.NA)
    return summary


def summarize_asset_kpis(df: pd.DataFrame) -> pd.DataFrame:
    asset_summary = (
        df.groupby(["venture_name", "asset_name"], as_index=False)
        .agg(
            production_bbl=("production_bbl", "sum"),
            opex_mm=("opex_mm", "sum"),
            capex_mm=("capex_mm", "sum"),
            earnings_mm=("earnings_mm", "sum"),
            cashflow_mm=("cashflow_mm", "sum"),
        )
    )

    asset_summary["opex_per_bbl"] = asset_summary["opex_mm"] * 1_000_000 / asset_summary["production_bbl"].replace(0, pd.NA)
    asset_summary["capex_intensity"] = asset_summary["capex_mm"] * 1_000_000 / asset_summary["production_bbl"].replace(0, pd.NA)
    return asset_summary