import streamlit as st
import pandas as pd
import numpy as np
import subprocess
import os

st.set_page_config(
    page_title="Fleet Health Intelligence",
    page_icon="📊",
    layout="wide"
)


@st.cache_data
def load_data():
    if os.path.exists("Master_Procurement_All_Trucks.csv"):
        return pd.read_csv("Master_Procurement_All_Trucks.csv")
    else:
        # Fallback if pipeline hasn't run yet
        st.warning(
            "Procurement ledger data file not found. Please trigger the pipeline.")
        return pd.DataFrame()


# Sidebar or header trigger for your data update
st.sidebar.header("Data Management")

if st.sidebar.button("Import Data & Re-run Pipeline"):
    with st.spinner("Executing ML Survival Lifecycles & compiling ledger... Please wait."):
        try:
            # Execute the pipeline script asynchronously and catch logs
            result = subprocess.run(
                ["python", "pipeline.py"], capture_output=True, text=True, check=True)

            # Clear Streamlit's cache so it re-reads the fresh CSV file
            st.cache_data.clear()

            st.sidebar.success("Pipeline Executed Successfully!")
            # Optional: view console outputs inside an expander
            with st.sidebar.expander("Show Logs"):
                st.code(result.stdout)

        except subprocess.CalledProcessError as e:
            st.sidebar.error("Pipeline failed to execute.")
            with st.sidebar.expander("View Error Logs"):
                st.code(e.stderr)

# Load the vectorized procurement ledger file
df = load_data()

# ---------------------------------------------------------------------
# DATA RECONCILIATION & TEMPORAL SPLIT (THE INVISIBLE FILTER)
# ---------------------------------------------------------------------
# Rename incoming ledger columns to seamlessly link with dashboard elements
df = df.rename(columns={
    "Age (Days)": "Calculated Age (Days)"
})

# Anchored baseline date matching the operational calendar day
base_date = pd.to_datetime('2026-06-10')

# Safe conversion of string dates to datetime objects
df['parsed_projected_date'] = pd.to_datetime(
    df['Projected 50% Date'], errors='coerce')
df['parsed_projected_date'] = df['parsed_projected_date'].fillna(
    pd.to_datetime('2099-12-31'))

# Calculate exact delta days from today until a part hits its 50% limit
df['Days to 50% Health'] = (df['parsed_projected_date'] - base_date).dt.days

# Define status rules based strictly on future planning windows


def assign_purchase_status(row):
    days_left = row['Days to 50% Health']
    if days_left < 0 or row['Current Health (%)'] <= 20:
        return "URGENT"
    elif 0 <= days_left <= 30:
        return "WARNING"
    else:
        return "NORMAL"


df['Purchase Status'] = df.apply(assign_purchase_status, axis=1)
df['Buy in 30 Days?'] = df['Days to 50% Health'].apply(
    lambda d: "Yes" if 0 <= d <= 30 else "No")

df["Truck ID"] = df["Truck ID"].astype(str)
df["Component Description"] = df["Component Description"].astype(str)
df["Purchase Status"] = df["Purchase Status"].astype(str)

