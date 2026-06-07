# SCS-CN Runoff Model

## Hydrological Modeling: Soil Conservation Service Curve Number Method

A professional-grade hydrological modeling system implementing the SCS-CN method for estimating direct runoff from rainfall. Developed for the AI-Augmented Software Engineering course — Smart Water Lab Series.

---

## Project Overview

This project translates the SCS-CN mathematical formula into production-quality Python code, handles physical boundary conditions, performs parameter sensitivity analysis, validates physical correctness, and generates scientific visualizations.

### Key Features

- Complete SCS-CN runoff equation implementation
- Physical boundary condition handling (P < Ia, CN = 0, CN = 100)
- Batch runoff calculations with NumPy vectorization
- Parameter sensitivity analysis with publication-quality plots
- Comprehensive physical validation suite
- Unit tests with 90%+ code coverage
- Professional documentation and prompt log

---

## Hydrological Background

The Soil Conservation Service Curve Number (SCS-CN) method is developed by the USDA Natural Resources Conservation Service (NRCS, formerly SCS). It is the most widely used method for estimating direct runoff from rainfall, particularly for small watersheds and urban hydrology.

### SCS-CN Theory

The method is based on the water balance equation and two fundamental hypotheses:

1. The ratio of actual runoff to potential runoff equals the ratio of actual retention to potential retention.
2. The initial abstraction (Ia) is proportional to the potential maximum retention (S).

### Mathematical Formulation

**Retention Parameter:**
```
S = (25400 / CN) - 254
```
Where:
- S = Potential maximum retention (mm)
- CN = Curve Number (dimensionless, 0–100)

**Initial Abstraction:**
```
Ia = 0.2 × S
```
Where:
- Ia = Initial abstraction (mm)

**Runoff Equation:**
```
If P <= Ia:
    Q = 0
Otherwise:
    Q = (P - Ia)² / (P - Ia + S)
```
Where:
- Q = Runoff depth (mm)
- P = Rainfall depth (mm)

### Boundary Conditions

| Condition | Behavior |
|-----------|----------|
| P = 0 | Q = 0 |
| P < Ia | Q = 0 |
| P = Ia | Q = 0 |
| CN = 0 | Q = 0 (all infiltration) |
| CN = 100 | S = 0, Ia = 0, Q = P (impervious) |
| Q ≤ P | Always satisfied |

### Curve Number Values

| Land Use / Cover | CN Range |
|-----------------|----------|
| Woods, good condition | 60–70 |
| Pasture, fair condition | 75–85 |
| Cultivated, straight row | 80–90 |
| Urban, residential | 75–95 |
| Paved / Impervious | 95–100 |

---

## Installation

### Prerequisites

- Python 3.10+
- pip

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd SCSCN_Runoff_Model

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Project Structure

```
SCSCN_Runoff_Model/
├── scscn_runoff.py            # Core SCS-CN implementation
├── sensitivity_analysis.py    # Sensitivity analysis & visualization
├── validation.py              # Physical validation module
├── runoff_examples.py         # Land use example applications
├── tests/
│   ├── test_scscn.py          # Unit tests for core module
│   ├── test_validation.py     # Validation tests
│   └── test_sensitivity.py    # Sensitivity analysis tests
├── outputs/
│   ├── runoff_comparison.png  # Rainfall vs runoff comparison plot
│   ├── sensitivity_curve.png  # CN vs runoff sensitivity curve
│   ├── analysis_report.csv    # Comprehensive data report
│   └── validation_report.txt  # Validation results
├── README.md                  # This file
├── requirements.txt           # Python dependencies
└── prompt_log.md              # AI interaction documentation
```

### Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  scscn_runoff   │────▶│  validation      │────▶│  Reports        │
│  (Core Engine)  │     │  (Constraints)   │     │  (Validation)   │
└──────┬──────────┘     └──────────────────┘     └─────────────────┘
       │
       ├──────────────────┐
       ▼                  ▼
┌──────────────┐  ┌──────────────────┐
│ sensitivity  │  │ runoff_examples  │
│ (Analysis)   │  │ (Demonstration)  │
└──────┬───────┘  └──────────────────┘
       │
       ▼
┌──────────────────┐
│ outputs/         │
│ (Plots + CSV)    │
└──────────────────┘
```

---

## Running the Project

### Quick Example

```python
from scscn_runoff import calculate_runoff

