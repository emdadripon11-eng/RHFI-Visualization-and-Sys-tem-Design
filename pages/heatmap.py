import streamlit as st
import pandas as pd
import plotly.express as px


# -----------------------------
# Load data
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/final_real_estate_dataset.csv")
    df = df.drop_duplicates().sort_values(["RegionName", "Year"])
    return df


df = load_data()
years = sorted(df["Year"].unique())
latest_year = max(years)

indicator_options = {
    "Price-to-Income Ratio (RHFI)": "price_income_ratio",
    "Price Growth (%)": "price_growth",
    "Rent Growth (%)": "rent_growth",
    "Inventory Change (%)": "inventory_change",
}

st.title("🗺️ RHFI Geographic Heatmap Suite")

tab1, tab2, tab3 = st.tabs([
    "Base Heatmap",
    "YoY Affordability Change",
    "Animated RHFI Map"
])

# -----------------------------
# TAB 1 — Base Heatmap + Top Risk
# -----------------------------
with tab1:
    st.header("📌 RHFI Geographic Heatmap")

    col1, col2 = st.columns([2, 1])

    with col1:
        selected_year = st.slider(
            "Select Year",
            min_value=min(years),
            max_value=max(years),
            value=latest_year,
            key="base_year"
        )

        selected_indicator_label = st.selectbox(
            "Select Indicator",
            list(indicator_options.keys()),
            index=0,
            key="base_indicator"
        )
        selected_indicator = indicator_options[selected_indicator_label]

        year_df = df[df["Year"] == selected_year]

        fig = px.choropleth(
            year_df,
            locations="RegionName",
            locationmode="USA-states",
            color=selected_indicator,
            hover_name="RegionName",
            hover_data={
                "price_income_ratio": True,
                "price_growth": True,
                "rent_growth": True,
                "inventory_change": True,
                "Year": False,
            },
            color_continuous_scale="RdYlGn_r",
            scope="usa",
            title=f"{selected_indicator_label} — {selected_year}"
        )

        fig.update_layout(
            geo=dict(bgcolor="rgba(0,0,0,0)"),
            margin=dict(l=0, r=0, t=50, b=0),
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🔥 Top 10 Highest-Risk Regions")
        top_risk = year_df.nlargest(10, selected_indicator)[["RegionName", selected_indicator]]
        top_risk = top_risk.rename(columns={selected_indicator: selected_indicator_label})
        st.dataframe(top_risk, use_container_width=True)

# -----------------------------
# TAB 2 — YoY Affordability Change
# -----------------------------
with tab2:
    st.header("📉 YoY Affordability Change Heatmap")

    df_yoy = df.sort_values(["RegionName", "Year"]).copy()
    df_yoy["rhfi_change"] = df_yoy.groupby("RegionName")["price_income_ratio"].pct_change() * 100

    yoy_year = st.slider(
        "Select Year (YoY change vs previous year)",
        min_value=min(years[1:]),
        max_value=max(years),
        value=latest_year,
        key="yoy_year"
    )

    yoy_df = df_yoy[df_yoy["Year"] == yoy_year]

    fig_yoy = px.choropleth(
        yoy_df,
        locations="RegionName",
        locationmode="USA-states",
        color="rhfi_change",
        color_continuous_scale="RdYlGn",
        scope="usa",
        title=f"YoY Change in Affordability — {yoy_year}",
        hover_data={
            "price_income_ratio": True,
            "rhfi_change": True,
            "Year": False
        }
    )

    fig_yoy.update_layout(
        geo=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=0, r=0, t=50, b=0),
    )

    st.plotly_chart(fig_yoy, use_container_width=True)

    st.markdown(
        "- Green → affordability improving (RHFI decreasing)\n"
        "- Red → affordability worsening (RHFI increasing)"
    )

# -----------------------------
# TAB 3 — Animated RHFI Map
# -----------------------------
with tab3:
    st.header("🎞️ Animated RHFI Map Over Time")

    fig_anim = px.choropleth(
        df,
        locations="RegionName",
        locationmode="USA-states",
        color="price_income_ratio",
        animation_frame="Year",
        color_continuous_scale="RdYlGn_r",
        scope="usa",
        title="RHFI Over Time (Animated)"
    )

    fig_anim.update_layout(
        geo=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=0, r=0, t=50, b=0),
    )

    st.plotly_chart(fig_anim, use_container_width=True)
