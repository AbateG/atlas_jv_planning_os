# pages/1_Home.py

import streamlit as st

from src.constants import APP_NAME, APP_TAGLINE
from src.ui_helpers import render_global_disclaimer

st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")

st.title("🏠 Home")
st.subheader(APP_TAGLINE)

st.markdown(
    """
Welcome to **Atlas JV Planning OS**! This page provides a guided orientation to help you understand the application,
its modules, and how to navigate effectively. Use this as your onboarding walkthrough for deeper understanding.
"""
)

st.markdown("### Application Snapshot")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Type", "Portfolio-Grade Demo")
col2.metric("Data", "100% Synthetic")
col3.metric("Backend", "SQLite Database")
col4.metric("Frontend", "Streamlit Pages")

st.markdown("---")

st.markdown("## 🗺️ Recommended First Clicks")
st.markdown("Start here for the best guided experience:")
first_clicks = [
    ("1️⃣ Planning Intake & Consolidation", "pages/2_Planning_Intake.py", "Begin with live workflow capture and validation"),
    ("2️⃣ Economic Evaluation", "pages/3_Economic_Evaluation.py", "See the analytical engine in action"),
    ("3️⃣ KPI Dashboard", "pages/5_KPI_Dashboard.py", "Explore reporting and trends"),
    ("4️⃣ Mid-Year Update / Reforecast", "pages/6_Mid_Year_Update.py", "Understand reforecast simulation"),
    ("5️⃣ Planning Database", "pages/4_Planning_Database.py", "Inspect the data structure"),
]
for name, path, desc in first_clicks:
    st.markdown(f"- **{name}** ({path}): {desc}")

st.markdown("---")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Project Overview",
    "Module Deep Dive",
    "Workflow Diagram",
    "Technical Architecture",
    "Review Guide",
])

with tab1:
    st.markdown(
        """
## Project Overview

Atlas JV Planning OS is designed as a compact but structured planning environment that connects several related workflows:

- capturing planning assumptions
- managing plan versions
- validating planning inputs
- evaluating project economics
- reporting KPIs
- simulating a mid-year reforecast

The project is intentionally educational and simplified, but it is built to feel like a coherent analytical product rather than a collection of isolated notebook-style outputs.

### What this app demonstrates
- structured planning data capture
- scenario and version-aware workflow design
- project economic screening
- relational data model design
- reporting and performance monitoring
- Python-based application architecture
- safe synthetic data generation and provenance awareness

### What this app does not do
- represent any real company, asset, venture, or partner
- reproduce any proprietary planning platform
- use confidential, internal, or personally identifiable data
- support real-world operational, engineering, financial, or investment decisions
"""
    )

with tab2:
    st.markdown("## 📚 Module Deep Dive")

    st.markdown("### Core Workflow Modules")

    modules_data = [
        {
            "icon": "📝",
            "title": "Planning Intake & Consolidation",
            "path": "pages/2_Planning_Intake.py",
            "steps": [
                "Select or create a plan version",
                "Copy assumptions from existing versions",
                "Edit assumptions interactively",
                "Run business-rule validation",
                "Save to SQLite with issue tracking"
            ]
        },
        {
            "icon": "💰",
            "title": "Economic Evaluation",
            "path": "pages/3_Economic_Evaluation.py",
            "steps": [
                "Select project and version",
                "Load synthetic planning data",
                "Execute DCF analysis",
                "Review NPV, IRR, payback metrics",
                "Run sensitivity testing"
            ]
        },
        {
            "icon": "🗄️",
            "title": "Planning Database",
            "path": "pages/4_Planning_Database.py",
            "steps": [
                "Explore database tables",
                "Compare plan versions",
                "Review stored outputs",
                "Inspect validation signals"
            ]
        },
        {
            "icon": "📊",
            "title": "KPI Dashboard",
            "path": "pages/5_KPI_Dashboard.py",
            "steps": [
                "Analyze monthly KPIs",
                "Compare assets and ventures",
                "View trends and rankings",
                "Assess cost efficiency"
            ]
        },
        {
            "icon": "🔄",
            "title": "Mid-Year Update / Reforecast",
            "path": "pages/6_Mid_Year_Update.py",
            "steps": [
                "Split YTD actuals from H2",
                "Apply revised assumptions",
                "Generate reforecast",
                "Compare against original plan"
            ]
        }
    ]

    for module in modules_data:
        with st.expander(f"{module['icon']} {module['title']}"):
            st.markdown(f"**Path:** {module['path']}")
            for step in module['steps']:
                st.markdown(f"- {step}")

    st.markdown("### Supporting Pages")
    supporting_data = [
        ("📖 Methodology", "pages/Methodology.py", "Workflow logic and assumptions"),
        ("📚 Data Dictionary", "pages/Data_Dictionary.py", "Data model reference"),
        ("⚖️ Legal & Limitations", "pages/Legal_Limitations.py", "Safe use guidelines"),
    ]
    for icon_title, path, desc in supporting_data:
        st.markdown(f"- **{icon_title}** ({path}): {desc}")

