import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import plotly.graph_objects as go

# ─── Three.js Hero ───────────────────────────────────────────────────────────
HERO_HTML = """
<!DOCTYPE html>
<html>
<head>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { background:#05070d; overflow:hidden; }
  #c { width:100%; height:480px; display:block; }

  /* HUD Overlay */
  #hud {
    position:absolute; top:0; left:0; width:100%; height:480px;
    pointer-events:none; display:flex; align-items:flex-start;
    justify-content:flex-end; flex-direction:column; padding:32px 32px;
    background: linear-gradient(to top, rgba(5,7,13,1.0) 0%, rgba(5,7,13,0.85) 15%, transparent 65%);
  }
  .kpi-row { display:flex; gap:32px; margin-bottom:12px; }
  .kpi {
    display:flex; flex-direction:column;
    border-left:2px solid rgba(34,211,238,0.7); padding-left:10px;
  }
  .kpi-label {
    font-family:'JetBrains Mono',monospace; font-size:10px;
    color:rgba(34,211,238,0.6); letter-spacing:2px; text-transform:uppercase;
  }
  .kpi-value {
    font-family:'JetBrains Mono',monospace; font-size:1.5rem;
    color:#22d3ee; text-shadow: 0 0 12px rgba(34,211,238,0.8);
    font-weight:700;
  }
  .kpi-unit { font-family:'JetBrains Mono',monospace; font-size:10px; color:rgba(255,255,255,0.4); }
  h1.hero-title {
    font-family:'Inter',sans-serif; font-size:2.4rem; font-weight:700;
    color:white; letter-spacing:-1px; margin-bottom:4px;
  }
  h1.hero-title span { color:#22d3ee; }
  .hero-sub { font-family:'Inter',sans-serif; font-size:0.85rem;
    color:rgba(148,163,184,0.9); letter-spacing:1px; text-transform:uppercase;
    margin-bottom:20px;
  }

  /* scanline effect */
  #hud::before {
    content:'';
    position:absolute; top:0; left:0; width:100%; height:100%;
    background: repeating-linear-gradient(
      to bottom, transparent 0px, transparent 3px,
      rgba(34,211,238,0.015) 3px, rgba(34,211,238,0.015) 4px
    );
    pointer-events:none;
  }
</style>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
</head>
<body>
<div style="position:relative; width:100%; height:480px; overflow:hidden;">
  <canvas id="c"></canvas>
  <div id="hud">
    <div class="hero-title">LIIS <span>MISSION CONTROL</span></div>
    <div class="hero-sub">Lunar Ice Intelligence System · Chandrayaan-2 DFSAR Pipeline</div>
    <div class="kpi-row">
      <div class="kpi">
        <span class="kpi-label">Max ICI</span>
        <span class="kpi-value" id="k1">0.00</span>
        <span class="kpi-unit">INDEX</span>
      </div>
      <div class="kpi">
        <span class="kpi-label">Best LSI</span>
        <span class="kpi-value" id="k2">0.00</span>
        <span class="kpi-unit">SCORE</span>
      </div>
      <div class="kpi">
        <span class="kpi-label">Est. Ice Vol.</span>
        <span class="kpi-value" id="k3">0</span>
        <span class="kpi-unit">km³</span>
      </div>
      <div class="kpi">
        <span class="kpi-label">Path Cost</span>
        <span class="kpi-value" id="k4">0</span>
        <span class="kpi-unit">kWh</span>
      </div>
      <div class="kpi">
        <span class="kpi-label">Area Mapped</span>
        <span class="kpi-value" id="k5">0</span>
        <span class="kpi-unit">km²</span>
      </div>
    </div>
  </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
// Count-up animation
function countUp(el, target, decimals, duration) {
  let start = 0, step = target / (duration / 16);
  let timer = setInterval(() => {
    start = Math.min(start + step, target);
    el.textContent = start.toFixed(decimals);
    if (start >= target) clearInterval(timer);
  }, 16);
}
setTimeout(() => {
  countUp(document.getElementById('k1'), 0.87, 2, 1800);
  countUp(document.getElementById('k2'), 0.91, 2, 1800);
  countUp(document.getElementById('k3'), 1.24, 2, 2200);
  countUp(document.getElementById('k4'), 4.7, 1, 1600);
  countUp(document.getElementById('k5'), 147, 0, 2000);
}, 400);

// Three.js Scene
const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
renderer.setSize(canvas.parentElement.offsetWidth, 480);
renderer.setPixelRatio(window.devicePixelRatio);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(50, canvas.parentElement.offsetWidth / 480, 0.1, 100);
camera.position.set(0, 0.4, 2.8);
camera.lookAt(0, 0, 0);

// Ambient light (lowered for darker shadows)
const ambient = new THREE.AmbientLight(0x1a1a1c, 0.4);
scene.add(ambient);

// Sun-like directional light (harsh, high intensity, crisp terminator)
const sun = new THREE.DirectionalLight(0xfff5e0, 3.5);
sun.position.set(5, 0.5, 2);
sun.castShadow = true;
sun.shadow.mapSize.width = 2048;
sun.shadow.mapSize.height = 2048;
sun.shadow.camera.near = 0.5;
sun.shadow.camera.far = 15;
sun.shadow.bias = -0.001;
scene.add(sun);

// Faint blue fill for the shadowed side
const fill = new THREE.DirectionalLight(0x22d3ee, 0.12);
fill.position.set(-5, -2, -2);
scene.add(fill);

// Enable shadows
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

// Generate 4096x4096 displacement and color map using Canvas API
const TEX_SIZE = 4096;
const texCanvas = document.createElement('canvas');
texCanvas.width = TEX_SIZE; texCanvas.height = TEX_SIZE;
const ctx = texCanvas.getContext('2d');

// Base regolith - darker lunar gray for depth
ctx.fillStyle = '#6a6a6a';
ctx.fillRect(0, 0, TEX_SIZE, TEX_SIZE);

const seededRandom = (s) => {
    return function() {
        s = Math.sin(s) * 10000; return s - Math.floor(s);
    };
};
const rnd = seededRandom(42);

// Add large craters (primary impact features) - deeper shadows
for(let i=0; i<100; i++) {
    const cx = rnd() * TEX_SIZE;
    const cy = rnd() * TEX_SIZE;
    const r = 50 + rnd() * 300;
    
    const drawCrater = (x, y) => {
        const grad = ctx.createRadialGradient(x, y, 0, x, y, r*1.4);
        grad.addColorStop(0, 'rgba(35, 35, 38, 1)');
        grad.addColorStop(0.25, 'rgba(55, 55, 58, 1)');
        grad.addColorStop(0.45, 'rgba(90, 90, 95, 1)');
        grad.addColorStop(0.65, 'rgba(150, 150, 155, 1)');
        grad.addColorStop(0.8, 'rgba(180, 180, 185, 0.95)');
        grad.addColorStop(1, 'rgba(106, 106, 106, 0)');
        
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(x, y, r*1.4, 0, Math.PI*2);
        ctx.fill();
    };
    
    drawCrater(cx, cy);
    if (cx < r * 1.4) drawCrater(cx + TEX_SIZE, cy);
    if (cx > TEX_SIZE - r * 1.4) drawCrater(cx - TEX_SIZE, cy);
}

// Add medium craters for secondary detail
for(let i=0; i<350; i++) {
    const cx = rnd() * TEX_SIZE;
    const cy = rnd() * TEX_SIZE;
    const r = 12 + rnd() * 55;
    
    const drawMedCrater = (x, y) => {
        const grad = ctx.createRadialGradient(x, y, 0, x, y, r*1.25);
        grad.addColorStop(0, 'rgba(40, 40, 43, 0.9)');
        grad.addColorStop(0.3, 'rgba(65, 65, 68, 0.9)');
        grad.addColorStop(0.5, 'rgba(110, 110, 115, 0.9)');
        grad.addColorStop(0.7, 'rgba(160, 160, 165, 0.9)');
        grad.addColorStop(1, 'rgba(106, 106, 106, 0)');
        
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(x, y, r*1.25, 0, Math.PI*2);
        ctx.fill();
    };
    
    drawMedCrater(cx, cy);
    if (cx < r * 1.25) drawMedCrater(cx + TEX_SIZE, cy);
    if (cx > TEX_SIZE - r * 1.25) drawMedCrater(cx - TEX_SIZE, cy);
}

// Add small craters for fine detail
for(let i=0; i<1200; i++) {
    const cx = rnd() * TEX_SIZE;
    const cy = rnd() * TEX_SIZE;
    const r = 2 + rnd() * 10;
    
    const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, r*1.2);
    grad.addColorStop(0, 'rgba(45, 45, 48, 0.75)');
    grad.addColorStop(0.35, 'rgba(70, 70, 73, 0.75)');
    grad.addColorStop(0.55, 'rgba(120, 120, 125, 0.75)');
    grad.addColorStop(0.75, 'rgba(165, 165, 170, 0.75)');
    grad.addColorStop(1, 'rgba(106, 106, 106, 0)');
    
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(cx, cy, r*1.2, 0, Math.PI*2);
    ctx.fill();
}

// Multi-layer noise for realistic surface roughness
const imgData = ctx.getImageData(0, 0, TEX_SIZE, TEX_SIZE);
const data = imgData.data;

// Layer 1: coarse noise
for (let i = 0; i < data.length; i += 4) {
    const n = (Math.random() - 0.5) * 25;
    let v = data[i] + n;
    v = Math.max(0, Math.min(255, v));
    data[i] = v; data[i+1] = v; data[i+2] = v;
}

// Layer 2: fine detail noise
for (let i = 0; i < data.length; i += 4) {
    const n = (Math.random() - 0.5) * 12;
    let v = data[i] + n;
    v = Math.max(0, Math.min(255, v));
    data[i] = v; data[i+1] = v; data[i+2] = v;
}

ctx.putImageData(imgData, 0, 0);

// Base color texture (neutral gray with faint blue pole)
const colorCanvas = document.createElement('canvas');
colorCanvas.width = TEX_SIZE; colorCanvas.height = TEX_SIZE;
const cCtx = colorCanvas.getContext('2d');
cCtx.fillStyle = '#9a9a92';
cCtx.fillRect(0, 0, TEX_SIZE, TEX_SIZE);
cCtx.globalCompositeOperation = 'overlay';
cCtx.drawImage(texCanvas, 0, 0);
cCtx.globalCompositeOperation = 'source-over';
// South pole faint glow
const pGrad = cCtx.createRadialGradient(TEX_SIZE/2, TEX_SIZE*0.9, 10, TEX_SIZE/2, TEX_SIZE*0.9, TEX_SIZE*0.3);
pGrad.addColorStop(0, 'rgba(34,211,238,0.25)');
pGrad.addColorStop(1, 'rgba(34,211,238,0)');
cCtx.fillStyle = pGrad;
cCtx.fillRect(0, 0, TEX_SIZE, TEX_SIZE);

const displacementMap = new THREE.CanvasTexture(texCanvas);
const colorMap = new THREE.CanvasTexture(colorCanvas);

const geo = new THREE.SphereGeometry(1, 512, 512);
const mat = new THREE.MeshStandardMaterial({
  map: colorMap,
  displacementMap: displacementMap,
  displacementScale: 0.02,
  bumpMap: displacementMap,
  bumpScale: 0.02,
  roughness: 1.0,
  metalness: 0.0
});

const moon = new THREE.Mesh(geo, mat);
moon.castShadow = true;
moon.receiveShadow = true;
scene.add(moon);

// Stars
const starGeo = new THREE.BufferGeometry();
const starVerts = [];
for (let i = 0; i < 2000; i++) {
  starVerts.push((Math.random()-0.5)*100, (Math.random()-0.5)*100, (Math.random()-0.5)*100);
}
starGeo.setAttribute('position', new THREE.Float32BufferAttribute(starVerts, 3));
const starMat = new THREE.PointsMaterial({ color:0xffffff, size:0.08, transparent:true, opacity:0.7 });
scene.add(new THREE.Points(starGeo, starMat));

// Initial rotation to show terminator and craters
moon.rotation.y = 1.8;
moon.rotation.x = -0.4;
moon.rotation.z = 0.2;

// Render loop
function animate() {
  requestAnimationFrame(animate);
  moon.rotation.y += 0.0010; // Slower rotation
  renderer.render(scene, camera);
}
animate();

window.addEventListener('resize', () => {
  const w = canvas.parentElement.offsetWidth;
  renderer.setSize(w, 480);
  camera.aspect = w / 480;
  camera.updateProjectionMatrix();
});
</script>
</body>
</html>
"""

