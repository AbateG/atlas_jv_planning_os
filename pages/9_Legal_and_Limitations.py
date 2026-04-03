# pages/9_Legal_and_Limitations.py

import streamlit as st

st.set_page_config(page_title="Legal & Limitations", page_icon="⚖️", layout="wide")

st.title("⚖️ Legal & Limitations")
st.caption("Transparency on fictitious data use, safe educational scope, and model limitations.")

top1, top2, top3 = st.columns(3)
top1.metric("Entities", "Fictitious")
top2.metric("Data", "100% Synthetic")
top3.metric("Use Case", "Educational / Portfolio")

tab1, tab2, tab3 = st.tabs(["Legal Notice", "Model Limitations", "Safe Use Guidance"])

with tab1:
    st.subheader("Legal Notice")
    st.markdown(
        """
This application is an independent educational and portfolio project.

### The project is built on the following safe-use principles:
- all names, ventures, assets, scenarios, projects, and values are fictitious
- all datasets are synthetic and generated programmatically
- no confidential, internal, proprietary, or personally identifiable information is used
- the project does not reproduce, reverse-engineer, or replicate any proprietary software or internal company workflow
- the application is intended solely for demonstration, learning, and portfolio presentation
"""
    )

with tab2:
    st.subheader("Model Limitations")
    st.markdown(
        """
Atlas JV Planning OS is intentionally simplified.

### Planning limitations
- planning assumptions are simplified educational representations
- validation rules are illustrative and not enterprise-complete
- version management is lightweight compared with production systems

### Economics limitations
- the economic engine uses a simplified annual DCF model
- it does not represent investment-grade project valuation
- it excludes financing, depreciation, entitlement complexity, abandonment, and detailed fiscal mechanics

### KPI and forecasting limitations
- KPI trends are derived from synthetic monthly actuals
- reforecasting logic uses scenario-style adjustments rather than a full operational forecasting model
- outputs should not be interpreted as realistic operational performance forecasts
"""
    )

with tab3:
    st.subheader("Safe Use Guidance")
    st.warning("Do not use this application for real business, financial, engineering, operational, regulatory, or investment decisions.")

    st.markdown(
        """
### Appropriate use
- portfolio demonstration
- educational analytics practice
- synthetic workflow simulation
- UI and database design showcase
- Python / Streamlit / SQLite project presentation

### Inappropriate use
- real asset planning
- reserves evaluation
- partner reporting
- budgeting approval
- investment screening for live opportunities
- regulatory or statutory submissions
"""
    )

st.markdown("---")
st.markdown(
    """
For more detail, refer to repository documentation:

- `README.md`
- `LEGAL_DISCLAIMER.md`
- `DATA_PROVENANCE.md`
- `LIMITATIONS.md`
- `MIT LICENSE`
"""
)