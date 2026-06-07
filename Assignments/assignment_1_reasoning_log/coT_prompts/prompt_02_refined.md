# Prompt 2: Chain-of-Thought (Structured)

**Strategy:** Assign role, decompose reasoning, specify constraints.

## Prompt

```
You are a Senior Hydrologist with 20 years of experience in rainfall-runoff modeling.
Implement the SCS Curve Number method in Python. Before writing ANY code, reason through:

=== REASONING PHASE (write this first) ===

1. List the known variables and their physical meanings:
   - P = total precipitation (mm)
   - CN = curve number (dimensionless, 30-100)
   - S = potential maximum retention (mm)
   - Ia = initial abstraction (mm)
   - Q = surface runoff (mm)

2. State the governing equations:
   - S = (25400 / CN) - 254
   - Ia = 0.2 * S
   - if P <= Ia: Q = 0
   - if P > Ia: Q = (P - Ia)^2 / (P - Ia + S)

3. Identify ALL boundary conditions:
   - What happens when CN approaches 100? (S approaches 0, runoff approaches P)
   - What happens when CN approaches 30? (S approaches large, runoff approaches 0)
   - What happens when P = Ia? (Q = 0)
   - What happens when P < Ia? (Q = 0, not negative)

4. List physical constraints for validation:
   - 0 <= Q <= P (runoff cannot exceed rainfall)
   - Q >= 0 (no negative runoff)
   - CN in [30, 100]
   - P >= 0

=== CODE PHASE (write this second) ===

Now implement a Python function `scs_cn_runoff(P: float, CN: float) -> float` that:
- Validates all inputs
- Handles all edge cases
- Returns Q in mm
- Uses type hints
- Includes a descriptive docstring

=== VERIFICATION PHASE (write this third) ===

After writing the code, list 5 test cases that verify physical plausibility.
```

## Expected AI Reasoning Trace

A well-structured AI should produce reasoning like:

1. "S = (25400/CN) - 254. For CN=80, S = (25400/80) - 254 = 317.5 - 254 = 63.5 mm"
2. "Ia = 0.2 * 63.5 = 12.7 mm"
3. "If P = 10 mm, then P < Ia (10 < 12.7), so Q = 0"
4. "If P = 50 mm, then Q = (50 - 12.7)^2 / (50 - 12.7 + 63.5) = 1391.29 / 100.8 = 13.8 mm"
5. "Check: 13.8 < 50, and 13.8 > 0"
