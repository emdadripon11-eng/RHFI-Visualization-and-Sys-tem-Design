import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------
# CONFIG
# ----------------------------
st.set_page_config(page_title="US Housing Dashboard", layout="wide")

st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top, #0b1220 0%, #050814 100%);
    color: white;
}
</style>
""", unsafe_allow_html=True)


# ----------------------------
# LOAD DATA
# ----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/map_dataset.csv")
    return df

df = load_data()


# ----------------------------
# TITLE
# ----------------------------
st.title("🇺🇸 Zillow-Style US Housing Dashboard")
st.caption("50-state panel dataset with interactive heatmap")


# ----------------------------
# CONTROLS
# ----------------------------
metric = st.selectbox("Select Metric", ["Home_price", "Rent", "Income"])
year = st.slider("Year", int(df.Year.min()), int(df.Year.max()), int(df.Year.max()))


# ----------------------------
# FILTER DATA
# ----------------------------
df_year = df[df["Year"] == year]


# ----------------------------
# 🇺🇸 USA MAP (CORE FEATURE)
# ----------------------------
st.subheader(f"{metric} Across US States - {year}")

fig = px.choropleth(
    df_year,
    locations="State",
    locationmode="USA-states",
    color=metric,
    scope="usa",
    hover_name="State",
    color_continuous_scale="Viridis"
)

fig.update_layout(height=650)

st.plotly_chart(fig, use_container_width=True)


# ----------------------------
# STATE TREND
# ----------------------------
st.subheader("State Trend")

state = st.selectbox("Pick State", df.State.unique())

state_df = df[df["State"] == state]

st.line_chart(state_df.set_index("Year")[metric])


# ----------------------------
# SUMMARY
# ----------------------------
st.subheader("Quick Stats")

col1, col2, col3 = st.columns(3)

col1.metric("Avg", round(df_year[metric].mean(), 2))
col2.metric("Max", round(df_year[metric].max(), 2))
col3.metric("Min", round(df_year[metric].min(), 2))