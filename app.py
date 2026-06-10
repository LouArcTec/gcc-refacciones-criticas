import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Fleet Predictive Maintenance",
    page_icon="📊",
    layout="wide"
)

# =========================
# CSS ENTERPRISE STYLE
# =========================
st.markdown("""
<style>
.stApp {
    background-color: #F7F9FC;
}
.main-title {
    font-size: 34px;
    font-weight: 700;
    color: #0B1F33;
    margin-bottom: 0px;
}
.subtitle {
    font-size: 15px;
    color: #5B677A;
    margin-bottom: 25px;
}
.metric-card {
    background-color: white;
    padding: 22px;
    border-radius: 10px;
    border: 1px solid #E5EAF0;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.04);
}
.metric-label {
    font-size: 13px;
    color: #6B7280;
    font-weight: 600;
    letter-spacing: .04em;
}
.metric-value {
    font-size: 32px;
    font-weight: 700;
    color: #111827;
}
.section-title {
    font-size: 20px;
    font-weight: 700;
    color: #0B1F33;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# LOAD DATA
# =========================
df = pd.read_csv("purchase_table_all_parts.csv")

df["Truck ID"] = df["Truck ID"].astype(str)
df["Component Description"] = df["Component Description"].astype(str)
df["Purchase Status"] = df["Purchase Status"].astype(str)

# =========================
# SIDEBAR FILTERS
# =========================
st.sidebar.header("Filters")

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
    filtered_df = filtered_df[
        filtered_df["Truck ID"].str.contains(truck_filter, na=False)
    ]

if component_filter:
    filtered_df = filtered_df[
        filtered_df["Component Description"].str.contains(
            component_filter,
            case=False,
            na=False
        )
    ]

# =========================
# HEADER
# =========================
st.markdown(
    '<div class="main-title">Predictive Maintenance Analytics</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Fleet component health monitoring and purchase prioritization platform</div>',
    unsafe_allow_html=True
)

# =========================
# KPI CARDS
# =========================
urgent = len(filtered_df[filtered_df["Purchase Status"] == "URGENT"])
warning = len(filtered_df[filtered_df["Purchase Status"] == "WARNING"])
normal = len(filtered_df[filtered_df["Purchase Status"] == "NORMAL"])
total = len(filtered_df)

avg_health = filtered_df["Current Health (%)"].mean() if total > 0 else 0

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 6px solid #C62828;">
        <div class="metric-label">URGENT</div>
        <div class="metric-value">{urgent:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 6px solid #F9A825;">
        <div class="metric-label">WARNING</div>
        <div class="metric-value">{warning:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 6px solid #2E7D32;">
        <div class="metric-label">NORMAL</div>
        <div class="metric-value">{normal:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 6px solid #0F4C81;">
        <div class="metric-label">TOTAL RECORDS</div>
        <div class="metric-value">{total:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="metric-card" style="border-left: 6px solid #4B5563;">
        <div class="metric-label">AVG HEALTH</div>
        <div class="metric-value">{avg_health:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# =========================
# CHARTS
# =========================
chart_col1, chart_col2 = st.columns(2)

status_counts = (
    filtered_df["Purchase Status"]
    .value_counts()
    .reset_index()
)

status_counts.columns = ["Status", "Count"]

with chart_col1:
    fig_status = px.bar(
        status_counts,
        x="Count",
        y="Status",
        orientation="h",
        title="Purchase Status Overview",
        color="Status",
        color_discrete_map={
            "URGENT": "#C62828",
            "WARNING": "#F9A825",
            "NORMAL": "#2E7D32"
        },
        text="Count"
    )

    fig_status.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color="#111827"),
        title_font=dict(size=18),
        showlegend=False,
        height=380
    )

    st.plotly_chart(fig_status, use_container_width=True)

with chart_col2:
    fig_health = px.histogram(
        filtered_df,
        x="Current Health (%)",
        nbins=30,
        title="Current Health Distribution",
        color_discrete_sequence=["#0F4C81"]
    )

    fig_health.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color="#111827"),
        title_font=dict(size=18),
        height=380
    )

    st.plotly_chart(fig_health, use_container_width=True)

# =========================
# BUY IN 30 DAYS
# =========================
if "Buy in 30 Days?" in filtered_df.columns:
    buy_counts = (
        filtered_df["Buy in 30 Days?"]
        .value_counts()
        .reset_index()
    )

    buy_counts.columns = ["Decision", "Count"]

    st.markdown('<div class="section-title">30-Day Procurement Indicator</div>', unsafe_allow_html=True)

    fig_buy = px.bar(
        buy_counts,
        x="Decision",
        y="Count",
        title="Components Recommended for Purchase Within 30 Days",
        text="Count",
        color="Decision",
        color_discrete_sequence=["#C62828", "#4B5563"]
    )

    fig_buy.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False,
        height=320
    )

    st.plotly_chart(fig_buy, use_container_width=True)

# =========================
# TOP CRITICAL
# =========================
st.markdown('<div class="section-title">Most Critical Components</div>', unsafe_allow_html=True)

top_critical = (
    filtered_df
    .sort_values(by="Current Health (%)", ascending=True)
    .head(10)
)

critical_cols = [
    "Truck ID",
    "Component Category",
    "Component Description",
    "Material ID",
    "Current Health (%)",
    "Purchase Status",
    "Buy in 30 Days?"
]

critical_cols = [c for c in critical_cols if c in top_critical.columns]

st.dataframe(
    top_critical[critical_cols],
    use_container_width=True,
    hide_index=True
)

# =========================
# MAIN TABLE
# =========================
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

def style_rows(row):
    status = row.get("Purchase Status", "")

    if status == "URGENT":
        return ["background-color: #FDECEC; color: #7F1D1D"] * len(row)

    if status == "WARNING":
        return ["background-color: #FFF7E0; color: #78350F"] * len(row)

    if status == "NORMAL":
        return ["background-color: #F0FDF4; color: #14532D"] * len(row)

    return [""] * len(row)

st.dataframe(
    filtered_df[display_cols].style.apply(style_rows, axis=1),
    use_container_width=True,
    height=620,
    hide_index=True
)

# =========================
# DOWNLOAD
# =========================
st.download_button(
    label="Download filtered dataset",
    data=filtered_df.to_csv(index=False),
    file_name="maintenance_predictions_filtered.csv",
    mime="text/csv"
)