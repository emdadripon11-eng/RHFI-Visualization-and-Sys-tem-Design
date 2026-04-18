import streamlit as st
import pandas as pd
import plotly.express as px

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="Region Comparison", layout="wide")

# =============================
# GLASS UI STYLE (MATCHES home.py)
# =============================
st.markdown("""
<style>

.stApp {
    background: radial-gradient(circle at top, #0a0f1f 0%, #050814 100%);
    color: #e5e7eb;
}

/* Glass container */
.glass {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    padding: 22px;
    border-radius: 18px;
    backdrop-filter: blur(14px);
    margin-bottom: 1rem;
}

/* Section header */
.section-title {
    font-size: 1.6rem;
    font-weight: 700;
    color: #60a5fa;
    margin-bottom: 0.5rem;
}

</style>
""", unsafe_allow_html=True)


# =============================
# LOAD DATA
# =============================
@st.cache_data
def load_data():
    df = pd.read_csv("/Users/emdadripon/Downloads/ProjectpoposalFinal/data/rhfi_final_ui_ready.csv")
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    df["Region"] = df["Region"].astype(str).str.strip()
    df = df.drop_duplicates().sort_values(["Region", "Year"])
    return df

df = load_data()


# =============================
# HEADER
# =============================
st.markdown("""
<div class="glass">
    <h1 style="margin-bottom:0;">⚖️ Region Comparison Dashboard</h1>
    <p style="color:#94a3b8;margin-top:4px;">Glass‑UI edition — clean, modern, and stable</p>
</div>
""", unsafe_allow_html=True)


# =============================
# CONTROLS
# =============================
regions = sorted(df["Region"].dropna().unique().tolist())

c1, c2, c3 = st.columns([1, 1, 1])

with c1:
    r1 = st.selectbox("Region A", regions, index=0)

with c2:
    r2 = st.selectbox("Region B", regions, index=1)

with c3:
    metric = st.selectbox(
        "Metric",
        [c for c in df.select_dtypes(include="number").columns if c != "Year"]
    )

r1 = str(r1).strip()
r2 = str(r2).strip()

latest_year = int(df["Year"].max())
latest = df[df["Year"] == latest_year]

def get_val(region):
    v = latest.loc[latest["Region"] == region, metric].values
    return float(v[0]) if len(v) else None

def get_prev(region):
    prev = df[df["Year"] == latest_year - 1]
    v = prev.loc[prev["Region"] == region, metric].values
    return float(v[0]) if len(v) else None

val1, val2 = get_val(r1), get_val(r2)
prev1, prev2 = get_prev(r1), get_prev(r2)


# =============================
# KPI CARDS (GLASS)
# =============================
st.markdown('<div class="section-title">📊 Key Metrics</div>', unsafe_allow_html=True)

k1, k2 = st.columns(2)

with k1:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.metric(
        label=f"Region {r1} — {metric}",
        value=f"{val1:,.2f}" if val1 else "N/A",
        delta=None if prev1 is None else f"{val1 - prev1:,.2f}"
    )
    st.markdown('</div>', unsafe_allow_html=True)

with k2:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.metric(
        label=f"Region {r2} — {metric}",
        value=f"{val2:,.2f}" if val2 else "N/A",
        delta=None if prev2 is None else f"{val2 - prev2:,.2f}"
    )
    st.markdown('</div>', unsafe_allow_html=True)


# =============================
# TABS
# =============================
tab1, tab2, tab3 = st.tabs(["📈 Trends", "📊 Comparison", "🧾 Raw Data"])

with tab1:
    st.markdown('<div class="section-title">Metric Trends Over Time</div>', unsafe_allow_html=True)
    trend_df = df[df["Region"].isin([r1, r2])]
    fig = px.line(trend_df, x="Year", y=metric, color="Region", markers=True, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown('<div class="section-title">Latest Year Comparison</div>', unsafe_allow_html=True)
    comp_df = latest[latest["Region"].isin([r1, r2])]
    fig2 = px.bar(comp_df, x="Region", y=metric, color="Region", text_auto=".2s", template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.markdown('<div class="section-title">Data Table</div>', unsafe_allow_html=True)
    st.dataframe(df[df["Region"].isin([r1, r2])], use_container_width=True)


# =============================
# INSIGHT SUMMARY
# =============================
st.markdown('<div class="section-title">🔍 Insight Summary</div>', unsafe_allow_html=True)

higher = r1 if val1 > val2 else r2
lower = r2 if val1 > val2 else r1

st.markdown(f"""
<div class="glass">
    • <b>Region {higher}</b> has a higher <b>{metric}</b> than <b>Region {lower}</b> in {latest_year}.<br><br>
    • Indicates differences in market pressure or affordability.<br><br>
    • Trend divergence may signal structural differences between regions.
</div>
""", unsafe_allow_html=True)
