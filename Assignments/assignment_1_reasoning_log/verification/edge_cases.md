# Edge Cases Verified

## Boundary Condition Matrix

| Test Case | P (mm) | CN | Expected Q | Physical Meaning |
|-----------|--------|-----|-----------|------------------|
| No rain | 0 | 80 | 0 | No precipitation |
| Below Ia | 10 | 80 | 0 | All rainfall absorbed |
| Above Ia | 50 | 80 | ~13.8 | Normal runoff event |
| High CN | 50 | 95 | ~33.5 | Impervious surface |
| Low CN | 50 | 30 | ~0.0 | Very pervious (sand) |
| Extreme CN=100 | 50 | 100 | ~50.0 | Fully impervious |
| Extreme CN=30 | 50 | 30 | ~0.01 | Maximum infiltration |
| Extreme rain | 1000 | 80 | ~910 | Hurricane event |

## Errors the AI Typically Makes

1. **Ia mis-definition:** Writing `(P - 0.2*S)**2 / (P + 0.8*S)` instead of defining Ia separately.
2. **Missing P < Ia check:** Some implementations fail to check `P <= Ia` and compute negative values, then take sqrt of negative number -> NaN.
3. **No lower bound on Q:** SCS-CN should never produce negative runoff, but floating-point edge cases can produce tiny negative values (-1e-16).
4. **CN boundary:** Some AIs allow CN > 100 or CN < 30 without warning.
5. **S at CN=100:** S = (25400/100) - 254 = 0. Then Ia = 0, and Q = P^2 / P = P. Correct.
