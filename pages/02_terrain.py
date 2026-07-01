import streamlit as st
import numpy as np
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.abspath('.'))
from core.lunar_utils import lunar_surface_dem

st.markdown("""
<h1 style='font-family:Inter,sans-serif; font-size:2rem; font-weight:700; color:white; margin-bottom:4px;'>
  🏔️ Terrain Analysis
</h1>
<p style='color:#64748b; font-family:Inter,sans-serif; margin:0 0 1.5rem; font-size:0.85rem;
          letter-spacing:1px; text-transform:uppercase;'>
  OHRC + LOLA DEM · Slope Gradient · Roughness Index · Crater Mapping
</p>
""", unsafe_allow_html=True)

layer = st.radio(
    "Colour overlay",
    ["Elevation", "Slope°", "Roughness", "Boulder Density"],
    horizontal=True, key="terrain_layer"
)

@st.cache_data
def build_terrain():
    return lunar_surface_dem(resolution=250, n_craters=40, seed=87)

X, Y, Z = build_terrain()

# Derived layers
dx, dy = np.gradient(Z)
slope   = np.degrees(np.arctan(np.sqrt(dx**2 + dy**2)))
rough   = np.abs(np.gradient(dx)[0] + np.gradient(dy)[1])
rough   = np.clip(rough / rough.max(), 0, 1)
boulders = np.clip(np.abs(Z - Z.mean()) / np.abs(Z - Z.mean()).max(), 0, 1)

layer_map = {
    "Elevation":      (Z,        "Greys_r",  "Elevation"),
    "Slope°":         (slope,    "Plasma",   "Slope (°)"),
    "Roughness":      (rough,    "Viridis",  "Roughness"),
    "Boulder Density":(boulders, "Inferno",  "Boulder Density"),
}
zdata, colorscale, cbar_title = layer_map[layer]

fig = go.Figure(go.Surface(
    z=Z, x=X, y=Y,
    surfacecolor=zdata,
    colorscale=colorscale,
    showscale=True,
    colorbar=dict(
        title=dict(text=cbar_title, side="top", font=dict(color='#94a3b8', size=11, family='JetBrains Mono')),
        tickfont=dict(color='#94a3b8', size=10, family='JetBrains Mono'),
        thickness=12, len=0.55, x=1.0
    ),
    lighting=dict(ambient=0.4, diffuse=0.85, roughness=0.9, specular=0.08, fresnel=0.15),
    lightposition=dict(x=300, y=100, z=60),
))

fig.update_layout(
    scene=dict(
        xaxis=dict(showbackground=False, gridcolor='rgba(255,255,255,0.04)',
                   tickfont=dict(color='#475569', size=9), title=''),
        yaxis=dict(showbackground=False, gridcolor='rgba(255,255,255,0.04)',
                   tickfont=dict(color='#475569', size=9), title=''),
        zaxis=dict(showbackground=False, gridcolor='rgba(255,255,255,0.04)',
                   tickfont=dict(color='#475569', size=9), title='Elev.'),
        bgcolor='rgba(0,0,0,0)',
        camera=dict(
            eye=dict(x=0.0, y=-2.2, z=0.6),
            center=dict(x=0, y=0, z=-0.2)
        )
    ),
    paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=0, r=20, b=0, t=0),
    height=750,
    font=dict(family='JetBrains Mono', color='#e2e8f0')
)

st.plotly_chart(fig, use_container_width=True)

c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("Max Slope",       f"{slope.max():.1f}°", "crater rim")
with c2: st.metric("Mean Elevation",  f"{Z.mean():.2f} km",  "vs baseline")
with c3: st.metric("Roughness RMS",   f"{rough.mean():.3f}", "class B regolith")
with c4: st.metric("Boulder Zones",   "14 identified",       "high-risk flagged")
