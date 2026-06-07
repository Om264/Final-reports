# Flood Inundation Analysis Using Digital Elevation Models (DEM)

A professional-grade flood inundation analysis and simulation system using Digital Elevation Models (DEM). This project implements spatial comparison algorithms to identify flooded areas based on water level, creates visual flood extent maps, calculates flooded area percentages, and validates physical constraints.

## Project Overview

This system provides a complete pipeline for DEM-based flood inundation analysis:

- DEM data preparation (synthetic generation and real data loading)
- Flood inundation calculation with spatial comparison
- Dynamic flood simulation across rising water levels
- Flood routing with 4- and 8-neighbour connectivity
- Building footprint barriers as impermeable flood obstacles
- Flood volume analysis
- Flood animation generation
- Physical validation suite
- Comprehensive testing

## Flood Inundation Background

Flood inundation mapping identifies areas where water would cover land given a specific water surface elevation. This is fundamental to flood risk assessment, emergency management, and urban planning.

### DEM Theory

A **Digital Elevation Model (DEM)** is a 2D raster grid where each cell stores an elevation value. Common sources include:

- **SRTM** (Shuttle Radar Topography Mission) — 30m resolution
- **ALOS PALSAR** — 12.5m resolution
- **LiDAR** — sub-meter resolution

### Flooding Logic

A cell is considered **flooded** when its elevation is below the water level:

```
flooded_mask = elevation < water_level
```

### Inundation Depth

Water depth at each cell is calculated as the difference between water level and ground elevation, clamped to zero:

```
depth = max(water_level - elevation, 0)
```

### Flooded Area Percentage

The proportion of the domain that is inundated:

```
flooded_% = (number_of_flooded_cells / total_cells) × 100
```

### Flood Routing

Water spreads from a source cell to connected neighbours where elevation is below water level. Supports both 4-neighbour (cardinal) and 8-neighbour (cardinal + diagonal) connectivity.

### Building Barriers

Buildings act as impermeable barriers — water cannot pass through building footprints, altering flood extent and volume.

### Flood Volume Analysis

Total flood volume is computed by summing the product of inundation depth and cell area across all flooded cells:

```
volume = sum(depth × cell_area)
```

## Architecture

```
flowchart TD
    DEM --> FloodCalculation
    FloodCalculation --> FloodMask
    FloodMask --> DepthAnalysis
    DepthAnalysis --> FloodVolume
    FloodMask --> Routing
    Routing --> BuildingBarriers
    BuildingBarriers --> Visualization
    Visualization --> Animation
    Animation --> Validation
    Validation --> Reports
```

## Project Structure

```
Flood_Inundation_Analysis/
├── flood_inundation.py      # Core DEM loading and flood calculation
├── flood_routing.py          # Spatial flood routing model
├── building_barriers.py      # Building footprint barrier analysis
├── volume_analysis.py        # Flood volume computation
├── animation_generator.py    # Flood animation (GIF) creation
├── visualization.py          # Plotting and figure generation
├── validation.py             # Physical validation suite
├── config.py                 # Configuration constants
├── data/                     # DEM data files
├── outputs/                  # Generated figures, reports, GIFs
├── tests/                    # pytest test suite
├── requirements.txt
└── README.md
```

## Installation

```bash
git clone <repository-url>
cd Flood_Inundation_Analysis
pip install -r requirements.txt
```

## Quick Start

```python
from flood_inundation import load_dem, calculate_flood, simulate_rising_water

dem = load_dem()
result = calculate_flood(dem, water_level=45.0)
print(f"Flooded: {result['flooded_percentage']:.2f}%")

sim = simulate_rising_water(dem)
print(f"Monotonically increasing: {sim['monotonically_increasing']}")
```

### Generate Full Pipeline Output

```bash
python flood_inundation.py
python visualization.py
python flood_routing.py
python building_barriers.py
python volume_analysis.py
python animation_generator.py
python validation.py
```

## Running Tests

```bash
cd Flood_Inundation_Analysis
pytest tests/ -v --cov=. --cov-report=term-missing
```

## Generated Outputs

| Output | Description |
|--------|-------------|
| `outputs/flood_extent_40m.png` | Flood map at 40m water level |
| `outputs/flood_extent_50m.png` | Flood map at 50m water level |
| `outputs/flood_curve.png` | Water level vs flooded percentage |
| `outputs/flood_volume_analysis.png` | Water level vs flood volume |
| `outputs/building_impact.png` | Building barrier comparison |
| `outputs/flood_routing_map.png` | Routing visualization |
| `outputs/rising_flood.gif` | Rising water animation |
| `outputs/flood_statistics.csv` | Numerical results table |
| `outputs/validation_report.txt` | Validation pass/fail report |

## Validation Results

The validation suite checks:
- Flooded area increases monotonically with water level
- Flood volume increases monotonically with water level
- Flood spread is spatially continuous
- Building barriers reduce flood extent
- Depth is always non-negative
- Flooded percentage is in [0%, 100%]
- Volume is always non-negative
- Edge cases (below min elevation yields 0% flood, above max yields 100% flood)

## Future Improvements

- Load real DEM data from USGS/OpenTopography
- Implement dynamic flood routing with velocity
- Add building footprints from OpenStreetMap
- Create interactive web-based flood maps
- Machine learning for flood susceptibility mapping
- Real-time flood forecasting integration

## License

MIT
