import numpy as np
import pandas as pd

def generate_radar_cpr_data(resolution=50):
    """Generates synthetic Circular Polarization Ratio (CPR) radar data."""
    x = np.linspace(-5, 5, resolution)
    y = np.linspace(-5, 5, resolution)
    X, Y = np.meshgrid(x, y)
    
    R = np.sqrt(X**2 + Y**2)
    Z = np.sin(R) / (R + 0.1)
    
    noise = np.random.normal(0, 0.1, Z.shape)
    Z = Z + noise
    Z = np.clip((Z - Z.min()) / (Z.max() - Z.min()) * 2, 0, 2)
    return X, Y, Z

def generate_lunar_surface(resolution=100, craters=5):
    """Generates a high-resolution synthetic lunar surface (DEM) with craters."""
    x = np.linspace(-10, 10, resolution)
    y = np.linspace(-10, 10, resolution)
    X, Y = np.meshgrid(x, y)
    
    # Base terrain (slight slope and low frequency noise)
    Z = 0.5 * np.sin(0.2 * X) + 0.3 * np.cos(0.2 * Y)
    
    # Add high-frequency regolith roughness
    Z += np.random.normal(0, 0.05, Z.shape)
    
    # Add craters
    np.random.seed(42) # Consistent terrain
    for _ in range(craters):
        cx = np.random.uniform(-8, 8)
        cy = np.random.uniform(-8, 8)
        r = np.random.uniform(1, 3)
        depth = r * 0.4
        
        dist = np.sqrt((X - cx)**2 + (Y - cy)**2)
        
        # Crater shape function: deep center, raised rim
        crater_mask = dist < (r * 1.5)
        if np.any(crater_mask):
            # Inside crater
            inner = dist < r
            # Raised rim
            rim = (dist >= r) & (dist < (r * 1.5))
            
            # Parabolic interior
            Z[inner] -= depth * (1 - (dist[inner] / r)**2)
            # Raised rim
            Z[rim] += (depth * 0.3) * (1 - (dist[rim] - r) / (r * 0.5))
            
    return X, Y, Z
