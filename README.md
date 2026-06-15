# AI-Augmented Software Engineering — Complete Project Portfolio

A comprehensive collection of hydrological modeling, rainfall monitoring, flood analysis, and reservoir optimization projects, developed as part of the AI-Augmented Software Engineering course.

This document covers all **8 projects** completed during the course: the first 4 are **experimental systems** (Smart Water Lab Series), and the last 4 are **formal assignments**.

---

## Table of Contents

### Experiments (Smart Water Lab Series)
1. [SCS-CN Runoff Model](#1-scs-cn-runoff-model)
2. [Short-Term Rainfall Forecasting & Alert System](#2-short-term-rainfall-forecasting--alert-system)
3. [Reservoir Dispatch Optimization](#3-reservoir-dispatch-optimization)
4. [Flood Inundation Analysis Using DEM](#4-flood-inundation-analysis-using-dem)

### Assignments
5. [Assignment 1: The Reasoning Log](#5-assignment-1-the-reasoning-log)
6. [Assignment 2: Legacy Code Modernization](#6-assignment-2-legacy-code-modernization)
7. [Assignment 3: The Swiss Cheese Test Suite](#7-assignment-3-the-swiss-cheese-test-suite)
8. [Assignment 4: Final Capstone Project](#8-assignment-4-final-capstone-project)

---

## Experiments

---

## 1. SCS-CN Runoff Model

**Hydrological Modeling: Soil Conservation Service Curve Number Method**

A professional-grade hydrological modeling system implementing the SCS-CN method for estimating direct runoff from rainfall.

### Key Features

- Complete SCS-CN runoff equation implementation
- Physical boundary condition handling (P < Ia, CN = 0, CN = 100)
- Batch runoff calculations with NumPy vectorization
- Parameter sensitivity analysis with publication-quality plots
- Comprehensive physical validation suite
- Unit tests with 90%+ code coverage

### Hydrological Background

The Soil Conservation Service Curve Number (SCS-CN) method is developed by the USDA Natural Resources Conservation Service (NRCS). It is the most widely used method for estimating direct runoff from rainfall, particularly for small watersheds and urban hydrology.

### Mathematical Formulation

**Retention Parameter:**
```
S = (25400 / CN) - 254
```

**Initial Abstraction:**
```
Ia = 0.2 × S
```

**Runoff Equation:**
```
If P <= Ia: Q = 0
Otherwise:  Q = (P - Ia)² / (P - Ia + S)
```

### Boundary Conditions

| Condition | Behavior |
|-----------|----------|
| P = 0 | Q = 0 |
| P < Ia | Q = 0 |
| P = Ia | Q = 0 |
| CN = 0 | Q = 0 (all infiltration) |
| CN = 100 | S = 0, Ia = 0, Q = P (impervious) |
| Q ≤ P | Always satisfied |

### Project Structure

```
SCSCN_Runoff_Model/
├── scscn_runoff.py            # Core SCS-CN implementation
├── sensitivity_analysis.py    # Sensitivity analysis & visualization
├── validation.py              # Physical validation module
├── runoff_examples.py         # Land use example applications
├── tests/
│   ├── test_scscn.py
│   ├── test_validation.py
│   └── test_sensitivity.py
├── outputs/
│   ├── runoff_comparison.png
│   ├── sensitivity_curve.png
│   ├── analysis_report.csv
│   └── validation_report.txt
├── README.md
├── requirements.txt
└── prompt_log.md
```

### Generated Outputs

| File | Description |
|------|-------------|
| `sensitivity_curve.png` | CN vs Runoff at P = 50 mm |
| `runoff_comparison.png` | Rainfall vs Runoff for multi-CN comparison |
| `analysis_report.csv` | Structured data with computed runoff for all scenarios |
| `validation_report.txt` | Physical validation results |

### Key Findings

1. **Non-linear response**: Runoff increases non-linearly with Curve Number. Small changes in CN near the upper end (90–100) produce much larger changes in runoff than equivalent changes at the lower end.
2. **Threshold behavior**: Initial abstraction (Ia) acts as a threshold — no runoff occurs until rainfall exceeds this value.
3. **Land use impact**: Converting from woods (CN=65) to urban (CN=92) at P=50 mm increases runoff from ~2-3 mm to 30+ mm — a >10× increase.
4. **Physical constraints**: The model always satisfies Q ≤ P and Q ≥ 0.

---

## 2. Short-Term Rainfall Forecasting & Alert System

A real-time rainfall monitoring and alert system with machine learning forecasting, anomaly detection, and an interactive Streamlit dashboard.

### System Architecture

```
Weather API (OpenWeatherMap) → WeatherAPI Module → Alert System → Notification Service
                                                → Data Storage → ML Predictor
                                                              → Anomaly Detector
                                                → Streamlit Dashboard → User
                                                                      → Interactive Map (Folium)
                                                                      → Data Export (CSV/Excel)
```

### Features

- **Real-time Weather Data**: Fetch current weather from OpenWeatherMap API for multiple cities
- **Offline Mode**: Synthetic rainfall generation for demonstration without internet
- **Threshold-based Alerts**: GREEN (< 10 mm/h), YELLOW (10-20 mm/h), RED (≥ 20 mm/h)
- **Multi-City Monitoring**: Compare rainfall, temperature, and alerts across Beijing, Shanghai, Guangzhou, Shenzhen, Wuhan
- **ML Rainfall Forecasting**: Linear regression model predicting 1-hour and 3-hour rainfall
- **Anomaly Detection**: Z-score based detection of unusual rainfall events
- **Interactive Map**: Folium map with color-coded markers for each city
- **Notification System**: Email/SMS alert framework (configurable)
- **Data Export**: Download historical data as CSV or Excel
- **Auto-refresh**: Configurable automatic data refresh

### ML Forecasting

- **Model**: Linear Regression (scikit-learn)
- **Features**: Temperature, humidity, pressure, 3 lagged rainfall values
- **Target**: Next-hour rainfall intensity
- **Retraining**: Automatic when 50+ new records are available
- **Confidence**: Based on model R² score
- **Uncertainty**: 95% confidence intervals via prediction with uncertainty

### Anomaly Detection

- **Method**: Z-Score analysis
- **Threshold**: \|z\| > 2 (configurable)
- **Severity Levels**: normal, high, extreme

### Dashboard Sections

| Section | Description |
|---------|-------------|
| Current Weather | Real-time rainfall, temperature, humidity, pressure, wind |
| Alert Center | Color-coded alerts with history log |
| Multi-City Monitoring | Compare all monitored cities with rankings |
| Historical Trends | Rainfall and temperature over time with moving averages |
| ML Forecast | 1h/3h rainfall predictions with confidence scores |
| Data Analytics | Distribution analysis, statistics, alert frequency |
| Anomaly Detection | Z-score analysis with severity classification |
| Notification Center | Send and track alert notifications |
| Interactive Map | Folium map with city markers and popups |

---

## 3. Reservoir Dispatch Optimization

Multi-objective reservoir operation optimization during drought conditions. Balances hydropower revenue with ecological flow requirements using `scipy.optimize`.

### Problem Overview

A reservoir must optimize a 7-day release schedule to maximize hydropower revenue while maintaining minimum ecological flow, subject to physical storage and release constraints.

### Mathematical Formulation

**Decision Variables**: Q₁, Q₂, ..., Q₇: Daily release rates (m³/s)

**Objective Functions**:
1. **Maximize Hydropower Revenue**: Revenue = Σᵢ Qᵢ × Pᵢ × C
2. **Minimize Ecological Deficit**: Deficit = Σᵢ max(0, Q_eco - Qᵢ)
3. **Combined (Weighted Sum)**: f = -w_r × Revenue + w_e × Deficit

### Constraints

| Constraint | Expression |
|---|---|
| Storage bounds | V_min ≤ V_t ≤ V_max |
| Release bounds | Q_eco ≤ Q_t ≤ Q_max |
| Mass balance | V_{t+1} = V_t + (I_t - Q_t) × Δt |

### Parameters

| Parameter | Value |
|---|---|
| Initial Storage | 500,000 m³ |
| Min Storage | 100,000 m³ |
| Max Storage | 1,000,000 m³ |
| Ecological Release | 10 m³/s |
| Max Release | 100 m³/s |
| Conversion Constant | 5,000 |

### Project Structure

```
Reservoir_Dispatch_Optimization/
├── reservoir_model.py        # Core simulation & objectives
├── reservoir_optimize.py     # scipy.optimize implementation
├── tradeoff_analysis.py      # Pareto frontier analysis
├── validation.py             # Constraint verification
├── revenue_analysis.py       # Revenue breakdown
├── outputs/
│   ├── optimal_schedule.csv
│   ├── tradeoff_analysis.png
│   ├── storage_trajectory.png
│   ├── revenue_breakdown.csv
│   └── validation_report.txt
├── tests/
│   ├── test_optimizer.py
│   ├── test_constraints.py
│   ├── test_validation.py
│   └── test_tradeoff.py
├── README.md
├── requirements.txt
└── prompt_log.md
```

### Optimization Method

Uses Sequential Least Squares Programming (SLSQP) from `scipy.optimize.minimize` — handles both equality and inequality constraints, supports bounds on decision variables, gradient-based for efficient convergence.

### Trade-off Analysis

The Pareto frontier is generated by sweeping the weight pair (w_revenue, w_ecology) from (1.0, 0.0) to (0.0, 1.0), revealing the trade-off between hydropower revenue and ecological protection.

### Validation

All solutions are verified against:
1. Storage bounds (V_min ≤ V ≤ V_max)
2. Release bounds (Q_eco ≤ Q ≤ Q_max)
3. Mass balance (conservation of volume)
4. Revenue calculation (independent verification)

---

## 4. Flood Inundation Analysis Using DEM

A professional-grade flood inundation analysis and simulation system using Digital Elevation Models (DEM). Implements spatial comparison algorithms to identify flooded areas based on water level, creates visual flood extent maps, calculates flooded area percentages, and validates physical constraints.

### Flood Inundation Background

Flood inundation mapping identifies areas where water would cover land given a specific water surface elevation. A **Digital Elevation Model (DEM)** is a 2D raster grid where each cell stores an elevation value.

### Flooding Logic

A cell is considered **flooded** when its elevation is below the water level: `flooded_mask = elevation < water_level`

**Inundation Depth**: `depth = max(water_level - elevation, 0)`

**Flooded Area Percentage**: `flooded_% = (number_of_flooded_cells / total_cells) × 100`

### Architecture

```
DEM → FloodCalculation → FloodMask → DepthAnalysis → FloodVolume
                                   → Routing → BuildingBarriers → Visualization → Animation → Validation → Reports
```

### Project Structure

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

### Generated Outputs

| Output | Description |
|--------|-------------|
| `flood_extent_40m.png` | Flood map at 40m water level |
| `flood_extent_50m.png` | Flood map at 50m water level |
| `flood_curve.png` | Water level vs flooded percentage |
| `flood_volume_analysis.png` | Water level vs flood volume |
| `building_impact.png` | Building barrier comparison |
| `flood_routing_map.png` | Routing visualization |
| `rising_flood.gif` | Rising water animation |
| `flood_statistics.csv` | Numerical results table |
| `validation_report.txt` | Validation pass/fail report |

### Validation Results

The validation suite checks:
- Flooded area increases monotonically with water level
- Flood volume increases monotonically with water level
- Flood spread is spatially continuous
- Building barriers reduce flood extent
- Depth is always non-negative
- Flooded percentage is in [0%, 100%]
- Volume is always non-negative
- Edge cases (below min elevation yields 0% flood, above max yields 100% flood)

---

## Assignments

---

## 5. Assignment 1: The Reasoning Log

**Weight:** 20% | **Due:** Week 4 | **Domain:** SCS-CN Hydrological Modeling

### Objective

Use **Chain-of-Thought (CoT)** prompting to solve the SCS-CN rainfall-runoff problem, then document the full reasoning trace and human verification steps.

### Deliverable Structure

```
assignment_1_reasoning_log/
├── coT_prompts/
│   ├── prompt_01_initial.md
│   ├── prompt_02_refined.md
│   └── prompt_03_verification.md
├── ai_responses/
│   ├── response_01_raw.md
│   ├── response_02_corrected.md
│   └── response_03_verified.md
├── verification/
│   ├── edge_cases.md
│   ├── physical_plausibility.md
│   └── final_report.md
└── README.md
```

### The SCS-CN Problem

The Soil Conservation Service Curve Number method estimates surface runoff:

```
Q = (P - Ia)^2 / (P - Ia + S)
S = (25400 / CN) - 254
Ia = 0.2 * S
```

### Physical Constraints Verified

| Rule | Why It Matters |
|------|----------------|
| Q = 0 when P < Ia | No runoff before abstraction satisfied |
| 0 <= Q <= P | Runoff cannot exceed rainfall |
| CN in [30, 100] | Physical range of curve numbers |
| Q increases with CN | Higher CN means more runoff |
| Q increases with P | More rain means more runoff |

### Task Steps

1. **Initial Prompt (Naive)**: Ask an AI to write the SCS-CN function without structure. Identify errors.
2. **CoT Prompt (Structured)**: Chain-of-Thought prompt with role assignment, formula, edge cases, step-by-step reasoning.
3. **Verification Prompt**: Ask AI to review its own output for physical correctness.
4. **Final Report**: Reflection comparing naive vs. CoT output quality, AI self-verification vs. human verification.

### Grading Criteria

| Criterion | Weight |
|-----------|--------|
| CoT Prompt Quality | 30% |
| Error Identification | 30% |
| Verification Depth | 25% |
| Reflection Quality | 15% |

---

## 6. Assignment 2: Legacy Code Modernization

**Weight:** 20% | **Due:** Week 8 | **Domain:** Rainfall Alert System

### Objective

Take an old, undocumented research script and modernize it using AI assistance. Deliver a Python 3.12 codebase with type hints, async patterns, and an AI-generated Code Map.

### Deliverable Structure

```
assignment_2_legacy_code/
├── legacy/
│   ├── rainfall_monitor_v1.py
│   └── data.csv
├── modernized/
│   └── src/
│       ├── __init__.py
│       ├── fetcher.py
│       ├── alerts.py
│       ├── logger.py
│       └── dashboard.py
├── code_map/
│   ├── ai_generated_map.md
│   ├── migration_notes.md
│   └── before_after_comparison.md
└── prompt_log.md
```

### Task

1. Analyze the legacy code using AI. Identify all issues.
2. Plan a migration strategy using AI.
3. Modernize each component: add types, async, proper error handling.
4. Generate an AI-created Code Map explaining the architecture.
5. Document AI interactions in `prompt_log.md`.

### Grading Criteria

| Criterion | Weight |
|-----------|--------|
| Code Modernization | 35% |
| AI Collaboration | 25% |
| Code Map Quality | 25% |
| Migration Documentation | 15% |

---

## 7. Assignment 3: The Swiss Cheese Test Suite

**Weight:** 20% | **Due:** Week 12 | **Domain:** Flood Inundation Mapping

### Objective

Use AI to generate a flood inundation model, then build a **Swiss Cheese test suite** that identifies the "Jagged Edges" — places where AI-generated code is wrong, incomplete, or physically invalid. Catch at least one AI hallucination.

### Deliverable Structure

```
assignment_3_swiss_cheese/
├── flood_model/
│   ├── inundation.py
│   ├── synthetic_dem.py
│   └── visualization.py
├── test_suite/
│   ├── test_flood_logic.py
│   ├── test_boundaries.py
│   ├── test_physical.py
│   └── test_regression.py
├── hallucination_report/
│   ├── detected_hallucinations.md
│   └── jagged_edge_analysis.md
└── README.md
```

### The Swiss Cheese Model

Each test layer catches what the previous layer missed:

```
Layer 1: Unit Tests     → "Does it run without crashing?"
Layer 2: Boundary Tests → "Does it handle extremes?"
Layer 3: Physical Tests → "Does it obey physics?"
Layer 4: Regression     → "Are results reproducible?"
```

### Known AI Weaknesses to Exploit

| AI Weakness | How to Test |
|-------------|-------------|
| Off-by-one in array indexing | Test min/max elevation cells |
| Forgets NaN/None handling | Inject bad data |
| Physical impossibility (depth > water level - min elev) | Cross-check depth vs water level |
| Floating-point instability | Test extreme values |
| Boundary at exactly water level | Test elevation == water level |

---

## 8. Assignment 4: Final Capstone Project

**Weight:** 40% | **Due:** Week 16 | **Domain:** Reservoir Optimization

### Objective

Build a complete, functional mini-application for reservoir dispatch optimization during drought. Integrates everything from the course: AI-assisted development, prompt engineering, testing, validation, and reflection.

### Deliverable Structure

```
assignment_4_capstone/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── reservoir.py
│   │   ├── optimizer.py
│   │   ├── constraints.py
│   │   └── objectives.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── io_utils.py
│   │   └── validation.py
│   └── tests/
│       ├── test_reservoir.py
│       ├── test_optimizer.py
│       ├── test_constraints.py
│       └── test_validation.py
├── docs/
│   ├── AGENTS.md
│   ├── prompt_log.md
│   ├── jagged_frontier_report.md
│   └── presentation_outline.md
├── outputs/
│   └── schedule.csv
└── README.md
```

### Problem

A reservoir must balance ecological flow (10 m³/s minimum) vs. hydropower revenue during a 7-day drought.

**Constraints:** V_min ≤ Storage ≤ V_max, Q_release ≥ Q_ecology, mass balance.

### How This Differs from Assignments 1–3

| Aspect | Assignments 1–3 | Assignment 4 |
|--------|----------------|--------------|
| Scope | Single skill | All skills integrated |
| Deliverable | Report or module | Complete runnable app |
| Reflection | Brief | Systematic Jagged Frontier analysis |

---

## Course Overview

| # | Project | Domain | Key Technique | Weight |
|---|---------|--------|---------------|--------|
| 1 | SCS-CN Runoff Model | Hydrology | SCS-CN equation, sensitivity analysis | Experiment |
| 2 | Rainfall Alert System | Meteorology | ML forecasting, Streamlit dashboard | Experiment |
| 3 | Reservoir Optimization | Water Resources | scipy.optimize, Pareto frontier | Experiment |
| 4 | Flood Inundation Analysis | Hydrology | DEM spatial analysis, flood routing | Experiment |
| 5 | Assignment 1: Reasoning Log | SCS-CN | Chain-of-Thought prompting | 20% |
| 6 | Assignment 2: Legacy Code | Rainfall Alert | Async modernization, type hints | 20% |
| 7 | Assignment 3: Swiss Cheese | Flood Mapping | Multi-layer testing, hallucination detection | 20% |
| 8 | Assignment 4: Capstone | Reservoir | Full-stack AI-assisted development | 40% |

---

## Common Themes

- **AI-Assisted Development**: All projects leverage AI for code generation, review, and documentation
- **Physical Validation**: Every project includes rigorous physical constraint verification
- **Professional Outputs**: Publication-quality plots, structured data exports, validation reports
- **Testing**: Comprehensive pytest suites with high coverage targets
- **Documentation**: Prompt logs, architecture diagrams, migration notes, and reflection reports
