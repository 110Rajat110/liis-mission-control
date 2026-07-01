import streamlit as st
import numpy as np
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.abspath('.'))
from core.lunar_utils import lunar_base_texture, LUNAR_GRAY, TRANS_INFERNO

st.markdown("""
<h1 style='font-family:Inter,sans-serif; font-size:2rem; font-weight:700; color:white; margin-bottom:4px;'>
  🚗 Rover Traverse Planning
</h1>
<p style='color:#64748b; font-family:Inter,sans-serif; margin:0 0 1.5rem; font-size:0.85rem;
          letter-spacing:1px; text-transform:uppercase;'>
  Hybrid A* Path &nbsp;·&nbsp; Traversability Cost Map &nbsp;·&nbsp; Kinematic Replay
</p>
""", unsafe_allow_html=True)

N = 384

@st.cache_data
def build_trav_map(N=384):
    base = lunar_base_texture(W=N, H=N, n_craters=7, seed=33)
    rng  = np.random.RandomState(33)
    # Cost: low in smooth areas, high near craters (dark/bright edges in base)
    dx   = np.gradient(base)[0]; dy = np.gradient(base)[1]
    slope_cost = np.clip(np.sqrt(dx**2 + dy**2) * 8, 0, 1).astype(np.float32)
    noise_cost = rng.uniform(0, 0.3, (N,N)).astype(np.float32)
    tmap = np.clip(0.35 + slope_cost * 0.5 + noise_cost * 0.15, 0, 1).astype(np.float32)
    return base, tmap

base, tmap = build_trav_map(N)

# A* path waypoints (pre-computed through low-cost corridor)
waypoints = np.array([
    [38,269],[58,240],[83,211],[106,189],[128,170],
    [154,160],[176,157],[198,160],[224,157],[250,154]
])

replay = st.slider("🔁 Replay step-by-step", 1, len(waypoints), len(waypoints), key="rover_step")
st.caption(f"Waypoint {replay}/{len(waypoints)} · Energy: {replay*0.47:.1f} kWh · Distance: {replay*112:.0f} m")

visible_path = waypoints[:replay]
rover_pos    = visible_path[-1]

fig = go.Figure()

# ── Lunar base texture ────────────────────────────────────────────────────────
fig.add_trace(go.Heatmap(z=base, colorscale=LUNAR_GRAY, zmin=0, zmax=1,
                         showscale=False, hoverinfo='skip'))

tmap_overlay = np.where(tmap < 0.45, np.nan, tmap)

# ── Traversability cost overlay (semi-transparent Inferno) ────────────────────
fig.add_trace(go.Heatmap(
    z=tmap_overlay, colorscale="inferno", zmin=0, zmax=1, showscale=True, opacity=0.6,
    colorbar=dict(
        title=dict(text="Traversal Cost", side="top",
                   font=dict(color='#94a3b8', size=11, family='JetBrains Mono')),
        tickfont=dict(color='#94a3b8', size=10, family='JetBrains Mono'),
        thickness=12, len=0.65, x=1.01
    ),
    hoverinfo='skip'
))

# ── Corridor highlight (wider translucent band) ──────────────────────────────
fig.add_trace(go.Scatter(
    x=waypoints[:,0], y=waypoints[:,1],
    mode='lines',
    line=dict(color='rgba(34,211,238,0.15)', width=30),
    name='Safe Corridor', hoverinfo='skip'
))

# ── Completed route ───────────────────────────────────────────────────────────
fig.add_trace(go.Scatter(
    x=visible_path[:,0], y=visible_path[:,1],
    mode='lines',
    line=dict(color='#22d3ee', width=4),
    name='Completed Route', showlegend=True
))

# ── Future (planned) route, dimmed ───────────────────────────────────────────
if replay < len(waypoints):
    fig.add_trace(go.Scatter(
        x=waypoints[replay-1:,0], y=waypoints[replay-1:,1],
        mode='lines',
        line=dict(color='rgba(34,211,238,0.22)', width=2.5, dash='dot'),
        name='Planned (ahead)', showlegend=True
    ))

# ── Waypoint dots ─────────────────────────────────────────────────────────────
fig.add_trace(go.Scatter(
    x=visible_path[:,0], y=visible_path[:,1],
    mode='markers',
    marker=dict(size=7, color='rgba(34,211,238,0.6)', line=dict(color='#22d3ee', width=1)),
    showlegend=False, hoverinfo='skip'
))

# ── Rover marker — label beside marker, not in legend corner ──────────────────
fig.add_trace(go.Scatter(
    x=[rover_pos[0]], y=[rover_pos[1]],
    mode='markers',
    marker=dict(size=18, color='#f43f5e', symbol='square',
                line=dict(color='white', width=2)),
    name='Pragyan Rover', showlegend=True,
    hovertemplate=f"ROVER · pos ({rover_pos[0]},{rover_pos[1]})<extra></extra>",
))
# Separate text annotation offset below the rover (avoids legend overlap)
fig.add_annotation(
    x=rover_pos[0], y=rover_pos[1] + 7,
    text="PRAGYAN", showarrow=False,
    font=dict(color='#f43f5e', size=9, family='JetBrains Mono'),
    bgcolor='rgba(5,7,13,0.75)',
    bordercolor='rgba(244,63,94,0.4)', borderwidth=1, borderpad=3
)

# ── Start / Target ────────────────────────────────────────────────────────────
fig.add_trace(go.Scatter(
    x=[waypoints[0,0], waypoints[-1,0]],
    y=[waypoints[0,1], waypoints[-1,1]],
    mode='markers+text',
    marker=dict(size=12, color=['#34d399','#f59e0b'], symbol='star'),
    text=["START","TARGET"], textposition=["top right","top left"],
    textfont=dict(color='white', size=9, family='JetBrains Mono'),
    showlegend=False, hoverinfo='skip'
))

fig.update_layout(
    height=530,
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=0, r=70, t=0, b=0),
    xaxis=dict(range=[0,N], showgrid=False, showticklabels=False),
    yaxis=dict(range=[N,0], showgrid=False, showticklabels=False),
    legend=dict(
        font=dict(color='#e2e8f0', family='JetBrains Mono', size=10),
        bgcolor='rgba(5,7,13,0.75)', bordercolor='rgba(34,211,238,0.2)', borderwidth=1,
        x=0.02, y=0.02, xanchor='left', yanchor='bottom'
    ),
    font=dict(family='JetBrains Mono')
)

st.plotly_chart(fig, use_container_width=True)

t1, t2, t3, t4 = st.columns(4)
with t1: st.metric("Energy Used",   f"{replay*0.47:.1f} kWh",   "of 12.0 kWh limit")
with t2: st.metric("Distance",      f"{replay*112:.0f} m",       f"waypoint {replay}/10")
with t3: st.metric("Peak Cost",     f"{tmap[waypoints[:replay,1].astype(int), waypoints[:replay,0].astype(int)].max():.2f}", "traversal index")
with t4: st.metric("ETA Target",    f"{(len(waypoints)-replay)*3.2:.0f} min", "at 0.5 cm/s speed")
