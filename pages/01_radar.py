import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys, os
sys.path.insert(0, os.path.abspath('.'))
from core.lunar_utils import lunar_base_texture, noisy_hotspot, LUNAR_GRAY

st.markdown("""
<style>
/* Single-pass sweep scan animation */
@keyframes radar-sweep {
  0% { transform: translateY(-100%); opacity: 0; }
  10% { opacity: 0.8; }
  90% { opacity: 0.8; }
  100% { transform: translateY(600px); opacity: 0; }
}
.scan-line {
  position: absolute; top: 0; left: 0; width: 100%; height: 2px;
  background: rgba(34, 211, 238, 0.8);
  box-shadow: 0 0 15px rgba(34, 211, 238, 0.5);
  animation: radar-sweep 2.5s ease-out forwards;
  pointer-events: none; z-index: 100;
}
.inset-panel {
  border: 1px solid rgba(255,255,255,0.1); border-radius: 4px;
  background: black; padding: 4px; display: inline-block;
  margin-right: 8px;
}
.inset-panel img { width: 80px; height: 80px; object-fit: cover; opacity: 0.8; filter: grayscale(100%); }
.inset-label { font-size: 0.65rem; color: #94a3b8; font-family: 'JetBrains Mono', monospace; text-align: center; margin-top: 4px; }
</style>
<div style="position:relative;">
  <div class="scan-line"></div>
</div>

<h1 style='font-family:Inter,sans-serif; font-size:2rem; font-weight:700; color:white; margin-bottom:4px;'>
  📡 Radar Analysis
</h1>
<p style='color:#64748b; font-family:Inter,sans-serif; margin:0 0 1.5rem; font-size:0.85rem;
          letter-spacing:1px; text-transform:uppercase;'>
  DFSAR L-Band · CPR · DOP · SAR Speckle Simulation
</p>
""", unsafe_allow_html=True)

# ── Cached data generation ────────────────────────────────────────────────────
@st.cache_data
def build_radar_maps(N=384):
    np.random.seed(42)
    base = lunar_base_texture(W=N, H=N, n_craters=18, seed=42)
    spot = noisy_hotspot(N, N, cx_frac=0.6, cy_frac=0.55, radius_frac=0.15,
                         peak=1.0, noise_scale=0.4, seed=11)

    # Multiplicative SAR Speckle (Rayleigh distributed-ish noise)
    speckle = np.random.rayleigh(scale=1.0, size=(N, N)).astype(np.float32)
    speckle = np.clip(speckle / speckle.mean(), 0.5, 2.0)

    # CPR: 0.7–2.2, anomaly pushes toward ~1.9. Speckled.
    cpr = np.clip((0.75 + base * 0.55 + spot * 0.85) * speckle, 0.5, 2.3)

    # DOP: 0–1
    dop = np.clip((0.2 + base * 0.45 + spot * 0.40) * speckle, 0.0, 1.0)

    # HH backscatter: -20 to 0 dB
    hh = np.clip(-16 + base * 10 + spot * 9 + np.random.normal(0, 1.2, (N, N)), -20, 0)

    # Polarimetric decomposition: 0–1
    pd = np.clip((0.1 + base * 0.5 + spot * 0.38) * speckle, 0.0, 1.0)

    return base, cpr, dop, hh, pd, speckle

base, cpr, dop, hh, pd, speckle = build_radar_maps()

# ── Live Interpretation Panel ──────────────────────────────────────────────────
import base64
from io import BytesIO
from PIL import Image

# Generate TMC inset from base texture (80x80 crop)
tmc_crop = (np.clip(base[150:230, 150:230], 0, 1) * 255).astype(np.uint8)
img = Image.fromarray(tmc_crop, mode='L')
buffered = BytesIO()
img.save(buffered, format="PNG")
tmc_b64 = base64.b64encode(buffered.getvalue()).decode()

# SVG for SAR noise, base64 encoded to avoid CSS string escape bugs
sar_svg = '<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><filter id="noise"><feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="3" stitchTiles="stitch"/></filter><rect width="100%" height="100%" filter="url(#noise)" opacity="0.6"/></svg>'
sar_b64 = base64.b64encode(sar_svg.encode()).decode()

