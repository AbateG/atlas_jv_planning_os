# tests/test_kpis.py

import pandas as pd

from src.kpi import (
    prepare_monthly_kpi_dataframe,
    summarize_monthly_kpis,
    summarize_asset_kpis,
)


def sample_kpi_df():
    return pd.DataFrame({
        "venture_name": ["V1", "V1", "V1", "V2"],
        "asset_name": ["A1", "A1", "A2", "A3"],
        "year_month": ["2025-01", "2025-02", "2025-01", "2025-01"],
        "production_bbl": [31000, 28000, 15000, 20000],
        "opex_mm": [1.0, 1.1, 0.7, 0.8],
        "capex_mm": [2.0, 1.5, 0.9, 1.2],
        "earnings_mm": [1.8, 1.6, 0.9, 1.1],
        "cashflow_mm": [1.5, 1.4, 0.8, 1.0],
    })


def test_prepare_monthly_kpi_dataframe_adds_columns():
    df = sample_kpi_df()
    out = prepare_monthly_kpi_dataframe(df)

    assert "production_bopd" in out.columns
    assert "opex_per_bbl" in out.columns
    assert "capex_intensity" in out.columns


def test_summarize_monthly_kpis_groups_correctly():
    df = sample_kpi_df()
    df = prepare_monthly_kpi_dataframe(df)
    summary = summarize_monthly_kpis(df)

    jan_row = summary[summary["year_month"] == pd.Timestamp("2025-01-01")]
    assert not jan_row.empty
    assert jan_row["production_bbl"].iloc[0] == 66000


def test_summarize_asset_kpis_groups_assets():
    df = sample_kpi_df()
    df = prepare_monthly_kpi_dataframe(df)
    asset_summary = summarize_asset_kpis(df)

    assert "opex_per_bbl" in asset_summary.columns
    assert "capex_intensity" in asset_summary.columns
    assert len(asset_summary) == 3