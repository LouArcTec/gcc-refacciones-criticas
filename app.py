import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Fleet Health Intelligence",
    page_icon="📊",
    layout="wide"
)

df = pd.read_csv("purchase_table_all_parts.csv")

df["Truck ID"] = df["Truck ID"].astype(str)
df["Component Description"] = df["Component Description"].astype(str)
df["Purchase Status"] = df["Purchase Status"].astype(str)

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

st.sidebar.title("Fleet Control Panel")
st.sidebar.caption("Filter operational risk and component health")

status_filter = st.sidebar.multiselect(
    "Purchase Status",
    options=["URGENT", "WARNING", "NORMAL"],
    default=["URGENT", "WARNING", "NORMAL"]
)

truck_filter = st.sidebar.text_input("Truck ID")
component_filter = st.sidebar.text_input("Component Description")

category_options = sorted(df["Component Category"].dropna().unique())

category_filter = st.sidebar.multiselect(
    "Component Category",
    options=category_options,
    default=category_options
)

health_range = st.sidebar.slider(
    "Current Health (%)",
    min_value=float(df["Current Health (%)"].min()),
    max_value=float(df["Current Health (%)"].max()),
    value=(
        float(df["Current Health (%)"].min()),
        float(df["Current Health (%)"].max())
    )
)

filtered_df = df.copy()

filtered_df = filtered_df[
    filtered_df["Purchase Status"].isin(status_filter)
]

filtered_df = filtered_df[
    filtered_df["Component Category"].isin(category_filter)
]

filtered_df = filtered_df[
    filtered_df["Current Health (%)"].between(
        health_range[0],
        health_range[1]
    )
]

if truck_filter:
    if truck_filter in df["Truck ID"].values:
        filtered_df = filtered_df[
            filtered_df["Truck ID"] == truck_filter
        ]
    else:
        st.sidebar.error("Truck ID not found")
        filtered_df = filtered_df.iloc[0:0]

if component_filter:
    filtered_df = filtered_df[
        filtered_df["Component Description"].str.contains(
            component_filter,
            case=False,
            na=False
        )
    ]

st.markdown("""
<div class="hero">
    <div class="hero-title">Fleet Health Intelligence Platform</div>
    <div class="hero-subtitle">
        Predictive maintenance analytics for component health monitoring,
        procurement prioritization and fleet risk management.
    </div>
</div>
""", unsafe_allow_html=True)

urgent = len(filtered_df[filtered_df["Purchase Status"] == "URGENT"])
warning = len(filtered_df[filtered_df["Purchase Status"] == "WARNING"])
normal = len(filtered_df[filtered_df["Purchase Status"] == "NORMAL"])
total = len(filtered_df)
avg_health = filtered_df["Current Health (%)"].mean() if total > 0 else 0
fleet_assets = filtered_df["Truck ID"].nunique() if total > 0 else 0
urgent_assets = filtered_df[filtered_df["Purchase Status"] == "URGENT"]["Truck ID"].nunique() if total > 0 else 0

col1, col2, col3, col4, col5 = st.columns(5)

