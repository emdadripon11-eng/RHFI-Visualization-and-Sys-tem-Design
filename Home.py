import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# =============================
# GLOBAL STYLE (PROFESSIONAL)
# =============================
st.markdown("""
<style>

/* App background */
.stApp {
    background: radial-gradient(circle at top, #0b1220 0%, #050814 100%);
    color: #e5e7eb;
}

/* Remove extra padding */
.block-container {
    padding: 2rem 3rem;
}

/* Title */
h1 {
    font-size: 3rem !important;
    font-weight: 800;
    color: white;
}

/* Subtitle */
p {
    color: #94a3b8;
    font-size: 1.05rem;
}

/* Card style */
.card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    padding: 18px;
    border-radius: 16px;
}

/* Metrics */
div[data-testid="metric-container"] {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    padding: 15px;
    border-radius: 14px;
}

/* Button */
.stButton button {
    background: linear-gradient(135deg, #4f46e5, #3b82f6);
    border-radius: 10px;
    color: white;
    border: none;
    padding: 0.5em 1.2em;
    font-weight: 600;
}

/* Image */
img {
    border-radius: 18px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.4);
}

</style>
""", unsafe_allow_html=True)

# =============================
# HERO SECTION
# =============================
st.markdown("""
<div style="
    background: linear-gradient(135deg, rgba(15,23,42,0.9), rgba(3,7,18,0.95)),
                url('https://images.unsplash.com/photo-1501183638710-841dd1904471?auto=format&fit=crop&w=1600&q=80');
    background-size: cover;
    background-position: center;
    padding: 4rem;
    border-radius: 22px;
    margin-bottom: 2rem;
">

<h1>🏡 RHFI Intelligence Dashboard</h1>

<p style="max-width:650px;">
Regional Housing Financial Index — A unified system to analyze housing affordability,
market pressure, and long-term financial risk across U.S. regions.
</p>

</div>
""", unsafe_allow_html=True)

# =============================
# HERO CONTENT (2-COLUMN)
# =============================
col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown("""
    <div class="card">
    
    ### 📊 What this dashboard provides

    - 📈 Price & Rent trend analysis  
    - 🗺️ Regional housing risk comparison  
    - 📉 Affordability & growth indicators  
    - 🔮 Forecasting of housing signals  

    <br>
    Designed to transform raw housing data into **decision-ready insights**.

    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀 Start Exploring"):
        st.success("Use the sidebar to navigate through dashboard sections")

with col2:
    st.image(
        "https://images.unsplash.com/photo-1560185127-6ed189bf02f4?auto=format&fit=crop&w=1400&q=80",
        use_container_width=True
    )

# =============================
# DATA LOAD
# =============================
df = pd.read_csv("data/final_dataset.csv")
df = df.drop_duplicates().sort_values(["RegionName", "Year"])

# =============================
# METRICS SECTION
# =============================
st.markdown("## 📌 Quick Overview")

m1, m2, m3, m4 = st.columns(4)

m1.metric("Regions", df["RegionName"].nunique())
m2.metric("Years", df["Year"].nunique())
m3.metric("Records", len(df))
m4.metric("Indicators", "7 Key Metrics")

st.markdown("---")

# =============================
# INSIGHT STRIP (NEW - HIGH IMPACT)
# =============================
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="card">
    <b>📉 Trend</b><br>
    RHFI shows gradual stabilization across most regions.
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="card">
    <b>⚡ Shock</b><br>
    2020 marks a structural housing market disruption.
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="card">
    <b>💰 Affordability</b><br>
    Price-to-rent ratios indicate improving balance.
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# =============================
# ABOUT SECTION
# =============================
with st.expander("ℹ️ About the RHFI Dataset"):
    st.markdown("""
    The RHFI dataset integrates multiple economic data sources:

    - Zillow Home Value Index (ZHVI)  
    - Zillow Rent Index (ZRI)  
    - U.S. Census income data  
    - Labor market indicators  

    **Derived Indicators:**
    - Price-to-Income Ratio  
    - Price Growth  
    - Rent Growth  
    - Inventory Change  

    **Objective:**  
    Quantify housing affordability, market pressure, and regional financial risk.
    """)