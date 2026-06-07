import numpy as np
import pytest
from validation import validate_solution, generate_report
from reservoir_model import (
    MIN_STORAGE,
    MAX_STORAGE,
    ECOLOGICAL_RELEASE,
    MAX_RELEASE,
    INITIAL_STORAGE,
    NUM_DAYS,
)


class TestValidationLogic:
    def test_valid_solution_passes(self):
        releases = np.array([12.5, 10.2, 10.0, 10.0, 13.2, 15.8, 18.0])
        results = validate_solution(releases)
        assert results["overall_status"] == "PASS"

    def test_storage_lower_bound_violation_detected(self):
        releases = np.full(NUM_DAYS, 0.0)
        results = validate_solution(releases)
        if not results["storage_constraints_passed"]:
            assert len(results["storage_violations"]) > 0

    def test_release_lower_bound_violation_detected(self):
        releases = np.full(NUM_DAYS, ECOLOGICAL_RELEASE - 5)
        results = validate_solution(releases)
        assert not results["release_constraints_passed"]
        assert len(results["release_violations"]) > 0

    def test_release_upper_bound_violation_detected(self):
        releases = np.full(NUM_DAYS, MAX_RELEASE + 20)
        results = validate_solution(releases)
        assert not results["release_constraints_passed"]
        assert len(results["release_violations"]) > 0

    def test_known_solution_passes_validation(self):
        releases = np.array([12.5, 10.2, 10.0, 10.0, 13.2, 15.8, 18.0])
        results = validate_solution(releases)
        assert results["storage_constraints_passed"]
        assert results["release_constraints_passed"]
        assert results["mass_balance_passed"]
        assert results["revenue_verified"]

    def test_validation_returns_expected_keys(self):
        releases = np.full(NUM_DAYS, ECOLOGICAL_RELEASE)
        results = validate_solution(releases)
        expected_keys = {
            "storage_constraints_passed",
            "release_constraints_passed",
            "mass_balance_passed",
            "revenue_verified",
            "overall_status",
            "storage_violations",
            "release_violations",
            "mass_balance_errors",
            "details",
        }
        assert set(results.keys()) == expected_keys

    def test_details_contains_expected_fields(self):
        releases = np.full(NUM_DAYS, ECOLOGICAL_RELEASE)
        results = validate_solution(releases)
        expected_fields = {
            "revenue_calculated",
            "revenue_from_sim",
            "ecological_deficit",
            "min_release",
            "max_release",
            "min_storage",
            "max_storage",
        }
        assert expected_fields.issubset(set(results["details"].keys()))


class TestReportGeneration:
    def test_report_generates_without_error(self):
        releases = np.array([12.5, 10.2, 10.0, 10.0, 13.2, 15.8, 18.0])
        results = validate_solution(releases)
        report = generate_report(releases, results, "/tmp/test_validation_report.txt")
        assert isinstance(report, str)
        assert len(report) > 0
        assert "PASS" in report or "FAIL" in report

    def test_report_contains_keywords(self):
        releases = np.full(NUM_DAYS, ECOLOGICAL_RELEASE)
        results = validate_solution(releases)
        report = generate_report(releases, results, "/tmp/test_validation_report_keywords.txt")
        assert "VALIDATION REPORT" in report
        assert "CONSTRAINT VALIDATION" in report
        assert "SUMMARY STATISTICS" in report


class TestEdgeCases:
    def test_validation_empty_releases(self):
        with pytest.raises(Exception):
            validate_solution(np.array([]))

    def test_mass_balance_error_detected(self):
        releases = np.full(NUM_DAYS, ECOLOGICAL_RELEASE)
        results = validate_solution(releases)
        assert results["mass_balance_passed"]
