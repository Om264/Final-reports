# Detected AI Hallucinations

## Hallucination 1: Non-flooded cells have negative depth

**Severity:** HIGH

The AI's `compute_flood` computes `depth = water_level - elevation` for ALL cells. Non-flooded cells get negative depth values.

**Impact:** flood_volume() sums all depths, so negative values reduce the total volume. max_flood_depth() returns negative when nothing is flooded.

**Caught by:** `test_depth_is_zero_for_non_flooded` — checks depth for non-flooded cell is 0. AI gives -40.0.

**Fix:** `depth = np.where(flooded, water_level - elevation, 0.0)`

## Hallucination 2: Flood volume incorrect for partially flooded terrain

**Severity:** HIGH

Because flood_volume sums depth over all cells including negative values from non-flooded cells, volume is lower than true value. Can be negative.

**Caught by:** `test_flood_volume_zero_when_no_flood` — volume should be >= 0.

## Hallucination 3: Max depth negative when nothing flooded

**Severity:** MEDIUM

When water level is below all terrain, max depth should be 0.0. AI returns maximum negative value.

**Caught by:** `test_max_depth_zero_when_no_flood`

## Hallucination 4: Missing input validation

**Severity:** LOW

No checks for NaN values in elevation, negative cell_area, or empty arrays.

## Summary

| # | Hallucination | Test That Caught It |
|---|--------------|-------------------|
| 1 | Negative depth for non-flooded | test_depth_is_zero_for_non_flooded |
| 2 | Volume includes negative depths | test_flood_volume_zero_when_no_flood |
| 3 | Max depth negative when no flood | test_max_depth_zero_when_no_flood |
| 4 | No NaN/empty validation | Manual inspection |
