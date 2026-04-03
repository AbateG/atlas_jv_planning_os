import sqlite3
from pathlib import Path
import pandas as pd

from src.config import DB_PATH, BASE_DIR


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def initialize_database(schema_path: Path = None) -> None:
    if schema_path is None:
        schema_path = BASE_DIR / "src" / "schema.sql"

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    with get_connection() as conn:
        conn.executescript(schema_sql)
        conn.commit()


def insert_dataframe(df: pd.DataFrame, table_name: str, if_exists: str = "append") -> None:
    with get_connection() as conn:
        df.to_sql(table_name, conn, if_exists=if_exists, index=False)


def read_table(table_name: str) -> pd.DataFrame:
    query = f"SELECT * FROM {table_name}"
    with get_connection() as conn:
        return pd.read_sql_query(query, conn)


def run_query(query: str, params: tuple = ()) -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=params)


def execute(query: str, params: tuple = ()) -> None:
    with get_connection() as conn:
        conn.execute(query, params)
        conn.commit()


def execute_many(query: str, params_list: list[tuple]) -> None:
    with get_connection() as conn:
        conn.executemany(query, params_list)
        conn.commit()


def table_exists(table_name: str) -> bool:
    query = """
    SELECT name
    FROM sqlite_master
    WHERE type='table' AND name=?
    """
    with get_connection() as conn:
        cursor = conn.execute(query, (table_name,))
        return cursor.fetchone() is not None


def clear_table(table_name: str) -> None:
    with get_connection() as conn:
        conn.execute(f"DELETE FROM {table_name}")
        conn.commit()


def get_row_count(table_name: str) -> int:
    query = f"SELECT COUNT(*) AS count FROM {table_name}"
    with get_connection() as conn:
        cursor = conn.execute(query)
        return cursor.fetchone()[0]


def create_plan_version(version_name: str, plan_year: int, scenario_id: int, status: str = "Draft") -> int:
    query = """
    INSERT INTO plan_versions (version_name, plan_year, scenario_id, status)
    VALUES (?, ?, ?, ?)
    """
    with get_connection() as conn:
        cursor = conn.execute(query, (version_name, plan_year, scenario_id, status))
        conn.commit()
        return cursor.lastrowid


def get_plan_versions() -> pd.DataFrame:
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


def get_assets_with_venture() -> pd.DataFrame:
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


def replace_validation_issues_for_version(version_id: int, issues_df: pd.DataFrame) -> None:
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


def get_asset_id_for_project(project_id: int) -> int:
    query = "SELECT asset_id FROM projects WHERE project_id = ?"
    with get_connection() as conn:
        cursor = conn.execute(query, (project_id,))
        row = cursor.fetchone()
        return row[0] if row else None


def get_economic_assumptions_from_plan_version(
    project_id: int,
    plan_version_id: int,
) -> dict:
    """
    Pull economic drivers from assumptions table for the project's asset in the plan version.
    Falls back to defaults where missing.
    """
    asset_id = get_asset_id_for_project(project_id)
    if asset_id is None:
        return get_project_defaults(project_id, plan_version_id)

    query = """
    SELECT oil_price, gas_price, fx_rate, inflation_rate, production_bopd, opex_per_bbl, capex_mm, royalty_rate, tax_rate
    FROM assumptions
    WHERE version_id = ? AND asset_id = ?
    """
    with get_connection() as conn:
        df = pd.read_sql_query(query, conn, params=[plan_version_id, asset_id])

    if df.empty:
        return get_project_defaults(project_id, plan_version_id)

    row = df.iloc[0]

    # Defaults for fields not in assumptions
    defaults = {
        "discount_rate": 0.10,
        "project_life": 20,
        "annual_decline_rate": 0.05,
    }

    # Map from assumptions
    mapping = {
        "oil_price": row["oil_price"],
        "production_uplift_bopd": row["production_bopd"],
        "opex_per_bbl": row["opex_per_bbl"],
        "capex": row["capex_mm"] * 1e6,  # Convert MM to actual
        "royalty_rate": row["royalty_rate"],
        "tax_rate": row["tax_rate"],
    }

    defaults.update(mapping)

    return defaults


def get_project_defaults(project_id: int, plan_version_id: int) -> dict:
    """
    Placeholder for project-specific defaults.
    """
    return {
        "oil_price": 80.0,
        "production_uplift_bopd": 1000.0,
        "opex_per_bbl": 15.0,
        "capex": 50e6,
        "royalty_rate": 0.10,
        "tax_rate": 0.30,
        "discount_rate": 0.10,
        "project_life": 20,
        "annual_decline_rate": 0.05,
    }