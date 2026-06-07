import numpy as np
from flood_model.inundation import compute_flood, flood_percentage


class TestRegression:
    def test_known_case_simple_valley(self):
        x = np.linspace(0, 1, 5)
        y = np.linspace(0, 1, 5)
        xx, yy = np.meshgrid(x, y)
        valley = 50 - 20 * np.sqrt((xx - 0.5)**2 + (yy - 0.5)**2)
        flooded, _ = compute_flood(valley, 45.0)
        pct = flood_percentage(flooded)
        assert 20 < pct < 80

    def test_reproducible_results(self):
        elev = np.array([[30, 50], [70, 90]])
        r1, d1 = compute_flood(elev, 55.0)
        r2, d2 = compute_flood(elev, 55.0)
        assert np.array_equal(r1, r2)
        assert np.array_equal(d1, d2)

    def test_flat_terrain_half_flooded(self):
        elev = np.full((100, 100), 50.0)
        flooded, _ = compute_flood(elev, 50.0)
        assert np.sum(flooded) == 0

    def test_flat_terrain_all_flooded(self):
        elev = np.full((100, 100), 50.0)
        flooded, _ = compute_flood(elev, 50.0001)
        assert np.sum(flooded) == 10000

    def test_known_depths_uniform_terrain(self):
        elev = np.full((10, 10), 40.0)
        _, depth = compute_flood(elev, 45.0)
        assert np.allclose(depth, 5.0)
