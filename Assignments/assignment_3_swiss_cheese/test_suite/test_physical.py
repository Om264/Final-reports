import numpy as np
from flood_model.inundation import compute_flood, flood_percentage, flood_volume


class TestPhysicalValidity:
    def test_flooded_area_increases_with_water_level(self):
        elev = np.array([[30, 50], [70, 90]])
        levels = [40, 60, 80, 100]
        pcts = [flood_percentage(compute_flood(elev, wl)[0]) for wl in levels]
        for i in range(len(pcts) - 1):
            assert pcts[i] <= pcts[i + 1], f"Decreased at level {levels[i+1]}"

    def test_flood_volume_increases_with_water_level(self):
        elev = np.array([[30, 50], [70, 90]])
        levels = [40, 60, 80, 100]
        vols = [flood_volume(compute_flood(elev, wl)[1]) for wl in levels]
        for i in range(len(vols) - 1):
            assert vols[i] <= vols[i + 1], f"Volume decreased at {levels[i+1]}"

    def test_depth_never_exceeds_max_possible(self):
        elev = np.array([[30.0, 50.0, 80.0]])
        water_level = 60.0
        _, depth = compute_flood(elev, water_level)
        max_possible = water_level - np.min(elev)
        assert np.all(depth[depth > 0] <= max_possible)

    def test_non_flooded_cells_have_non_positive_depth(self):
        elev = np.array([[30.0, 50.0, 80.0]])
        water_level = 60.0
        flooded, depth = compute_flood(elev, water_level)
        assert np.all(depth[~flooded] <= 0)

    def test_higher_terrain_has_less_flood(self):
        rng = np.random.default_rng(42)
        elev1 = rng.uniform(30, 80, (50, 50))
        elev2 = elev1 + 10
        pct1 = flood_percentage(compute_flood(elev1, 55.0)[0])
        pct2 = flood_percentage(compute_flood(elev2, 55.0)[0])
        assert pct1 >= pct2
