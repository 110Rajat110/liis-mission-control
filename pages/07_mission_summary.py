import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.insert(0, os.path.abspath('.'))
from core.lunar_utils import lunar_base_texture, noisy_hotspot, LUNAR_GRAY, TRANS_ICI

st.markdown("""
<style>
.summary-kpi-row { display:flex; justify-content:space-between; background:rgba(11,15,26,0.9); border:1px solid rgba(34,211,238,0.2); border-radius:8px; padding:16px; margin-bottom:1.5rem; }
.summary-kpi { text-align:center; }
.summary-kpi-label { font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:#94a3b8; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px; }
.summary-kpi-val { font-family:Inter,sans-serif; font-size:1.6rem; font-weight:700; color:#22d3ee; }
.summary-kpi-unit { font-size:0.8rem; color:#64748b; margin-left:2px; }

.module-grid { display:grid; grid-template-columns:repeat(3, 1fr); gap:16px; margin-bottom:2rem; }
.module-card { background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:6px; padding:12px; transition:all 0.2s; cursor:default; }
.module-card:hover { background:rgba(34,211,238,0.05); border-color:rgba(34,211,238,0.3); transform:translateY(-2px); }
.module-card-title { font-family:'JetBrains Mono',monospace; font-size:0.75rem; color:#e2e8f0; margin-bottom:8px; display:flex; justify-content:space-between; }
.module-card-val { font-family:Inter,sans-serif; font-size:1.2rem; font-weight:700; color:white; }
.module-card-sub { font-size:0.7rem; color:#94a3b8; margin-top:2px; }

/* Hide default streamlit checkboxes' generic style and make them fit the theme */
.stCheckbox > div > div > label { color:#e2e8f0 !important; font-family:'JetBrains Mono',monospace; font-size:0.8rem; }
</style>

<h1 style='font-family:Inter,sans-serif; font-size:2rem; font-weight:700; color:white; margin-bottom:4px;'>
  📑 Executive Mission Report
</h1>
<p style='color:#64748b; font-family:Inter,sans-serif; margin:0 0 1.5rem; font-size:0.85rem; letter-spacing:1px; text-transform:uppercase;'>
  Chandrayaan-2 DFSAR · Lunar South Pole Synthesis
</p>

<!-- Top KPI Strip -->
<div class="summary-kpi-row">
  <div class="summary-kpi"><div class="summary-kpi-label">Max ICI</div><div class="summary-kpi-val">0.87<span class="summary-kpi-unit"></span></div></div>
  <div class="summary-kpi"><div class="summary-kpi-label">Best LSI</div><div class="summary-kpi-val">0.91<span class="summary-kpi-unit"></span></div></div>
  <div class="summary-kpi"><div class="summary-kpi-label">Est. Ice Vol</div><div class="summary-kpi-val">1.24<span class="summary-kpi-unit">km³</span></div></div>
  <div class="summary-kpi"><div class="summary-kpi-label">Path Cost</div><div class="summary-kpi-val">4.7<span class="summary-kpi-unit">kWh</span></div></div>
  <div class="summary-kpi"><div class="summary-kpi-label">Area Mapped</div><div class="summary-kpi-val">147<span class="summary-kpi-unit">km²</span></div></div>
</div>

<!-- Middle Grid -->
<div class="module-grid">
  <div class="module-card">
    <div class="module-card-title"><span>📡 RADAR ANALYSIS</span><span style="color:#22d3ee;">✓</span></div>
    <div class="module-card-val">CPR > 1.2</div>
    <div class="module-card-sub">Strong volumetric scattering</div>
  </div>
  <div class="module-card">
    <div class="module-card-title"><span>🏔️ TERRAIN DEM</span><span style="color:#22d3ee;">✓</span></div>
    <div class="module-card-val">3.2°</div>
    <div class="module-card-sub">Mean slope at target</div>
  </div>
  <div class="module-card">
    <div class="module-card-title"><span>❄️ ICE CONFIDENCE</span><span style="color:#22d3ee;">✓</span></div>
    <div class="module-card-val">0.87 Peak</div>
    <div class="module-card-sub">Zone centroid (74, 64)</div>
  </div>
  <div class="module-card">
    <div class="module-card-title"><span>🎯 LANDING SITE</span><span style="color:#22d3ee;">✓</span></div>
    <div class="module-card-val">Haworth-A</div>
    <div class="module-card-sub">Primary candidate selected</div>
  </div>
  <div class="module-card">
    <div class="module-card-title"><span>🚗 ROVER TRAVERSE</span><span style="color:#22d3ee;">✓</span></div>
    <div class="module-card-val">1.12 km</div>
    <div class="module-card-sub">Safe corridor mapped</div>
  </div>
  <div class="module-card">
    <div class="module-card-title"><span>📦 ICE VOLUME</span><span style="color:#22d3ee;">✓</span></div>
    <div class="module-card-val">1.1 Mt</div>
    <div class="module-card-sub">P50 Mass Estimate</div>
  </div>
</div>
""", unsafe_allow_html=True)

