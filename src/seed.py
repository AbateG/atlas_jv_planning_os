from pathlib import Path

from src.db import initialize_database, insert_dataframe, get_connection
from src.synthetic_data import generate_all_data
from src.config import GENERATED_DIR


TABLE_LOAD_ORDER = [
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


def clear_existing_data():
    """
    Clears tables in reverse dependency order to avoid FK issues.
    Resets autoincrement sequences.
    """
    reverse_order = list(reversed(TABLE_LOAD_ORDER))
    with get_connection() as conn:
        for table in reverse_order:
            conn.execute(f"DELETE FROM {table}")
            # Reset autoincrement sequence for SQLite
            conn.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
        conn.commit()


def export_generated_csvs(data_dict: dict):
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    for table_name, df in data_dict.items():
        output_path = GENERATED_DIR / f"{table_name}.csv"
        df.to_csv(output_path, index=False)


def seed_database(reset: bool = True, export_csv: bool = True):
    if reset:
        print("Initializing database schema...")
        initialize_database()
        print("Clearing existing data...")
        clear_existing_data()

    print("Generating synthetic data...")
    data_dict = generate_all_data()

    print("Loading data into SQLite...")
    for table_name in TABLE_LOAD_ORDER:
        df = data_dict[table_name]
        insert_dataframe(df, table_name, if_exists="append")
        print(f"Loaded {len(df)} rows into '{table_name}'")

    if export_csv:
        print("Exporting generated CSV snapshots...")
        export_generated_csvs(data_dict)

    print("Database seeding complete.")


if __name__ == "__main__":
    seed_database(reset=True, export_csv=True)