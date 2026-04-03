# tests/test_reporting.py

import pandas as pd

from src.reporting import (
    build_table_profile,
    build_plan_comparison,
    build_validation_summary,
)


def sample_assumptions():
    return pd.DataFrame({
        "version_name": ["V1", "V1", "V2", "V2"],
        "venture_name": ["VentA", "VentB", "VentA", "VentB"],
        "asset_name": ["Asset1", "Asset2", "Asset1", "Asset2"],
        "production_bopd": [1000, 2000, 1100, 1800],
        "capex_mm": [10, 20, 12, 18],
        "oil_price": [70, 70, 75, 75],
        "opex_per_bbl": [15, 18, 16, 17],
    })


def sample_validation():
    return pd.DataFrame({
        "severity": ["High", "High", "Medium", "Low"]
    })


def test_build_table_profile():
    df = pd.DataFrame({"a": [1, 2], "b": ["x", None]})
    profile = build_table_profile(df)
    assert "column" in profile.columns
    assert len(profile) == 2


def test_build_plan_comparison_venture_level():
    df = sample_assumptions()
    comparison = build_plan_comparison(df, "V1", "V2", compare_level="Venture")
    assert "production_delta" in comparison.columns
    assert "capex_delta" in comparison.columns


def test_build_plan_comparison_asset_level():
    df = sample_assumptions()
    comparison = build_plan_comparison(df, "V1", "V2", compare_level="Asset")
    assert "production_delta" in comparison.columns


def test_build_validation_summary():
    df = sample_validation()
    summary = build_validation_summary(df)
    assert "issue_count" in summary.columns
    assert summary["issue_count"].sum() == 4