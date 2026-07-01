import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.insert(0, os.path.abspath('.'))
from core.lunar_utils import lunar_base_texture, noisy_hotspot, LUNAR_GRAY, TRANS_BLUE

st.markdown("""
<h1 style='font-family:Inter,sans-serif; font-size:2rem; font-weight:700; color:white; margin-bottom:4px;'>
  🎯 Landing Site Selection
</h1>
<p style='color:#64748b; font-family:Inter,sans-serif; margin:0 0 1.5rem; font-size:0.85rem;
          letter-spacing:1px; text-transform:uppercase;'>
  Multi-criteria LSI · Slope · Ice Proximity · Illumination · Hazard Score
</p>
""", unsafe_allow_html=True)

N = 384

@st.cache_data
def build_lsi_map(N=384):
    base = lunar_base_texture(W=N, H=N, n_craters=18, seed=55)
    spot = noisy_hotspot(N, N, 0.6, 0.55, 0.2, peak=0.9, noise_scale=0.4, seed=7)
    lsi  = np.clip(base * 0.45 + spot * 0.55, 0, 1).astype(np.float32)
    return base, lsi

base, lsi = build_lsi_map(N)

sites = pd.DataFrame([
    {"Site":"Haworth-A",    "x":230, "y":211, "ICI":0.87, "Slope°":3.2, "Illumination%":18, "HazardScore":0.12, "LSI":0.91},
    {"Site":"Shackleton-B", "x":115, "y":96,  "ICI":0.72, "Slope°":5.7, "Illumination%":12, "HazardScore":0.28, "LSI":0.74},
    {"Site":"Nobile-C",     "x":250, "y":230, "ICI":0.65, "Slope°":7.1, "Illumination%":21, "HazardScore":0.35, "LSI":0.62},
    {"Site":"Amundsen-D",   "x":77,  "y":211, "ICI":0.58, "Slope°":9.4, "Illumination%":9,  "HazardScore":0.45, "LSI":0.51},
    {"Site":"Sverdrup-E",   "x":269, "y":77,  "ICI":0.48, "Slope°":12.3,"Illumination%":26, "HazardScore":0.55, "LSI":0.44},
])

# Interactive table
selected = st.dataframe(
    sites[["Site","LSI","ICI","Slope°","Illumination%","HazardScore"]].style
        .background_gradient(subset=["LSI","ICI"], cmap="Blues")
        .format({"LSI":"{:.2f}","ICI":"{:.2f}","Slope°":"{:.1f}","HazardScore":"{:.2f}"}),
    use_container_width=True, hide_index=True,
    selection_mode="single-row", on_select="rerun", key="site_table"
)

sel_idx = selected.selection.rows[0] if selected.selection.rows else 0
chosen  = sites.iloc[sel_idx]

st.markdown(f"""
<div style="background:rgba(34,211,238,0.05); border:1px solid rgba(34,211,238,0.25);
            border-radius:8px; padding:9px 16px; font-family:'JetBrains Mono',monospace;
            font-size:0.82rem; color:#22d3ee; margin-bottom:1rem;">
  SELECTED → <strong>{chosen['Site']}</strong> &nbsp;·&nbsp;
  LSI={chosen['LSI']:.2f} &nbsp;·&nbsp; ICI={chosen['ICI']:.2f} &nbsp;·&nbsp;
  Slope={chosen['Slope°']:.1f}°
</div>
""", unsafe_allow_html=True)

fig = go.Figure()

# ── Lunar base texture ────────────────────────────────────────────────────────
fig.add_trace(go.Heatmap(z=base, colorscale=LUNAR_GRAY, zmin=0, zmax=1,
                         showscale=False, hoverinfo='skip'))

lsi_overlay = np.where(lsi < 0.25, np.nan, lsi)

# ── LSI heatmap overlay ───────────────────────────────────────────────────────
fig.add_trace(go.Heatmap(
    z=lsi_overlay, colorscale="Blues", zmin=0, zmax=1, showscale=True, opacity=0.75,
    colorbar=dict(
        title=dict(text="LSI Score", side="top",
                   font=dict(color='#94a3b8', size=11, family='JetBrains Mono')),
        tickfont=dict(color='#94a3b8', size=10, family='JetBrains Mono'),
        thickness=12, len=0.7, x=1.01
    ),
    hoverinfo='skip'
))

# ── Site markers ──────────────────────────────────────────────────────────────
for i, row in sites.iterrows():
    is_sel = (i == sel_idx)
    if not is_sel:
        fig.add_trace(go.Scatter(
            x=[row["x"]], y=[row["y"]], mode='markers',
            marker=dict(size=8, color='#64748b', symbol='circle', line=dict(color='#1e293b', width=1)),
            name=row["Site"], showlegend=False,
            hovertemplate=f"<b>{row['Site']}</b><br>LSI={row['LSI']:.2f}<br>ICI={row['ICI']:.2f}<extra></extra>"
        ))
    else:
        # Prominent yellow crosshair for selected site
        fig.add_trace(go.Scatter(
            x=[row["x"]], y=[row["y"]], mode='markers',
            marker=dict(size=24, color='rgba(0,0,0,0)', symbol='cross', line=dict(color='#facc15', width=2)),
            name=row["Site"], showlegend=False, hoverinfo='skip'
        ))
        fig.add_trace(go.Scatter(
            x=[row["x"]], y=[row["y"]], mode='markers',
            marker=dict(size=4, color='#facc15'),
            showlegend=False, hoverinfo='skip'
        ))
        # Label annotation
        fig.add_annotation(
            x=row["x"], y=row["y"],
            text=f"TARGET: {row['Site']} (LSI {row['LSI']:.2f})",
            font=dict(color="#facc15", size=11, family="JetBrains Mono", weight="bold"),
            showarrow=True, arrowhead=0, arrowcolor="#facc15", ax=50, ay=-35,
            bgcolor="rgba(11,15,26,0.85)", bordercolor="rgba(250,204,21,0.5)", borderpad=4
        )

# ── Pulsing glow ring around selected site ────────────────────────────────────
for r_mult, op in [(1.8, 0.4), (2.6, 0.2), (3.6, 0.08)]:
    fig.add_trace(go.Scatter(
        x=[chosen["x"]], y=[chosen["y"]], mode='markers',
        marker=dict(size=24 * r_mult, color=f'rgba(250,204,21,{op})', line=dict(color='rgba(250,204,21,0.5)', width=1 if r_mult < 2.5 else 0)),
        hoverinfo='skip', showlegend=False
    ))

fig.update_layout(
    height=500,
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=0,r=70,t=0,b=0),
    xaxis=dict(range=[0,N], showgrid=False, showticklabels=False),
    yaxis=dict(range=[N,0], showgrid=False, showticklabels=False),
    font=dict(family='JetBrains Mono'), showlegend=False
)

st.plotly_chart(fig, use_container_width=True)
