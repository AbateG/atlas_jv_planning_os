# pages/7_Methodology.py

import streamlit as st

from src.ui_helpers import render_global_disclaimer

st.set_page_config(page_title="Methodology", page_icon="🧭", layout="wide")

st.title("🧭 Methodology")
st.caption("How Atlas JV Planning OS is structured, what it simulates, and what its outputs mean.")

st.info(
    """
Atlas JV Planning OS is an educational and portfolio project that simulates selected upstream JV planning,
economics, and performance reporting workflows using entirely fictitious entities and 100% synthetic data.
"""
)

top_col1, top_col2, top_col3 = st.columns(3)
top_col1.metric("Data Type", "100% Synthetic")
top_col2.metric("Purpose", "Educational / Portfolio")
top_col3.metric("Safety Status", "No Real Confidential Data")

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs([
    "Workflow",
    "Economics Engine",
    "KPI Logic",
    "Limits & Safe Use",
])

with tab1:
    st.subheader("Workflow Architecture")
    st.markdown(
        """
Atlas JV Planning OS is designed as a simplified multi-step planning workflow:

1. **Planning Intake & Consolidation**
   - captures and edits plan assumptions by asset and plan version
   - validates business rules
   - stores assumptions and validation issues in SQLite

2. **Economic Evaluation**
   - links project-level uplift and capex with asset/version assumptions
   - runs a simplified annual discounted cash flow model
   - calculates NPV, IRR, payback, and sensitivity views

3. **Planning Database**
   - exposes structured tables for transparency and review

4. **KPI Dashboard**
   - summarizes synthetic monthly performance trends
   - provides production, cost, earnings, and cash flow reporting
   - supports filtering and comparison by venture and asset

5. **Mid-Year Update / Reforecast**
   - intended to compare original plan assumptions with updated actuals and revised outlooks
"""
    )

    st.subheader("Data Model")
    st.markdown(
        """
Core entities include:

- `ventures`
- `assets`
- `scenarios`
- `plan_versions`
- `assumptions`
- `projects`
- `economics_results`
- `monthly_actuals`
- `kpis`
- `validation_issues`

The design is relational, schema-first, and built to support traceability between planning assumptions, project economics, and KPI reporting.
"""
    )

with tab2:
    st.subheader("Economic Evaluation Logic")
    st.markdown(
        """
The Economic Evaluation module uses a simplified annual discounted cash flow framework.

### Inputs
- oil price
- production uplift (bopd)
- opex per barrel
- capex
- royalty rate
- tax rate
- discount rate
- project life
- annual decline rate

### Annual cash flow logic
- **Year 0:** capex outflow
- **Years 1..N:** declining annual production
- revenue = production × oil price
- opex = production × opex per bbl
- royalty = revenue × royalty rate
- pre-tax cash flow = revenue − opex − royalty
- tax = max(pre-tax cash flow, 0) × tax rate
- free cash flow = pre-tax cash flow − tax

### Outputs
- NPV
- IRR
- payback period
- annual DCF table
- sensitivity analysis
- downside/base/upside case comparison
"""
    )

    st.subheader("How planning assumptions are linked")
    st.markdown(
        """
The model uses:

- **project-level inputs** from the synthetic `projects` table
  - capex
  - expected uplift

- **asset/version assumptions** from the synthetic `assumptions` table
  - oil price
  - opex per bbl
  - royalty rate
  - tax rate

This creates a simplified but coherent bridge between planning assumptions and project-level economics.
"""
    )

with tab3:
    st.subheader("KPI Reporting Logic")
    st.markdown(
        """
The KPI dashboard summarizes synthetic monthly operating and financial performance.

### Source data
- `monthly_actuals`
- joined with asset and venture metadata

### Core displayed measures
- production (bbl)
- production rate (bopd)
- opex ($MM)
- capex ($MM)
- earnings ($MM)
- cash flow ($MM)

### Derived measures
- opex per bbl
- capex intensity
- asset comparison and ranking views

The KPI page is designed to mimic executive-style monthly reporting in a simplified and synthetic form.
"""
    )

with tab4:
    st.subheader("Important Limitations")
    st.markdown(
        """
This project is intentionally simplified.

### It does not represent:
- reserves-certified field development economics
- proprietary planning systems
- partner reporting templates
- real JV commercial arrangements
- detailed fiscal regime simulation
- investment committee-grade valuation

### It excludes:
- depreciation schedules
- financing structure
- working interest / entitlement complexity
- PSC mechanics
- abandonment liabilities
- inflation roll-forward in the DCF
- gas commercialization logic in the economics engine
"""
    )

    st.subheader("Safe-use foundation")
    st.markdown(
        """
- all venture names, assets, scenarios, people, and values are fictitious
- all data is synthetic and generated programmatically
- no confidential, internal, proprietary, or personally identifiable information is used
- the project does not reproduce or reverse-engineer any proprietary system
- it is strictly educational and for portfolio demonstration
"""
    )

render_global_disclaimer()