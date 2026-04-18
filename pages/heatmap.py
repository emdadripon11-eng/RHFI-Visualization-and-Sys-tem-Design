import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------
st.set_page_config(page_title="Zillow Pro Dashboard", layout="wide")

# ----------------------------------------------------
# ZILLOW STYLE UI
# ----------------------------------------------------
st.markdown("""
<style>

.stApp {
    background: radial-gradient(circle at top, #0b1220 0%, #050814 100%);
    color: white;
}

.block-container {
    padding: 2rem;
}

h1, h2, h3 {
    color: #f8fafc;
}

/* card style */
div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 10px;
}

</style>
""", unsafe_allow_html=True)


# ----------------------------------------------------
# LOAD DATA
# ----------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/map_dataset.csv")
    df.columns = df.columns.str.strip()
    return df

df = load_data()


# ----------------------------------------------------
# SAFETY CHECK
# ----------------------------------------------------
df["State"] = df["State"].astype(str)
df = df[df["State"].str.len() == 2]

years = sorted(df["Year"].unique())


# ----------------------------------------------------
# TITLE
# ----------------------------------------------------
st.title("🏡 Zillow Pro Analytics Dashboard")
st.caption("Affordability • Prices • Rent • Income • Heatmap Insights")


# ----------------------------------------------------
# SIDEBAR
# ----------------------------------------------------
year = st.sidebar.slider("Select Year", min(years), max(years), max(years))

metric = st.sidebar.selectbox(
    "Base Metric",
    ["Home_price", "Rent", "Income"]
)


# ----------------------------------------------------
# FILTER DATA
# ----------------------------------------------------
df_year = df[df["Year"] == year].copy()

if df_year.empty:
    st.stop()


# ----------------------------------------------------
# 🧠 ZILLOW AFFORDABILITY INDEX (NEW CORE METRIC)
# ----------------------------------------------------
df_year["Affordability_Index"] = (
                                         df_year["Income"] / (df_year["Home_price"] + 1e-9)
                                 ) * 1000

df_year["Rent_Burden"] = (
                                 df_year["Rent"] / (df_year["Income"] + 1e-9)
                         ) * 100


# ----------------------------------------------------
# 🇺🇸 HEATMAP (ZILLOW STYLE)
# ----------------------------------------------------
st.subheader("🇺🇸 US Housing Heatmap")

color_metric = st.selectbox(
    "Heatmap Metric",
    ["Home_price", "Rent", "Income", "Affordability_Index", "Rent_Burden"]
)

fig = px.choropleth(
    df_year,
    locations="State",
    locationmode="USA-states",
    color=color_metric,
    scope="usa",
    color_continuous_scale="Viridis",
    hover_name="State",
    hover_data={
        "Home_price": ":,.0f",
        "Rent": ":,.0f",
        "Income": ":,.0f",
        "Affordability_Index": ":.2f",
        "Rent_Burden": ":.2f"
    }
)

fig.update_layout(
    template="plotly_dark",
    height=650,
    margin=dict(l=0, r=0, t=40, b=0)
)

st.plotly_chart(fig, use_container_width=True)


# ----------------------------------------------------
# 📊 KEY METRICS (ZILLOW CARDS)
# ----------------------------------------------------
st.subheader("📊 Market Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Avg Home Price", f"{df_year['Home_price'].mean():,.0f}")
col2.metric("Avg Rent", f"{df_year['Rent'].mean():,.0f}")
col3.metric("Avg Income", f"{df_year['Income'].mean():,.0f}")
col4.metric("Avg Affordability", f"{df_year['Affordability_Index'].mean():.2f}")


# ----------------------------------------------------
# 🔥 TOP & BOTTOM STATES
# ----------------------------------------------------
st.subheader("🔥 Market Leaders")

colA, colB = st.columns(2)

with colA:
    st.markdown("### 🔴 Most Expensive States")
    top = df_year.nlargest(10, "Home_price")[["State", "Home_price"]]
    st.dataframe(top, use_container_width=True)

with colB:
    st.markdown("### 🟢 Most Affordable States")
    low = df_year.nsmallest(10, "Home_price")[["State", "Home_price"]]
    st.dataframe(low, use_container_width=True)


# ----------------------------------------------------
# 📈 STATE DEEP DIVE
# ----------------------------------------------------
st.subheader("📈 State Deep Dive")

state = st.selectbox("Select State", sorted(df["State"].unique()))

state_df = df[df["State"] == state].sort_values("Year")

fig2 = go.Figure()

fig2.add_trace(go.Scatter(
    x=state_df["Year"],
    y=state_df["Home_price"],
    name="Home Price",
    mode="lines+markers"
))

fig2.add_trace(go.Scatter(
    x=state_df["Year"],
    y=state_df["Rent"],
    name="Rent",
    mode="lines+markers"
))

fig2.add_trace(go.Scatter(
    x=state_df["Year"],
    y=state_df["Income"],
    name="Income",
    mode="lines+markers"
))

fig2.update_layout(
    template="plotly_dark",
    height=450,
    title=f"{state} Housing Trends"
)

st.plotly_chart(fig2, use_container_width=True)


# ----------------------------------------------------
# 📥 DOWNLOAD
# ----------------------------------------------------
st.download_button(
    "⬇️ Download Zillow Dataset (Year View)",
    df_year.to_csv(index=False),
    file_name=f"zillow_snapshot_{year}.csv",
    mime="text/csv"
)