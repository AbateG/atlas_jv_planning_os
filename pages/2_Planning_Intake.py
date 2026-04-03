import streamlit as st
import pandas as pd

from src.db import get_plan_versions, read_table, replace_validation_issues_for_version
from src.planning import (
    build_editable_assumptions_frame,
    create_new_plan_version,
    copy_assumptions_to_new_version,
    save_assumptions_df,
    consolidate_assumptions,
    validate_and_prepare_issues,
)
from src.ui_helpers import load_joined_validation_issues, render_global_disclaimer, dataframe_download_button


st.title("Planning Intake & Consolidation")

# ---------------------------------------------------------
# SECTION 1: Version selection / creation
# ---------------------------------------------------------
st.markdown("## 1. Plan Version Management")

versions_df = get_plan_versions()
scenarios_df = read_table("scenarios")

col1, col2 = st.columns([2, 1])

with col1:
    if versions_df.empty:
        st.warning("No plan versions found. Create one below.")
        selected_version_id = None
    else:
        version_display = versions_df["version_name"] + " | " + versions_df["scenario_name"] + " | " + versions_df["status"]
        selected_display = st.selectbox("Select Existing Version", version_display.tolist())
        selected_version_id = int(versions_df.loc[version_display == selected_display, "version_id"].iloc[0])

with col2:
    st.markdown("### Create New Version")
    with st.form("create_version_form"):
        new_version_name = st.text_input("Version Name", value="BP2026_Base_v2")
        new_plan_year = st.number_input("Plan Year", min_value=2024, max_value=2035, value=2026, step=1)
        scenario_options = scenarios_df["scenario_name"].tolist()
        selected_scenario_name = st.selectbox("Scenario", scenario_options)
        copy_from_existing = st.checkbox("Copy assumptions from selected version", value=True)
        submitted_new_version = st.form_submit_button("Create Version")

        if submitted_new_version:
            scenario_id = int(
                scenarios_df.loc[scenarios_df["scenario_name"] == selected_scenario_name, "scenario_id"].iloc[0]
            )

            try:
                new_version_id = create_new_plan_version(
                    version_name=new_version_name,
                    plan_year=int(new_plan_year),
                    scenario_id=scenario_id,
                )

                if copy_from_existing and selected_version_id is not None:
                    copy_assumptions_to_new_version(selected_version_id, new_version_id)

                st.success(f"Created new version: {new_version_name} (ID {new_version_id})")
                st.cache_data.clear()
                st.rerun()

            except Exception as e:
                st.error(f"Could not create version: {e}")

if selected_version_id is None:
    render_global_disclaimer()
    st.stop()

# ---------------------------------------------------------
# SECTION 2: Editable assumptions
# ---------------------------------------------------------
st.markdown("## 2. Edit Assumptions")

editable_df = build_editable_assumptions_frame(selected_version_id)

display_cols = [
    "venture_name",
    "asset_name",
    "asset_type",
    "oil_price",
    "gas_price",
    "fx_rate",
    "inflation_rate",
    "production_bopd",
    "opex_per_bbl",
    "capex_mm",
    "royalty_rate",
    "tax_rate",
]

edited_df = st.data_editor(
    editable_df[display_cols + ["version_id", "asset_id"]].copy(),
    use_container_width=True,
    num_rows="fixed",
    hide_index=True,
    column_config={
        "venture_name": st.column_config.TextColumn("Venture", disabled=True),
        "asset_name": st.column_config.TextColumn("Asset", disabled=True),
        "asset_type": st.column_config.TextColumn("Asset Type", disabled=True),
        "oil_price": st.column_config.NumberColumn("Oil Price", min_value=0.0, format="%.2f"),
        "gas_price": st.column_config.NumberColumn("Gas Price", min_value=0.0, format="%.2f"),
        "fx_rate": st.column_config.NumberColumn("FX Rate", min_value=0.0, format="%.2f"),
        "inflation_rate": st.column_config.NumberColumn("Inflation", min_value=0.0, max_value=1.0, format="%.4f"),
        "production_bopd": st.column_config.NumberColumn("Production (bopd)", min_value=0.0, format="%.2f"),
        "opex_per_bbl": st.column_config.NumberColumn("Opex ($/bbl)", min_value=0.0, format="%.2f"),
        "capex_mm": st.column_config.NumberColumn("Capex ($MM)", min_value=0.0, format="%.2f"),
        "royalty_rate": st.column_config.NumberColumn("Royalty Rate", min_value=0.0, max_value=1.0, format="%.4f"),
        "tax_rate": st.column_config.NumberColumn("Tax Rate", min_value=0.0, max_value=1.0, format="%.4f"),
        "version_id": st.column_config.NumberColumn("Version ID", disabled=True),
        "asset_id": st.column_config.NumberColumn("Asset ID", disabled=True),
    },
)

