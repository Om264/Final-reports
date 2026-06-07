import pytest
from pathlib import Path


@pytest.fixture
def dem():
    from flood_inundation import load_dem
    return load_dem()


class TestFloodAnimation:
    def test_animation_generates_gif(self, dem):
        from animation_generator import create_flood_animation
        output_path = Path("outputs/test_rising_flood.gif")
        output_path.parent.mkdir(exist_ok=True)
        result = create_flood_animation(
            dem, min_level=40, max_level=42, step=1.0,
            save_path=str(output_path)
        )
        assert result is not None
        assert output_path.exists()
        assert output_path.stat().st_size > 0
        output_path.unlink(missing_ok=True)

    def test_animation_default_path(self, dem):
        from animation_generator import create_flood_animation
        result = create_flood_animation(
            dem, min_level=40, max_level=45, step=2.5
        )
        assert result is not None
        default_path = Path("outputs/rising_flood.gif")
        assert default_path.exists()
        default_path.unlink(missing_ok=True)
