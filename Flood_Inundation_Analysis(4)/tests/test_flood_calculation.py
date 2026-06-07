import numpy as np
import pytest
from flood_inundation import load_dem, calculate_flood, dem_metadata


@pytest.fixture
def dem():
    return load_dem()


@pytest.fixture
def flat_dem():
    return np.full((10, 10), 50.0, dtype=np.float64)


class TestFloodCalculation:
    def test_flood_basic(self, dem):
        result = calculate_flood(dem, 45)
        assert isinstance(result["flooded_mask"], np.ndarray)
        assert result["flooded_mask"].dtype == bool
        assert result["flooded_mask"].shape == dem.shape

    def test_depth_calculation(self, dem):
        wl = 45.0
        result = calculate_flood(dem, wl)
        depth = result["depth_array"]
        assert np.all(depth >= 0)
        assert np.all(depth[depth > 0] <= wl - dem.min())

    def test_percentage_range(self, dem):
        for wl in [30, 40, 50, 60, 80]:
            result = calculate_flood(dem, float(wl))
            assert 0.0 <= result["flooded_percentage"] <= 100.0

    def test_no_flood_below_min(self, dem):
        min_elev = float(dem.min())
        result = calculate_flood(dem, min_elev - 10)
        assert result["flooded_percentage"] == 0.0
        assert np.all(result["depth_array"] == 0)

    def test_full_flood_above_max(self, dem):
        max_elev = float(dem.max())
        result = calculate_flood(dem, max_elev + 10)
        assert result["flooded_percentage"] == 100.0

    def test_flooded_percentage_increases(self, dem):
        pcts = []
        for wl in range(40, 51):
            r = calculate_flood(dem, float(wl))
            pcts.append(r["flooded_percentage"])
        assert all(pcts[i] <= pcts[i + 1] for i in range(len(pcts) - 1))

    def test_maximum_depth_consistency(self, dem):
        wl = 50.0
        result = calculate_flood(dem, wl)
        expected_max = wl - float(dem[dem < wl].min())
        assert abs(result["maximum_depth"] - expected_max) < 1e-6

    def test_average_depth(self, dem):
        result = calculate_flood(dem, 45.0)
        if result["flooded_percentage"] > 0:
            flooded_depths = result["depth_array"][result["flooded_mask"]]
            assert abs(result["average_depth"] - float(flooded_depths.mean())) < 1e-6

    def test_dem_metadata(self, dem):
        meta = dem_metadata(dem)
        assert "min_elevation" in meta
        assert "max_elevation" in meta
        assert "mean_elevation" in meta
        assert "shape" in meta
        assert meta["shape"] == dem.shape
        assert 30 <= meta["min_elevation"] <= 80
        assert 30 <= meta["max_elevation"] <= 80


class TestFlatDEM:
    def test_flat_dem_at_level(self, flat_dem):
        result = calculate_flood(flat_dem, 50.0)
        assert result["flooded_percentage"] == 0.0

    def test_flat_dem_above(self, flat_dem):
        result = calculate_flood(flat_dem, 51.0)
        assert result["flooded_percentage"] == 100.0

    def test_flat_dem_below(self, flat_dem):
        result = calculate_flood(flat_dem, 49.0)
        assert result["flooded_percentage"] == 0.0
