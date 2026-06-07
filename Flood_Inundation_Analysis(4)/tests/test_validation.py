import numpy as np
import pytest


@pytest.fixture
def dem():
    from flood_inundation import load_dem
    return load_dem()


@pytest.fixture
def building_result(dem):
    from building_barriers import create_building_mask, calculate_flood_with_buildings
    bm = create_building_mask(dem.shape)
    return calculate_flood_with_buildings(dem, 45, bm)


@pytest.fixture
def routing_result(dem):
    from flood_routing import simulate_flood_routing
    return simulate_flood_routing(dem, 45, connectivity="8")


class TestValidation:
    def test_validation_pass(self, dem, building_result, routing_result):
        from validation import validate_flood_model
        result = validate_flood_model(dem, list(range(40, 51)), building_result, routing_result)
        assert result["overall_status"] == "PASS"

    def test_area_monotonic(self, dem, building_result, routing_result):
        from validation import validate_flood_model
        result = validate_flood_model(dem, list(range(40, 51)), {}, routing_result)
        assert result["area_monotonic"] is True

    def test_volume_monotonic(self, dem, building_result, routing_result):
        from validation import validate_flood_model
        result = validate_flood_model(dem, list(range(40, 51)), {}, routing_result)
        assert result["volume_monotonic"] is True

    def test_percentage_range(self, dem, building_result, routing_result):
        from validation import validate_flood_model
        result = validate_flood_model(dem, list(range(40, 51)), {}, routing_result)
        assert result["percentage_range"] is True

    def test_depth_nonnegative(self, dem, building_result, routing_result):
        from validation import validate_flood_model
        result = validate_flood_model(dem, list(range(40, 51)), {}, routing_result)
        assert result["depth_nonnegative"] is True

    def test_volume_nonnegative(self, dem, building_result, routing_result):
        from validation import validate_flood_model
        result = validate_flood_model(dem, list(range(40, 51)), {}, routing_result)
        assert result["volume_nonnegative"] is True

    def test_buildings_reduce_flood(self, dem, building_result, routing_result):
        from validation import validate_flood_model
        result = validate_flood_model(dem, list(range(40, 51)), building_result, routing_result)
        assert result["buildings_reduce_flood"] is True

    def test_routing_continuous(self, dem, building_result, routing_result):
        from validation import validate_flood_model
        result = validate_flood_model(dem, list(range(40, 51)), {}, routing_result)
        assert result["routing_continuous"] is True

    def test_edge_cases(self, dem):
        from validation import _check_edge_cases
        edges = _check_edge_cases(dem)
        assert edges["below_min_elevation_zero_flood"]
        assert edges["above_max_elevation_full_flood"]
