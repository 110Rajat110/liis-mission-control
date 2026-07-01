# LIIS - Lunar Ice Intelligence System

A comprehensive mission control dashboard for Chandrayaan-2 DFSAR (Dual Frequency Synthetic Aperture Radar) data analysis, focused on lunar south pole ice detection and landing site evaluation.

## Features

- **Radar Analysis**: L-band SAR visualization with CPR, DOP, and speckle simulation
- **Terrain Analysis**: OHRC DEM processing with slope, roughness, and crater mapping
- **Ice Confidence**: ICI (Ice Confidence Index) with pixel-level explainability
- **Landing Site**: LSI (Landing Site Index) ranking with 3D terrain overlay
- **Rover Traverse**: A* path planning with traversability analysis
- **Ice Volume**: P10/P50/P90 volumetric estimation with 3D visualization
- **Mission Summary**: Integrated mission overview and telemetry

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Local Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd isro_a
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

## Deployment

### Streamlit Cloud

1. Push your code to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app" and connect your repository
4. Set the main file path to `app.py`
5. Deploy

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t liis-app .
```

2. Run the container:
```bash
docker run -p 8501:8501 liis-app
```

### Traditional Server

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run with custom port:
```bash
streamlit run app.py --server.port 80 --server.address 0.0.0.0
```

## Configuration

### Secrets Management

The app uses `.streamlit/secrets.toml` for sensitive configuration:

```toml
# Cesium Ion Token for 3D terrain visualization (optional)
# Get your token from: https://cesium.com/ion/tokens
CESIUM_ION_TOKEN = ""
```

**Important**: Never commit secrets to version control. Use environment variables in production:

```bash
export CESIUM_ION_TOKEN="your-token-here"
```

### Streamlit Configuration

Customize `.streamlit/config.toml` for additional settings:

```toml
[theme]
primaryColor = "#00E5FF"
backgroundColor = "#050810"
secondaryBackgroundColor = "#0F172A"

[server]
port = 8501
headless = true
```

## Project Structure

```
isro_a/
├── app.py                 # Main application entry point
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .gitignore            # Git ignore rules
├── .streamlit/           # Streamlit configuration
│   ├── secrets.toml      # Secrets (do not commit)
│   └── config.toml       # App configuration
├── core/                 # Core utilities
│   ├── lunar_utils.py    # Lunar texture & noise generation
│   └── mock_data.py      # Mock data generators
├── config/               # Configuration modules
│   └── theme.py          # Design tokens & theme
├── components/           # Reusable UI components
│   ├── cards.py          # Card components
│   └── layout.py         # Layout utilities
├── pages/               # Page modules
│   ├── 00_home.py        # Landing page with 3D moon
│   ├── 01_radar.py       # Radar analysis
│   ├── 02_terrain.py     # Terrain analysis
│   ├── 03_ice_confidence.py
│   ├── 04_landing_site.py
│   ├── 05_rover_traverse.py
│   ├── 06_ice_volume.py
│   ├── 07_mission_summary.py
│   ├── 08_settings.py
│   └── 09_about.py
├── assets/              # Static assets
└── data/                # Data files
```

## Performance Optimization

The application uses Streamlit's caching (`@st.cache_data`) for:
- Terrain generation
- Radar map processing
- Ice confidence calculations
- Path planning algorithms

Cached data persists across sessions for faster loading.

## Dependencies

- `streamlit>=1.36.0` - Web framework
- `streamlit-option-menu>=0.3.6` - Navigation menu
- `plotly>=5.22.0` - Interactive visualizations
- `pydeck>=0.9.1` - 3D mapping
- `pandas>=2.2.0` - Data manipulation
- `numpy>=1.26.0` - Numerical computing

## Browser Compatibility

- Chrome/Edge (recommended)
- Firefox
- Safari

## License

This project is part of the LIIS Mission Control system for lunar exploration data analysis.

## Support

For issues or questions, please refer to the project documentation or contact the development team.
