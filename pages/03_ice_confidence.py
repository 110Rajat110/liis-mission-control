import streamlit as st
import numpy as np
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.abspath('.'))
from core.lunar_utils import lunar_base_texture, noisy_hotspot, LUNAR_GRAY, TRANS_ICI

st.markdown("""
<h1 style='font-family:Inter,sans-serif; font-size:2rem; font-weight:700; color:white; margin-bottom:4px;'>
  ❄️ Ice Confidence Index
</h1>
<p style='color:#64748b; font-family:Inter,sans-serif; margin:0 0 1rem; font-size:0.85rem;
          letter-spacing:1px; text-transform:uppercase;'>
  ICI = wR·R + wT·T + wI·I + wM·M &nbsp;·&nbsp; Live Recompute &nbsp;·&nbsp; Pixel Explainer
</p>
""", unsafe_allow_html=True)

N = 384

@st.cache_data
def build_evidence_maps(N=384):
    base = lunar_base_texture(W=N, H=N, n_craters=12, seed=42)
    spot = noisy_hotspot(N, N, 0.6, 0.55, 0.16, peak=1.0, noise_scale=0.45, seed=13)
    rng = np.random.RandomState(77)
    R = np.clip(base * 0.5 + spot * 0.55 + rng.normal(0, 0.04, (N,N)), 0, 1).astype(np.float32)
    T = np.clip(base * 0.45 + spot * 0.40 + rng.normal(0, 0.05, (N,N)), 0, 1).astype(np.float32)
    I = np.clip(base * 0.40 + spot * 0.38 + rng.normal(0, 0.06, (N,N)), 0, 1).astype(np.float32)
    M = np.clip(base * 0.35 + spot * 0.30 + rng.normal(0, 0.04, (N,N)), 0, 1).astype(np.float32)
    return R, T, I, M, base

R_map, T_map, I_map, M_map, base = build_evidence_maps(N)

# ── Weight sliders ────────────────────────────────────────────────────────────
st.markdown("### ⚙️ Evidence Weights")
wcols = st.columns(4)
with wcols[0]: wR = st.slider("wR · Radar",        0.0, 1.0, 0.35, 0.05, key="wR")
with wcols[1]: wT = st.slider("wT · Terrain",      0.0, 1.0, 0.25, 0.05, key="wT")
with wcols[2]: wI = st.slider("wI · Illumination", 0.0, 1.0, 0.25, 0.05, key="wI")
with wcols[3]: wM = st.slider("wM · Mission",      0.0, 1.0, 0.15, 0.05, key="wM")

total = wR + wT + wI + wM
if total < 0.01: total = 1.0
wR, wT, wI, wM = wR/total, wT/total, wI/total, wM/total

ICI = np.clip(wR*R_map + wT*T_map + wI*I_map + wM*M_map, 0, 1)

# ── Stats bar ─────────────────────────────────────────────────────────────────
s1, s2, s3, s4 = st.columns(4)
with s1: st.metric("Max ICI",   f"{ICI.max():.3f}",  "peak confidence")
with s2: st.metric("Mean ICI",  f"{ICI.mean():.3f}", "global average")
with s3: st.metric("Area >0.7", f"{(ICI>0.7).sum()*0.09:.1f} km²", "high-conf zone")
with s4: st.metric("Weights",   f"R{wR:.2f}/T{wT:.2f}/I{wI:.2f}/M{wM:.2f}", "normalised")

col_map, col_explain = st.columns([2, 1])

