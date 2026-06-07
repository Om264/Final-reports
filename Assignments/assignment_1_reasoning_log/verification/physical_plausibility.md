# Physical Plausibility Verification

## Hydrological Sanity Checks

### 1. Monotonicity Test
Runoff must increase monotonically with both P and CN.

```
CN = 80:
  P = 0   -> Q = 0
  P = 10  -> Q = 0      (below Ia = 12.7)
  P = 20  -> Q = 2.9    (above Ia)
  P = 50  -> Q = 13.8
  P = 100 -> Q = 43.7
  P = 200 -> Q = 127.9
```

### 2. Boundedness Test
Runoff must satisfy 0 <= Q <= P.

| P (mm) | CN | Q (mm) | Q/P | Pass? |
|--------|-----|--------|-----|-------|
| 10 | 80 | 0.0 | 0.0 | YES |
| 50 | 80 | 13.8 | 0.28 | YES |
| 50 | 95 | 33.5 | 0.67 | YES |
| 50 | 100 | 50.0 | 1.0 | YES |

### 3. CN Sensitivity Test
For fixed P, Q must increase with CN.

| P (mm) | CN=60 | CN=80 | CN=95 | Monotonic? |
|--------|-------|-------|-------|------------|
| 30 | 0.0 | 4.1 | 16.4 | YES |
| 50 | 1.7 | 13.8 | 33.5 | YES |
| 100 | 20.6 | 43.7 | 72.6 | YES |

### 4. Asymptotic Behavior
- As CN -> 100, S -> 0, Ia -> 0, Q -> P
- As CN -> 30, S -> 592.7, Ia -> 118.5, Q -> 0 for typical rainfall
- As P -> infinity, Q -> P - Ia

## Common AI Hallucinations Detected

| Hallucination | How We Caught It |
|--------------|------------------|
| AI wrote `(P - 0.2*S)**2 / (P + 0.8*S)` — formula correct but hides Ia | Physical meaning check failed |
| AI claimed CN must be integer between 30 and 100 | CN can be fractional per SCS docs |
| AI added random "safety factor" multiplying Q by 0.9 | Monotonicity test flagged discontinuity |
| AI returned negative Q for P just below Ia | Edge case test caught immediately |
