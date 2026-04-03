from __future__ import annotations

import pandas as pd

from src.db import (
    get_assets_with_venture,
    get_assumptions_by_version,
    upsert_assumption,
    create_plan_version,
)
from src.validation import validate_assumptions_df


DEFAULT_ASSUMPTIONS = {
    "oil_price": 65.0,
    "gas_price": 3.5,
    "fx_rate": 36.0,
    "inflation_rate": 0.04,
    "production_bopd": 10000.0,
    "opex_per_bbl": 10.0,
    "capex_mm": 20.0,
    "royalty_rate": 0.1667,
    "tax_rate": 0.30,
}


def build_editable_assumptions_frame(version_id: int) -> pd.DataFrame:
    """
    Build an editable assumptions frame for a given version_id,
    combining asset metadata with any existing saved assumptions.
    """
    assets_df = get_assets_with_venture()
    assumptions_df = get_assumptions_by_version(version_id)

    editable_df = assets_df.merge(assumptions_df, on="asset_id", how="left", suffixes=("", "_assumption"))

    editable_df["version_id"] = version_id

    for field, default_value in DEFAULT_ASSUMPTIONS.items():
        if field not in editable_df.columns:
            editable_df[field] = default_value
        editable_df[field] = editable_df[field].fillna(default_value)

    keep_cols = [
        "version_id",
        "venture_id",
        "venture_name",
        "basin",
        "fluid_type",
        "asset_id",
        "asset_name",
        "asset_type",
        "status",
        "oil_price",
        "gas_price",
        "fx_rate",
        "inflation_rate",
        "production_bopd",
        "opex_per_bbl",
        "capex_mm",
        "royalty_rate",
        "tax_rate",
    ]

    return editable_df[keep_cols].sort_values(["venture_name", "asset_name"]).reset_index(drop=True)


def create_new_plan_version(version_name: str, plan_year: int, scenario_id: int) -> int:
    return create_plan_version(version_name=version_name, plan_year=plan_year, scenario_id=scenario_id, status="Draft")


def copy_assumptions_to_new_version(source_version_id: int, target_version_id: int) -> pd.DataFrame:
    """
    Copy assumptions from one version to another.
    Returns the copied assumptions dataframe.
    """
    source_df = get_assumptions_by_version(source_version_id).copy()
    if source_df.empty:
        return pd.DataFrame()

    source_df["version_id"] = target_version_id

    for _, row in source_df.iterrows():
        upsert_assumption(
            version_id=int(row["version_id"]),
            asset_id=int(row["asset_id"]),
            oil_price=float(row["oil_price"]),
            gas_price=float(row["gas_price"]),
            fx_rate=float(row["fx_rate"]),
            inflation_rate=float(row["inflation_rate"]),
            production_bopd=float(row["production_bopd"]),
            opex_per_bbl=float(row["opex_per_bbl"]),
            capex_mm=float(row["capex_mm"]),
            royalty_rate=float(row["royalty_rate"]),
            tax_rate=float(row["tax_rate"]),
        )

    return source_df


def save_assumptions_df(df: pd.DataFrame) -> None:
    """
    Save editable assumptions dataframe to DB.
    """
    required_cols = [
        "version_id",
        "asset_id",
        "oil_price",
        "gas_price",
        "fx_rate",
        "inflation_rate",
        "production_bopd",
        "opex_per_bbl",
        "capex_mm",
        "royalty_rate",
        "tax_rate",
    ]
    save_df = df[required_cols].copy()

    for _, row in save_df.iterrows():
        upsert_assumption(
            version_id=int(row["version_id"]),
            asset_id=int(row["asset_id"]),
            oil_price=float(row["oil_price"]),
            gas_price=float(row["gas_price"]),
            fx_rate=float(row["fx_rate"]),
            inflation_rate=float(row["inflation_rate"]),
            production_bopd=float(row["production_bopd"]),
            opex_per_bbl=float(row["opex_per_bbl"]),
            capex_mm=float(row["capex_mm"]),
            royalty_rate=float(row["royalty_rate"]),
            tax_rate=float(row["tax_rate"]),
        )


def consolidate_assumptions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Produce a consolidated planning summary.
    """
    consolidated = (
        df.groupby(["venture_name"], as_index=False)
        .agg(
            production_bopd=("production_bopd", "sum"),
            capex_mm=("capex_mm", "sum"),
            avg_opex_per_bbl=("opex_per_bbl", "mean"),
            avg_oil_price=("oil_price", "mean"),
            avg_gas_price=("gas_price", "mean"),
        )
        .sort_values("venture_name")
        .reset_index(drop=True)
    )
    return consolidated


def validate_and_prepare_issues(df: pd.DataFrame) -> pd.DataFrame:
    return validate_assumptions_df(df)