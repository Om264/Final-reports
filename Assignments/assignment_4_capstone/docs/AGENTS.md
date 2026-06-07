# AGENTS.md — Reservoir Optimization Project

## Project Objective
Build a constrained optimization system for reservoir dispatch during drought, balancing ecological flow against hydropower revenue.

## Physical Assumptions
- Single-node reservoir (no cascade)
- Deterministic inflow forecast (7-day)
- No evaporation or seepage losses
- Constant hydraulic head
- Constant turbine efficiency

## Constraints
| Variable | Bound | Unit |
|----------|-------|------|
| Storage | [50, 500] | hm3 |
| Release | [10, 100] | m3/s |
| Mass balance | V_{t+1} = V_t + I_t - R_t | hm3 |

## Validation Rules
1. Storage within bounds at all times
2. Release never below ecological minimum (10 m3/s)
3. Mass balance closes within 1e-3 hm3
4. No negative storage or release

## Known Limitations
- Weighted-sum scalarization (no Pareto frontier)
- Deterministic inflows (no stochastic optimization)
- Constant head assumption
- No environmental flow beyond minimum

## AI Collaboration Protocol
1. Ask Mode for planning
2. Code Mode only after plan approved
3. Validate Mode after every code generation
4. Log Mode for every prompt and response

## File Map
```
src/core/reservoir.py    — Reservoir state model
src/core/optimizer.py    — scipy.optimize SLSQP solver
src/core/constraints.py  — Physical constraints
src/core/objectives.py   — Multi-objective functions
src/utils/validation.py  — Validation layer
src/utils/io_utils.py    — CSV input/output
```
