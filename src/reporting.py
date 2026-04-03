# src/reporting.py

import pandas as pd


def build_table_profile(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["column", "dtype", "non_null_count", "null_count", "unique_values"])

    return pd.DataFrame({
        "column": df.columns,
        "dtype": [str(dtype) for dtype in df.dtypes],
        "non_null_count": [df[col].notna().sum() for col in df.columns],
        "null_count": [df[col].isna().sum() for col in df.columns],
        "unique_values": [df[col].nunique(dropna=True) for col in df.columns],
    })


def build_plan_comparison(
    assumptions_df: pd.DataFrame,
    version_a: str,
    version_b: str,
    compare_level: str = "Venture",
) -> pd.DataFrame:
    if assumptions_df.empty:
        return pd.DataFrame()

    key_col = "venture_name" if compare_level == "Venture" else "asset_name"

    df_a = assumptions_df[assumptions_df["version_name"] == version_a].copy()
    df_b = assumptions_df[assumptions_df["version_name"] == version_b].copy()

    grouped_a = (
        df_a.groupby(key_col, as_index=False)
        .agg(
            production_bopd=("production_bopd", "sum"),
            capex_mm=("capex_mm", "sum"),
            oil_price=("oil_price", "mean"),
            opex_per_bbl=("opex_per_bbl", "mean"),
        )
        .rename(columns={
            "production_bopd": "production_a",
            "capex_mm": "capex_a",
            "oil_price": "oil_price_a",
            "opex_per_bbl": "opex_per_bbl_a",
        })
    )

    grouped_b = (
        df_b.groupby(key_col, as_index=False)
        .agg(
            production_bopd=("production_bopd", "sum"),
            capex_mm=("capex_mm", "sum"),
            oil_price=("oil_price", "mean"),
            opex_per_bbl=("opex_per_bbl", "mean"),
        )
        .rename(columns={
            "production_bopd": "production_b",
            "capex_mm": "capex_b",
            "oil_price": "oil_price_b",
            "opex_per_bbl": "opex_per_bbl_b",
        })
    )

    comparison = grouped_a.merge(grouped_b, on=key_col, how="outer")
    comparison["production_delta"] = comparison["production_b"] - comparison["production_a"]
    comparison["capex_delta"] = comparison["capex_b"] - comparison["capex_a"]
    comparison["oil_price_delta"] = comparison["oil_price_b"] - comparison["oil_price_a"]
    comparison["opex_per_bbl_delta"] = comparison["opex_per_bbl_b"] - comparison["opex_per_bbl_a"]

    return comparison.reset_index(drop=True)


def build_validation_summary(validation_df: pd.DataFrame) -> pd.DataFrame:
    if validation_df.empty or "severity" not in validation_df.columns:
        return pd.DataFrame(columns=["severity", "issue_count"])

    return (
        validation_df.groupby("severity", as_index=False)
        .size()
        .rename(columns={"size": "issue_count"})
        .reset_index(drop=True)
    )