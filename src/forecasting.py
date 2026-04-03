# src/forecasting.py

import pandas as pd


REQUIRED_MID_YEAR_COLUMNS = [
    "venture_name",
    "asset_name",
    "year_month",
    "production_bbl",
    "opex_mm",
    "capex_mm",
    "earnings_mm",
    "cashflow_mm",
]


def prepare_mid_year_actuals(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    missing_cols = [col for col in REQUIRED_MID_YEAR_COLUMNS if col not in out.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns for mid-year update: {missing_cols}")

    out["year_month"] = pd.to_datetime(out["year_month"], errors="coerce")
    out = out.dropna(subset=["year_month"]).reset_index(drop=True)
    out["month_num"] = out["year_month"].dt.month
    out["year_label"] = out["year_month"].dt.strftime("%Y-%m")

    return out


def filter_mid_year_df(
    df: pd.DataFrame,
    selected_venture: str = "All",
    selected_asset: str = "All",
) -> pd.DataFrame:
    out = df.copy()

    if selected_venture != "All":
        out = out[out["venture_name"] == selected_venture]

    if selected_asset != "All":
        out = out[out["asset_name"] == selected_asset]

    return out.sort_values("year_month").reset_index(drop=True)


def split_ytd_h2(df: pd.DataFrame, cutoff_month: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    ytd_df = df[df["month_num"] <= cutoff_month].copy().reset_index(drop=True)
    h2_df = df[df["month_num"] > cutoff_month].copy().reset_index(drop=True)
    return ytd_df, h2_df


def apply_h2_adjustments(
    h2_df: pd.DataFrame,
    production_factor: float = 1.0,
    opex_factor: float = 1.0,
    capex_factor: float = 1.0,
    earnings_factor: float = 1.0,
    cashflow_factor: float = 1.0,
) -> pd.DataFrame:
    out = h2_df.copy()

    out["production_bbl"] = out["production_bbl"] * production_factor
    out["opex_mm"] = out["opex_mm"] * opex_factor
    out["capex_mm"] = out["capex_mm"] * capex_factor
    out["earnings_mm"] = out["earnings_mm"] * earnings_factor
    out["cashflow_mm"] = out["cashflow_mm"] * cashflow_factor

    return out.reset_index(drop=True)


def combine_ytd_and_reforecast(ytd_df: pd.DataFrame, reforecast_h2: pd.DataFrame) -> pd.DataFrame:
    out = pd.concat([ytd_df, reforecast_h2], ignore_index=True)
    return out.sort_values("year_month").reset_index(drop=True)


def build_period_summary(df_in: pd.DataFrame, label: str) -> dict:
    return {
        "period": label,
        "production_bbl": float(df_in["production_bbl"].sum()),
        "opex_mm": float(df_in["opex_mm"].sum()),
        "capex_mm": float(df_in["capex_mm"].sum()),
        "earnings_mm": float(df_in["earnings_mm"].sum()),
        "cashflow_mm": float(df_in["cashflow_mm"].sum()),
    }


def build_summary_table(
    ytd_df: pd.DataFrame,
    original_h2: pd.DataFrame,
    reforecast_h2: pd.DataFrame,
    original_fy: pd.DataFrame,
    reforecast_fy: pd.DataFrame,
    cutoff_month: int,
) -> pd.DataFrame:
    rows = [
        build_period_summary(ytd_df, f"YTD Actuals (Jan-{cutoff_month:02d})"),
        build_period_summary(original_h2, f"Original H2 ({cutoff_month+1:02d}-12)"),
        build_period_summary(reforecast_h2, f"Reforecast H2 ({cutoff_month+1:02d}-12)"),
        build_period_summary(original_fy, "Original FY"),
        build_period_summary(reforecast_fy, "Reforecast FY"),
    ]
    return pd.DataFrame(rows)


def build_reforecast_compare_table(
    original_fy: pd.DataFrame,
    reforecast_fy: pd.DataFrame,
) -> pd.DataFrame:
    metrics = {
        "production_bbl": (
            float(original_fy["production_bbl"].sum()),
            float(reforecast_fy["production_bbl"].sum()),
        ),
        "opex_mm": (
            float(original_fy["opex_mm"].sum()),
            float(reforecast_fy["opex_mm"].sum()),
        ),
        "capex_mm": (
            float(original_fy["capex_mm"].sum()),
            float(reforecast_fy["capex_mm"].sum()),
        ),
        "earnings_mm": (
            float(original_fy["earnings_mm"].sum()),
            float(reforecast_fy["earnings_mm"].sum()),
        ),
        "cashflow_mm": (
            float(original_fy["cashflow_mm"].sum()),
            float(reforecast_fy["cashflow_mm"].sum()),
        ),
    }

    rows = []
    for metric, (original_val, reforecast_val) in metrics.items():
        rows.append({
            "metric": metric,
            "original_fy": original_val,
            "reforecast_fy": reforecast_val,
            "delta": reforecast_val - original_val,
        })

    return pd.DataFrame(rows)


def build_monthly_compare_table(
    original_fy: pd.DataFrame,
    reforecast_fy: pd.DataFrame,
) -> pd.DataFrame:
    monthly_original = (
        original_fy.groupby("year_label", as_index=False)
        .agg(
            original_production_bbl=("production_bbl", "sum"),
            original_cashflow_mm=("cashflow_mm", "sum"),
        )
    )

    monthly_reforecast = (
        reforecast_fy.groupby("year_label", as_index=False)
        .agg(
            reforecast_production_bbl=("production_bbl", "sum"),
            reforecast_cashflow_mm=("cashflow_mm", "sum"),
        )
    )

    return (
        monthly_original.merge(monthly_reforecast, on="year_label", how="outer")
        .sort_values("year_label")
        .reset_index(drop=True)
    )


def make_display_df(df_in: pd.DataFrame) -> pd.DataFrame:
    out = df_in.copy()
    if "year_month" in out.columns:
        out["year_month"] = out["year_month"].dt.strftime("%Y-%m")
    return out.reset_index(drop=True)