# app.py

import streamlit as st

from src.constants import APP_NAME, APP_TAGLINE
from src.db import initialize_database_if_needed, get_database_status_summary


st.set_page_config(
    page_title=APP_NAME,
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Deployment-safe bootstrap
# -----------------------------
bootstrap_error = None
try:
    initialize_database_if_needed()
    system_status = get_database_status_summary()
except Exception as e:
    bootstrap_error = e
    system_status = None

# -----------------------------
# Header
# -----------------------------
st.title("🧭 Atlas JV Planning OS")
st.subheader(APP_TAGLINE)

st.info(
    """
Atlas JV Planning OS is an educational, portfolio-grade application that simulates selected
upstream joint venture planning, economics, and performance reporting workflows using entirely
fictitious entities and 100% synthetic data.
"""
)

# -----------------------------
# Startup health banner
# -----------------------------
if bootstrap_error is not None:
    st.error(
        f"Database bootstrap or diagnostics failed during startup: {bootstrap_error}"
    )
    st.warning(
        """
The application UI may still load, but one or more workflow pages could be unavailable until
the synthetic database is correctly initialized.
"""
    )
elif system_status is not None:
    if system_status["status"] == "Healthy":
        st.success(
            "System check passed: the synthetic planning database appears ready for interactive use."
        )
    else:
        st.warning(
            """
System check detected one or more database completeness issues. Some pages may show limited
data or empty states until the environment is fully seeded.
"""
        )

# -----------------------------
# Top metrics
# -----------------------------
st.markdown("### Project Highlights")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Core Workflow Modules", "5")
col2.metric("Data Safety", "100% Synthetic")
col3.metric("Tech Stack", "Python + Streamlit")
col4.metric("Database", "SQLite")

# Optional second row of operational metrics
if system_status is not None:
    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Critical Tables", system_status["critical_table_count"])
    col6.metric("Tracked Tables", system_status["existing_table_count"])
    col7.metric("Missing Critical Tables", len(system_status["missing_tables"]))
    col8.metric("System Status", system_status["status"])

# -----------------------------
# Overview
# -----------------------------
st.markdown("## Quick Overview")
st.markdown(
    """
Atlas JV Planning OS demonstrates a structured planning workflow that connects assumption capture,
scenario planning, economic evaluation, KPI reporting, and mid-year reforecasting.

The application is intentionally built as a modular analytical system:
- **workflow-oriented** enough to feel operational,
- **safe** for public demonstration because all data is synthetic,
- **transparent** enough for reviewers to inspect assumptions, outputs, and database health.
"""
)

# -----------------------------
# Main modules
# -----------------------------
st.markdown("### Core Workflow Modules")
modules = [
    ("📝 Planning Intake", "Capture, review, and validate planning assumptions across scenarios and versions."),
    ("💰 Economics", "Run synthetic project economics with DCF-style outputs such as NPV, IRR, and payback framing."),
    ("📊 KPI Dashboard", "Review production, cost, and earnings-style performance trends from synthetic operating actuals."),
    ("🔄 Mid-Year Update", "Simulate revised full-year expectations using actuals-to-date and updated H2 assumptions."),
    ("🗄️ Planning Database", "Inspect synthetic records, compare plan versions, and understand how the data model fits together."),
]
for module_name, desc in modules:
    st.markdown(f"- **{module_name}** — {desc}")

# -----------------------------
# Supporting pages
# -----------------------------
st.markdown("### Supporting Pages")
supporting = [
    ("🏠 Home", "Guided onboarding, product framing, and suggested reviewer path."),
    ("📖 Methodology", "Explains synthetic workflow assumptions, planning logic, and calculation approach."),
    ("📚 Data Dictionary", "Documents the portfolio data model and key tables/fields."),
    ("⚖️ Legal & Limitations", "Clarifies synthetic-only scope, educational purpose, and non-production limitations."),
    ("🛠️ System Status", "Provides deployment diagnostics, table row counts, completeness checks, and database previews."),
]
for page_name, desc in supporting:
    st.markdown(f"- **{page_name}** — {desc}")

# -----------------------------
# Reviewer guidance
# -----------------------------
st.markdown("---")
st.markdown("### Suggested Reviewer Path")
st.markdown(
    """
For the strongest portfolio walkthrough, explore the application in this order:

1. **Home** — get oriented on scope, synthetic-data design, and module purpose
2. **Planning Intake** — review the assumption capture and validation workflow
3. **Economics** — inspect the analytical engine and scenario evaluation outputs
4. **KPI Dashboard** — see synthetic operational performance reporting
5. **Mid-Year Update** — review reforecasting logic and actuals-versus-plan framing
6. **Planning Database** — inspect records, plan versions, and comparison structure
7. **System Status** — verify database completeness and deployment readiness
"""
)

# -----------------------------
# Operational transparency
# -----------------------------
st.markdown("---")
st.markdown("### Operational Transparency")
st.markdown(
    """
A dedicated **System Status** page is included to make deployment diagnostics visible to reviewers.
This helps confirm whether the SQLite database is fully initialized and whether key synthetic tables
required by the workflow are populated.

This is especially useful for portfolio review in hosted environments, where partial seeding can
otherwise make an otherwise-functional app appear incomplete.
"""
)

if system_status is not None and system_status["status"] != "Healthy":
    st.caption(
        f"Recommended action: {system_status['recommended_action']}"
    )

# -----------------------------
# Safety footer
# -----------------------------
st.markdown("---")
st.caption(
    "All entities, ventures, assets, scenarios, assumptions, projects, economics, KPI values, and "
    "performance datasets used in Atlas JV Planning OS are entirely fictitious and synthetic. "
    "This application is strictly educational and intended for portfolio demonstration only."
)