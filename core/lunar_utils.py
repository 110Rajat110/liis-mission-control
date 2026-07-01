"""
Shared utilities for LIIS — lunar base texture, noise generation, and shared styling.
All map pages import from here for visual consistency.
"""
import numpy as np
from typing import Tuple

def _hash(n: int) -> int:
    """Simple integer hash for reproducible noise."""
    n = ((n >> 16) ^ n) * 0x45d9f3b
    n = ((n >> 16) ^ n) * 0x45d9f3b
    n = (n >> 16) ^ n
    return n & 0xFFFFFF


def _smoothstep(t: np.ndarray) -> np.ndarray:
    return t * t * (3 - 2 * t)


def _lerp(a: np.ndarray, b: np.ndarray, t: np.ndarray) -> np.ndarray:
    return a + t * (b - a)


def value_noise_2d(W: int, H: int, scale: int = 8, octaves: int = 5, 
                  persistence: float = 0.5, lacunarity: float = 2.0, 
                  seed: int = 0) -> np.ndarray:
    """
    Fast value-noise (no scipy dependency). Returns array [H, W] in [0, 1].
    
    Args:
        W: Width of the output array
        H: Height of the output array
        scale: Base scale for noise
        octaves: Number of octaves for fractal noise
        persistence: Amplitude decay per octave
        lacunarity: Frequency growth per octave
        seed: Random seed for reproducibility
        
    Returns:
        2D numpy array of shape (H, W) with values in [0, 1]
    """
    np.random.seed(seed)
    result = np.zeros((H, W), dtype=np.float32)
    amp = 1.0
    freq = 1.0
    max_val = 0.0
    for _ in range(octaves):
        # Grid size for this octave
        gw = max(2, int(W / scale * freq) + 2)
        gh = max(2, int(H / scale * freq) + 2)
        grid = np.random.rand(gh, gw).astype(np.float32)

        # Interpolate grid → image
        xs = np.linspace(0, gw - 1, W)
        ys = np.linspace(0, gh - 1, H)
        xi = xs.astype(int); xf = xs - xi
        yi = ys.astype(int); yf = ys - yi
        xi = np.clip(xi, 0, gw - 2)
        yi = np.clip(yi, 0, gh - 2)

        tx = _smoothstep(xf)
        ty = _smoothstep(yf)

        # Bilinear interpolation
        c00 = grid[np.ix_(yi,   xi)]
        c10 = grid[np.ix_(yi,   xi+1)]
        c01 = grid[np.ix_(yi+1, xi)]
        c11 = grid[np.ix_(yi+1, xi+1)]
        layer = _lerp(_lerp(c00, c10, tx), _lerp(c01, c11, tx), ty[:, None])

        result += layer * amp
        max_val += amp
        amp      *= persistence
        freq     *= lacunarity

    return (result / max_val).astype(np.float32)


def lunar_base_texture(W: int = 200, H: int = 200, n_craters: int = 10, 
                      seed: int = 42) -> np.ndarray:
    """
    Generate a realistic grayscale lunar regolith texture as a float32 [H,W] array in [0,1].
    Uses layered value-noise + explicit crater imprints (shadow bowl + raised rim + ejecta).
    No external dependencies beyond numpy.
    
    Args:
        W: Width of the texture
        H: Height of the texture
        n_craters: Number of craters to generate
        seed: Random seed for reproducibility
        
    Returns:
        2D numpy array of shape (H, W) with values in [0, 1]
    """
    np.random.seed(seed)

    # Base regolith: coarse low-freq base + fine high-freq noise
    base = value_noise_2d(W, H, scale=32, octaves=4, persistence=0.55, seed=seed) * 0.55
    fine = value_noise_2d(W, H, scale=6,  octaves=3, persistence=0.45, seed=seed+1) * 0.2
    speck = np.random.rand(H, W).astype(np.float32) * 0.06   # speckle grain
    Z = np.clip(base + fine + speck + 0.15, 0, 1)

    # Add craters
    xs = np.linspace(0, 1, W)
    ys = np.linspace(0, 1, H)
    X, Y = np.meshgrid(xs, ys)

    # Fixed reproducible craters
    crater_params = []
    rng = np.random.RandomState(seed)
    for _ in range(n_craters):
        cx   = rng.uniform(0.05, 0.95)
        cy   = rng.uniform(0.05, 0.95)
        r    = rng.uniform(0.025, 0.12)
        depth= rng.uniform(0.12, 0.25)
        crater_params.append((cx, cy, r, depth))

    for (cx, cy, r, depth) in crater_params:
        dist = np.sqrt((X - cx)**2 + (Y - cy)**2)
        # Dark bowl interior
        mask_inner = dist < r
        t_inner = dist[mask_inner] / r
        Z[mask_inner] -= depth * (1 - t_inner**2)

        # Bright rim
        rim_w = r * 0.35
        mask_rim = (dist >= r) & (dist < r + rim_w)
        t_rim = (dist[mask_rim] - r) / rim_w
        Z[mask_rim] += depth * 0.4 * (1 - t_rim)

        # Ejecta halo (slight brightening)
        mask_ejecta = (dist >= r + rim_w) & (dist < r * 3.0)
        t_ejecta = (dist[mask_ejecta] - (r + rim_w)) / (r * 3.0 - r - rim_w)
        noise_e = np.random.rand(*dist[mask_ejecta].shape).astype(np.float32) * 0.06
        Z[mask_ejecta] += (0.05 - 0.05 * t_ejecta) * (1 + noise_e)

    return np.clip(Z, 0, 1).astype(np.float32)


