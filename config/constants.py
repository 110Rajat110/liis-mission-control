"""
Centralized configuration constants for LIIS application.
All magic numbers and configuration values should be defined here.
"""

class AppConfig:
    """Application-wide configuration"""
    APP_NAME = "LIIS"
    APP_VERSION = "1.0.0"
    DEBUG = False

class DataConfig:
    """Data generation and processing configuration"""
    DEFAULT_RESOLUTION = 384
    MAX_RESOLUTION = 512
    MIN_RESOLUTION = 128
    
    # Terrain generation
    DEFAULT_TERRAIN_RESOLUTION = 250
    DEFAULT_TERRAIN_CRATERS = 40
    DEFAULT_TERRAIN_SEED = 87
    
    # Radar analysis
    DEFAULT_RADAR_RESOLUTION = 384
    DEFAULT_RADAR_CRATERS = 18
    DEFAULT_RADAR_SEED = 42
    
    # Ice confidence
    DEFAULT_ICE_RESOLUTION = 384
    DEFAULT_ICE_CRATERS = 12
    DEFAULT_ICE_SEED = 42
    
    # Landing site
    DEFAULT_LANDING_RESOLUTION = 384
    DEFAULT_LANDING_CRATERS = 18
    DEFAULT_LANDING_SEED = 55
    
    # Rover traverse
    DEFAULT_ROVER_RESOLUTION = 384
    DEFAULT_ROVER_CRATERS = 7
    DEFAULT_ROVER_SEED = 33

class ThresholdConfig:
    """Threshold values for analysis"""
    ICI_THRESHOLD = 0.7
    ICI_HIGH_CONFIDENCE = 0.65
    ICI_MODERATE = 0.4
    
    LSI_THRESHOLD = 0.5
    LSI_HIGH = 0.7
    LSI_MODERATE = 0.5
    
    CPR_ICE_THRESHOLD = 1.2
    CPR_MIN = 0.5
    CPR_MAX = 2.3
    
    DOP_THRESHOLD = 0.4
    DOP_MIN = 0.0
    DOP_MAX = 1.0
    
    SLOPE_SAFE_MAX = 5.0
    SLOPE_MODERATE_MAX = 10.0
    
    TRAVERSABILITY_LOW_COST = 0.45
    TRAVERSABILITY_HIGH_COST = 0.8

class IceVolumeConfig:
    """Ice volume estimation configuration"""
    DEFAULT_AREA_KM2 = 12.4
    ICE_DENSITY_KG_M3 = 917  # kg/m³
    DEFAULT_DEPTH_M = 1.5
    DEFAULT_ICE_FRACTION = 0.45
    MIN_DEPTH_M = 0.2
    MAX_DEPTH_M = 5.0
    MIN_ICE_FRACTION = 0.1
    MAX_ICE_FRACTION = 1.0
    
    # Uncertainty factors
    P10_FACTOR = 0.60
    P50_FACTOR = 1.00
    P90_FACTOR = 1.55

class RoverConfig:
    """Rover traverse configuration"""
    DEFAULT_WAYPOINTS = 10
    ENERGY_PER_WAYPOINT_KWH = 0.47
    DISTANCE_PER_WAYPOINT_M = 112
    SPEED_CM_S = 0.5
    TIME_PER_WAYPOINT_MIN = 3.2
    MAX_ENERGY_KWH = 12.0

class ColorConfig:
    """Color constants for visualizations"""
    PRIMARY = "#22d3ee"
    SECONDARY = "#a78bfa"
    SUCCESS = "#34d399"
    WARNING = "#f59e0b"
    DANGER = "#f43f5e"
    INFO = "#2979ff"
    
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#94a3b8"
    TEXT_MUTED = "#64748b"
    
    BACKGROUND = "#05070d"
    SURFACE = "rgba(11, 15, 26, 0.6)"

class CacheConfig:
    """Caching configuration"""
    ENABLE_CACHING = True
    CACHE_TTL_SECONDS = 3600  # 1 hour
