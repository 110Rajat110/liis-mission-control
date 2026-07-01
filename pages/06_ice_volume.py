import streamlit as st
import numpy as np
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.abspath('.'))
from config.constants import IceVolumeConfig, ColorConfig
from core.error_handling import clamp_value

st.markdown("""
<h1 style='font-family:Inter,sans-serif; font-size:2rem; font-weight:700; color:white; margin-bottom:4px;'>
  📦 Ice Volume Estimation
</h1>
<p style='color:#64748b; font-family:Inter,sans-serif; margin:0 0 1.5rem; font-size:0.85rem;
          letter-spacing:1px; text-transform:uppercase;'>
  Area × Depth × Ice Fraction · P10/P50/P90 Uncertainty · 3D Ice Mesh
</p>
""", unsafe_allow_html=True)

ctrl1, ctrl2 = st.columns(2)
with ctrl1: 
    depth_m = st.slider(
        "Assumed Ice Depth (m)",
        IceVolumeConfig.MIN_DEPTH_M,
        IceVolumeConfig.MAX_DEPTH_M,
        IceVolumeConfig.DEFAULT_DEPTH_M,
        0.1
    )
with ctrl2: 
    ice_frac = st.slider(
        "Ice Fraction (φ)",
        IceVolumeConfig.MIN_ICE_FRACTION,
        IceVolumeConfig.MAX_ICE_FRACTION,
        IceVolumeConfig.DEFAULT_ICE_FRACTION,
        0.05
    )

# Validate and clamp values
depth_m = clamp_value(depth_m, IceVolumeConfig.MIN_DEPTH_M, IceVolumeConfig.MAX_DEPTH_M)
ice_frac = clamp_value(ice_frac, IceVolumeConfig.MIN_ICE_FRACTION, IceVolumeConfig.MAX_ICE_FRACTION)

area_km2 = IceVolumeConfig.DEFAULT_AREA_KM2
density = IceVolumeConfig.ICE_DENSITY_KG_M3
vol_p50 = area_km2 * 1e6 * depth_m * ice_frac
mass_p50 = vol_p50 * density / 1e6
vol_p10 = vol_p50 * IceVolumeConfig.P10_FACTOR
vol_p90 = vol_p50 * IceVolumeConfig.P90_FACTOR

m1,m2,m3,m4 = st.columns(4)
with m1: st.metric("P50 Volume", f"{vol_p50/1e6:.2f} km³",  f"depth={depth_m}m")
with m2: st.metric("P50 Mass",   f"{mass_p50/1e6:.2f} Mt",  "× 10⁶ tonnes")
with m3: st.metric("Area",       f"{area_km2} km²",          "Haworth-A sector")
with m4: st.metric("Ice φ",      f"{ice_frac:.0%}",          f"{ice_frac*100:.0f}% purity")

col3d, colbar = st.columns([3, 2])

