import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

df = pd.read_csv("data/final_dataset.csv")
df = df.drop_duplicates().sort_values(["RegionName", "Year"])

st.title("📊 Advanced Indicator Breakdown Panel")

# Sidebar
st.sidebar.header("Controls")
region = st.sidebar.selectbox("Select Region", df['RegionName'].unique())

indicators = [
    "Home_price", "Rent", "Income",
    "price_income_ratio", "price_growth",
    "rent_growth", "inventory_change"
]

selected_indicators = st.sidebar.multiselect(
    "Select Indicators to Display",
    indicators,
    default=indicators
)

filtered = df[df['RegionName'] == region].copy()

# Summary statistics
st.subheader(f"📌 Summary Statistics – {region}")
summary = filtered[selected_indicators].describe().T
st.dataframe(summary.style.format("{:.2f}"))

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Grouped Bars",
    "📦 Boxplot",
    "📈 YoY Change",
    "🧭 Radar Chart",
    "🔗 Correlation Heatmap"
])

# ---------------- TAB 1: Grouped Bars ----------------
with tab1:
    fig = px.bar(
        filtered,
        x="Year",
        y=selected_indicators,
        barmode="group",
        title=f"Indicator Breakdown – {region}"
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------- TAB 2: Boxplot ----------------
with tab2:
    fig2 = px.box(
        filtered[selected_indicators],
        title="Distribution of Selected Indicators"
    )
    st.plotly_chart(fig2, use_container_width=True)

# ---------------- TAB 3: YoY Change ----------------
with tab3:
    yoy_df = filtered.copy()
    for col in selected_indicators:
        yoy_df[col + "_YoY"] = yoy_df[col].pct_change() * 100

    yoy_cols = [c for c in yoy_df.columns if c.endswith("_YoY")]

    fig3 = px.line(
        yoy_df,
        x="Year",
        y=yoy_cols,
        markers=True,
        title=f"Year-over-Year % Change – {region}"
    )
    st.plotly_chart(fig3, use_container_width=True)

# ---------------- TAB 4: Radar Chart ----------------
with tab4:
    latest = filtered.tail(1)[selected_indicators]

    # Normalize 0–1
    radar = (latest - latest.min()) / (latest.max() - latest.min())
    radar_values = radar.values.flatten()

    fig4 = go.Figure()
    fig4.add_trace(go.Scatterpolar(
        r=radar_values,
        theta=[col.replace("_", " ").title() for col in selected_indicators],
        fill='toself',
        name=region
    ))

    fig4.update_layout(title="Normalized Indicator Radar Chart")
    st.plotly_chart(fig4, use_container_width=True)

# ---------------- TAB 5: Correlation Heatmap ----------------
with tab5:
    corr = filtered[selected_indicators].corr()

    fig5 = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale="RdBu_r",
        title="Indicator Correlation Matrix"
    )
    st.plotly_chart(fig5, use_container_width=True)