with tab3:
    st.markdown("## 🔄 Workflow Diagram")
    st.markdown("Visual representation of how modules connect:")

    diagram = """
```
[Planning Intake] --> [Economic Evaluation] --> [KPI Dashboard]
     |                    |                        |
     |                    |                        |
     v                    v                        v
[Database Storage] <-- [Validation] <-- [Reforecast Simulation]
                                   |
                                   |
                                   v
                            [Planning Database]
                                   |
                                   |
                                   v
                            [Supporting Pages]
```
    """
    st.code(diagram, language="text")

    st.markdown("### Workflow Explanation")
    st.markdown(
        """
- **Planning Intake** captures assumptions and validates them
- **Economic Evaluation** uses assumptions for DCF analysis
- **KPI Dashboard** reports on synthetic performance data
- **Mid-Year Update** simulates reforecasting with revised H2 assumptions
- **Planning Database** provides transparency into stored data
- **Supporting Pages** offer context, definitions, and legal framing

All modules connect through the SQLite database for persistence and traceability.
"""
    )

with tab4:
    st.markdown("## 🏗️ Technical Architecture")

    st.markdown("### Core Technology Stack")
    tech_stack = [
        "🐍 Python - Primary language",
        "🌊 Streamlit - Web UI framework",
        "🗄️ SQLite - Relational database",
        "📊 Pandas - Data manipulation",
        "🔢 NumPy - Numerical computing",
        "📈 Plotly - Interactive charts",
        "💰 numpy-financial - Financial calculations",
        "🎭 Faker - Synthetic data generation",
        "🧪 Pytest - Testing framework",
    ]
    for item in tech_stack:
        st.markdown(f"- {item}")

    st.markdown("### Compact Architecture Diagram")
    arch_diagram = """
```
User Interface (Streamlit Pages)
    ├── app.py (Landing Page)
    ├── pages/1_Home.py (Onboarding)
    ├── pages/2_Planning_Intake.py
    ├── pages/3_Economic_Evaluation.py
    ├── pages/4_Planning_Database.py
    ├── pages/5_KPI_Dashboard.py
    └── pages/6_Mid_Year_Update.py

Business Logic (src/)
    ├── constants.py
    ├── ui_helpers.py
    ├── data_generation.py
    ├── forecasting.py
    ├── reporting.py
    └── economics.py

Data Layer (SQLite)
    ├── ventures, assets, scenarios
    ├── assumptions, projects, economics_results
    ├── monthly_actuals, kpis, validation_issues
    └── plan_versions
```
    """
    st.code(arch_diagram, language="text")

    st.markdown("### Architectural Principles")
    principles = [
        "Schema-first database design",
        "Synthetic-data-first development",
        "Modular business logic in `src/`",
        "Page-based Streamlit navigation",
        "SQLite persistence for all data",
        "Test coverage for core logic",
        "Clear separation of UI and business logic",
    ]
    for principle in principles:
        st.markdown(f"- {principle}")

    st.markdown("### Portfolio Value Signals")
    signals = [
        "Analytical application design",
        "Business workflow modeling",
        "Python system architecture",
        "Database integration skills",
        "Defensible simplification strategies",
        "Clear documentation and safety framing",
        "Modular, testable code structure",
    ]
    for signal in signals:
        st.markdown(f"- {signal}")

with tab5:
    st.markdown("## 📋 Review Guide")

    st.markdown("### Optimal Review Path")
    st.markdown("For hiring/portfolio evaluation, follow this sequence:")

    review_path = [
        ("1. Planning Intake", "Live workflow, validation, data persistence"),
        ("2. Economic Evaluation", "DCF engine, NPV/IRR calculations"),
        ("3. KPI Dashboard", "Reporting, trends, portfolio views"),
        ("4. Mid-Year Update", "Reforecast simulation logic"),
        ("5. Planning Database", "Data structure, version comparisons"),
        ("6. Supporting Pages", "Methodology, data dictionary, legal framing"),
    ]
    for step, desc in review_path:
        st.markdown(f"**{step}** — {desc}")

    st.markdown("### Key Evaluation Criteria")
    criteria = [
        "Workflow coherence and user experience",
        "Modular Python architecture",
        "Database design and data integrity",
        "Synthetic data generation and traceability",
        "Analytical calculation accuracy",
        "Clear documentation and limitations",
        "Presentation quality and usability",
        "Test coverage and code quality",
        "Safety framing and legal awareness",
    ]
    for criterion in criteria:
        st.markdown(f"- {criterion}")

    st.markdown("### What This Project Demonstrates")
    st.markdown(
        """
This application showcases the ability to:
- Design end-to-end analytical workflows
- Build database-backed web applications
- Implement financial modeling logic
- Create user-friendly interfaces for complex data
- Handle synthetic data responsibly
- Communicate technical concepts clearly
"""
    )

st.markdown("---")

st.markdown("## 🎯 Onboarding Complete")
st.markdown(
    """
You've now completed the guided orientation to Atlas JV Planning OS. This synthetic planning environment demonstrates
how structured workflows can connect assumption capture, economic evaluation, performance reporting, and reforecasting.

**Next Steps:**
- Start with Planning Intake to see live workflows
- Explore Economic Evaluation for analytical depth
- Use this page as a reference for module connections

Remember: All data is 100% synthetic and fictitious. This is a portfolio demonstration tool only.
"""
)

render_global_disclaimer()