# Single event: P = 50 mm, CN = 80
result = calculate_runoff(50.0, 80.0)
print(f"Runoff Q = {result['runoff']:.2f} mm")
# Output: Runoff Q = 13.80 mm
```

### Command Line

```bash
# Run all examples
python runoff_examples.py

# Run sensitivity analysis
python sensitivity_analysis.py

# Run physical validation
python validation.py
```

### Batch Calculations

```python
from scscn_runoff import calculate_runoff_series

# Multiple rainfall events and curve numbers
df = calculate_runoff_series(
    rainfall_values=[10, 20, 30, 40, 50],
    curve_numbers=[60, 70, 80, 90]
)
print(df)
```

---

## Sensitivity Analysis

Two key plots are generated:

### 1. CN vs Runoff (sensitivity_curve.png)
Shows how runoff changes with Curve Number at a fixed rainfall depth (P = 50 mm). Demonstrates the non-linear relationship between CN and runoff.

### 2. Rainfall vs Runoff (runoff_comparison.png)
Compares runoff response for different land use types (woods CN=60, pasture CN=80, urban CN=95) across a range of rainfall depths.

### Data Analytics

The analysis report (CSV) includes:
- Average, maximum, minimum, and standard deviation of runoff
- Correlation between CN and runoff
- Correlation between rainfall and runoff
- Runoff ratio (total runoff / total rainfall)

---

## Validation Results

The validation module checks all physical constraints:

| Test | Description |
|------|-------------|
| Q ≥ 0 | Runoff is never negative |
| Q ≤ P | Runoff never exceeds rainfall |
| Monotonic | Higher CN produces more runoff |
| Threshold | No runoff when P < Ia |
| CN = 100 | Impervious surface behavior |
| CN = 0 | Complete infiltration |
| Numerical | Edge case stability |

### Verified Example

```
P = 50 mm, CN = 80
S = (25400 / 80) - 254 = 63.5 mm
Ia = 0.2 × 63.5 = 12.7 mm
Q = (50 - 12.7)² / (50 - 12.7 + 63.5) = 13.8 mm
Verification: 13.8 ≤ 50 ✓
```

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=term-missing

# Run specific test file
pytest tests/test_scscn.py -v
```

### Test Coverage

| Module | Coverage Target |
|--------|----------------|
| scscn_runoff.py | 95%+ |
| validation.py | 90%+ |
| sensitivity_analysis.py | 85%+ |

---

## Generated Outputs

After running the complete pipeline, the `outputs/` directory contains:

| File | Description |
|------|-------------|
| `sensitivity_curve.png` | CN vs Runoff at P = 50 mm |
| `runoff_comparison.png` | Rainfall vs Runoff for multi-CN comparison |
| `analysis_report.csv` | Structured data with computed runoff for all scenarios |
| `validation_report.txt` | Physical validation results |

---

## Results Interpretation

### Key Findings

1. **Non-linear response**: Runoff increases non-linearly with Curve Number. Small changes in CN near the upper end (90–100) produce much larger changes in runoff than equivalent changes at the lower end.

2. **Threshold behavior**: Initial abstraction (Ia) acts as a threshold — no runoff occurs until rainfall exceeds this value. For CN=80 (pasture), Ia = 12.7 mm, meaning the first 12.7 mm of rainfall is entirely abstracted.

3. **Land use impact**: Converting from woods (CN=65) to urban (CN=92) at P=50 mm increases runoff from approximately 2-3 mm to 30+ mm — a >10× increase.

4. **Physical constraints**: The model always satisfies Q ≤ P and Q ≥ 0, confirming physically realistic behavior.

---

## Future Improvements

- Implement antecedent moisture condition (AMC) adjustments for dry/wet soil states
- Add time-area method for watershed routing
- Create interactive plots with sliders for P and CN
- Compare SCS-CN with Rational method and other runoff models
- Add GIS spatial analysis for distributed CN mapping
- Implement Monte Carlo simulation for uncertainty analysis

---

## License

Educational project — AI-Augmented Software Engineering Course.

## References

- USDA NRCS. (2004). "National Engineering Handbook: Part 630 Hydrology."
- Chow, V.T., Maidment, D.R., & Mays, L.W. (1988). *Applied Hydrology*. McGraw-Hill.
- USDA SCS. (1986). "Urban Hydrology for Small Watersheds: TR-55."
