# app.py

import streamlit as st

from src.constants import APP_NAME, APP_TAGLINE

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🧭 Atlas JV Planning OS")
st.subheader(APP_TAGLINE)

st.info(
    """
Atlas JV Planning OS is an educational, portfolio-grade application that simulates selected upstream joint venture
planning, economics, and performance reporting workflows using entirely fictitious entities and 100% synthetic data.
"""
)

st.markdown("### Project Highlights")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Core Modules", "5")
col2.metric("Data Safety", "100% Synthetic")
col3.metric("Tech Stack", "Python + Streamlit")
col4.metric("Database", "SQLite")

st.markdown("## Quick Overview")
st.markdown(
    """
Atlas JV Planning OS demonstrates a structured planning workflow connecting assumption capture, economic evaluation,
KPI reporting, and reforecasting. Built as a modular analytical system with synthetic data for safe portfolio demonstration.
"""
)

st.markdown("### Core Workflow Modules")
modules = [
    ("📝 Planning Intake", "Capture and validate planning assumptions"),
    ("💰 Economic Evaluation", "Run DCF analysis with NPV, IRR, sensitivities"),
    ("📊 KPI Dashboard", "Review production, costs, earnings trends"),
    ("🔄 Mid-Year Update", "Simulate reforecast with revised H2 assumptions"),
    ("🗄️ Planning Database", "Inspect data model and version comparisons"),
]
for icon_name, desc in modules:
    st.markdown(f"- **{icon_name}**: {desc}")

st.markdown("### Supporting Pages")
supporting = [
    ("📖 Methodology", "Workflow logic and assumptions"),
    ("📚 Data Dictionary", "Synthetic data model reference"),
    ("⚖️ Legal & Limitations", "Safe use and constraints"),
    ("🏠 Home", "Guided walkthrough and onboarding"),
]
for icon_name, desc in supporting:
    st.markdown(f"- **{icon_name}**: {desc}")

st.markdown("---")

st.markdown("### Suggested First Steps")
st.markdown(
    """
For the best first impression, explore in this order:
1. **Planning Intake** — Live workflow and validation
2. **Economic Evaluation** — Analytical engine demo
3. **KPI Dashboard** — Reporting views
4. **Mid-Year Update** — Reforcast simulation
5. **Home** — Detailed onboarding walkthrough
"""
)

st.markdown("---")
st.caption(
    "All entities, scenarios, projects, values, and datasets used in Atlas JV Planning OS are fictitious and synthetic. "
    "This application is strictly educational and intended for portfolio demonstration only."
)