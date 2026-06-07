# Prompt Log — Reservoir Optimization Capstone

## Interaction 1: Architecture Design
**Prompt:** Design a reservoir optimization system using scipy.optimize SLSQP with multi-objective (ecological flow vs hydropower) and constraints.

**AI Output:** Suggested 3-module structure, missed separate objective functions and test files.
**Human Correction:** Added separate objectives.py and split tests into 4 files.

## Interaction 2: Constraint Implementation
**Prompt:** Implement mass balance constraint for scipy.optimize.minimize.

**AI Output:** Used NonlinearConstraint incorrectly (scalar vs array). Forgot m3/s to hm3 conversion.
**Human Correction:** Fixed unit conversion and changed to return full storage trajectory array.

## Interaction 3: Multi-Objective Formulation
**Prompt:** Combine ecological deficit + hydropower revenue using weighted sum.

**AI Output:** Set revenue weight negative for minimization but double-negated it.
**Human Correction:** Simplified to np.maximum(0, min_eco_flow - releases) and verified sign convention.

## Interaction 4: Validation Layer
**Prompt:** Create validation module checking storage, releases, mass balance, and physical plausibility.

**AI Output:** Used assert statements instead of collecting all errors first.
**Human Correction:** Changed to collect all errors into list, raise once with complete report.

## Interaction 5: Tests
**Prompt:** Write pytest tests for optimizer covering bounds, storage trajectory, drought scenario.

**AI Output:** Missed edge cases (zero inflow, extreme storage, floating-point tolerance).
**Human Correction:** Added tolerance checks and boundary test cases.

## Interaction 6: Schedule Output
**Prompt:** Export optimal schedule to CSV.

**AI Output:** Column order didn't match spec; wrote row-by-row instead of column-wise.
**Human Correction:** Reordered columns and wrote all rows at once.