N = 384
@st.cache_data
def build_summary_map(N):
    np.random.seed(42)
    base = lunar_base_texture(W=N, H=N, n_craters=12, seed=99)
    spot = noisy_hotspot(N, N, 0.6, 0.55, 0.16, peak=0.9, noise_scale=0.45, seed=13)
    ici = np.clip(spot + np.random.normal(0,0.05,(N,N)), 0, 1)
    return base, ici

base, ici = build_summary_map(N)

st.markdown("<h3 style='color:white; font-size:1.1rem; font-family:Inter,sans-serif; margin-bottom:8px;'>Mission Overview Map</h3>", unsafe_allow_html=True)

# Clean checkboxes
c1, c2, c3, c4 = st.columns(4)
with c1: show_ici = st.checkbox("Ice Confidence Overlay", value=True)
with c2: show_lsi = st.checkbox("Landing Sites", value=True)
with c3: show_path = st.checkbox("Rover Corridor", value=True)
with c4: show_haz = st.checkbox("Hazard Zones", value=False)

fig = go.Figure()

# Base Map
fig.add_trace(go.Heatmap(z=base, colorscale=LUNAR_GRAY, zmin=0, zmax=1,
                         showscale=False, hoverinfo='skip'))

# ICI Overlay
if show_ici:
    ici_overlay = np.where(ici < 0.35, np.nan, ici)
    fig.add_trace(go.Heatmap(z=ici_overlay, colorscale="RdBu_r", zmin=0, zmax=1,
                             showscale=True, opacity=0.75,
                             colorbar=dict(title=dict(text="ICI", font=dict(color='#94a3b8')),
                                           tickfont=dict(color='#94a3b8'), thickness=10, len=0.6, x=1.01),
                             hoverinfo='skip'))
    # Contour
    fig.add_trace(go.Contour(z=ici, contours=dict(start=0.7, end=0.7, size=1),
                             line=dict(color='#22d3ee', width=1, dash='dash'), showscale=False, hoverinfo='skip'))

# Rover Corridor
if show_path:
    waypoints = np.array([[38,269],[58,240],[83,211],[106,189],[128,170],[154,160],[176,157],[198,160],[224,157],[230,211]])
    # Wide corridor
    fig.add_trace(go.Scatter(x=waypoints[:,0], y=waypoints[:,1], mode='lines',
                             line=dict(color='rgba(34,211,238,0.2)', width=25), hoverinfo='skip'))
    # Centerline
    fig.add_trace(go.Scatter(x=waypoints[:,0], y=waypoints[:,1], mode='lines',
                             line=dict(color='#22d3ee', width=2), hoverinfo='skip'))

# Landing Sites
if show_lsi:
    # Selected target
    fig.add_trace(go.Scatter(x=[230], y=[211], mode='markers',
                             marker=dict(size=20, color='rgba(0,0,0,0)', symbol='cross', line=dict(color='#facc15', width=2)),
                             hoverinfo='skip'))
    fig.add_trace(go.Scatter(x=[230], y=[211], mode='markers+text',
                             marker=dict(size=4, color='#facc15'),
                             text=["TARGET: Haworth-A"], textposition="top right",
                             textfont=dict(color='#facc15', size=11, family='JetBrains Mono', weight='bold'),
                             hoverinfo='skip'))
    # Alternates
    fig.add_trace(go.Scatter(x=[115, 250, 77], y=[96, 230, 211], mode='markers',
                             marker=dict(size=8, color='#64748b', symbol='circle', line=dict(color='#1e293b', width=1)),
                             hoverinfo='skip'))

# Hazard Zones
if show_haz:
    np.random.seed(10)
    hx = np.random.randint(15, 368, 12)
    hy = np.random.randint(15, 368, 12)
    fig.add_trace(go.Scatter(x=hx, y=hy, mode='markers',
                             marker=dict(size=12, color='rgba(244,63,94,0.4)', symbol='x', line=dict(color='#f43f5e', width=1.5)),
                             hoverinfo='skip'))

fig.update_layout(
    height=550, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=0,r=80,t=10,b=0),
    xaxis=dict(range=[0,N], showgrid=False, showticklabels=False),
    yaxis=dict(range=[N,0], showgrid=False, showticklabels=False),
    showlegend=False
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)
report_data = pd.DataFrame({
    "Parameter": ["Primary Site", "LSI Score", "ICI Peak", "Est. Ice Volume", "Path Length", "Energy Cost"],
    "Value": ["Haworth-A", "0.91", "0.87", "1.24 km3", "1.12 km", "4.7 kWh"]
})
csv = report_data.to_csv(index=False)
st.download_button("⬇️ EXPORT FINAL MISSION DOSSIER (CSV)", csv, "liis_dossier.csv", "text/csv", use_container_width=True)
