# tests/test_forecasting.py

import pandas as pd

from src.forecasting import (
    prepare_mid_year_actuals,
    filter_mid_year_df,
    split_ytd_h2,
    apply_h2_adjustments,
    combine_ytd_and_reforecast,
    build_summary_table,
    build_reforecast_compare_table,
    build_monthly_compare_table,
)


def sample_actuals():
    return pd.DataFrame({
        "venture_name": ["V1", "V1", "V1", "V1"],
        "asset_name": ["A1", "A1", "A1", "A1"],
        "year_month": ["2025-01", "2025-06", "2025-07", "2025-12"],
        "production_bbl": [1000, 1200, 1300, 1400],
        "opex_mm": [1.0, 1.1, 1.2, 1.3],
        "capex_mm": [2.0, 2.1, 2.2, 2.3],
        "earnings_mm": [1.5, 1.6, 1.7, 1.8],
        "cashflow_mm": [1.2, 1.3, 1.4, 1.5],
    })


def test_prepare_mid_year_actuals_adds_fields():
    df = prepare_mid_year_actuals(sample_actuals())
    assert "month_num" in df.columns
    assert "year_label" in df.columns


def test_filter_mid_year_df_filters_correctly():
    df = prepare_mid_year_actuals(sample_actuals())
    out = filter_mid_year_df(df, selected_venture="V1", selected_asset="A1")
    assert len(out) == 4


def test_split_ytd_h2():
    df = prepare_mid_year_actuals(sample_actuals())
    ytd_df, h2_df = split_ytd_h2(df, cutoff_month=6)
    assert len(ytd_df) == 2
    assert len(h2_df) == 2


def test_apply_h2_adjustments_changes_values():
    df = prepare_mid_year_actuals(sample_actuals())
    _, h2_df = split_ytd_h2(df, cutoff_month=6)
    adjusted = apply_h2_adjustments(h2_df, production_factor=1.1, opex_factor=0.9)

    assert adjusted["production_bbl"].iloc[0] == h2_df["production_bbl"].iloc[0] * 1.1
    assert adjusted["opex_mm"].iloc[0] == h2_df["opex_mm"].iloc[0] * 0.9


def test_combine_ytd_and_reforecast():
    df = prepare_mid_year_actuals(sample_actuals())
    ytd_df, h2_df = split_ytd_h2(df, cutoff_month=6)
    adjusted = apply_h2_adjustments(h2_df, production_factor=1.1)
    combined = combine_ytd_and_reforecast(ytd_df, adjusted)
    assert len(combined) == 4


def test_build_reforecast_compare_table_has_delta():
    df = prepare_mid_year_actuals(sample_actuals())
    ytd_df, h2_df = split_ytd_h2(df, cutoff_month=6)
    adjusted = apply_h2_adjustments(h2_df, production_factor=1.1)
    original_fy = df.copy()
    reforecast_fy = combine_ytd_and_reforecast(ytd_df, adjusted)

    compare = build_reforecast_compare_table(original_fy, reforecast_fy)
    assert "delta" in compare.columns
    assert len(compare) == 5


def test_build_monthly_compare_table():
    df = prepare_mid_year_actuals(sample_actuals())
    ytd_df, h2_df = split_ytd_h2(df, cutoff_month=6)
    adjusted = apply_h2_adjustments(h2_df, production_factor=1.1)
    reforecast_fy = combine_ytd_and_reforecast(ytd_df, adjusted)

    monthly = build_monthly_compare_table(df, reforecast_fy)
    assert "year_label" in monthly.columns
    assert "original_cashflow_mm" in monthly.columns
    assert "reforecast_cashflow_mm" in monthly.columns