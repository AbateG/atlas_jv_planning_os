# tests/test_economics.py

import pytest

from src.economics import (
    EconomicInputs,
    validate_economic_inputs,
    build_dcf_table,
    summarize_economics,
    build_tornado_summary,
)


@pytest.fixture
def base_inputs():
    return EconomicInputs(
        project_id=1,
        project_name="Synthetic Project Alpha",
        asset_id=1,
        asset_name="Synthetic Asset",
        venture_name="Synthetic Venture",
        plan_version_id=1,
        project_version_id=1,
        oil_price=75.0,
        production_uplift_bopd=2500.0,
        opex_per_bbl=18.0,
        capex=75_000_000.0,
        royalty_rate=0.10,
        tax_rate=0.30,
        discount_rate=0.10,
        project_life=10,
        annual_decline_rate=0.12,
    )


def test_validate_economic_inputs_valid(base_inputs):
    assert validate_economic_inputs(base_inputs) == []


def test_validate_economic_inputs_invalid():
    bad = EconomicInputs(
        project_id=1,
        project_name="Bad Case",
        oil_price=-1.0,
        production_uplift_bopd=-100.0,
        opex_per_bbl=-5.0,
        capex=-10.0,
        royalty_rate=1.5,
        tax_rate=-0.1,
        discount_rate=1.2,
        project_life=0,
        annual_decline_rate=1.5,
    )
    issues = validate_economic_inputs(bad)
    assert len(issues) >= 1


def test_build_dcf_table_contains_year_zero(base_inputs):
    df = build_dcf_table(base_inputs)
    assert len(df) == 11
    assert df.iloc[0]["year"] == 0
    assert df.iloc[0]["free_cash_flow"] == -75_000_000.0


def test_production_declines(base_inputs):
    df = build_dcf_table(base_inputs)
    y1 = df.loc[df["year"] == 1, "production_bbl"].iloc[0]
    y2 = df.loc[df["year"] == 2, "production_bbl"].iloc[0]
    assert y2 < y1


def test_summary_returns_numeric_outputs(base_inputs):
    df = build_dcf_table(base_inputs)
    summary = summarize_economics(df)
    assert isinstance(summary.npv, float)
    assert isinstance(summary.total_revenue, float)
    assert isinstance(summary.total_fcf, float)


def test_higher_price_improves_npv(base_inputs):
    base_npv = summarize_economics(build_dcf_table(base_inputs)).npv

    richer = EconomicInputs(**base_inputs.__dict__)
    richer.oil_price = 90.0

    richer_npv = summarize_economics(build_dcf_table(richer)).npv
    assert richer_npv > base_npv


def test_higher_capex_reduces_npv(base_inputs):
    base_npv = summarize_economics(build_dcf_table(base_inputs)).npv

    worse = EconomicInputs(**base_inputs.__dict__)
    worse.capex = 100_000_000.0

    worse_npv = summarize_economics(build_dcf_table(worse)).npv
    assert worse_npv < base_npv


def test_tornado_summary_returns_rows(base_inputs):
    tornado = build_tornado_summary(base_inputs)
    assert not tornado.empty
    assert "variable" in tornado.columns
    assert "swing" in tornado.columns