with col_map:
    fig = go.Figure()

    # Base lunar texture
    fig.add_trace(go.Heatmap(
        z=base, colorscale=LUNAR_GRAY, zmin=0, zmax=1,
        showscale=False, hoverinfo='skip'
    ))

    # Mask low values to np.nan so they are 100% transparent in Plotly
    ici_overlay = np.where(ICI < 0.35, np.nan, ICI)

    # ICI overlay 
    fig.add_trace(go.Heatmap(
        z=ici_overlay, colorscale="RdBu_r", zmin=0, zmax=1,
        showscale=True, opacity=0.75,
        colorbar=dict(
            title=dict(text="ICI Score", side="top",
                       font=dict(color='#94a3b8', size=11, family='JetBrains Mono')),
            tickfont=dict(color='#94a3b8', size=10, family='JetBrains Mono'),
            thickness=12, len=0.75, x=1.01
        ),
        hovertemplate="Lon: %{x}<br>Lat: %{y}<br>ICI: %{z:.3f}<extra></extra>"
    ))

    # Isopleth Contour line around high-confidence region
    fig.add_trace(go.Contour(
        z=ICI,
        contours=dict(start=0.7, end=0.7, size=1),
        contours_coloring='lines',
        line=dict(color='#22d3ee', width=1.5, dash='dash'),
        showscale=False, hoverinfo='skip'
    ))

    # Leader line pointing to the centroid
    cx, cy = int(0.61 * N), int(0.53 * N)
    fig.add_annotation(
        x=cx, y=cy,
        text="Target Candidate",
        font=dict(color="#22d3ee", size=10, family="JetBrains Mono"),
        showarrow=True, arrowhead=2, arrowcolor="#22d3ee", arrowsize=1, arrowwidth=1.5,
        ax=45, ay=-35,
        bgcolor="rgba(11,15,26,0.8)", bordercolor="rgba(34,211,238,0.5)", borderpad=4
    )

    fig.update_layout(
        height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0,r=60,t=0,b=0),
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=False, showticklabels=False),
        font=dict(family='JetBrains Mono')
    )
    st.plotly_chart(fig, use_container_width=True)

with col_explain:
    # Pixel explainer for centre of hotspot
    px, py = int(0.61 * N), int(0.53 * N)
    pr = float(R_map[py, px]); pt = float(T_map[py, px])
    pi = float(I_map[py, px]); pm = float(M_map[py, px])
    ici_px = wR*pr + wT*pt + wI*pi + wM*pm

    st.markdown(f"""
    <div style="background:rgba(11,15,26,0.85); border:1px solid rgba(34,211,238,0.2);
                border-radius:10px; padding:16px; font-family:'JetBrains Mono',monospace;">
      <div style="color:#22d3ee; font-size:0.75rem; letter-spacing:2px; text-transform:uppercase; margin-bottom:12px;">
        ● PIXEL ({px}, {py}) EXPLAINED
      </div>
    """, unsafe_allow_html=True)

    scores = [
        ("Radar R",       pr, wR, "#22d3ee"),
        ("Terrain T",     pt, wT, "#a78bfa"),
        ("Illumination I",pi, wI, "#34d399"),
        ("Mission M",     pm, wM, "#f59e0b"),
    ]

    bfig = go.Figure()
    for label, score, weight, color in scores:
        bfig.add_trace(go.Bar(
            y=[label], x=[score * weight],
            orientation='h', marker=dict(color=color, opacity=0.8),
            hovertemplate=f"{label}: {score:.2f} × {weight:.2f} = {score*weight:.3f}<extra></extra>",
            name=label, text=[f"{score*weight:.3f}"],
            textfont=dict(color='white', size=9), textposition='inside'
        ))
    bfig.update_layout(
        height=200, barmode='stack',
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0,r=0,t=0,b=0),
        xaxis=dict(range=[0,1], showgrid=False, tickfont=dict(color='#64748b', size=9)),
        yaxis=dict(showgrid=False, tickfont=dict(color='#94a3b8', size=9)),
        showlegend=False, font=dict(family='JetBrains Mono')
    )
    st.plotly_chart(bfig, use_container_width=True, key="ici_explain")

    verdict = "✅ HIGH CONFIDENCE — ice deposit likely" if ici_px > 0.65 else \
              "⚠️ MODERATE — further investigation" if ici_px > 0.4 else "❌ LOW CONFIDENCE"
    clr = "#34d399" if ici_px > 0.65 else "#f59e0b" if ici_px > 0.4 else "#f43f5e"

    st.markdown(f"""
    <div style="padding:12px; background:rgba(34,211,238,0.06);
                border-radius:8px; border:1px solid rgba(34,211,238,0.2); margin-top:8px;">
      <div style="color:#22d3ee; font-size:1.6rem; font-weight:700;">{ici_px:.3f}</div>
      <div style="color:#94a3b8; font-size:0.72rem;">Final ICI Score</div>
      <div style="color:{clr}; font-size:0.8rem; margin-top:6px;">{verdict}</div>
    </div>
    </div>
    """, unsafe_allow_html=True)