st.markdown(f"""
<div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:1rem;">
  <div style="background:rgba(11,15,26,0.9); border:1px solid rgba(34,211,238,0.3); border-radius:8px; padding:12px 16px; flex-grow:1; margin-right:20px;">
    <div style="font-family:'JetBrains Mono',monospace; font-size:0.75rem; color:#22d3ee; letter-spacing:1px; margin-bottom:8px;">
      INTERPRETATION LOGIC [L-BAND]
    </div>
    <div style="font-family:Inter,sans-serif; font-size:0.9rem; color:#e2e8f0; line-height:1.5;">
      <strong>Anomaly Detected:</strong> Region (230, 192) exhibits <span style="color:#22d3ee;">CPR > 1.2</span> and <span style="color:#22d3ee;">DOP < 0.4</span>.<br>
      <span style="color:#94a3b8; font-size:0.8rem;">Conclusion: High volumetric scattering with low depolarization is consistent with thick subsurface water-ice deposits. Not characteristic of surface rock clutter (which would show high DOP).</span>
    </div>
  </div>
  <div style="display:flex;">
    <div class="inset-panel">
      <div style="width:80px; height:80px; background:url('data:image/png;base64,{tmc_b64}'); background-size:cover;"></div>
      <div class="inset-label">TMC OPTICAL</div>
    </div>
    <div class="inset-panel">
      <div style="width:80px; height:80px; background:url('data:image/svg+xml;base64,{sar_b64}') black;"></div>
      <div class="inset-label">SAR RAW</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── 2×2 subplot grid ─────────────────────────────────────────────────────────
panels = [
    ("CPR (Ice > 1.2)",    cpr,  "Viridis",  0.5,  2.3, 1.2),
    ("DOP",                dop,  "Plasma",   0.0,  1.0, None),
    ("HH Backscatter (dB)",hh,   "Greys",  -20.0,  0.0, None),
    ("Polarimetric",       pd,   "Cividis",  0.0,  1.0, None),
]

fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=["CPR (Circ. Pol. Ratio)", "DOP (Degree of Polarisation)",
                    "HH Backscatter (dB)", "Polarimetric Decomposition"],
    horizontal_spacing=0.10,
    vertical_spacing=0.12,
)

for i, (label, data, scale, zmin, zmax, threshold) in enumerate(panels):
    r, c = divmod(i, 2)
    cb_x = 0.44 if c == 0 else 1.01
    cb_y = 0.80 if r == 0 else 0.21
    
    colorbar_dict = dict(
        x=cb_x, y=cb_y, len=0.38, thickness=11,
        title=dict(text=label, side="top", font=dict(color='#94a3b8', size=10, family='JetBrains Mono')),
        tickfont=dict(color='#94a3b8', size=9, family='JetBrains Mono'),
    )
    
    if threshold is not None:
        colorbar_dict['tickvals'] = [zmin, threshold, zmax]
        colorbar_dict['ticktext'] = [f"{zmin}", f"{threshold} (ICE)", f"{zmax}"]

    fig.add_trace(
        go.Heatmap(
            z=data, colorscale=scale, zmin=zmin, zmax=zmax, showscale=True,
            colorbar=colorbar_dict,
            hovertemplate=f"<b>{label}</b><br>x: %{{x}}<br>y: %{{y}}<br>val: %{{z:.3f}}<extra></extra>",
        ),
        row=r+1, col=c+1
    )

for r in [1, 2]:
    for c in [1, 2]:
        fig.add_shape(type="circle", x0=192, y0=134, x1=288, y1=250,
                      line=dict(color="rgba(34,211,238,0.7)", width=1.5, dash="dot"),
                      row=r, col=c)

fig.update_layout(
    height=680, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='JetBrains Mono', color='#e2e8f0'), margin=dict(l=0, r=70, t=45, b=10),
)

for ann in fig.layout.annotations:
    ann.font.update(color='#94a3b8', size=11, family='JetBrains Mono')

for axis in ['xaxis','xaxis2','xaxis3','xaxis4','yaxis','yaxis2','yaxis3','yaxis4']:
    fig.layout[axis].update(showgrid=False, showticklabels=False, linecolor='rgba(34,211,238,0.05)')

st.plotly_chart(fig, use_container_width=True)
