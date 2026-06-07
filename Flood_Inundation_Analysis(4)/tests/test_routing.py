import numpy as np
import pytest
from flood_routing import simulate_flood_routing, flood_spread_continuous


@pytest.fixture
def dem():
    from flood_inundation import load_dem
    return load_dem()


class TestFloodRouting:
    def test_routing_4_connectivity(self, dem):
        result = simulate_flood_routing(dem, 45, connectivity="4")
        assert result["flood_extent"].shape == dem.shape
        assert result["depth_map"].shape == dem.shape
        assert result["arrival_time"].shape == dem.shape
        assert np.all(result["depth_map"] >= 0)

    def test_routing_8_connectivity(self, dem):
        result = simulate_flood_routing(dem, 45, connectivity="8")
        assert result["flood_extent"].shape == dem.shape
        assert result["depth_map"].shape == dem.shape
        assert result["arrival_time"].shape == dem.shape

    def test_8_connects_more_than_4(self, dem):
        r4 = simulate_flood_routing(dem, 45, connectivity="4")
        r8 = simulate_flood_routing(dem, 45, connectivity="8")
        assert np.sum(r8["flood_extent"]) >= np.sum(r4["flood_extent"])

    def test_arrival_time_nonnegative(self, dem):
        result = simulate_flood_routing(dem, 45, connectivity="8")
        flooded = result["flood_extent"]
        assert np.all(result["arrival_time"][flooded] >= 0)
        assert np.all(result["arrival_time"][~flooded] == -1)

    def test_depth_consistency(self, dem):
        wl = 45.0
        result = simulate_flood_routing(dem, wl, connectivity="8")
        flooded = result["flood_extent"]
        expected_depth = np.maximum(wl - dem, 0)
        assert np.allclose(result["depth_map"][flooded], expected_depth[flooded])

    def test_flood_spread_continuous_4(self, dem):
        result = simulate_flood_routing(dem, 45, connectivity="4")
        continuous = flood_spread_continuous(result["flood_extent"], "4")
        assert continuous

    def test_flood_spread_continuous_8(self, dem):
        result = simulate_flood_routing(dem, 45, connectivity="8")
        continuous = flood_spread_continuous(result["flood_extent"], "8")
        assert continuous

    def test_no_flood_above_water(self, dem):
        min_elev = float(dem.min())
        result = simulate_flood_routing(dem, min_elev - 5, connectivity="8")
        assert np.sum(result["flood_extent"]) == 0

    def test_source_out_of_bounds(self, dem):
        with pytest.raises(ValueError):
            simulate_flood_routing(dem, 45, connectivity="8", source=(999, 999))
