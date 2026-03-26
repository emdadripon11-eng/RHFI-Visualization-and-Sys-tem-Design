import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load data
df = pd.read_csv("data/final_dataset.csv")
df = df.drop_duplicates().sort_values(["RegionName", "Year"])

st.title("📈 Advanced Time-Series Explorer")

# Sidebar controls
st.sidebar.header("Controls")
region = st.sidebar.selectbox("Select Region", df['RegionName'].unique())
metrics = ["Home_price", "Rent", "Income", "price_income_ratio",
           "price_growth", "rent_growth", "inventory_change"]

metric = st.sidebar.selectbox("Select Metric", metrics)
smooth_window = st.sidebar.slider("Smoothing Window (years)", 1, 5, 3)

filtered = df[df['RegionName'] == region].copy()

# Compute smoothing
filtered["Smoothed"] = filtered[metric].rolling(smooth_window).mean()

# Compute YoY change
filtered["YoY_change"] = filtered[metric].pct_change() * 100

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Metric Trend",
    "📉 YoY Change",
    "📈 Smoothed Trend",
    "🔀 Dual-Axis Compare"
])

# ---------------- TAB 1: Metric Trend ----------------
with tab1:
    fig = px.line(
        filtered, x="Year", y=metric, markers=True,
        title=f"{metric.replace('_',' ').title()} Trend – {region}"
    )
    fig.update_traces(line=dict(width=3))
    st.plotly_chart(fig, use_container_width=True)

# ---------------- TAB 2: YoY Change ----------------
with tab2:
    fig2 = px.bar(
        filtered, x="Year", y="YoY_change",
        title=f"Year-over-Year % Change – {metric.replace('_',' ').title()} – {region}",
        color="YoY_change",
        color_continuous_scale="RdBu"
    )
    st.plotly_chart(fig2, use_container_width=True)

# ---------------- TAB 3: Smoothed Trend ----------------
with tab3:
    fig3 = px.line(
        filtered, x="Year", y="Smoothed",
        title=f"Smoothed {metric.replace('_',' ').title()} ({smooth_window}-year MA) – {region}"
    )
    fig3.update_traces(line=dict(width=3, dash="dash"))
    st.plotly_chart(fig3, use_container_width=True)

# ---------------- TAB 4: Dual-Axis Compare ----------------
with tab4:
    compare_metric = st.selectbox("Compare Against", metrics, index=1)

    fig4 = go.Figure()

    fig4.add_trace(go.Scatter(
        x=filtered["Year"], y=filtered[metric],
        name=metric.replace("_"," ").title(),
        mode="lines+markers", line=dict(width=3)
    ))

    fig4.add_trace(go.Scatter(
        x=filtered["Year"], y=filtered[compare_metric],
        name=compare_metric.replace("_"," ").title(),
        mode="lines+markers", line=dict(width=3, dash="dash"),
        yaxis="y2"
    ))

    fig4.update_layout(
        title=f"Dual-Axis Comparison – {region}",
        yaxis=dict(title=metric.replace("_"," ").title()),
        yaxis2=dict(title=compare_metric.replace("_"," ").title(),
                    overlaying="y", side="right")
    )

    st.plotly_chart(fig4, use_container_width=True)

# ---------------- Download Button ----------------
st.download_button(
    "⬇️ Download Region Data as CSV",
    filtered.to_csv(index=False),
    file_name=f"{region}_timeseries.csv",
    mime="text/csv"
)
