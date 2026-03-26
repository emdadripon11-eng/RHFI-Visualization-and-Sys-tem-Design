import streamlit as st
import pandas as pd
from prophet import Prophet
from prophet.plot import plot_components_plotly
import plotly.express as px
import plotly.graph_objects as go

df = pd.read_csv("data/final_dataset.csv")
df = df.drop_duplicates().sort_values(["RegionName", "Year"])

st.title("🔮 Advanced Forecasting Panel")

# Sidebar controls
st.sidebar.header("Forecast Settings")

region = st.sidebar.selectbox("Select Region", df['RegionName'].unique())

metrics = ["Home_price", "Rent", "Income"]
metric = st.sidebar.selectbox("Select Metric to Forecast", metrics)

forecast_years = st.sidebar.slider("Forecast Horizon (years)", 3, 15, 5)
changepoint_scale = st.sidebar.slider("Changepoint Sensitivity", 0.01, 0.5, 0.15)
seasonality = st.sidebar.selectbox("Seasonality Mode", ["additive", "multiplicative"])

# Prepare data
filtered = df[df['RegionName'] == region][["Year", metric]].rename(
    columns={"Year": "ds", metric: "y"}
)

filtered["ds"] = pd.to_datetime(filtered["ds"], format="%Y")

# Build Prophet model
m = Prophet(
    interval_width=0.85,
    changepoint_prior_scale=changepoint_scale,
    seasonality_mode=seasonality
)

m.fit(filtered)

future = m.make_future_dataframe(periods=forecast_years, freq="Y")
forecast = m.predict(future)

# Tabs
tab1, tab2, tab3 = st.tabs([
    "📈 Forecast Plot",
    "📊 Components",
    "⬇️ Download"
])

# ---------------- TAB 1: Forecast Plot ----------------
with tab1:
    fig = go.Figure()

    # Historical data
    fig.add_trace(go.Scatter(
        x=filtered["ds"], y=filtered["y"],
        mode="lines+markers",
        name="Historical",
        line=dict(color="blue", width=3)
    ))

    # Forecast line
    fig.add_trace(go.Scatter(
        x=forecast["ds"], y=forecast["yhat"],
        mode="lines",
        name="Forecast",
        line=dict(color="orange", width=3)
    ))

    # Confidence interval
    fig.add_trace(go.Scatter(
        x=forecast["ds"], y=forecast["yhat_upper"],
        mode="lines",
        line=dict(width=0),
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=forecast["ds"], y=forecast["yhat_lower"],
        mode="lines",
        fill="tonexty",
        line=dict(width=0),
        name="Confidence Interval"
    ))

    fig.update_layout(
        title=f"{metric.replace('_',' ').title()} Forecast – {region}",
        xaxis_title="Year",
        yaxis_title=metric.replace("_", " ").title()
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------- TAB 2: Components ----------------
with tab2:
    comp_fig = plot_components_plotly(m, forecast)
    st.plotly_chart(comp_fig, use_container_width=True)

# ---------------- TAB 3: Download ----------------
with tab3:
    st.write("Download the forecasted values as CSV:")
    st.download_button(
        "⬇️ Download Forecast CSV",
        forecast.to_csv(index=False),
        file_name=f"{region}_{metric}_forecast.csv",
        mime="text/csv"
    )
