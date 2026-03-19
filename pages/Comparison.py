import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load data
df = pd.read_csv("data/final_real_estate_dataset.csv")
df = df.drop_duplicates().sort_values(["RegionName", "Year"])

st.title("🔁 Advanced Region Comparison Tool")

# Sidebar
st.sidebar.header("Comparison Settings")
region1 = st.sidebar.selectbox("Region A", df['RegionName'].unique())
region2 = st.sidebar.selectbox("Region B", df['RegionName'].unique())

metrics = [
    "Home_price", "Rent", "Income", "price_income_ratio",
    "price_growth", "rent_growth", "inventory_change"
]

metric = st.sidebar.selectbox("Metric to Compare", metrics)

subset = df[df['RegionName'].isin([region1, region2])].copy()

# Latest values for summary cards
latest = subset.groupby("RegionName").tail(1).set_index("RegionName")

# Summary cards
colA, colB = st.columns(2)
colA.metric(f"{region1} – Latest {metric}", f"{latest.loc[region1, metric]:,.2f}")
colB.metric(f"{region2} – Latest {metric}", f"{latest.loc[region2, metric]:,.2f}")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Trend Comparison",
    "📉 YoY Change",
    "📊 Distribution",
    "🧭 Radar Chart",
    "🔀 Dual-Axis Compare"
])

# ---------------- TAB 1: Trend Comparison ----------------
with tab1:
    fig = px.line(
        subset, x="Year", y=metric, color="RegionName", markers=True,
        title=f"{metric.replace('_',' ').title()} Trend"
    )
    fig.update_traces(line=dict(width=3))
    st.plotly_chart(fig, use_container_width=True)

# ---------------- TAB 2: YoY Change ----------------
with tab2:
    subset["YoY"] = subset.groupby("RegionName")[metric].pct_change() * 100
    fig2 = px.bar(
        subset, x="Year", y="YoY", color="RegionName",
        title=f"Year-over-Year % Change – {metric.replace('_',' ').title()}",
        barmode="group"
    )
    st.plotly_chart(fig2, use_container_width=True)

# ---------------- TAB 3: Distribution ----------------
with tab3:
    fig3 = px.violin(
        subset, y=metric, x="RegionName", box=True, points="all",
        title=f"Distribution of {metric.replace('_',' ').title()}"
    )
    st.plotly_chart(fig3, use_container_width=True)

# ---------------- TAB 4: Radar Chart ----------------
with tab4:
    radar_vars = ["price_income_ratio", "price_growth", "rent_growth", "inventory_change"]
    radar_labels = ["Price/Income", "Price Growth", "Rent Growth", "Inventory Change"]

    # Normalize values 0–1 for fair comparison
    radar_df = latest[radar_vars].copy()
    radar_df = (radar_df - radar_df.min()) / (radar_df.max() - radar_df.min())

    fig4 = go.Figure()

    for region in [region1, region2]:
        fig4.add_trace(go.Scatterpolar(
            r=radar_df.loc[region].values,
            theta=radar_labels,
            fill='toself',
            name=region
        ))

    fig4.update_layout(title="Indicator Radar Comparison")
    st.plotly_chart(fig4, use_container_width=True)

# ---------------- TAB 5: Dual-Axis Compare ----------------
with tab5:
    compare_metric = st.selectbox("Compare Against", metrics, index=1)

    fig5 = go.Figure()

    # Region A
    dfA = subset[subset["RegionName"] == region1]
    fig5.add_trace(go.Scatter(
        x=dfA["Year"], y=dfA[metric],
        name=f"{region1} – {metric}",
        mode="lines+markers", line=dict(width=3)
    ))
    fig5.add_trace(go.Scatter(
        x=dfA["Year"], y=dfA[compare_metric],
        name=f"{region1} – {compare_metric}",
        mode="lines+markers", line=dict(width=3, dash="dash"),
        yaxis="y2"
    ))

    # Region B
    dfB = subset[subset["RegionName"] == region2]
    fig5.add_trace(go.Scatter(
        x=dfB["Year"], y=dfB[metric],
        name=f"{region2} – {metric}",
        mode="lines+markers", line=dict(width=3)
    ))
    fig5.add_trace(go.Scatter(
        x=dfB["Year"], y=dfB[compare_metric],
        name=f"{region2} – {compare_metric}",
        mode="lines+markers", line=dict(width=3, dash="dash"),
        yaxis="y2"
    ))

    fig5.update_layout(
        title="Dual-Axis Metric Comparison",
        yaxis=dict(title=metric),
        yaxis2=dict(title=compare_metric, overlaying="y", side="right")
    )

    st.plotly_chart(fig5, use_container_width=True)

# ---------------- Download Button ----------------
st.download_button(
    "⬇️ Download Comparison Data",
    subset.to_csv(index=False),
    file_name=f"{region1}_vs_{region2}_comparison.csv",
    mime="text/csv"
)