cards = [
    ("Critical Components", urgent, "Require immediate review", "#C62828"),
    ("Warning Components", warning, "Monitor procurement window", "#F9A825"),
    ("Normal Components", normal, "No immediate action", "#2E7D32"),
    ("Fleet Assets", fleet_assets, "Unique trucks in view", "#0F4C81"),
    ("Avg. Health", f"{avg_health:.1f}%", "Mean component health", "#4B5563"),
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

st.markdown('<div class="section-title">Executive Overview</div>', unsafe_allow_html=True)

summary_col1, summary_col2, summary_col3 = st.columns(3)

with summary_col1:
    st.markdown(f"""
    <div class="info-card">
        <div class="card-small-label">Operational Risk</div>
        <div class="card-title">{urgent_assets:,} trucks with urgent components</div>
        <div class="card-text">These assets include at least one component classified as critical under the current health threshold.</div>
    </div>
    """, unsafe_allow_html=True)

with summary_col2:
    buy_30 = 0
    if "Buy in 30 Days?" in filtered_df.columns:
        buy_30 = len(
            filtered_df[
                filtered_df["Buy in 30 Days?"].astype(str).str.upper().isin(["YES", "TRUE", "1"])
            ]
        )

    st.markdown(f"""
    <div class="info-card">
        <div class="card-small-label">Procurement Signal</div>
        <div class="card-title">{buy_30:,} components flagged for 30-day purchase</div>
        <div class="card-text">This indicator supports short-term inventory planning and purchase prioritization.</div>
    </div>
    """, unsafe_allow_html=True)

with summary_col3:
    low_health = len(filtered_df[filtered_df["Current Health (%)"] <= 20])

    st.markdown(f"""
    <div class="info-card">
        <div class="card-small-label">Health Threshold</div>
        <div class="card-title">{low_health:,} components below 20% health</div>
        <div class="card-text">Low-health parts are prioritized for operational review and replacement planning.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="section-title">Component Category Insights</div>', unsafe_allow_html=True)

if len(filtered_df) > 0:
    category_health = (
        filtered_df
        .groupby("Component Category")
        .agg(
            Avg_Health=("Current Health (%)", "mean"),
            Components=("Component Description", "count")
        )
        .reset_index()
        .sort_values("Avg_Health", ascending=True)
    )

    st.bar_chart(
        category_health.set_index("Component Category")["Avg_Health"],
        use_container_width=True
    )
else:
    st.info("No data available under the current filters.")

st.markdown('<div class="section-title">Priority Procurement Watchlist</div>', unsafe_allow_html=True)

top_critical = (
    filtered_df
    .sort_values(by="Current Health (%)", ascending=True)
    .head(18)
)

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
            <div class="card-small-label">Truck {row["Truck ID"]}</div>
            <div class="card-title">{component_name}</div>
            <div class="card-text">Health: <b>{row["Current Health (%)"]:.1f}%</b></div>
            <div class="card-text">Age: <b>{row["Calculated Age (Days)"]:,} days</b></div>
            <br>
            <span class="{status_class}">{row["Purchase Status"]}</span>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<div class="section-title">Procurement Planning Horizon</div>', unsafe_allow_html=True)

planning_cols = [
    "Truck ID",
    "Component Category",
    "Installation Date",
    "Component Description",
    "Material ID",
    "Calculated Age (Days)",
    "Current Health (%)",
    "Purchase Status",
    "Buy in 30 Days?"
]

planning_cols = [c for c in planning_cols if c in filtered_df.columns]

month1 = filtered_df[
    filtered_df["Current Health (%)"] <= 20
]

month2 = filtered_df[
    (filtered_df["Current Health (%)"] > 20)
    &
    (filtered_df["Current Health (%)"] <= 40)
]

month3 = filtered_df[
    (filtered_df["Current Health (%)"] > 40)
    &
    (filtered_df["Current Health (%)"] <= 60)
]

month4 = filtered_df[
    (filtered_df["Current Health (%)"] > 60)
    &
    (filtered_df["Current Health (%)"] <= 80)
]

tab1, tab2, tab3, tab4 = st.tabs([
    "Month 1: Immediate Purchase",
    "Month 2: Planned Purchase",
    "Month 3: Preventive Planning",
    "Month 4: Monitoring Window"
])

with tab1:
    st.write(f"Components in this horizon: {len(month1):,}")
    st.dataframe(
        month1.sort_values(by="Current Health (%)")[planning_cols],
        use_container_width=True,
        hide_index=True
    )

with tab2:
    st.write(f"Components in this horizon: {len(month2):,}")
    st.dataframe(
        month2.sort_values(by="Current Health (%)")[planning_cols],
        use_container_width=True,
        hide_index=True
    )

with tab3:
    st.write(f"Components in this horizon: {len(month3):,}")
    st.dataframe(
        month3.sort_values(by="Current Health (%)")[planning_cols],
        use_container_width=True,
        hide_index=True
    )

with tab4:
    st.write(f"Components in this horizon: {len(month4):,}")
    st.dataframe(
        month4.sort_values(by="Current Health (%)")[planning_cols],
        use_container_width=True,
        hide_index=True
    )

st.markdown('<div class="section-title">Truck Lookup</div>', unsafe_allow_html=True)

lookup_truck = st.text_input(
    "Enter an exact Truck ID for detailed component review",
    key="lookup_truck"
)

if lookup_truck:
    truck_df = df[df["Truck ID"] == lookup_truck]

    if len(truck_df) > 0:
        truck_avg_health = truck_df["Current Health (%)"].mean()
        truck_urgent = len(truck_df[truck_df["Purchase Status"] == "URGENT"])

        tcol1, tcol2, tcol3 = st.columns(3)

        tcol1.metric("Components", f"{len(truck_df):,}")
        tcol2.metric("Urgent", f"{truck_urgent:,}")
        tcol3.metric("Average Health", f"{truck_avg_health:.1f}%")

        truck_cols = [
            "Component Category",
            "Installation Date",
            "Component Description",
            "Material ID",
            "Current Health (%)",
            "Purchase Status",
            "Buy in 30 Days?"
        ]

        truck_cols = [c for c in truck_cols if c in truck_df.columns]

        st.dataframe(
            truck_df[truck_cols],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("No records found for this exact Truck ID.")

st.markdown('<div class="section-title">Fleet Component Inventory</div>', unsafe_allow_html=True)

display_cols = [
    "Truck ID",
    "Component Category",
    "Installation Date",
    "Component Description",
    "Material ID",
    "Calculated Age (Days)",
    "Current Health (%)",
    "30-Day Health Outlook",
    "Purchase Status",
    "Buy in 30 Days?"
]

display_cols = [c for c in display_cols if c in filtered_df.columns]

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

with st.expander("View full filtered inventory table", expanded=False):
    st.dataframe(
        filtered_df[display_cols].style.apply(highlight_columns, axis=1),
        use_container_width=True,
        height=620,
        hide_index=True
    )

st.download_button(
    label="Download filtered dataset",
    data=filtered_df.to_csv(index=False),
    file_name="maintenance_predictions_filtered.csv",
    mime="text/csv"
)
