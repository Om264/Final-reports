# Jagged Frontier Report — Reservoir Optimization

## What AI Did Well
- scipy.optimize API (excellent)
- Mathematical formula translation (excellent)
- Docstrings and comments (good)
- CSV export (good)
- Test structure (good)

## Where AI Failed
| Task | Impact |
|------|--------|
| Unit conversion (m3/s to hm3) | Wrong numerical results |
| Sign convention in optimization | Maximized wrong objective |
| NonlinearConstraint array output | Constraint violation |
| Collecting all errors vs assert-first | Only first error reported |
| Floating-point tolerance on bounds | False bound violations |
| Edge case: zero inflow, extreme storage | Silent numerical issues |

## Root Cause Analysis
1. **Unit conversion failure**: LLMs see numbers but don't track physical dimensionality
2. **Sign convention failure**: AI applies minimize mechanically without checking intent
3. **Numerical tolerance failure**: Concept of 1e-6 tolerance is underrepresented in training data

## The Jagged Frontier Map
```
+-------------------------------------------+
|      AI STRENGTH ZONE                     |
|  scipy API  Formula Translation           |
|  Docstrings  Test Structure               |
+-------------------------------------------+
                    |
+-------------------v------------------------+
|      GRAY ZONE (Review Always)             |
|  Constraint Setup  Data Classes            |
|  CSV I/O  Error Handling                   |
+-------------------------------------------+
                    |
+-------------------v------------------------+
|      AI WEAKNESS ZONE                      |
|  Unit Conversion  Sign Convention          |
|  Num Tolerances  Error Aggregation         |
|  Edge Cases  Physical Validation           |
+-------------------------------------------+
```

## Recommendation
- Always verify unit conversions with dimensional analysis
- Always test with known analytical solution first
- Never trust AI-generated numerical tolerances
- Do trust AI for scipy API usage and documentation
