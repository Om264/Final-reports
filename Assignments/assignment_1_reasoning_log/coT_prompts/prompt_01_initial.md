# Prompt 1: Naive (Unstructured)

**Strategy:** Minimal context, no role, no constraints.

## Prompt

```
Write a Python function to calculate runoff using the SCS-CN method.
The formula is Q = (P - 0.2S)^2 / (P + 0.8S).
```

## Why This Will Fail

1. **Missing Ia definition** — The prompt writes `0.2S` inline instead of defining Ia.
2. **No edge case handling** — P < Ia will produce negative values under the square root.
3. **No input validation** — Negative P or out-of-range CN will silently pass.
4. **No type hints** — Unclear what types P and CN should be.
