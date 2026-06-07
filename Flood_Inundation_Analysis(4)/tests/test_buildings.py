import numpy as np
import pytest
from building_barriers import create_building_mask, calculate_flood_with_buildings
from flood_inundation import load_dem


@pytest.fixture
def dem():
    return load_dem()


class TestBuildingBarriers:
    def test_building_mask_creation(self):
        mask = create_building_mask((100, 100), num_buildings=8, seed=42)
        assert mask.shape == (100, 100)
        assert mask.dtype == bool
        assert np.sum(mask) > 0

    def test_buildings_reduce_flood(self, dem):
        building_mask = create_building_mask(dem.shape, num_buildings=8, seed=42)
        result = calculate_flood_with_buildings(dem, 45, building_mask)
        assert result["flooded_cells_without_buildings"] >= result["flooded_cells_with_buildings"]

    def test_buildings_reduction_percentage(self, dem):
        building_mask = create_building_mask(dem.shape, num_buildings=8, seed=42)
        result = calculate_flood_with_buildings(dem, 45, building_mask)
        assert 0.0 <= result["reduction_percentage"] <= 100.0

    def test_depth_nonnegative_with_buildings(self, dem):
        building_mask = create_building_mask(dem.shape, num_buildings=8, seed=42)
        result = calculate_flood_with_buildings(dem, 45, building_mask)
        assert np.all(result["depth_array_with_buildings"] >= 0)

    def test_multiple_water_levels(self, dem):
        building_mask = create_building_mask(dem.shape, num_buildings=8, seed=42)
        for wl in range(40, 51):
            result = calculate_flood_with_buildings(dem, float(wl), building_mask)
            assert result["flooded_cells_without_buildings"] >= result["flooded_cells_with_buildings"]

    def test_building_mask_differs_from_no_buildings(self, dem):
        building_mask = create_building_mask(dem.shape, num_buildings=8, seed=42)
        result = calculate_flood_with_buildings(dem, 45, building_mask)
        if result["reduction_percentage"] > 0:
            assert result["flooded_cells_with_buildings"] < result["flooded_cells_without_buildings"]
