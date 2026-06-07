# Prompt Log: AI-Assisted Development

## AI-Augmented Software Engineering — Experiment 2

This document logs all AI interactions during the development of the SCS-CN Runoff Model. Each entry includes the original prompt, AI-generated solution, problems identified, hydrological validation performed, corrections applied, and the final result.

---

## Prompt 1: Formula Implementation

### Original Prompt

```
I am implementing the SCS-CN runoff calculation method. Please write a Python
function calculate_runoff(P, CN) that:
1. Calculates S using: S = (25400 / CN) - 254
2. Calculates Ia = 0.2 * S
3. Returns Q = 0 if P < Ia
4. Otherwise returns Q = (P - Ia)^2 / (P - Ia + S)
5. Ensures Q never exceeds P
Include docstring and type hints.
```

### AI-Generated Solution

The AI generated a function `calculate_runoff(P, CN)` with:
- Type hints and docstring
- S and Ia calculation
- Conditional runoff formula
- Q ≤ P enforcement
- Return dictionary with all parameters

### Problems Found

1. **Division by zero**: CN = 0 caused division by zero when calculating S = (25400 / CN) - 254. Handled by checking CN == 0 as a special case.

2. **Floating-point precision**: Boundary cases near P = Ia produced tiny negative values due to floating-point arithmetic. Fixed by using `np.minimum(Q, P)` and clamping to zero.

3. **No input validation**: The initial implementation lacked CN range checks. Added validation for negative rainfall and CN outside [0, 100].

### Hydrological Validation

Verified the formula against the known reference case:
- P = 50 mm, CN = 80
- S = 63.5 mm, Ia = 12.7 mm
- Q = 13.8 mm

### Corrections Applied

- Added explicit handling for CN = 0 (returns Q = 0 with infinite S)
- Added input validation with `ValueError` for invalid inputs
- Added `min(Q, P)` constraint to ensure Q never exceeds P
- Added rounding to 4 decimal places for numerical stability

### Final Result

Correct implementation with full boundary condition handling, input validation, and numerical stability.

---

## Prompt 2: Boundary Condition Handling

### Original Prompt

```
I need to handle all physical boundary conditions for the SCS-CN method:
1. P = 0: Q = 0
2. P < Ia: Q = 0
3. P = Ia: Q = 0
4. CN = 0: Q = 0
5. CN = 100: Q = P
6. Verify Q <= P for all inputs
Implement comprehensive tests for each case.
```

### AI-Generated Solution

Generated a comprehensive test suite `test_scscn.py` with tests for all boundary conditions.

### Problems Found

1. **Missing test for CN = 0**: The AI did not initially produce a test for CN = 0. Added explicitly.

2. **Near-boundary precision**: Tests for P = Ia required exact floating-point values. Added `pytest.approx` for tolerance-based comparisons.

3. **Large rainfall stability**: Initial tests didn't cover very large rainfall values (e.g., P = 10000 mm). Added to ensure numerical stability.

### Hydrological Validation

- Confirmed CN = 100 produces Q = P (impervious surface)
- Confirmed CN = 0 produces Q = 0 (complete infiltration)
- Confirmed monotonic behavior: higher CN → more runoff
- Verified Q ≤ P across 20+ test cases

### Corrections Applied

- Added CN = 0 test case
- Used `pytest.approx` for floating-point comparisons
- Added large rainfall and tiny rainfall stability tests
- Added hand-calculated reference values for validation

### Final Result

Comprehensive test suite with 20+ tests covering all boundary conditions, edge cases, and numerical stability.

---

## Prompt 3: Sensitivity Analysis

### Original Prompt

```
Write a sensitivity analysis module for the SCS-CN method that:
1. Fixes P = 50 mm
2. Calculates Q for CN = [60, 70, 80, 90, 95, 100]
3. Creates a line plot: CN vs Q
4. Creates a comparison plot: Rainfall vs Runoff for CN = 60, 80, 95
5. Generates a CSV with analysis report
```

### AI-Generated Solution

The AI generated `sensitivity_analysis.py` with:
- `sensitivity_cn_vs_runoff()` — CN vs Q line plot
- `rainfall_vs_runoff_comparison()` — multi-CN comparison plot
- `generate_analytics_report()` — CSV generation
- `run_full_sensitivity_analysis()` — complete pipeline

### Problems Found

1. **Plot style**: Default matplotlib style was not publication-quality. Switched to `seaborn-v0_8-darkgrid` style.

2. **Missing annotations**: The initial plots lacked annotations showing S, Ia, and Q values for each CN. Added annotations with bounding boxes.

3. **Line styles**: Multiple CN curves were hard to distinguish. Added distinct colors, line styles, and markers for each CN.

### Hydrological Validation

- Verified that CN vs Q curve is monotonically increasing and convex (non-linear)
- Confirmed that the Q = P line serves as an upper bound for all CN curves
- Verified that increasing P increases Q for all CN values

### Corrections Applied

- Added seaborn style for publication-quality plots
- Added data point annotations with S and Ia values
- Added distinct line styles per CN curve
- Added Q = P reference line on comparison plot
- Added grid, labels, and descriptive titles

### Final Result

Publication-quality sensitivity plots with annotations, clear legends, and professional styling. CSV report with complete analysis data.

---

## Prompt 4: Visualization

### Original Prompt

```
Enhance the visualizations for the SCS-CN model to be publication-quality.
Include:
- Professional color scheme
- Annotations showing key values
- Grid lines
- Descriptive titles and axis labels
- Legend with land use descriptions
- Save figures at 300 DPI
```

