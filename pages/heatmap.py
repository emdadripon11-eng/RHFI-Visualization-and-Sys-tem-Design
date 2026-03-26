import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# -----------------------------
# Load data
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/final_dataset.csv")
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

# -----------------------------
# TAB 1 — Enhanced Heatmap
# -----------------------------
st.header("📌 RHFI Geographic Heatmap")
st.markdown("Explore housing fragility across U.S. states using a refined, high‑clarity map.")

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

    # Optional: highlight a state
    highlight_state = st.selectbox(
        "Highlight a State (Optional)",
        ["None"] + sorted(df["RegionName"].unique())
    )

    # Filter for selected year
    year_df = df[df["Year"] == selected_year].copy()

    # -----------------------------
    # FIX: Convert RegionName to string
    # -----------------------------
    year_df["RegionName"] = year_df["RegionName"].astype(str)

    # -----------------------------
    # Custom tooltip
    # -----------------------------
    year_df["tooltip"] = (
            "<b>" + year_df["RegionName"] + "</b><br>" +
            "RHFI: " + year_df["price_income_ratio"].round(2).astype(str) + "<br>" +
            "Price Growth: " + year_df["price_growth"].round(2).astype(str) + "%<br>" +
            "Rent Growth: " + year_df["rent_growth"].round(2).astype(str) + "%<br>" +
            "Inventory Change: " + year_df["inventory_change"].round(2).astype(str) + "%"
    )

    # -----------------------------
    # Custom color scale
    # -----------------------------
    custom_scale = [
        [0.0, "#1a9850"],   # green
        [0.5, "#fee08b"],   # yellow
        [1.0, "#d73027"]    # red
    ]

    # -----------------------------
    # Quantile scaling (5th–95th percentile)
    # -----------------------------
    qmin, qmax = np.percentile(year_df[selected_indicator], [5, 95])

    # -----------------------------
    # Build heatmap
    # -----------------------------
    fig = px.choropleth(
        year_df,
        locations="RegionName",
        locationmode="USA-states",
        color=selected_indicator,
        hover_name="RegionName",
        hover_data={"tooltip": True},
        color_continuous_scale=custom_scale,
        scope="usa",
        title=f"{selected_indicator_label} — {selected_year}"
    )

    # Apply quantile scaling
    fig.update_coloraxes(cmin=qmin, cmax=qmax)

    # Add borders
    fig.update_traces(marker_line_width=0.8, marker_line_color="black")

    # Improved layout
    fig.update_layout(
        geo=dict(
            bgcolor="rgba(0,0,0,0)",
            landcolor="#f7f7f7",
            showland=True,
            projection_type="albers usa"
        ),
        coloraxis_colorbar=dict(
            title=selected_indicator_label,
            ticks="outside",
            thickness=16,
            len=0.75
        ),
        margin=dict(l=0, r=0, t=40, b=0),
    )

    # -----------------------------
    # OPTION 1: Add State Labels on Map
    # -----------------------------
    state_centers = {
        "AL": [32.806671, -86.791130], "AK": [61.370716, -152.404419],
        "AZ": [33.729759, -111.431221], "AR": [34.969704, -92.373123],
        "CA": [36.116203, -119.681564], "CO": [39.059811, -105.311104],
        "CT": [41.597782, -72.755371], "DE": [39.318523, -75.507141],
        "FL": [27.766279, -81.686783], "GA": [33.040619, -83.643074],
        "HI": [21.094318, -157.498337], "ID": [44.240459, -114.478828],
        "IL": [40.349457, -88.986137], "IN": [39.849426, -86.258278],
        "IA": [42.011539, -93.210526], "KS": [38.526600, -96.726486],
        "KY": [37.668140, -84.670067], "LA": [31.169546, -91.867805],
        "ME": [44.693947, -69.381927], "MD": [39.063946, -76.802101],
        "MA": [42.230171, -71.530106], "MI": [43.326618, -84.536095],
        "MN": [45.694454, -93.900192], "MS": [32.741646, -89.678696],
        "MO": [38.456085, -92.288368], "MT": [46.921925, -110.454353],
        "NE": [41.125370, -98.268082], "NV": [38.313515, -117.055374],
        "NH": [43.452492, -71.563896], "NJ": [40.298904, -74.521011],
        "NM": [34.840515, -106.248482], "NY": [42.165726, -74.948051],
        "NC": [35.630066, -79.806419], "ND": [47.528912, -99.784012],
        "OH": [40.388783, -82.764915], "OK": [35.565342, -96.928917],
        "OR": [44.572021, -122.070938], "PA": [40.590752, -77.209755],
        "RI": [41.680893, -71.511780], "SC": [33.856892, -80.945007],
        "SD": [44.299782, -99.438828], "TN": [35.747845, -86.692345],
        "TX": [31.054487, -97.563461], "UT": [40.150032, -111.862434],
        "VT": [44.045876, -72.710686], "VA": [37.769337, -78.169968],
        "WA": [47.400902, -121.490494], "WV": [38.491226, -80.954453],
        "WI": [44.268543, -89.616508], "WY": [42.755966, -107.302490]
    }

    fig.add_scattergeo(
        lat=[v[0] for v in state_centers.values()],
        lon=[v[1] for v in state_centers.values()],
        text=list(state_centers.keys()),
        mode="text",
        textfont=dict(size=10, color="black"),
        showlegend=False
    )

    # -----------------------------
    # Highlight selected state
    # -----------------------------
    if highlight_state != "None":
        fig.add_scattergeo(
            locations=[highlight_state],
            locationmode="USA-states",
            marker=dict(size=18, color="black", opacity=0.8),
            name="Selected State"
        )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🔥 Top 10 Highest-Risk Regions")
    top_risk = year_df.nlargest(10, selected_indicator)[["RegionName", selected_indicator]]
    top_risk = top_risk.rename(columns={selected_indicator: selected_indicator_label})
    st.dataframe(top_risk, use_container_width=True)
