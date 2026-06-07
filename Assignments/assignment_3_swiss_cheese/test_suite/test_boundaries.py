import numpy as np
import pytest
from flood_model.inundation import compute_flood, flood_percentage


class TestBoundaryConditions:
    def test_water_level_equals_elevation(self):
        elev = np.array([[50.0]])
        flooded, depth = compute_flood(elev, water_level=50.0)
        assert flooded[0, 0] == False
        assert depth[0, 0] == 0.0

    def test_water_level_just_above_elevation(self):
        elev = np.array([[50.0]])
        flooded, _ = compute_flood(elev, water_level=50.0001)
        assert flooded[0, 0] == True

    def test_water_level_just_below_elevation(self):
        elev = np.array([[50.0]])
        flooded, _ = compute_flood(elev, water_level=49.9999)
        assert flooded[0, 0] == False

    def test_extreme_negative_water_level(self):
        elev = np.full((10, 10), 50.0)
        flooded, _ = compute_flood(elev, water_level=-1000.0)
        assert np.sum(flooded) == 0

    def test_extreme_high_water_level(self):
        elev = np.full((10, 10), 50.0)
        flooded, _ = compute_flood(elev, water_level=10000.0)
        assert np.sum(flooded) == 100

    def test_single_cell_dem(self):
        elev = np.array([[55.0]])
        flooded, depth = compute_flood(elev, water_level=60.0)
        assert flooded[0, 0] == True
        assert depth[0, 0] == 5.0

    def test_zero_size_array(self):
        elev = np.zeros((0, 10))
        with pytest.raises((ValueError, IndexError)):
            compute_flood(elev, water_level=50.0)
