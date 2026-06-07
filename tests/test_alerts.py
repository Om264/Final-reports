import tempfile
import unittest
from pathlib import Path

from app.alert_system import AlertSystem


class TestAlertSystem(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = Path(self.temp_dir) / "test_alert_log.txt"
        self.alert_system = AlertSystem(log_file=self.log_file)

    def tearDown(self) -> None:
        if self.log_file.exists():
            self.log_file.unlink()

    def test_green_alert_below_10(self) -> None:
        level, status = self.alert_system.evaluate(5.0, "Beijing")
        self.assertEqual(level, "GREEN")
        self.assertEqual(status, "Normal")

    def test_green_alert_zero(self) -> None:
        level, status = self.alert_system.evaluate(0.0, "Beijing")
        self.assertEqual(level, "GREEN")

    def test_yellow_alert_between_10_and_20(self) -> None:
        level, status = self.alert_system.evaluate(15.0, "Beijing")
        self.assertEqual(level, "YELLOW")
        self.assertEqual(status, "Warning")

    def test_yellow_alert_at_10(self) -> None:
        level, status = self.alert_system.evaluate(10.0, "Beijing")
        self.assertEqual(level, "YELLOW")

    def test_red_alert_at_20(self) -> None:
        level, status = self.alert_system.evaluate(20.0, "Beijing")
        self.assertEqual(level, "RED")
        self.assertEqual(status, "Danger - ALERT")

    def test_red_alert_above_20(self) -> None:
        level, status = self.alert_system.evaluate(35.5, "Beijing")
        self.assertEqual(level, "RED")

    def test_red_alert_logs_to_file(self) -> None:
        self.alert_system.evaluate(25.0, "Shanghai")
        self.assertTrue(self.log_file.exists())
        content = self.log_file.read_text()
        self.assertIn("Shanghai", content)
        self.assertIn("RED", content)
        self.assertIn("25.00", content)

    def test_load_alert_history(self) -> None:
        self.alert_system.evaluate(25.0, "Beijing")
        self.alert_system.evaluate(5.0, "Shanghai")
        history = self.alert_system.load_alert_history()
        self.assertGreaterEqual(len(history), 1)

    def test_alert_summary(self) -> None:
        self.alert_system.evaluate(5.0, "Beijing")
        self.alert_system.evaluate(15.0, "Shanghai")
        self.alert_system.evaluate(25.0, "Guangzhou")
        self.alert_system.evaluate(30.0, "Shenzhen")
        self.alert_system.evaluate(3.0, "Wuhan")
        summary = self.alert_system.alert_summary()
        self.assertEqual(summary["GREEN"], 2)
        self.assertEqual(summary["YELLOW"], 1)
        self.assertEqual(summary["RED"], 2)

    def test_get_current_alert_level(self) -> None:
        self.alert_system.evaluate(5.0, "Beijing")
        self.assertEqual(self.alert_system.get_current_alert_level("Beijing"), "GREEN")

    def test_clear_alerts(self) -> None:
        self.alert_system.evaluate(25.0, "Beijing")
        self.assertEqual(self.alert_system.get_current_alert_level("Beijing"), "RED")
        self.alert_system.clear_alerts()
        self.assertEqual(self.alert_system.get_current_alert_level("Beijing"), "GREEN")

    def test_load_empty_history(self) -> None:
        history = self.alert_system.load_alert_history()
        self.assertEqual(history, [])

    def test_edge_case_negative_rainfall(self) -> None:
        level, status = self.alert_system.evaluate(-1.0, "Beijing")
        self.assertEqual(level, "GREEN")


if __name__ == "__main__":
    unittest.main()
