PRAGMA foreign_keys = ON;

-- =========================================================
-- TABLE: ventures
-- =========================================================
CREATE TABLE IF NOT EXISTS ventures (
    venture_id INTEGER PRIMARY KEY AUTOINCREMENT,
    venture_name TEXT NOT NULL UNIQUE,
    basin TEXT NOT NULL,
    fluid_type TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================
-- TABLE: assets
-- =========================================================
CREATE TABLE IF NOT EXISTS assets (
    asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
    venture_id INTEGER NOT NULL,
    asset_name TEXT NOT NULL,
    asset_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Active',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (venture_id) REFERENCES ventures(venture_id)
);

-- =========================================================
-- TABLE: scenarios
-- =========================================================
CREATE TABLE IF NOT EXISTS scenarios (
    scenario_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_name TEXT NOT NULL UNIQUE,
    description TEXT
);

-- =========================================================
-- TABLE: plan_versions
-- =========================================================
CREATE TABLE IF NOT EXISTS plan_versions (
    version_id INTEGER PRIMARY KEY AUTOINCREMENT,
    version_name TEXT NOT NULL UNIQUE,
    plan_year INTEGER NOT NULL,
    scenario_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'Draft',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scenario_id) REFERENCES scenarios(scenario_id)
);

-- =========================================================
-- TABLE: assumptions
-- One row per asset per plan version
-- =========================================================
CREATE TABLE IF NOT EXISTS assumptions (
    assumption_id INTEGER PRIMARY KEY AUTOINCREMENT,
    version_id INTEGER NOT NULL,
    asset_id INTEGER NOT NULL,
    oil_price REAL NOT NULL,
    gas_price REAL NOT NULL,
    fx_rate REAL NOT NULL,
    inflation_rate REAL NOT NULL,
    production_bopd REAL NOT NULL,
    opex_per_bbl REAL NOT NULL,
    capex_mm REAL NOT NULL,
    royalty_rate REAL NOT NULL,
    tax_rate REAL NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (version_id) REFERENCES plan_versions(version_id),
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id),
    UNIQUE(version_id, asset_id)
);

-- =========================================================
-- TABLE: projects
-- =========================================================
CREATE TABLE IF NOT EXISTS projects (
    project_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    version_id INTEGER NOT NULL,
    project_name TEXT NOT NULL,
    project_type TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    capex_mm REAL NOT NULL,
    expected_uplift_bopd REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'Planned',
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id),
    FOREIGN KEY (version_id) REFERENCES plan_versions(version_id)
);

-- =========================================================
-- TABLE: economics_results
-- One row per project per scenario calculation
-- =========================================================
CREATE TABLE IF NOT EXISTS economics_results (
    economics_result_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    plan_version_id INTEGER,
    npv REAL,
    irr REAL,
    payback_period_years REAL,
    total_revenue REAL,
    total_opex REAL,
    total_royalty REAL,
    total_tax REAL,
    total_fcf REAL,
    oil_price REAL,
    production_uplift_bopd REAL,
    opex_per_bbl REAL,
    capex REAL,
    royalty_rate REAL,
    tax_rate REAL,
    discount_rate REAL,
    project_life INTEGER,
    annual_decline_rate REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (plan_version_id) REFERENCES plan_versions(version_id)
);

-- =========================================================
-- TABLE: monthly_actuals
-- One row per asset per month
-- =========================================================
CREATE TABLE IF NOT EXISTS monthly_actuals (
    actual_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    year_month TEXT NOT NULL,
    production_bbl REAL NOT NULL,
    opex_mm REAL NOT NULL,
    capex_mm REAL NOT NULL,
    earnings_mm REAL NOT NULL,
    cashflow_mm REAL NOT NULL,
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id),
    UNIQUE(asset_id, year_month)
);

-- =========================================================
-- TABLE: kpis
-- Derived KPI storage
-- =========================================================
CREATE TABLE IF NOT EXISTS kpis (
    kpi_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    version_id INTEGER NOT NULL,
    year_month TEXT NOT NULL,
    production_bopd REAL NOT NULL,
    lifting_cost_per_bbl REAL NOT NULL,
    capex_intensity REAL NOT NULL,
    earnings_margin REAL NOT NULL,
    cashflow_margin REAL NOT NULL,
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id),
    FOREIGN KEY (version_id) REFERENCES plan_versions(version_id),
    UNIQUE(asset_id, version_id, year_month)
);

-- =========================================================
-- TABLE: validation_issues
-- =========================================================
CREATE TABLE IF NOT EXISTS validation_issues (
    issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
    version_id INTEGER NOT NULL,
    asset_id INTEGER NOT NULL,
    severity TEXT NOT NULL,
    issue_type TEXT NOT NULL,
    issue_message TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (version_id) REFERENCES plan_versions(version_id),
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
);