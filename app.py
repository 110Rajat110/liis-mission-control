import streamlit as st
from streamlit_option_menu import option_menu
import os

# Must be the first Streamlit command
st.set_page_config(
    page_title="LIIS Mission Control",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide default Streamlit UI and enforce Theme
st.markdown("""
<style>
    /* ── Starfield background on EVERY page ───────────────────────────── */
    [data-testid="stAppViewContainer"] {
        background-color: #05070d;
        background-image:
            radial-gradient(1px 1px at 12% 8%,  rgba(255,255,255,0.55) 0%, transparent 100%),
            radial-gradient(1px 1px at 34% 22%, rgba(255,255,255,0.40) 0%, transparent 100%),
            radial-gradient(1px 1px at 56% 5%,  rgba(255,255,255,0.50) 0%, transparent 100%),
            radial-gradient(1px 1px at 78% 18%, rgba(255,255,255,0.35) 0%, transparent 100%),
            radial-gradient(1px 1px at 91% 42%, rgba(255,255,255,0.45) 0%, transparent 100%),
            radial-gradient(1px 1px at 5%  65%, rgba(255,255,255,0.40) 0%, transparent 100%),
            radial-gradient(1px 1px at 23% 78%, rgba(255,255,255,0.30) 0%, transparent 100%),
            radial-gradient(1px 1px at 47% 88%, rgba(255,255,255,0.45) 0%, transparent 100%),
            radial-gradient(1px 1px at 68% 72%, rgba(255,255,255,0.35) 0%, transparent 100%),
            radial-gradient(1px 1px at 85% 95%, rgba(255,255,255,0.50) 0%, transparent 100%),
            radial-gradient(2px 2px at 19% 45%, rgba(255,255,255,0.20) 0%, transparent 100%),
            radial-gradient(2px 2px at 63% 33%, rgba(255,255,255,0.18) 0%, transparent 100%),
            radial-gradient(circle at 15% 50%, rgba(34,211,238,0.03) 0%, transparent 25%),
            radial-gradient(circle at 85% 30%, rgba(34,211,238,0.04) 0%, transparent 25%);
    }

    /* ── Sidebar ──────────────────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background-color: #0b0f1a;
        border-right: 1px solid rgba(34, 211, 238, 0.1);
    }
    [data-testid="stHeader"] { background-color: transparent; }

    /* ── Hide default nav ─────────────────────────────────────────────── */
    [data-testid="stSidebarNav"] { display: none !important; }

    /* ── Glassmorphism cards ──────────────────────────────────────────── */
    .glass-card {
        background: rgba(11, 15, 26, 0.6);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(34, 211, 238, 0.15);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 30px rgba(0,0,0,0.5), inset 0 0 20px rgba(34,211,238,0.02);
        margin-bottom: 1rem;
    }

    /* ── Fonts ────────────────────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=JetBrains+Mono:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    h1, h2, h3 { font-weight: 600; letter-spacing: -0.5px; }

    /* ── st.metric styling ────────────────────────────────────────────── */
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace;
        color: #22d3ee !important;
        font-size: 1.8rem !important;
        text-shadow: 0 0 10px rgba(34,211,238,0.3);
    }
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 1px;
    }

    /* ── Plotly panel border radius ───────────────────────────────────── */
    .stPlotlyChart {
        border: 1px solid rgba(34,211,238,0.08);
        border-radius: 10px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# ── Page routing map ───────────────────────────────────────────────────────────
pages = {
    "Home":             "pages/00_home.py",
    "Radar Analysis":   "pages/01_radar.py",
    "Terrain Analysis": "pages/02_terrain.py",
    "Ice Confidence":   "pages/03_ice_confidence.py",
    "Landing Site":     "pages/04_landing_site.py",
    "Rover Traverse":   "pages/05_rover_traverse.py",
    "Ice Volume":       "pages/06_ice_volume.py",
    "Mission Summary":  "pages/07_mission_summary.py",
}

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div style='text-align:center; padding: 12px 0 20px; font-family:Inter,sans-serif;'>"
        "<span style='font-size:1.5rem; font-weight:700; color:white;'>L<span style='color:#22d3ee;'>II</span>S</span>"
        "<div style='font-size:0.65rem; color:#475569; letter-spacing:2px; text-transform:uppercase; margin-top:2px;'>MISSION CONTROL</div>"
        "</div>",
        unsafe_allow_html=True
    )

    selected = option_menu(
        menu_title=None,
        options=list(pages.keys()),
        icons=["house-fill","broadcast","layers-fill","snow","geo-alt-fill","truck","box-fill","bar-chart-fill"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container":         {"padding": "0!important", "background-color": "transparent"},
            "icon":              {"color": "#64748b", "font-size": "0.95rem"},
            "nav-link":          {"color": "#cbd5e1", "font-size": "0.88rem", "text-align": "left",
                                  "margin": "1px 0", "border-radius": "7px", "padding": "8px 12px"},
            "nav-link-selected": {"background-color": "rgba(34,211,238,0.1)", "color": "#22d3ee",
                                  "border": "1px solid rgba(34,211,238,0.35)"},
        }
    )

    # ── Status footer — flows naturally below nav ─────────────────────────
    st.markdown("""
    <div style="margin-top: 2rem; border-top: 1px solid rgba(255,255,255,0.07);
                padding-top: 14px; padding-left: 4px;">
      <div style="font-family:'JetBrains Mono',monospace; font-size:0.72rem;
                  color:#475569; line-height:2;">
        <div>🛰️ &nbsp;<span style="color:#22d3ee;">CHANDRAYAAN-2</span> &nbsp;·&nbsp; DFSAR</div>
        <div>📡 &nbsp;UPLINK &nbsp;
          <span style="background:rgba(52,211,153,0.15); color:#34d399; border:1px solid rgba(52,211,153,0.4);
                       padding:1px 8px; border-radius:100px; font-size:0.65rem; letter-spacing:1px;">
            NOMINAL
          </span>
        </div>
        <div>🌑 &nbsp;89.9°S · SOUTH POLE</div>
        <div style="margin-top:8px; color:#334155;">2026-07-01 · MET+312d</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── Execute selected page ──────────────────────────────────────────────────────
page_path = pages[selected]
if os.path.exists(page_path):
    with open(page_path, encoding='utf-8') as f:
        code = compile(f.read(), page_path, 'exec')
        exec(code, globals())
else:
    st.error(f"Page '{page_path}' not found.")
