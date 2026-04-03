from __future__ import annotations

import pandas as pd


def validate_assumption_row(row: pd.Series, asset_name: str | None = None) -> list[dict]:
    """
    Validate a single planning assumption row and return a list of issue dictionaries.
    """
    issues = []

    production_bopd = row.get("production_bopd")
    opex_per_bbl = row.get("opex_per_bbl")
    capex_mm = row.get("capex_mm")
    oil_price = row.get("oil_price")
    gas_price = row.get("gas_price")
    fx_rate = row.get("fx_rate")
    inflation_rate = row.get("inflation_rate")
    royalty_rate = row.get("royalty_rate")
    tax_rate = row.get("tax_rate")

    if production_bopd is None or production_bopd <= 0:
        issues.append(_issue("Error", "Production", "Production must be greater than zero."))

    if opex_per_bbl is None or opex_per_bbl < 0:
        issues.append(_issue("Error", "Opex", "Opex per barrel cannot be negative."))

    if capex_mm is None or capex_mm < 0:
        issues.append(_issue("Error", "Capex", "Capex cannot be negative."))

    if oil_price is None or oil_price <= 0:
        issues.append(_issue("Error", "Oil Price", "Oil price must be greater than zero."))
    elif oil_price < 35 or oil_price > 100:
        issues.append(_issue("Warning", "Oil Price", "Oil price is outside the typical synthetic planning range."))

    if gas_price is None or gas_price < 0:
        issues.append(_issue("Error", "Gas Price", "Gas price cannot be negative."))

    if fx_rate is None or fx_rate <= 0:
        issues.append(_issue("Error", "FX Rate", "FX rate must be greater than zero."))

    if inflation_rate is None or inflation_rate < 0 or inflation_rate > 1:
        issues.append(_issue("Warning", "Inflation", "Inflation rate should generally fall between 0 and 1."))

    if royalty_rate is None or royalty_rate < 0 or royalty_rate > 1:
        issues.append(_issue("Error", "Royalty", "Royalty rate must be between 0 and 1."))

    if tax_rate is None or tax_rate < 0 or tax_rate > 1:
        issues.append(_issue("Error", "Tax", "Tax rate must be between 0 and 1."))

    if capex_mm is not None and production_bopd is not None:
        if capex_mm > 80 and production_bopd < 5000:
            issues.append(
                _issue(
                    "Warning",
                    "Capex-Production Consistency",
                    "High capex with relatively low production should be reviewed."
                )
            )

    if opex_per_bbl is not None:
        if opex_per_bbl > 25:
            issues.append(
                _issue(
                    "Warning",
                    "Opex Reasonability",
                    "Opex per barrel is above the expected synthetic benchmark range."
                )
            )

    return issues


def validate_assumptions_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate a full assumptions dataframe.
    Expected columns include version_id and asset_id.
    Returns a dataframe of validation issues.
    """
    issue_rows = []

    for _, row in df.iterrows():
        row_issues = validate_assumption_row(row)
        for issue in row_issues:
            issue_rows.append(
                {
                    "version_id": row["version_id"],
                    "asset_id": row["asset_id"],
                    "severity": issue["severity"],
                    "issue_type": issue["issue_type"],
                    "issue_message": issue["issue_message"],
                }
            )

    return pd.DataFrame(issue_rows)


def _issue(severity: str, issue_type: str, issue_message: str) -> dict:
    return {
        "severity": severity,
        "issue_type": issue_type,
        "issue_message": issue_message,
    }