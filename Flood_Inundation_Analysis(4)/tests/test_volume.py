import numpy as np
import pytest
from volume_analysis import calculate_flood_volume, flood_volume_curve


@pytest.fixture
def dem():
    from flood_inundation import load_dem
    return load_dem()


class TestFloodVolume:
    def test_volume_nonnegative(self, dem):
        depth = np.zeros_like(dem)
        vol = calculate_flood_volume(dem, depth)
        assert vol["total_volume_m3"] == 0

    def test_volume_positive_for_flooded(self, dem):
        depth = np.ones_like(dem) * 2.0
        vol = calculate_flood_volume(dem, depth)
        expected = 2.0 * dem.size * (30.0 ** 2)
        assert vol["total_volume_m3"] == pytest.approx(expected)

    def test_volume_increases_with_level(self, dem):
        levels = list(range(40, 51))
        r = flood_volume_curve(dem, levels)
        assert all(r["volumes"][i] <= r["volumes"][i + 1] for i in range(len(r["volumes"]) - 1))

    def test_cell_area(self, dem):
        depth = np.ones_like(dem) * 1.0
        vol = calculate_flood_volume(dem, depth, cell_size=30.0)
        assert vol["cell_area_m2"] == 900.0
        assert vol["total_volume_m3"] == float(dem.size * 900.0)

    def test_average_depth(self, dem):
        depth = np.full_like(dem, 3.0)
        vol = calculate_flood_volume(dem, depth)
        assert vol["average_depth"] == pytest.approx(3.0)
        assert vol["maximum_depth"] == pytest.approx(3.0)

    def test_flooded_cells_count(self, dem):
        depth = np.zeros_like(dem)
        depth[:10, :10] = 2.0
        vol = calculate_flood_volume(dem, depth)
        assert vol["flooded_cells"] == 100

    def test_volume_zero_if_no_flood(self, dem):
        depth = np.zeros_like(dem)
        vol = calculate_flood_volume(dem, depth)
        assert vol["total_volume_m3"] == 0.0
        assert vol["average_depth"] == 0.0
        assert vol["maximum_depth"] == 0.0

    def test_custom_cell_size(self, dem):
        depth = np.ones_like(dem) * 2.0
        vol = calculate_flood_volume(dem, depth, cell_size=10.0)
        assert vol["cell_area_m2"] == 100.0
        expected_vol = 2.0 * dem.size * 100.0
        assert vol["total_volume_m3"] == pytest.approx(expected_vol)

    def test_volume_curve_returns_all_keys(self, dem):
        r = flood_volume_curve(dem)
        assert "levels" in r
        assert "volumes" in r
        assert "depths" in r
        assert len(r["levels"]) == len(r["volumes"]) == len(r["depths"])
