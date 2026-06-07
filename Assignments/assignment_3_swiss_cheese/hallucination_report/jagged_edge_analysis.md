# Jagged Edge Analysis

## Systematic AI Weaknesses in Flood Modeling

### Category 1: Boundary Condition Blindness
| Weakness | Example | Frequency |
|----------|---------|-----------|
| Edge equality (== water level) | AI treats elevation == water_level as flooded | Common |
| Non-flooded cell handling | Negative depths for dry cells | Very common |
| Empty/invalid input | No NaN or edge-case validation | Universal |

### Category 2: Physics Approximation
| Weakness | Example | Frequency |
|----------|---------|-----------|
| Volume conservation ignored | Volume sums all cells including negatives | Common |
| Monotonicity not checked | AI rarely ensures flood % increases with water level | Very common |
| Depth bounds not validated | No check that depth <= water_level - min(elevation) | Common |

### Category 3: Numerical Instability
| Weakness | Example | Frequency |
|----------|---------|-----------|
| Floating point equality | Using == for water level comparison | Occasional |
| Extreme values | No handling of very large/small water levels | Common |

## The Swiss Cheese Layers

```
Layer 1: Unit Tests
  Catches: Basic logic errors
  Misses: Physical impossibility

Layer 2: Boundary Tests
  Catches: Off-by-one, extreme values
  Misses: Cumulative errors (volume summing)

Layer 3: Physical Tests
  Catches: Monotonicity violations, impossible depths
  Misses: Numerical stability

Layer 4: Regression Tests
  Catches: Result reproducibility
  Misses: Novel edge cases
```

## Recommendation

1. Always test depth arrays for negative values
2. Always verify monotonicity — catches 80% of AI errors
3. Never trust volume calculations from AI
4. Always add explicit np.where for depth masking
