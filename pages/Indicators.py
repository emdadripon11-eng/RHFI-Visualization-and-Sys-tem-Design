import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="Indicators Dashboard", layout="wide")

# =====================================================
# 🌌 GLASSMORPHISM UI (HOME.PY STYLE)
# =====================================================
st.markdown("""
<style>

/* Background */
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

/* Tabs */
div[data-baseweb="tab-list"] {
    gap: 10px;
}

button[data-baseweb="tab"] {
    background: rgba(255,255,255,0.05);
    border-radius: 10px;
    padding: 8px 14px;
    border: 1px solid rgba(255,255,255,0.08);
}

button[aria-selected="true"] {
    background: rgba(99,102,241,0.25) !important;
    border: 1px solid rgba(99,102,241,0.6);
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

    # Ensure correct format
    if "RegionName" not in df.columns:
        st.error("Dataset must contain 'RegionName' column")
        st.stop()

    df["RegionName"] = df["RegionName"].astype(str)
    df = df.drop_duplicates().sort_values(["RegionName", "Year"])

    return df

df = load_data()

# =====================================================
# TITLE
# =====================================================
st.title("📊 Zillow-Style Indicator Intelligence Dashboard")
st.caption("Glass UI • Multi-Metric Analytics • Trend Intelligence Engine")

# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.header("Controls")

region = st.sidebar.selectbox("Select Region", df["RegionName"].unique())

indicators = [
    "Home_price", "Rent", "Income",
    "price_income_ratio", "price_growth",
    "rent_growth", "inventory_change"
]

selected_indicators = st.sidebar.multiselect(
    "Select Indicators",
    indicators,
    default=indicators[:3]
)

filtered = df[df["RegionName"] == region].copy()

# =====================================================
# SAFETY CHECK
# =====================================================
if len(selected_indicators) == 0:
    st.warning("Please select at least one indicator.")
    st.stop()

# =====================================================
# SUMMARY STATS
# =====================================================
st.subheader(f"📌 Key Statistics – {region}")

summary = filtered[selected_indicators].describe().T

summary["trend_slope"] = filtered[selected_indicators].apply(
    lambda x: np.polyfit(range(len(x.dropna())), x.dropna(), 1)[0]
)

st.dataframe(summary.style.format("{:.2f}"))

# =====================================================
# TREND INTELLIGENCE ENGINE
# =====================================================
st.subheader("🧠 Trend Intelligence Engine")

trend_rows = []

for col in selected_indicators:
    series = filtered[col].dropna()

    if len(series) < 3:
        continue

    slope = np.polyfit(range(len(series)), series, 1)[0]
    volatility = series.pct_change().std()

    direction = "📈 Uptrend" if slope > 0 else "📉 Downtrend"

    if volatility > 0.12:
        stability = "⚠️ Highly Volatile"
    elif volatility > 0.05:
        stability = "🟡 Moderate"
    else:
        stability = "🟢 Stable"

    trend_rows.append([
        col,
        direction,
        stability,
        round(abs(slope), 3)
    ])

trend_df = pd.DataFrame(
    trend_rows,
    columns=["Indicator", "Trend", "Stability", "Strength"]
)

st.dataframe(trend_df.sort_values("Strength", ascending=False))

# =====================================================
# TABS
# =====================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Trends",
    "📦 Distribution",
    "📈 YoY Change",
    "🧭 Radar Profile",
    "🔗 Correlation"
])

# =====================================================
# TAB 1: TRENDS
# =====================================================
with tab1:
    fig = px.line(
        filtered,
        x="Year",
        y=selected_indicators,
        markers=True,
        title="Multi-Indicator Trends"
    )
    fig.update_layout(template="plotly_dark", height=500)
    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# TAB 2: DISTRIBUTION
# =====================================================
with tab2:
    melted = filtered.melt(id_vars=["Year"], value_vars=selected_indicators)

    fig2 = px.violin(
        melted,
        x="variable",
        y="value",
        box=True,
        color="variable",
        title="Indicator Distribution"
    )

    fig2.update_layout(template="plotly_dark", height=500)
    st.plotly_chart(fig2, use_container_width=True)

# =====================================================
# TAB 3: YOY CHANGE
# =====================================================
with tab3:
    yoy_df = filtered.copy()

    for col in selected_indicators:
        yoy_df[col + "_YoY"] = yoy_df[col].pct_change() * 100

    yoy_cols = [c for c in yoy_df.columns if "_YoY" in c]

    yoy_df[yoy_cols] = yoy_df[yoy_cols].replace([np.inf, -np.inf], np.nan)

    fig3 = px.line(
        yoy_df,
        x="Year",
        y=yoy_cols,
        markers=True,
        title="Year-over-Year Change"
    )

    fig3.update_layout(template="plotly_dark", height=500)
    st.plotly_chart(fig3, use_container_width=True)

# =====================================================
# TAB 4: RADAR PROFILE
# =====================================================
with tab4:
    latest = filtered.tail(1)[selected_indicators]

    min_vals = filtered[selected_indicators].min()
    max_vals = filtered[selected_indicators].max()

    radar = (latest - min_vals) / (max_vals - min_vals + 1e-9)

    fig4 = go.Figure()

    fig4.add_trace(go.Scatterpolar(
        r=radar.values.flatten(),
        theta=[c.replace("_", " ").title() for c in selected_indicators],
        fill="toself",
        name=region
    ))

    fig4.update_layout(
        template="plotly_dark",
        title="Normalized Indicator Profile",
        polar=dict(radialaxis=dict(range=[0, 1]))
    )

    st.plotly_chart(fig4, use_container_width=True)

# =====================================================
# TAB 5: CORRELATION
# =====================================================
with tab5:
    corr = filtered[selected_indicators].corr()

    fig5 = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale="RdBu_r",
        title="Correlation Matrix"
    )

    fig5.update_layout(template="plotly_dark", height=500)

    st.plotly_chart(fig5, use_container_width=True)