components.html(HERO_HTML, height=480, scrolling=False)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Quick Nav Cards ──────────────────────────────────────────────────────────
st.markdown("""
<div style="margin: 1rem 0 0.5rem;">
  <span style="font-family:'Inter',sans-serif; font-size:0.75rem; letter-spacing:2px; text-transform:uppercase; color:#94a3b8;">
    MISSION MODULES
  </span>
</div>
""", unsafe_allow_html=True)

# Mini sparkline data
np.random.seed(77)
def mini_spark(label, vals, color):
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=vals, mode='lines', line=dict(color=color, width=2),
                             fill='tozeroy', fillcolor=color.replace('1)', '0.1)') if 'rgba' in color else color))
    fig.update_layout(height=60, margin=dict(l=0,r=0,t=0,b=0),
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      xaxis=dict(visible=False), yaxis=dict(visible=False), showlegend=False)
    return fig

cards = [
    ("📡 Radar Analysis", "L-band SAR · CPR · DOP · Polarimetry", np.random.uniform(0.8,2.0,20), "#22d3ee"),
    ("🏔️ Terrain Analysis", "OHRC DEM · Slope · Craters · Roughness", np.random.uniform(0.2,1.0,20), "#a78bfa"),
    ("❄️ Ice Confidence", "ICI live weights · Pixel explainer", np.random.uniform(0.3,0.9,20), "#34d399"),
    ("🎯 Landing Site", "LSI ranked · 3D site overlay", np.random.uniform(0.4,1.0,20), "#f59e0b"),
    ("🚗 Rover Traverse", "A* path · Traversability · Replay", np.random.uniform(0.1,0.8,20), "#f43f5e"),
    ("📦 Ice Volume", "P10/P50/P90 · 3D mesh", np.random.uniform(0.5,1.2,20), "#818cf8"),
]

cols = st.columns(3)
for i, (title, desc, vals, clr) in enumerate(cards):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="glass-card" style="border-color: {clr}33;">
          <div style="font-family:'Inter',sans-serif; font-size:1rem; font-weight:600; color:white; margin-bottom:4px;">{title}</div>
          <div style="font-size:0.78rem; color:#64748b; margin-bottom:8px;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(mini_spark(title, vals, clr), use_container_width=True, key=f"spark_{i}")
