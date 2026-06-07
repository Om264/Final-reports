# Assignment 3: The Swiss Cheese Test Suite

**Weight:** 20% | **Due:** Week 12 | **Domain:** Flood Inundation Mapping

## Objective

Use AI to generate a flood inundation model, then build a **Swiss Cheese test suite** that identifies the "Jagged Edges" — places where AI-generated code is wrong, incomplete, or physically invalid. Catch at least one AI hallucination.

## Deliverable Structure

```
assignment_3_swiss_cheese/
├── flood_model/
│   ├── inundation.py          # AI-generated flood model (with known flaws)
│   ├── synthetic_dem.py       # DEM generator
│   └── visualization.py       # Flood mapping visualizations
├── test_suite/
│   ├── test_flood_logic.py    # Core flood algorithm tests
│   ├── test_boundaries.py     # Edge case boundary tests
│   ├── test_physical.py       # Physical law validation
│   └── test_regression.py     # Regression against known cases
├── hallucination_report/
│   ├── detected_hallucinations.md  # What the AI got wrong
│   └── jagged_edge_analysis.md     # Systematic weakness mapping
└── README.md
```

## The Swiss Cheese Model

Each test layer catches what the previous layer missed:

```
Layer 1: Unit Tests     -> "Does it run without crashing?"
Layer 2: Boundary Tests -> "Does it handle extremes?"
Layer 3: Physical Tests -> "Does it obey physics?"
Layer 4: Regression     -> "Are results reproducible?"
```

## Known AI Weaknesses to Exploit

| AI Weakness | How to Test |
|------------|-------------|
| Off-by-one in array indexing | Test min/max elevation cells |
| Forgets NaN/None handling | Inject bad data |
| Physical impossibility (depth > water level - min elev) | Cross-check depth vs water level |
| Floating-point instability | Test extreme values |
| Boundary at exactly water level | Test elevation == water level |