# ---------------------------------------------------------------------
# DESIGN CSS STYLING ARCHITECTURE
# ---------------------------------------------------------------------
st.markdown("""
<style>
.stApp {
    background-color: #F4F6F9;
    color: #111827;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #081423 0%, #0B1F33 50%, #103B67 100%);
}

[data-testid="stSidebar"] * {
    color: white;
}

span[data-baseweb="tag"] {
    background-color: #DBEAFE !important;
    color: #1D4ED8 !important;
    border: 1px solid #93C5FD !important;
}

span[data-baseweb="tag"] * {
    color: #1D4ED8 !important;
}

span[data-baseweb="tag"] svg {
    fill: #1D4ED8 !important;
}
            
.stSelectbox div[data-baseweb="select"] {
    border-color: #BFDBFE !important;
}

div[data-baseweb="select"] {
    background-color: #F8FAFC !important;
    color: #111827 !important;
    border-radius: 8px !important;
}

.stTextInput input {
    background-color: #F8FAFC !important;
    color: #111827 !important;
    border: 1px solid #93C5FD !important;
}

.stTextInput input:focus {
    border: 2px solid #2563EB !important;
    box-shadow: 0 0 0 1px #2563EB !important;
}
            
.stTextInput input {
    border: 1px solid #BFDBFE !important;
}

.stSlider {
    color: #2563EB !important;
}            

.hero {
    background: linear-gradient(135deg, #0B1F33 0%, #0F4C81 100%);
    padding: 30px 34px;
    border-radius: 16px;
    color: white;
    margin-bottom: 24px;
}

.hero-title {
    font-size: 40px;
    font-weight: 800;
    margin-bottom: 6px;
}

.hero-subtitle {
    font-size: 16px;
    opacity: 0.9;
}

.metric-card {
    background-color: white;
    padding: 22px 24px;
    border-radius: 14px;
    border: 1px solid #E5EAF0;
    box-shadow: 0px 4px 14px rgba(15, 23, 42, 0.06);
}

.metric-label {
    font-size: 12px;
    color: #6B7280;
    font-weight: 700;
    letter-spacing: .08em;
    text-transform: uppercase;
}

.metric-value {
    font-size: 34px;
    font-weight: 800;
    color: #111827;
    margin-top: 4px;
}

.metric-caption {
    font-size: 12px;
    color: #6B7280;
    margin-top: 4px;
}

.section-title {
    font-size: 22px;
    font-weight: 800;
    color: #0B1F33;
    margin-top: 28px;
    margin-bottom: 12px;
}

.info-card {
    background-color: white;
    padding: 18px 20px;
    border-radius: 14px;
    border: 1px solid #E5EAF0;
    box-shadow: 0px 4px 14px rgba(15, 23, 42, 0.05);
    height: 100%;
}

.critical-card {
    background-color: white;
    padding: 18px;
    border-radius: 14px;
    border-left: 6px solid #C62828;
    border-top: 1px solid #E5EAF0;
    border-right: 1px solid #E5EAF0;
    border-bottom: 1px solid #E5EAF0;
    box-shadow: 0px 4px 14px rgba(15, 23, 42, 0.05);
    margin-bottom: 12px;
}

.card-small-label {
    font-size: 11px;
    color: #6B7280;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .06em;
}

.card-title {
    font-size: 15px;
    color: #111827;
    font-weight: 800;
    margin-top: 3px;
}

.card-text {
    font-size: 13px;
    color: #374151;
    margin-top: 4px;
}

.status-pill-urgent {
    background-color: #FEE2E2;
    color: #991B1B;
    padding: 4px 10px;
    border-radius: 999px;
    font-weight: 800;
    font-size: 12px;
}

.status-pill-warning {
    background-color: #FEF3C7;
    color: #92400E;
    padding: 4px 10px;
    border-radius: 999px;
    font-weight: 800;
    font-size: 12px;
}

.status-pill-normal {
    background-color: #DCFCE7;
    color: #166534;
    padding: 4px 10px;
    border-radius: 999px;
    font-weight: 800;
    font-size: 12px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------
# SIDEBAR CONTROL FILTERS
# ---------------------------------------------------------------------
st.sidebar.title("Fleet Control Panel")
st.sidebar.caption("Filter active operational metrics")

status_filter = st.sidebar.multiselect(
    "Purchase Status",
    options=["URGENT", "WARNING", "NORMAL"],
    default=["URGENT", "WARNING", "NORMAL"]
)

truck_filter = st.sidebar.text_input("Truck ID Search")
component_filter = st.sidebar.text_input("Part Description Search")

health_range = st.sidebar.slider(
    "Current Health (%) Window",
    min_value=float(df["Current Health (%)"].min()),
    max_value=float(df["Current Health (%)"].max()),
    value=(float(df["Current Health (%)"].min()),
           float(df["Current Health (%)"].max()))
)

# ---------------------------------------------------------------------
# TEMPORAL PARTITION FILTERS (OPERATIONAL VS BACKLOG)
# ---------------------------------------------------------------------
# Create two independent data branches based on the invisible date threshold
op_base = df[df['Days to 50% Health'] >= 0].copy()
backlog_base = df[df['Days to 50% Health'] < 0].copy()

# Filter Branch A: Active Operational View (Each row = 1 Distinct Spare Part Unit)
filtered_op_df = op_base[
    (op_base["Purchase Status"].isin(status_filter)) &
    (op_base["Current Health (%)"].between(health_range[0], health_range[1]))
]

# Filter Branch B: Historical Backlog View
filtered_backlog_df = backlog_base[
    (backlog_base["Current Health (%)"].between(
        health_range[0], health_range[1]))
]

if truck_filter:
    if truck_filter in df["Truck ID"].values:
        filtered_op_df = filtered_op_df[filtered_op_df["Truck ID"]
                                        == truck_filter]
        filtered_backlog_df = filtered_backlog_df[filtered_backlog_df["Truck ID"] == truck_filter]
    else:
        st.sidebar.error("Truck ID not found")
        filtered_op_df = filtered_op_df.iloc[0:0]
        filtered_backlog_df = filtered_backlog_df.iloc[0:0]

if component_filter:
    filtered_op_df = filtered_op_df[filtered_op_df["Component Description"].str.contains(
        component_filter, case=False, na=False)]
    filtered_backlog_df = filtered_backlog_df[filtered_backlog_df["Component Description"].str.contains(
        component_filter, case=False, na=False)]

# Header Title Card
st.markdown("""
<div class="hero">
    <div class="hero-title">Fleet Health Intelligence Platform</div>
    <div class="hero-subtitle">
        Predictive survival analytics tracking individual physical part volumes and asset-level demand pipelines.
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------
# HIGH-LEVEL EXECUTIVE KPIS (OPERATIONAL ONLY)
# ---------------------------------------------------------------------
urgent_units = len(
    filtered_op_df[filtered_op_df["Purchase Status"] == "URGENT"])
warning_units = len(
    filtered_op_df[filtered_op_df["Purchase Status"] == "WARNING"])
normal_units = len(
    filtered_op_df[filtered_op_df["Purchase Status"] == "NORMAL"])
total_op_units = len(filtered_op_df)

avg_health = filtered_op_df["Current Health (%)"].mean(
) if total_op_units > 0 else 0
fleet_assets = filtered_op_df["Truck ID"].nunique(
) if total_op_units > 0 else 0
urgent_assets = filtered_op_df[filtered_op_df["Purchase Status"]
                               == "URGENT"]["Truck ID"].nunique() if total_op_units > 0 else 0

col1, col2, col3, col4, col5 = st.columns(5)
cards = [
    ("Urgent Units Due", urgent_units,
     "Parts due inside 30 days or low health", "#C62828"),
    ("Warning Units Due", warning_units,
     "Parts entering procurement windows", "#F9A825"),
    ("Stable Units", normal_units, "Parts running without constraints", "#2E7D32"),
    ("Active Trucks", fleet_assets, "Unique trucks monitored", "#0F4C81"),
    ("Operational Health", f"{avg_health:.1f}%",
     "Mean active part health", "#4B5563"),
]

for col, (label, value, caption, color) in zip([col1, col2, col3, col4, col5], cards):
    with col:
        st.markdown(f"""
        <div class="metric-card" style="border-left: 6px solid {color};">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value if isinstance(value, str) else f"{value:,}"}</div>
            <div class="metric-caption">{caption}</div>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------------------
# EXECUTIVE INSIGHT CARDS
# ---------------------------------------------------------------------
st.markdown('<div class="section-title">Executive Overview</div>',
            unsafe_allow_html=True)
summary_col1, summary_col2, summary_col3 = st.columns(3)

with summary_col1:
    st.markdown(f"""
    <div class="info-card">
        <div class="card-small-label">Operational Risk</div>
        <div class="card-title">{urgent_assets:,} trucks with active demands</div>
        <div class="card-text">Total trucks with physical part replacements scheduled within upcoming maintenance intervals.</div>
    </div>
    """, unsafe_allow_html=True)

with summary_col2:
    buy_30 = len(filtered_op_df[filtered_op_df["Buy in 30 Days?"] == "Yes"])
    st.markdown(f"""
    <div class="info-card">
        <div class="card-small-label">Procurement Signals</div>
        <div class="card-title">{buy_30:,} specific units required</div>
        <div class="card-text">Total quantity of individual spare parts scheduled to hit their 50% threshold strictly post-June 10, 2026.</div>
    </div>
    """, unsafe_allow_html=True)

with summary_col3:
    total_backlog_count = len(filtered_backlog_df)
    st.markdown(f"""
    <div class="info-card" style="border-left: 6px solid #991B1B;">
        <div class="card-small-label" style="color: #991B1B;">Accrued Maintenance Debt</div>
        <div class="card-title">{total_backlog_count:,} Overdue Units Isolated</div>
        <div class="card-text">Accumulated parts list where historical metrics indicate threshold depletion prior to today's date.</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------
# DETACHED HISTORICAL BACKLOG TABLE SECTION
# ---------------------------------------------------------------------
st.markdown('<div class="section-title" style="color: #C62828;">⚠️ Overdue Maintenance Backlog Ledger (Past Due Units)</div>', unsafe_allow_html=True)
st.markdown(
    f"""<div style="background-color: #FFF5F5; border-left: 5px solid #C62828; padding: 15px; border-radius: 6px; margin-bottom: 15px; color: #7F1D1D; font-size: 14px;">
        <b>Audit Notice:</b> The <b>{total_backlog_count:,}</b> part units listed below were calculated to have crossed their 50% degradation limit <b>prior to June 10, 2026</b>. 
        These have been isolated from your forward-looking operational horizons. Each row signifies 1 individual unexecuted changeout.
    </div>""", unsafe_allow_html=True
)

backlog_cols = [
    "Truck ID",
    "Installation Date",
    "Component Description",
    "Calculated Age (Days)",
    "Current Health (%)",
    "Projected 50% Date",
    "Days to 50% Health"
]
backlog_cols = [c for c in backlog_cols if c in filtered_backlog_df.columns]

if total_backlog_count > 0:
    st.dataframe(
        filtered_backlog_df.sort_values(
            by="Days to 50% Health", ascending=True)[backlog_cols],
        use_container_width=True,
        height=320,
        hide_index=True
    )
    st.download_button(
        label="Export Isolated Backlog Data (CSV)",
        data=filtered_backlog_df.to_csv(index=False),
        file_name="fleet_maintenance_backlog.csv",
        mime="text/csv",
        key="backlog_dl"
    )
else:
    st.success(
        "No historical maintenance backlog found matching your active filters.")

# ---------------------------------------------------------------------
# FLEET DEMAND DISTRIBUTION BY ASSET UNIT
# ---------------------------------------------------------------------
st.markdown('<div class="section-title">Active Part Units Needed by Truck Unit</div>',
            unsafe_allow_html=True)
if len(filtered_op_df) > 0:
    truck_distribution = (
        filtered_op_df
        .groupby("Truck ID")
        .size()
        .reset_index(name="Physical Units Required")
        .sort_values("Physical Units Required", ascending=False)
        .head(25)
    )
    st.bar_chart(truck_distribution.set_index("Truck ID")[
                 "Physical Units Required"], use_container_width=True)
else:
    st.info("No active operational data available under the current filters.")

# ---------------------------------------------------------------------
# PRIORITY CRITICAL WATCHLIST
# ---------------------------------------------------------------------
st.markdown('<div class="section-title">Priority Operational Procurement Watchlist</div>',
            unsafe_allow_html=True)
top_critical = filtered_op_df.sort_values(
    by="Current Health (%)", ascending=True).head(18)
card_cols = st.columns(3)

for i, (_, row) in enumerate(top_critical.iterrows()):
    with card_cols[i % 3]:
        status_class = "status-pill-urgent"
        if row["Purchase Status"] == "WARNING":
            status_class = "status-pill-warning"
        elif row["Purchase Status"] == "NORMAL":
            status_class = "status-pill-normal"

        component_name = str(row["Component Description"])
        if len(component_name) > 75:
            component_name = component_name[:75] + "..."

        st.markdown(f"""
        <div class="critical-card">
            <div class="card-small-label">Truck ID: {row["Truck ID"]}</div>
            <div class="card-title">{component_name}</div>
            <div class="card-text">Current Health: <b>{row["Current Health (%)"]:.1f}%</b></div>
            <div class="card-text">Estimated 50% Target Date: <b>{row["Projected 50% Date"]}</b></div>
            <br>
            <span class="{status_class}">{row["Purchase Status"]}</span>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------------------
# ROLLING OPERATIONAL PLANNING HORIZON WINDOWS
# ---------------------------------------------------------------------
st.markdown('<div class="section-title">Forward Procurement Planning Horizon</div>',
            unsafe_allow_html=True)

planning_cols = [
    "Truck ID",
    "Installation Date",
    "Component Description",
    "Calculated Age (Days)",
    "Current Health (%)",
    "Projected 50% Date",
    "Purchase Status",
    "Buy in 30 Days?"
]
planning_cols = [c for c in planning_cols if c in filtered_op_df.columns]

# Slicing rolling windows for items whose limits expire in the future
month1 = filtered_op_df[filtered_op_df["Days to 50% Health"] <= 30]
month2 = filtered_op_df[(filtered_op_df["Days to 50% Health"] > 30) & (
    filtered_op_df["Days to 50% Health"] <= 60)]
month3 = filtered_op_df[(filtered_op_df["Days to 50% Health"] > 60) & (
    filtered_op_df["Days to 50% Health"] <= 90)]
month4 = filtered_op_df[filtered_op_df["Days to 50% Health"] > 90]

tab1, tab2, tab3, tab4 = st.tabs([
    "Month 1: Immediate Procurement Window (0-30 Days)",
    "Month 2: Planned Procurement Window (31-60 Days)",
    "Month 3: Preventive Procurement Window (61-90 Days)",
    "Month 4: Stable Monitoring Window (>90 Days)"
])

with tab1:
    st.write(
        f"Total separate part units requiring purchase within 30 days: **{len(month1):,}**")
    st.dataframe(month1.sort_values(by="Current Health (%)")[
                 planning_cols], use_container_width=True, hide_index=True)

with tab2:
    st.write(
        f"Total separate part units queued for Month 2 deployment: **{len(month2):,}**")
    st.dataframe(month2.sort_values(by="Current Health (%)")[
                 planning_cols], use_container_width=True, hide_index=True)

with tab3:
    st.write(
        f"Total separate part units queued for Month 3 deployment: **{len(month3):,}**")
    st.dataframe(month3.sort_values(by="Current Health (%)")[
                 planning_cols], use_container_width=True, hide_index=True)

with tab4:
    st.write(f"Stable part units running clear: **{len(month4):,}**")
    st.dataframe(month4.sort_values(by="Current Health (%)")[
                 planning_cols], use_container_width=True, hide_index=True)

# ---------------------------------------------------------------------
# ASSET SPECIFIC LOOKUP
# ---------------------------------------------------------------------
st.markdown('<div class="section-title">Truck Lookup</div>',
            unsafe_allow_html=True)
lookup_truck = st.text_input(
    "Enter an exact Truck ID for localized unit review", key="lookup_truck")

if lookup_truck:
    truck_df = df[df["Truck ID"] == lookup_truck]
    if len(truck_df) > 0:
        truck_avg_health = truck_df["Current Health (%)"].mean()
        truck_urgent = len(truck_df[truck_df["Purchase Status"] == "URGENT"])

        tcol1, tcol2, tcol3 = st.columns(3)
        tcol1.metric("Total Spare Parts Tracking", f"{len(truck_df):,} Units")
        tcol2.metric("Urgent Changes Pending", f"{truck_urgent:,} Units")
        tcol3.metric("Mean Part Health", f"{truck_avg_health:.1f}%")

        truck_cols = [
            "Installation Date",
            "Component Description",
            "Current Health (%)",
            "Projected 50% Date",
            "Purchase Status",
            "Buy in 30 Days?"
        ]
        truck_cols = [c for c in truck_cols if c in truck_df.columns]
        st.dataframe(truck_df[truck_cols],
                     use_container_width=True, hide_index=True)
    else:
        st.warning("No records found for this exact Truck ID.")

# ---------------------------------------------------------------------
# SYSTEM-WIDE COMPONENT INVENTORY EXPANDER
# ---------------------------------------------------------------------
st.markdown('<div class="section-title">Operational Component Inventory</div>',
            unsafe_allow_html=True)

display_cols = [
    "Truck ID",
    "Installation Date",
    "Component Description",
    "Calculated Age (Days)",
    "Current Health (%)",
    "Projected 50% Date",
    "Purchase Status",
    "Buy in 30 Days?"
]
display_cols = [c for c in display_cols if c in filtered_op_df.columns]


def highlight_columns(row):
    styles = [""] * len(row)
    try:
        status_idx = row.index.get_loc("Purchase Status")
        truck_idx = row.index.get_loc("Truck ID")
        component_idx = row.index.get_loc("Component Description")
        status = row["Purchase Status"]

        if status == "URGENT":
            color = "background-color: #FDECEC; color: #7F1D1D; font-weight: bold;"
        elif status == "WARNING":
            color = "background-color: #FFF7E0; color: #78350F; font-weight: bold;"
        else:
            color = "background-color: #F0FDF4; color: #14532D; font-weight: bold;"

        styles[status_idx] = color
        styles[truck_idx] = color
        styles[component_idx] = color
    except:
        pass
    return styles


with st.expander("View full filtered operational unit inventory table", expanded=False):
    st.dataframe(
        filtered_op_df[display_cols].style.apply(highlight_columns, axis=1),
        use_container_width=True,
        height=620,
        hide_index=True
    )

st.download_button(
    label="Download Forward Operational Dataset (CSV)",
    data=filtered_op_df.to_csv(index=False),
    file_name="maintenance_predictions_filtered.csv",
    mime="text/csv"
)