# Rebuild a clean save dataframe from edited inputs + original metadata
input_cols = [
    "version_id",
    "asset_id",
    "oil_price",
    "gas_price",
    "fx_rate",
    "inflation_rate",
    "production_bopd",
    "opex_per_bbl",
    "capex_mm",
    "royalty_rate",
    "tax_rate",
]

metadata_cols = [
    "asset_id",
    "venture_id",
    "venture_name",
    "basin",
    "fluid_type",
    "asset_name",
    "asset_type",
    "status",
]

edited_inputs_df = edited_df[input_cols].copy()
metadata_df = editable_df[metadata_cols].drop_duplicates(subset=["asset_id"]).copy()

merged_save_df = pd.merge(
    edited_inputs_df,
    metadata_df,
    on="asset_id",
    how="left",
    validate="many_to_one"
)

ordered_cols = [
    "version_id",
    "venture_id",
    "venture_name",
    "basin",
    "fluid_type",
    "asset_id",
    "asset_name",
    "asset_type",
    "status",
    "oil_price",
    "gas_price",
    "fx_rate",
    "inflation_rate",
    "production_bopd",
    "opex_per_bbl",
    "capex_mm",
    "royalty_rate",
    "tax_rate",
]

missing_cols = [col for col in ordered_cols if col not in merged_save_df.columns]
if missing_cols:
    st.error(f"Internal dataframe assembly error. Missing columns: {missing_cols}")
    st.stop()

merged_save_df = merged_save_df[ordered_cols]

action_col1, action_col2 = st.columns(2)

with action_col1:
    if st.button("Validate Assumptions", type="primary"):
        issues_df = validate_and_prepare_issues(merged_save_df)
        replace_validation_issues_for_version(selected_version_id, issues_df)
        st.success("Validation completed and issues refreshed.")
        st.cache_data.clear()
        st.rerun()

with action_col2:
    if st.button("Save Assumptions"):
        try:
            save_assumptions_df(merged_save_df)
            issues_df = validate_and_prepare_issues(merged_save_df)
            replace_validation_issues_for_version(selected_version_id, issues_df)
            st.success("Assumptions saved successfully.")
            st.cache_data.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Save failed: {e}")

# ---------------------------------------------------------
# SECTION 3: Consolidated summary
# ---------------------------------------------------------
st.markdown("## 3. Consolidated Plan Summary")
consolidated_df = consolidate_assumptions(merged_save_df)
st.dataframe(consolidated_df, use_container_width=True)

dataframe_download_button(consolidated_df, "consolidated_plan_summary.csv", "Download Consolidated Summary CSV")

# ---------------------------------------------------------
# SECTION 4: Validation issues
# ---------------------------------------------------------
st.markdown("## 4. Validation Issues")
issues_df = load_joined_validation_issues()
issues_filtered = issues_df[issues_df["version_id"] == selected_version_id].copy()

if issues_filtered.empty:
    st.success("No validation issues found for this version.")
else:
    st.dataframe(issues_filtered, use_container_width=True)
    dataframe_download_button(issues_filtered, "validation_issues.csv", "Download Validation Issues CSV")

render_global_disclaimer()