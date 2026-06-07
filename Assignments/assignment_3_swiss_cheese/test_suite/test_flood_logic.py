import numpy as np
from flood_model.inundation import compute_flood, flood_percentage, flood_volume, max_flood_depth


class TestFloodLogic:
    def test_basic_flood_detection(self):
        elev = np.array([[50, 60], [70, 80]])
        flooded, depth = compute_flood(elev, water_level=55.0)
        assert flooded[0, 0] == True
        assert flooded[0, 1] == False
        assert flooded[1, 0] == False
        assert flooded[1, 1] == False

    def test_depth_correctness(self):
        elev = np.array([[50.0]])
        flooded, depth = compute_flood(elev, water_level=55.0)
        assert depth[0, 0] == 5.0

    def test_all_above_water(self):
        elev = np.full((10, 10), 100.0)
        flooded, _ = compute_flood(elev, water_level=50.0)
        assert np.sum(flooded) == 0

    def test_all_below_water(self):
        elev = np.full((10, 10), 30.0)
        flooded, _ = compute_flood(elev, water_level=50.0)
        assert np.sum(flooded) == 100

    def test_flood_percentage_zero(self):
        elev = np.full((10, 10), 50.0)
        flooded, _ = compute_flood(elev, water_level=40.0)
        assert flood_percentage(flooded) == 0.0

    def test_flood_percentage_hundred(self):
        elev = np.full((10, 10), 30.0)
        flooded, _ = compute_flood(elev, water_level=50.0)
        assert flood_percentage(flooded) == 100.0

    def test_depth_is_zero_for_non_flooded(self):
        elev = np.array([[50.0, 100.0]])
        flooded, depth = compute_flood(elev, water_level=60.0)
        assert flooded[0, 0] == True
        assert depth[0, 0] == 10.0
        assert depth[0, 1] == 0.0, f"Expected 0, got {depth[0, 1]}"

    def test_flood_volume_zero_when_no_flood(self):
        elev = np.full((10, 10), 100.0)
        flooded, depth = compute_flood(elev, water_level=50.0)
        vol = flood_volume(depth)
        assert vol >= 0, f"Volume should be >= 0, got {vol}"

    def test_max_depth_zero_when_no_flood(self):
        elev = np.full((10, 10), 100.0)
        _, depth = compute_flood(elev, water_level=50.0)
        max_d = max_flood_depth(depth)
        assert max_d >= 0, f"Max depth should be >= 0, got {max_d}"
