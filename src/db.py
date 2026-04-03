# src/db.py

from pathlib import Path
import sqlite3
from typing import Any

import pandas as pd

from src.config import DB_PATH

CRITICAL_TABLES = [
    "ventures",
    "assets",
    "scenarios",
    "plan_versions",
    "assumptions",
    "projects",
    "economics_results",
    "monthly_actuals",
    "kpis",
    "validation_issues",
]


def get_connection():
    """Create and return a SQLite connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def initialize_database(schema_path: Path = None) -> None:
    """Initialize the database schema from SQL file."""
    from src.config import BASE_DIR
    if schema_path is None:
        schema_path = BASE_DIR / "src" / "schema.sql"

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    with get_connection() as conn:
        conn.executescript(schema_sql)
        conn.commit()


def insert_dataframe(df: pd.DataFrame, table_name: str, if_exists: str = "append") -> None:
    """Insert a DataFrame into a table."""
    with get_connection() as conn:
        df.to_sql(table_name, conn, if_exists=if_exists, index=False)


def run_query(query: str, params: tuple = ()) -> pd.DataFrame:
    """Execute a query and return results as DataFrame."""
    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=params)


def execute(query: str, params: tuple = ()) -> None:
    """Execute a query without returning results."""
    with get_connection() as conn:
        conn.execute(query, params)
        conn.commit()


def get_plan_versions() -> pd.DataFrame:
    """Get all plan versions with scenario info."""
    query = """
        SELECT
            pv.version_id,
            pv.version_name,
            pv.plan_year,
            pv.scenario_id,
            s.scenario_name,
            pv.status,
            pv.created_at
        FROM plan_versions pv
        JOIN scenarios s ON pv.scenario_id = s.scenario_id
        ORDER BY pv.version_id
    """
    return run_query(query)


def replace_validation_issues_for_version(version_id: int, issues_df: pd.DataFrame) -> None:
    """Replace validation issues for a specific version."""
    with get_connection() as conn:
        conn.execute("DELETE FROM validation_issues WHERE version_id = ?", (version_id,))

        if not issues_df.empty:
            insert_query = """
                INSERT INTO validation_issues (
                    version_id, asset_id, severity, issue_type, issue_message
                )
                VALUES (?, ?, ?, ?, ?)
            """
            rows = [
                (
                    int(row["version_id"]),
                    int(row["asset_id"]),
                    row["severity"],
                    row["issue_type"],
                    row["issue_message"],
                )
                for _, row in issues_df.iterrows()
            ]
            conn.executemany(insert_query, rows)

        conn.commit()


def table_exists(table_name: str) -> bool:
    """Return True if the given table exists in the SQLite database."""
    conn = get_connection()
    try:
        query = """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table' AND name = ?
        """
        result = pd.read_sql_query(query, conn, params=(table_name,))
        return not result.empty
    finally:
        conn.close()


def get_existing_tables() -> list[str]:
    """Return a sorted list of all existing tables in the SQLite database."""
    conn = get_connection()
    try:
        query = """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name
        """
        result = pd.read_sql_query(query, conn)
        return result["name"].tolist() if not result.empty else []
    finally:
        conn.close()


def read_table(table_name: str) -> pd.DataFrame:
    """Read an entire table into a DataFrame."""
    conn = get_connection()
    try:
        return pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    finally:
        conn.close()


def get_table_row_counts() -> dict[str, int | None]:
    """
    Return row counts for all existing tables.

    If a table cannot be counted for any reason, return None for that table.
    """
    conn = get_connection()
    try:
        tables = get_existing_tables()
        counts: dict[str, int | None] = {}
        for table in tables:
            try:
                result = pd.read_sql_query(
                    f"SELECT COUNT(*) AS row_count FROM {table}",
                    conn,
                )
                counts[table] = int(result.loc[0, "row_count"])
            except Exception:
                counts[table] = None
        return counts
    finally:
        conn.close()


def evaluate_database_completeness() -> dict[str, Any]:
    """
    Assess whether the deployed SQLite database is ready for the core demo workflow.

    Completeness criteria:
    - all critical tables exist
    - all critical tables have at least one row
    """
    db_path = Path(DB_PATH)
    db_exists = db_path.exists()

    existing_tables = get_existing_tables() if db_exists else []
    existing_table_set = set(existing_tables)
    row_counts = get_table_row_counts() if db_exists else {}

    missing_tables = [table for table in CRITICAL_TABLES if table not in existing_table_set]
    empty_tables = [
        table
        for table in CRITICAL_TABLES
        if table in existing_table_set and row_counts.get(table, 0) == 0 and table != "validation_issues"
    ]

    is_complete = db_exists and not missing_tables and not empty_tables

    if is_complete:
        recommended_action = (
            "Database appears complete. No bootstrap action is currently required."
        )
    else:
        recommended_action = (
            "Critical database gaps detected. Recommended action: initialize schema and "
            "reseed synthetic data to restore a complete demo environment."
        )

    return {
        "db_path": str(db_path.resolve()) if db_exists else str(db_path),
        "db_exists": db_exists,
        "critical_tables": CRITICAL_TABLES,
        "critical_table_count": len(CRITICAL_TABLES),
        "existing_tables": existing_tables,
        "existing_table_count": len(existing_tables),
        "row_counts": row_counts,
        "missing_tables": missing_tables,
        "empty_tables": empty_tables,
        "is_complete": is_complete,
        "recommended_action": recommended_action,
    }


def get_database_status_summary() -> dict[str, Any]:
    """
    Return a UI-friendly summary of database health and completeness.
    """
    diagnostics = evaluate_database_completeness()

    status = "Healthy" if diagnostics["is_complete"] else "Attention Required"

    return {
        "status": status,
        "db_path": diagnostics["db_path"],
        "db_exists": diagnostics["db_exists"],
        "critical_tables": diagnostics["critical_tables"],
        "critical_table_count": diagnostics["critical_table_count"],
        "existing_tables": diagnostics["existing_tables"],
        "existing_table_count": diagnostics["existing_table_count"],
        "row_counts": diagnostics["row_counts"],
        "missing_tables": diagnostics["missing_tables"],
        "empty_tables": diagnostics["empty_tables"],
        "recommended_action": diagnostics["recommended_action"],
    }


def initialize_database_if_needed() -> dict[str, Any]:
    """
    Deployment-safe database bootstrap.

    Behavior:
    - if the database is complete, do nothing
    - if the database is missing, partially initialized, or incompletely seeded,
      rebuild deterministically to a known-good synthetic demo state

    Returns:
        post-bootstrap diagnostics dictionary
    """
    diagnostics = evaluate_database_completeness()
    if diagnostics["is_complete"]:
        return diagnostics

    # Import locally to avoid circular imports
    from src.seed import seed_database

    # For a portfolio MVP, deterministic rebuild is the safest deployment behavior.
    seed_database(reset=True, export_csv=False)

    return evaluate_database_completeness()


def create_plan_version(version_name: str, plan_year: int, scenario_id: int, status: str = "Draft") -> int:
    """Create a new plan version and return its ID."""
    query = """
        INSERT INTO plan_versions (version_name, plan_year, scenario_id, status)
        VALUES (?, ?, ?, ?)
    """
    with get_connection() as conn:
        cursor = conn.execute(query, (version_name, plan_year, scenario_id, status))
        conn.commit()
        return cursor.lastrowid


def get_assets_with_venture() -> pd.DataFrame:
    """Get all assets with their venture information."""
    query = """
        SELECT
            a.asset_id,
            a.asset_name,
            a.asset_type,
            a.status,
            v.venture_id,
            v.venture_name,
            v.basin,
            v.fluid_type
        FROM assets a
        JOIN ventures v ON a.venture_id = v.venture_id
        ORDER BY v.venture_name, a.asset_name
    """
    return run_query(query)


def get_assumptions_by_version(version_id: int) -> pd.DataFrame:
    """Get assumptions for a specific version."""
    query = """
        SELECT *
        FROM assumptions
        WHERE version_id = ?
        ORDER BY asset_id
    """
    return run_query(query, (version_id,))


def upsert_assumption(
    version_id: int,
    asset_id: int,
    oil_price: float,
    gas_price: float,
    fx_rate: float,
    inflation_rate: float,
    production_bopd: float,
    opex_per_bbl: float,
    capex_mm: float,
    royalty_rate: float,
    tax_rate: float,
) -> None:
    """Upsert an assumption record."""
    query = """
        INSERT INTO assumptions (
            version_id, asset_id, oil_price, gas_price, fx_rate, inflation_rate,
            production_bopd, opex_per_bbl, capex_mm, royalty_rate, tax_rate
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(version_id, asset_id) DO UPDATE SET
            oil_price = excluded.oil_price,
            gas_price = excluded.gas_price,
            fx_rate = excluded.fx_rate,
            inflation_rate = excluded.inflation_rate,
            production_bopd = excluded.production_bopd,
            opex_per_bbl = excluded.opex_per_bbl,
            capex_mm = excluded.capex_mm,
            royalty_rate = excluded.royalty_rate,
            tax_rate = excluded.tax_rate
    """
    execute(
        query,
        (
            version_id,
            asset_id,
            oil_price,
            gas_price,
            fx_rate,
            inflation_rate,
            production_bopd,
            opex_per_bbl,
            capex_mm,
            royalty_rate,
            tax_rate,
        ),
    )