def noisy_hotspot(W: int, H: int, cx_frac: float, cy_frac: float, 
                  radius_frac: float, peak: float = 0.9, 
                  noise_scale: float = 0.35, seed: int = 7) -> np.ndarray:
    """
    Generate a geologically-plausible irregular confidence hotspot:
    gaussian base + value-noise warping so edges are ragged, not smooth.
    Returns float32 [H, W] in [0, 1].
    
    Args:
        W: Width of the output array
        H: Height of the output array
        cx_frac: X center position as fraction of width
        cy_frac: Y center position as fraction of height
        radius_frac: Radius as fraction of dimensions
        peak: Peak intensity value
        noise_scale: Amount of noise to add
        seed: Random seed for reproducibility
        
    Returns:
        2D numpy array of shape (H, W) with values in [0, 1]
    """
    xs = np.linspace(0, 1, W)
    ys = np.linspace(0, 1, H)
    X, Y = np.meshgrid(xs, ys)
    dist = np.sqrt((X - cx_frac)**2 + (Y - cy_frac)**2)
    gauss = np.exp(-dist**2 / (2 * radius_frac**2)).astype(np.float32)
    noise = value_noise_2d(W, H, scale=10, octaves=3, persistence=0.6, seed=seed)
    warped = gauss * (1 - noise_scale) + gauss * noise * noise_scale
    return np.clip(warped * peak, 0, 1).astype(np.float32)


def lunar_surface_dem(resolution: int = 250, n_craters: int = 25, 
                      seed: int = 21) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Generate a clean, readable lunar DEM (X, Y, Z arrays).
    Scaled up for a wider spatial extent (flyover view).
    Low-frequency rolling hills + discrete crater depressions with raised rims.
    
    Args:
        resolution: Resolution of the DEM grid
        n_craters: Number of craters to generate
        seed: Random seed for reproducibility
        
    Returns:
        Tuple of (X, Y, Z) numpy arrays, each of shape (resolution, resolution)
    """
    np.random.seed(seed)
    x = np.linspace(-40, 40, resolution)
    X, Y = np.meshgrid(x, x)

    # Smooth rolling base (very low frequency)
    Z = (1.5 * np.sin(0.05 * X + 0.02 * Y) +
         1.0 * np.cos(0.08 * Y - 0.03 * X) +
         0.6 * np.sin(0.12 * X) * np.cos(0.09 * Y))

    # Add gentle broad-scale slope
    Z += 0.04 * X - 0.02 * Y

    # Fine regolith roughness (reduced amplitude so craters are readable)
    Z += np.random.normal(0, 0.005, X.shape)

    # Craters
    rng = np.random.RandomState(seed)
    for _ in range(n_craters):
        cx   = rng.uniform(-38, 38)
        cy   = rng.uniform(-38, 38)
        r    = rng.uniform(1.0, 5.5)
        depth = r * 0.45
        d = np.sqrt((X - cx)**2 + (Y - cy)**2)
        inner = d < r
        rim   = (d >= r) & (d < r * 1.45)
        Z[inner] -= depth * (1 - (d[inner] / r)**2)
        Z[rim]   += depth * 0.32 * np.exp(-((d[rim] - r) / (r * 0.25))**2)

    return X, Y, Z

# ── Custom Colormaps ──────────────────────────────────────────────────────────

# Strictly grayscale/neutral regolith with slight warm highlight
LUNAR_GRAY = [
    [0.0, "#1c1c1f"],
    [0.2, "#2a2a2e"],
    [0.5, "#5c5c60"],
    [0.8, "#a0a09a"],
    [1.0, "#c8c8c0"]
]

# Transparent-to-color scales for compositing data over regolith
# ICI (Transparent -> Blue -> Cyan -> Red for high confidence)
TRANS_ICI = [
    [0.0, "rgba(10, 25, 45, 0.0)"],
    [0.3, "rgba(34, 211, 238, 0.1)"],
    [0.6, "rgba(34, 211, 238, 0.6)"],
    [0.85, "rgba(245, 158, 11, 0.85)"],
    [1.0, "rgba(239, 68, 68, 1.0)"]
]

# Landing Site Index (Transparent -> Blue)
TRANS_BLUE = [
    [0.0, "rgba(15, 23, 42, 0.0)"],
    [0.4, "rgba(56, 189, 248, 0.3)"],
    [0.7, "rgba(14, 165, 233, 0.6)"],
    [1.0, "rgba(2, 132, 199, 0.9)"]
]

# Traversability (Transparent -> Red/Yellow)
TRANS_INFERNO = [
    [0.0, "rgba(0, 0, 0, 0.0)"],
    [0.3, "rgba(88, 28, 135, 0.3)"],
    [0.6, "rgba(225, 29, 72, 0.6)"],
    [0.85, "rgba(245, 158, 11, 0.85)"],
    [1.0, "rgba(253, 224, 71, 0.95)"]
]
