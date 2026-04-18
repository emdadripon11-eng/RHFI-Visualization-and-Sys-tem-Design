import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="Time-Series Explorer", layout="wide")

# =====================================================
# 🌌 GLASS UI (HOME STYLE)
# =====================================================
st.markdown("""
<style>

.stApp {
    background: radial-gradient(circle at top, #0b1220 0%, #050814 60%, #02040a 100%);
    color: #e5e7eb;
}

/* Glass cards */
div[data-testid="stDataFrame"],
div[data-testid="stPlotlyChart"],
div[data-testid="stMetric"],
div[data-testid="stTabs"] {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(14px);
    border-radius: 16px;
    padding: 16px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 8px 30px rgba(0,0,0,0.3);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(10, 15, 30, 0.6);
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255,255,255,0.08);
}

/* Headings */
h1, h2, h3 {
    color: #f8fafc !important;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# LOAD DATA
# =====================================================
@st.cache_data
def load_data():
    df = pd.read_csv("data/final_dataset.csv")
    df.columns = df.columns.str.strip()

    if "RegionName" not in df.columns:
        st.error("Dataset must contain 'RegionName'")
        st.stop()

    df["RegionName"] = df["RegionName"].astype(str)
    df = df.drop_duplicates().sort_values(["RegionName", "Year"])

    return df

df = load_data()

# =====================================================
# TITLE
# =====================================================
st.title("📈 Zillow-Style Time-Series Intelligence Explorer")
st.caption("Glass UI • Trend Engine • Volatility Analysis • Forecast Insights")

# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.header("Controls")

region = st.sidebar.selectbox("Select Region", df["RegionName"].unique())

metrics = [
    "Home_price", "Rent", "Income",
    "price_income_ratio",
    "price_growth",
    "rent_growth",
    "inventory_change"
]

metric = st.sidebar.selectbox("Select Metric", metrics)
smooth_window = st.sidebar.slider("Smoothing Window", 2, 7, 3)

filtered = df[df["RegionName"] == region].copy().sort_values("Year")

# =====================================================
# SAFE CALCULATIONS
# =====================================================
filtered["YoY_change"] = filtered[metric].pct_change() * 100
filtered["YoY_change"] = filtered["YoY_change"].replace([np.inf, -np.inf], np.nan)

filtered["Smoothed"] = filtered[metric].rolling(
    smooth_window, min_periods=1
).mean()

series = filtered[metric].dropna()

# =====================================================
# TREND INTELLIGENCE ENGINE
# =====================================================
st.subheader("🧠 Trend Intelligence Engine")

if len(series) > 2:
    slope = np.polyfit(range(len(series)), series, 1)[0]
else:
    slope = 0

volatility = series.pct_change().std()

trend = "📈 Upward Trend" if slope > 0 else "📉 Downward Trend"

if volatility > 0.15:
    regime = "🔴 Highly Volatile"
elif volatility > 0.08:
    regime = "🟡 Moderate"
else:
    regime = "🟢 Stable"

col1, col2, col3 = st.columns(3)
col1.metric("Trend", trend)
col2.metric("Volatility", f"{volatility:.3f}")
col3.metric("Market Regime", regime)

# =====================================================
# PEAK / LOW ANALYSIS
# =====================================================
max_row = filtered.loc[filtered[metric].idxmax()]
min_row = filtered.loc[filtered[metric].idxmin()]

st.write(f"📊 Peak Year: **{int(max_row['Year'])} → {max_row[metric]:.2f}**")
st.write(f"📉 Lowest Year: **{int(min_row['Year'])} → {min_row[metric]:.2f}**")

# =====================================================
# TABS
# =====================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Raw Trend",
    "📉 YoY Change",
    "📈 Smoothed + Band",
    "🔀 Dual Comparison"
])

# =====================================================
# TAB 1
# =====================================================
with tab1:
    fig = px.line(
        filtered,
        x="Year",
        y=metric,
        markers=True,
        title=f"{metric.replace('_',' ').title()} Trend – {region}"
    )
    fig.update_layout(template="plotly_dark", height=500)
    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# TAB 2
# =====================================================
with tab2:
    fig2 = px.bar(
        filtered,
        x="Year",
        y="YoY_change",
        color="YoY_change",
        color_continuous_scale="RdBu",
        title="Year-over-Year Change"
    )
    fig2.update_layout(template="plotly_dark", height=500)
    st.plotly_chart(fig2, use_container_width=True)

# =====================================================
# TAB 3 (SMOOTH + CONFIDENCE BAND)
# =====================================================
with tab3:
    std = series.pct_change().std()

    upper = filtered["Smoothed"] * (1 + std)
    lower = filtered["Smoothed"] * (1 - std)

    fig3 = go.Figure()

    fig3.add_trace(go.Scatter(
        x=filtered["Year"],
        y=filtered["Smoothed"],
        mode="lines",
        name="Smoothed",
        line=dict(width=3)
    ))

    fig3.add_trace(go.Scatter(
        x=filtered["Year"],
        y=upper,
        line=dict(width=0),
        showlegend=False
    ))

    fig3.add_trace(go.Scatter(
        x=filtered["Year"],
        y=lower,
        fill="tonexty",
        name="Confidence Band",
        opacity=0.25
    ))

    fig3.update_layout(
        template="plotly_dark",
        title="Smoothed Trend with Confidence Band"
    )

    st.plotly_chart(fig3, use_container_width=True)

# =====================================================
# TAB 4 (DUAL AXIS)
# =====================================================
with tab4:
    compare_metric = st.selectbox("Compare Against", metrics, index=1)

    fig4 = go.Figure()

    fig4.add_trace(go.Scatter(
        x=filtered["Year"],
        y=filtered[metric],
        name=metric,
        mode="lines+markers"
    ))

    fig4.add_trace(go.Scatter(
        x=filtered["Year"],
        y=filtered[compare_metric],
        name=compare_metric,
        mode="lines",
        line=dict(dash="dash"),
        yaxis="y2"
    ))

    fig4.update_layout(
        template="plotly_dark",
        title="Dual Metric Comparison",
        yaxis=dict(title=metric),
        yaxis2=dict(title=compare_metric, overlaying="y", side="right"),
        height=500
    )

    st.plotly_chart(fig4, use_container_width=True)

# =====================================================
# DOWNLOAD
# =====================================================
st.download_button(
    "⬇️ Download Data",
    filtered.to_csv(index=False),
    file_name=f"{region}_timeseries.csv",
    mime="text/csv"
)