with col3d:
    theta    = np.linspace(0, 2*np.pi, 72)
    r_base   = np.sqrt(area_km2 / np.pi)
    depth_km = depth_m / 1000

    T, Z_wall = np.meshgrid(theta, [0, -depth_km])
    X_wall = r_base * np.cos(T)
    Y_wall = r_base * np.sin(T)

    # Cap grids
    r_grid = np.linspace(0, r_base, 24)
    T2, R2 = np.meshgrid(theta, r_grid)
    X_cap  = R2 * np.cos(T2)
    Y_cap  = R2 * np.sin(T2)

    fig3d = go.Figure()

    # ── Side wall — glassy gradient top=light bottom=darker ──────────────
    fig3d.add_trace(go.Surface(
        x=X_wall, y=Y_wall, z=Z_wall,
        colorscale=[[0,'rgba(186,230,253,0.55)'],[1,'rgba(14,165,233,0.25)']],
        showscale=False, opacity=0.45,
        lighting=dict(ambient=0.5, diffuse=0.8, specular=0.6, fresnel=0.4, roughness=0.15),
        lightposition=dict(x=100,y=200,z=200)
    ))

    # ── Regolith surface cap (semi-opaque grey) ───────────────────────────
    fig3d.add_trace(go.Surface(
        x=X_cap, y=Y_cap, z=np.zeros_like(R2),
        colorscale=[[0,'rgba(100,116,139,0.3)'],[1,'rgba(148,163,184,0.45)']],
        showscale=False, opacity=0.38
    ))

    # ── Ice base cap — glowing bright cyan ───────────────────────────────
    fig3d.add_trace(go.Surface(
        x=X_cap, y=Y_cap, z=np.full_like(R2, -depth_km),
        colorscale=[[0,'rgba(103,232,249,0.6)'],[1,'rgba(34,211,238,0.9)']],
        showscale=False, opacity=0.75,
        lighting=dict(ambient=0.6, diffuse=0.7, specular=0.8, fresnel=0.6)
    ))

    # ── Depth label ───────────────────────────────────────────────────────
    fig3d.add_trace(go.Scatter3d(
        x=[0], y=[r_base*1.1], z=[-depth_km/2],
        mode='text', text=[f"▲ {depth_m}m depth"],
        textfont=dict(color='#67e8f9', size=11, family='JetBrains Mono')
    ))

    fig3d.update_layout(
        scene=dict(
            xaxis=dict(title='km', gridcolor='rgba(255,255,255,0.04)',
                       tickfont=dict(color='#475569', size=9)),
            yaxis=dict(title='km', gridcolor='rgba(255,255,255,0.04)',
                       tickfont=dict(color='#475569', size=9)),
            zaxis=dict(title='Depth (km)', gridcolor='rgba(255,255,255,0.04)',
                       tickfont=dict(color='#475569', size=9)),
            bgcolor='rgba(0,0,0,0)',
            camera=dict(eye=dict(x=1.4, y=1.1, z=0.75))
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        height=430, margin=dict(l=0,r=0,t=0,b=0),
        font=dict(family='JetBrains Mono')
    )
    st.plotly_chart(fig3d, use_container_width=True)

with colbar:
    labels  = ["P10 (Conservative)", "P50 (Best Estimate)", "P90 (Optimistic)"]
    volumes = [vol_p10/1e6, vol_p50/1e6, vol_p90/1e6]
    colors  = ["#475569", "#22d3ee", "#a78bfa"]

    bfig = go.Figure(go.Bar(
        x=labels, y=volumes,
        marker=dict(color=colors, opacity=0.85, line=dict(color=colors, width=1.5)),
        text=[f"{v:.2f} km³" for v in volumes],
        textposition='outside',
        textfont=dict(color='white', family='JetBrains Mono', size=11)
    ))
    bfig.add_hline(y=vol_p50/1e6, line=dict(color='#22d3ee', dash='dot', width=1.5),
                   annotation_text="P50", annotation_font=dict(color='#22d3ee', size=9))
    bfig.update_layout(
        height=430, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0,r=0,t=30,b=0),
        xaxis=dict(showgrid=False, tickfont=dict(color='#94a3b8', family='JetBrains Mono', size=10)),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)',
                   tickfont=dict(color='#64748b', size=9),
                   title=dict(text='Volume (km³)', font=dict(color='#64748b', size=10))),
        font=dict(family='JetBrains Mono')
    )
    st.plotly_chart(bfig, use_container_width=True)

st.markdown(f"""
<div style="background:rgba(34,211,238,0.04); border:1px solid rgba(34,211,238,0.2);
            border-radius:8px; padding:12px 18px; font-family:'JetBrains Mono',monospace;
            font-size:0.82rem;">
  <span style="color:#22d3ee;">REPORT:</span>
  <span style="color:#94a3b8; margin-left:8px;">
    At φ={ice_frac:.0%} fraction and {depth_m}m depth — Haworth-A deposit contains
    <strong style="color:white;">{mass_p50/1e6:.2f} Mt</strong> water-ice equivalent
    (P10={vol_p10/1e6:.2f} – P90={vol_p90/1e6:.2f} km³). Sufficient for ISRO base operations.
  </span>
</div>
""", unsafe_allow_html=True)
