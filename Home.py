import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# -----------------------------
# Title + Subtitle
# -----------------------------
st.markdown(
    """
    <h1 style="font-size: 3rem; margin-bottom: -10px;">🏡 RHFI Dashboard</h1>
    <p style="font-size: 1.2rem; color: #555;">
        Regional Housing Financial Index — Insights, Trends, and Forecasts
    </p>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# -----------------------------
# Two-column Hero Section
# -----------------------------
col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown(
        """
        <div style="font-size: 1.1rem; line-height: 1.6;">
        Welcome to the <strong>Regional Housing Financial Index (RHFI)</strong> dashboard — 
        your interactive hub for exploring housing affordability, price dynamics, rental trends, 
        and long‑term financial signals across U.S. regions.
        <br><br>
        Use the sidebar to navigate through:
        <ul>
            <li>🗺️ Geographic Heatmap</li>
            <li>📈 Time-Series Trends</li>
            <li>🔁 Region Comparison</li>
            <li>📊 Indicator Breakdown</li>
            <li>🔮 Forecasting (Prophet)</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀 Start Exploring"):
        st.sidebar.success("Use the sidebar to navigate!")

with col2:
    st.image(
        "https://images.unsplash.com/photo-1560185127-6ed189bf02f4",
        use_column_width=True,
        caption="U.S. Housing Market Landscape"
    )

st.markdown("---")

# -----------------------------
# Metrics Row
# -----------------------------
st.subheader("📌 Quick Overview")

df = pd.read_csv("data/final_real_estate_dataset.csv")
df = df.drop_duplicates().sort_values(["RegionName", "Year"])

m1, m2, m3 = st.columns(3)
m1.metric("Regions Tracked", df["RegionName"].nunique())
m2.metric("Years of Data", df["Year"].nunique())
m3.metric("Indicators", "7")

# -----------------------------
# About Section
# -----------------------------
with st.expander("ℹ️ About the RHFI Dataset"):
    st.markdown(
        """
        The RHFI dataset integrates multiple sources including:
        - Zillow Home Value Index (ZHVI)
        - Zillow Rent Index (ZRI)
        - U.S. Census Income Data
        - Employment & Labor Statistics  
        
        Derived indicators include:
        - Price-to-Income Ratio  
        - Price Growth  
        - Rent Growth  
        - Inventory Change  
        
        These metrics help quantify affordability, market pressure, and long‑term housing risk.
        """
    )
