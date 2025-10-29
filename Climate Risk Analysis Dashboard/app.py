
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Climate Risk Analysis", page_icon="🌍", layout="wide")

st.markdown('''
    <style>
    @import url("https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap");
    html, body, [class*="css"]  { font-family: "Poppins", sans-serif !important; }
    .block { background:#0f0f10; border:1px solid #1c1c1f; border-radius:20px; padding:20px; box-shadow:0 0 20px rgba(167,139,250,0.08); }
    .kpi { background:#111214; border:1px solid #1f1f22; border-radius:16px; padding:16px; text-align:center; }
    .kpi h3 { margin:0; font-weight:600; font-size:0.95rem; color:#cbd5e1; }
    .kpi p { margin:6px 0 0 0; font-size:1.25rem; font-weight:700; color:#ffffff; }
    .title { font-weight:700; font-size:1.6rem; margin-bottom:6px; }
    .subtitle { color:#94a3b8; font-size:0.95rem; margin-bottom:1rem; }
    </style>
''', unsafe_allow_html=True)

BASE = Path(__file__).resolve().parent
PROCESSED = BASE / "etl" / "data" / "processed" / "processed_data.csv"

# Auto-generate processed file if missing (downloads Kaggle dataset via ETL)
if not PROCESSED.exists():
    import runpy
    runpy.run_path(str(BASE / "etl" / "ingest_and_process.py"))

df = pd.read_csv(PROCESSED)

# Sidebar filters
st.sidebar.header("Filters")
years = sorted(df["year"].dropna().unique().tolist())
if len(years) == 1:
    year_sel = years[0]
    st.sidebar.write(f"**Year:** {year_sel}")
else:
    year_sel = st.sidebar.slider("Year", int(min(years)), int(max(years)), int(max(years)))
countries = sorted(df["country"].dropna().unique().tolist())
default_countries = [c for c in ["India","Bangladesh","Philippines","Honduras"] if c in countries] or countries[:3]
country_sel = st.sidebar.multiselect("Countries (for trends)", countries, default=default_countries)
metric_sel = st.sidebar.selectbox("Trend Metric", ["temperature_anomaly", "co2_growth", "sea_level_change"])

# Overview
st.markdown('<div class="block">', unsafe_allow_html=True)
st.markdown('<div class="title">Overview</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Global risk map and key indicators</div>', unsafe_allow_html=True)

df_year = df[df["year"] == year_sel]
avg_risk = float(df_year["risk_score"].mean()) if len(df_year) else 0.0
top_row = df_year.sort_values("risk_score", ascending=False).head(1)
top_country = top_row.iloc[0]["country"] if len(top_row) else "-"
top_score = float(top_row.iloc[0]["risk_score"]) if len(top_row) else 0.0
avg_temp = float(df_year["temperature_anomaly"].mean()) if len(df_year) else 0.0

c1, c2, c3, c4 = st.columns(4)
c1.markdown(f'<div class="kpi"><h3>Selected Year</h3><p>{year_sel}</p></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="kpi"><h3>Avg Risk Score</h3><p>{avg_risk:.3f}</p></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="kpi"><h3>Top Risk (Country)</h3><p>{top_country} · {top_score:.3f}</p></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="kpi"><h3>Avg Temp Anomaly</h3><p>{avg_temp:.3f}</p></div>', unsafe_allow_html=True)

if len(df_year):
    fig_map = px.choropleth(
        df_year,
        locations="country",
        locationmode="country names",
        color="risk_score",
        hover_name="country",
        color_continuous_scale="Viridis",
        title=f"Global Climate Risk (Risk Score) — {year_sel}"
    )
    fig_map.update_layout(margin=dict(l=0,r=0,b=0,t=50), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Poppins"))
    st.plotly_chart(fig_map, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# Trends
st.markdown('<div class="block" style="margin-top:16px;">', unsafe_allow_html=True)
st.markdown('<div class="title">Trends</div>', unsafe_allow_html=True)
st.markdown(f'<div class="subtitle">Yearly trend for <b>{metric_sel}</b></div>', unsafe_allow_html=True)

df_trend = df[df["country"].isin(country_sel)]
if len(df_trend):
    fig_trend = px.line(df_trend, x="year", y=metric_sel, color="country", markers=True, title=f"Trend: {metric_sel}")
    fig_trend.update_layout(margin=dict(l=0,r=0,b=0,t=50), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Poppins"))
    st.plotly_chart(fig_trend, use_container_width=True)

# Leaderboard
st.markdown('<div class="block" style="margin-top:16px;">', unsafe_allow_html=True)
st.markdown('<div class="title">Leaderboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Top countries by climate risk</div>', unsafe_allow_html=True)

top_n = st.slider("Show Top N", 5, 20, 10, 1)
cols = ["country","risk_score","temperature_anomaly","co2_growth","sea_level_change"]
top_df = df_year.sort_values("risk_score", ascending=False).head(top_n)[cols] if len(df_year) else pd.DataFrame(columns=cols)
st.dataframe(top_df.reset_index(drop=True), use_container_width=True)

if len(top_df):
    fig_bar = px.bar(top_df.sort_values("risk_score"), x="risk_score", y="country", orientation="h", title=f"Top {top_n} Risk Scores — {year_sel}")
    fig_bar.update_layout(margin=dict(l=0,r=0,b=0,t=50), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Poppins"))
    st.plotly_chart(fig_bar, use_container_width=True)

with st.expander("Methods", expanded=False):
    st.markdown('''
    **Risk Score** = `0.5 * temp_anomaly_z + 0.3 * co2_growth_norm + 0.2 * sea_level_z`  
    Pipeline: Download (kagglehub) → Clean/Map → Feature Engineering → Save processed CSV → Visualize.
    ''')