### AI-Generated Solution

Enhanced all plots with:
- Seaborn styling
- Color-coded curves for land use types (green=woods, orange=pasture, red=urban)
- Annotations with bounding boxes
- 300 DPI output resolution
- Professional typography

### Problems Found

1. **Figure size**: Default size was too small for publication. Changed to (10, 6) inches.

2. **Annotation overlap**: Annotations for high CN values overlapped with Q=P line. Added dynamic positioning based on runoff value.

3. **Color accessibility**: Initial color choices were not colorblind-friendly. Adjusted to use distinguishable colors.

### Hydrological Validation

- Visual check confirms monotonic behavior
- Non-linear runoff increase with CN is clearly visible
- Q ≤ P constraint is visually verified by all curves remaining below the 1:1 line

### Corrections Applied

- Increased figure size and DPI
- Dynamic annotation positioning
- Colorblind-friendly color palette
- Added legend descriptions matching land use types

### Final Result

Professional, publication-quality visualizations suitable for inclusion in reports and presentations.

---

## Prompt 5: Physical Validation

### Original Prompt

```
Create a physical validation module that automatically checks:
1. Q >= 0 for all inputs
2. Q <= P for all inputs
3. Higher CN produces more runoff (monotonic)
4. No runoff when P < Ia
5. CN = 100 behaves as impervious surface
6. CN = 0 produces zero runoff
7. Numerical stability for edge cases
Generate a validation report.
```

### AI-Generated Solution

Generated `validation.py` with:
- Individual validation functions for each constraint
- Grid-based validation (rainfall × CN combinations)
- Validation report generation
- Detailed pass/fail output

### Problems Found

1. **Infinite S for CN = 0**: The validation module needed to handle `inf` values in the DataFrame from infinite retention. Added `np.isinf` checks.

2. **Monotonicity edge case**: At very low rainfall below Ia, multiple CN values produce Q = 0, which could be flagged as non-monotonic (equal values are fine). Adjusted to allow equality with tolerance.

### Hydrological Validation

All physical constraints verified:
- Q ≥ 0: PASS (all 420 grid combinations)
- Q ≤ P: PASS (all 420 grid combinations)
- Monotonic: PASS (higher CN → more runoff at all rainfall levels)
- Threshold: PASS (P < Ia → Q = 0)
- CN = 100: PASS (impervious behavior)
- CN = 0: PASS (zero runoff)
- Numerical: PASS (edge cases stable)

### Corrections Applied

- Added handling for `inf` values in retention/abstraction columns
- Added tolerance for monotonicity check (equal values allowed)
- Updated validation DataFrame column names to match module conventions

### Final Result

Comprehensive validation module that automatically verifies all physical constraints and generates a formatted report.

---

## Prompt 6: Testing and Debugging

### Original Prompt

```
Write comprehensive unit tests for the SCS-CN model:
1. Test formula correctness with known values
2. Test all boundary conditions
3. Test input validation
4. Test batch calculations
5. Test validation module
6. Test sensitivity analysis
7. Achieve 90%+ code coverage
8. Use pytest conventions
```

### AI-Generated Solution

Generated three test files:
- `tests/test_scscn.py` — 20+ tests for core module
- `tests/test_validation.py` — 10+ tests for validation
- `tests/test_sensitivity.py` — 10+ tests for sensitivity analysis

### Problems Found

1. **Import path**: Initial tests used relative imports that failed when running from project root. Added proper import paths.

2. **Matplotlib backend**: Tests that generate plots failed in headless environments. Added `matplotlib.use("Agg")` before imports.

3. **Temporary files**: CSV and PNG tests needed cleanup. Used `tempfile` module for proper cleanup.

### Hydrological Validation

- Verified all known reference values match within tolerance
- Confirmed physical constraints hold across full input range
- Validated monotonic behavior with multiple CN sequences

### Corrections Applied

- Set `matplotlib.use("Agg")` for headless test environments
- Used `tempfile.NamedTemporaryFile` for file output tests
- Added `pytest.approx` for all numeric comparisons
- Added comprehensive docstrings to all test functions

### Final Result

Three test modules with 45+ tests achieving >90% code coverage. All tests pass with pytest.

---

## Summary of AI Interactions

| Prompt | Module | Key Corrections Applied |
|--------|--------|------------------------|
| 1 | Formula Implementation | Division by zero fix, input validation, numerical clamping |
| 2 | Boundary Conditions | CN=0 test, floating-point tolerance, edge case tests |
| 3 | Sensitivity Analysis | Plot styling, annotations, line styles |
| 4 | Visualization | Figure sizing, color accessibility, dynamic annotations |
| 5 | Physical Validation | Infinity handling, monotonic tolerance, report formatting |
| 6 | Testing | Headless matplotlib, tempfile cleanup, import paths |

### Key Lessons

1. **Always validate AI output with domain knowledge** — the formula may be correct, but boundary conditions and edge cases require human oversight.

2. **Floating-point arithmetic requires tolerance** — exact equality checks fail for computed values; use `pytest.approx` or relative tolerances.

3. **Test files need environment-aware setup** — headless environments, import paths, and temporary files must be handled explicitly.

4. **Physical validation is essential** — mathematical correctness does not guarantee physical plausibility. Always verify that results make hydrological sense.

5. **AI excels at structure but needs human refinement** — the AI generates good initial structure, but details like plot annotations, color schemes, and error messages require human judgment.
