# Prompt 3: AI Self-Verification

**Strategy:** Ask the AI to audit its own code for physical and numerical errors.

## Prompt

```
You are a Code Reviewer specializing in hydrological software validation.
Review the SCS-CN function you just wrote. Check for:

=== NUMERICAL ISSUES ===
1. Floating-point comparison: P <= Ia uses approximate equality. Is this safe?
2. Division by zero: Can P - Ia + S ever be 0? Under what conditions?
3. Extreme values: What happens at CN=100? At CN=30? At P=0?

=== PHYSICAL ISSUES ===
1. Is runoff monotonic with respect to P? (dQ/dP should always be positive)
2. Is runoff monotonic with respect to CN? (higher CN -> more runoff)
3. Does Q approach P as CN -> 100 for large P?
4. Does Q approach 0 as CN -> 30?

=== EDGE CASES ===
1. What if P is extremely large (e.g., 10000 mm)?
2. What if CN is a float like 80.5?
3. What if CN is exactly 30 or exactly 100?
4. What if P is extremely small but positive (e.g., 0.001 mm)?

Write a validation function that checks all these conditions automatically.
If you find any issues in the original code, explain the fix.
```

## Purpose

This tests whether the AI can:
- Detect numerical instability in its own code
- Identify missing boundary checks
- Self-correct without human intervention
- Distinguish between "runs without error" and "physically correct"
