"""Tests for annotations module.

This module contains comprehensive tests for the get_sig_marker function,
covering various edge cases, custom configurations, and error handling.
"""

import numpy as np
import pytest

from matplotkit.annotations import get_sig_marker


class TestGetSigMarkerDefaultBehavior:
    """Test default behavior of get_sig_marker function.

    Tests the standard statistical significance markers with default
    thresholds (0.001, 0.01, 0.05).
    """

    @pytest.mark.parametrize(
        "p_val,expected",
        [
            (0.0005, "***"),  # Very significant, below 0.001
            (0.0001, "***"),  # Extremely significant
            (0.0009, "***"),  # Just below 0.001
            (0.005, "**"),  # Significant, below 0.01
            (0.009, "**"),  # Just below 0.01
            (0.03, "*"),  # Marginally significant, below 0.05
            (0.049, "*"),  # Just below 0.05
            (0.1, ""),  # Not significant
            (0.5, ""),  # Not significant
            (1.0, ""),  # Maximum p-value, not significant
        ],
    )
    def test_default_thresholds(self, p_val, expected):
        """Test that default thresholds work correctly.

        This test verifies that the function correctly assigns markers
        based on standard statistical significance levels.
        """
        assert get_sig_marker(p_val) == expected

    @pytest.mark.parametrize(
        "p_val,expected",
        [
            (0.001, "**"),  # Boundary: exactly at 0.001, should not match
            (0.01, "*"),  # Boundary: exactly at 0.01, should not match
            (0.05, ""),  # Boundary: exactly at 0.05, should not match
        ],
    )
    def test_boundary_values(self, p_val, expected):
        """Test boundary values (exact threshold matches).

        This test ensures that p-values exactly equal to thresholds
        are not considered significant at that level (strict inequality).
        """
        assert get_sig_marker(p_val) == expected

    def test_zero_p_value(self):
        """Test p-value of exactly 0.

        Zero p-value should be highly significant (***).
        """
        assert get_sig_marker(0.0) == "***"


class TestGetSigMarkerCustomThresholds:
    """Test get_sig_marker with custom thresholds and markers.

    Tests the function's flexibility with user-defined significance
    levels and marker symbols.
    """

    @pytest.mark.parametrize(
        "p_val,thresholds,markers,expected",
        [
            (
                0.05,
                [0.2, 0.1],
                ["+", "-"],
                "-",
            ),  # Custom thresholds (descending): p<0.1 returns "-"
            (
                0.15,
                [0.2, 0.1],
                ["+", "-"],
                "+",
            ),  # Custom thresholds (descending): p<0.2 returns "+"
            (0.25, [0.2, 0.1], ["+", "-"], ""),  # Not significant
            (
                0.0001,
                [0.001, 0.0001],
                ["!!", "!"],
                "!!",
            ),  # Very strict (descending): p=0.0001 < 0.001 returns "!!"
            (
                0.0005,
                [0.001, 0.0001],
                ["!!", "!"],
                "!!",
            ),  # Very strict (descending): p<0.001 returns "!!"
        ],
    )
    def test_custom_thresholds_and_markers(self, p_val, thresholds, markers, expected):
        """Test custom thresholds and markers.

        This test verifies that users can define their own significance
        levels and corresponding marker symbols.
        """
        result = get_sig_marker(p_val, thresholds=thresholds, markers=markers)
        assert result == expected

    def test_single_threshold(self):
        """Test with a single custom threshold.

        Tests the function with only one significance level.
        """
        assert get_sig_marker(0.03, thresholds=[0.05], markers=["*"]) == "*"
        assert get_sig_marker(0.1, thresholds=[0.05], markers=["*"]) == ""

    def test_multiple_thresholds(self):
        """Test with multiple custom thresholds.

        Tests the function with more than three significance levels.
        """
        thresholds = [0.1, 0.05, 0.01, 0.001, 0.0001]  # Descending order
        markers = ["+", "*", "**", "***", "****"]
        # Check from most strict (last) to least strict (first)
        assert (
            get_sig_marker(0.00005, thresholds=thresholds, markers=markers)
            == "****"  # Matches 0.0001 (most strict)
        )
        assert (
            get_sig_marker(0.0005, thresholds=thresholds, markers=markers)
            == "***"  # Matches 0.001
        )
        assert (
            get_sig_marker(0.005, thresholds=thresholds, markers=markers)
            == "**"  # Matches 0.01
        )
        assert (
            get_sig_marker(0.03, thresholds=thresholds, markers=markers)
            == "*"  # Matches 0.05
        )
        assert (
            get_sig_marker(0.08, thresholds=thresholds, markers=markers)
            == "+"  # Matches 0.1
        )
        assert (
            get_sig_marker(0.15, thresholds=thresholds, markers=markers)
            == ""  # Not significant
        )


class TestGetSigMarkerNsMarker:
    """Test the ns_marker parameter.

    Tests the ability to customize the marker returned for
    non-significant p-values.
    """

    @pytest.mark.parametrize(
        "p_val,ns_marker,expected",
        [
            (0.1, "ns", "ns"),  # Standard ns marker
            (0.5, "ns", "ns"),  # Standard ns marker
            (0.1, "n.s.", "n.s."),  # Alternative format
            (0.1, "NS", "NS"),  # Uppercase
            (0.1, "", ""),  # Empty string (default)
            (0.1, "not sig", "not sig"),  # Descriptive text
        ],
    )
    def test_custom_ns_marker(self, p_val, ns_marker, expected):
        """Test custom non-significant markers.

        This test verifies that users can specify what marker to use
        for non-significant p-values.
        """
        result = get_sig_marker(p_val, ns_marker=ns_marker)
        assert result == expected

    def test_ns_marker_with_significant_p(self):
        """Test that ns_marker is not used for significant p-values.

        Ensures that ns_marker only applies to non-significant results.
        """
        assert get_sig_marker(0.001, ns_marker="ns") == "**"
        assert get_sig_marker(0.01, ns_marker="ns") == "*"
        assert get_sig_marker(0.03, ns_marker="ns") == "*"


class TestGetSigMarkerInputValidation:
    """Test input validation and error handling.

    Tests the function's behavior with invalid inputs, both in
    strict mode (raises errors) and non-strict mode (returns ns_marker).
    """

    @pytest.mark.parametrize(
        "invalid_input",
        [
            -0.1,  # Negative p-value
            -1.0,  # Strongly negative
            -0.0001,  # Small negative
            1.1,  # Greater than 1
            2.0,  # Much greater than 1
            100,  # Very large number
        ],
    )
    def test_invalid_p_value_range_strict(self, invalid_input):
        """Test that invalid p-value ranges raise ValueError in strict mode.

        P-values must be between 0 and 1. This test verifies that
        out-of-range values raise appropriate errors.
        """
        with pytest.raises(ValueError, match="p_val must be between 0 and 1"):
            get_sig_marker(invalid_input, strict=True)

    @pytest.mark.parametrize(
        "invalid_input",
        [
            -0.1,
            -1.0,
            1.1,
            2.0,
            100,
        ],
    )
    def test_invalid_p_value_range_non_strict(self, invalid_input):
        """Test that invalid p-value ranges return ns_marker in non-strict mode.

        When strict=False, invalid p-values should return ns_marker
        instead of raising an error.
        """
        result = get_sig_marker(invalid_input, strict=False)
        assert result == ""

    @pytest.mark.parametrize(
        "invalid_type",
        [
            "0.05",  # String
            "not a number",  # Invalid string
            None,  # None
            [],  # Empty list
            [0.05],  # List
            {},  # Dictionary
            {"p": 0.05},  # Dictionary with value
        ],
    )
    def test_invalid_type_strict(self, invalid_type):
        """Test that non-numeric types raise TypeError in strict mode.

        The function should only accept numeric types (int, float).
        """
        with pytest.raises(TypeError, match="p_val must be a number"):
            get_sig_marker(invalid_type, strict=True)

    @pytest.mark.parametrize(
        "invalid_type",
        [
            "0.05",
            "not a number",
            None,
            [],
            {},
        ],
    )
    def test_invalid_type_non_strict(self, invalid_type):
        """Test that non-numeric types return ns_marker in non-strict mode.

        When strict=False, invalid types should return ns_marker
        instead of raising an error.
        """
        result = get_sig_marker(invalid_type, strict=False)
        assert result == ""

    def test_numpy_types(self):
        """Test that numpy numeric types are accepted.

        Numpy int and float types should work correctly.
        Note: np.float32 has precision limitations, so we use values
        that can be accurately represented.
        """
        assert get_sig_marker(np.float64(0.001)) == "**"
        # np.float32(0.01) has precision issues, use a value that works correctly
        # 0.03 is between 0.01 and 0.05, so it should return "*"
        assert get_sig_marker(np.float32(0.03)) == "*"
        assert get_sig_marker(np.int32(0)) == "***"
        assert get_sig_marker(np.int64(0)) == "***"


class TestGetSigMarkerThresholdValidation:
    """Test validation of thresholds and markers parameters.

    Tests that the function properly validates the thresholds and
    markers arguments.
    """

    def test_mismatched_lengths(self):
        """Test that mismatched threshold and marker lengths raise error.

        thresholds and markers must have the same length.
        """
        with pytest.raises(
            ValueError, match="thresholds and markers must have the same length"
        ):
            get_sig_marker(0.05, thresholds=[0.01, 0.05], markers=["*"])

    def test_invalid_threshold_range(self):
        """Test that thresholds outside [0, 1] raise error.

        All thresholds must be between 0 and 1.
        """
        with pytest.raises(ValueError, match="All thresholds must be between 0 and 1"):
            get_sig_marker(0.05, thresholds=[-0.1, 0.05], markers=["*", "**"])

        with pytest.raises(ValueError, match="All thresholds must be between 0 and 1"):
            get_sig_marker(0.05, thresholds=[0.05, 1.5], markers=["*", "**"])

    def test_non_descending_thresholds(self):
        """Test that non-descending thresholds raise error.

        Thresholds must be provided in descending order.
        """
        with pytest.raises(ValueError, match="thresholds must be in descending order"):
            get_sig_marker(
                0.05, thresholds=[0.01, 0.001, 0.05], markers=["*", "**", "***"]
            )

    def test_empty_thresholds(self):
        """Test that empty thresholds list works correctly.

        Empty thresholds should always return ns_marker.
        """
        assert get_sig_marker(0.001, thresholds=[], markers=[]) == ""


class TestGetSigMarkerEdgeCases:
    """Test various edge cases and special scenarios.

    Tests unusual but valid inputs and combinations of parameters.
    """

    def test_very_small_p_values(self):
        """Test extremely small p-values.

        Tests p-values close to machine epsilon.
        """
        assert get_sig_marker(1e-10) == "***"
        assert get_sig_marker(1e-6) == "***"
        assert get_sig_marker(1e-4) == "***"

    def test_p_value_near_one(self):
        """Test p-values very close to 1.

        Tests p-values just below 1.0.
        """
        assert get_sig_marker(0.999) == ""
        assert get_sig_marker(0.9999) == ""

    def test_integer_p_values(self):
        """Test that integer p-values work correctly.

        Integer 0 and 1 should be handled properly.
        """
        assert get_sig_marker(0) == "***"
        assert get_sig_marker(1) == ""

    def test_float_precision(self):
        """Test handling of floating point precision issues.

        Tests p-values that might have floating point representation issues.
        """
        # Values just above and below thresholds
        assert get_sig_marker(0.001 + 1e-10) == "**"
        assert get_sig_marker(0.001 - 1e-10) == "***"
        assert get_sig_marker(0.01 + 1e-10) == "*"
        assert get_sig_marker(0.01 - 1e-10) == "**"
        assert get_sig_marker(0.05 + 1e-10) == ""
        assert get_sig_marker(0.05 - 1e-10) == "*"

    def test_custom_thresholds_with_ns_marker(self):
        """Test combining custom thresholds with custom ns_marker.

        Tests that both customizations work together.
        """
        result = get_sig_marker(
            0.15,
            thresholds=[0.2, 0.1],  # Descending order
            markers=["+", "-"],
            ns_marker="ns",
        )
        assert result == "+"

        result = get_sig_marker(
            0.25,
            thresholds=[0.2, 0.1],  # Descending order
            markers=["+", "-"],
            ns_marker="ns",
        )
        assert result == "ns"

    def test_all_parameters_customized(self):
        """Test with all parameters customized simultaneously.

        Tests the function with maximum customization.
        """
        result = get_sig_marker(
            p_val=0.0005,
            thresholds=[0.01, 0.001, 0.0001],  # Descending order
            markers=["!", "!!", "!!!"],
            ns_marker="n.s.",
            strict=True,
        )
        assert result == "!!"  # Matches 0.001 (second most strict)


class TestGetSigMarkerFixtures:
    """Test using pytest fixtures for common test data.

    Demonstrates the use of fixtures for reusable test configurations.
    """

    @pytest.fixture
    def standard_thresholds(self):
        """Fixture providing standard significance thresholds."""
        return [0.05, 0.01, 0.001]  # Descending order

    @pytest.fixture
    def standard_markers(self):
        """Fixture providing standard significance markers."""
        return ["*", "**", "***"]  # Corresponding to thresholds

    @pytest.fixture
    def custom_config(self):
        """Fixture providing a custom configuration."""
        return {
            "thresholds": [0.3, 0.2, 0.1],  # Descending order
            "markers": ["+++", "++", "+"],
            "ns_marker": "ns",
        }

    def test_with_standard_fixtures(self, standard_thresholds, standard_markers):
        """Test using standard threshold and marker fixtures.

        Demonstrates how fixtures can be used to provide common
        test data across multiple tests.
        """
        assert (
            get_sig_marker(
                0.0005, thresholds=standard_thresholds, markers=standard_markers
            )
            == "***"
        )
        assert (
            get_sig_marker(
                0.005, thresholds=standard_thresholds, markers=standard_markers
            )
            == "**"
        )
        assert (
            get_sig_marker(
                0.05, thresholds=standard_thresholds, markers=standard_markers
            )
            == ""
        )

    def test_with_custom_fixture(self, custom_config):
        """Test using custom configuration fixture.

        Shows how fixtures can encapsulate complex test configurations.
        """
        # thresholds = [0.3, 0.2, 0.1], markers = ["+++", "++", "+"]
        result = get_sig_marker(0.05, **custom_config)
        assert result == "+"  # Matches 0.1 (most strict)

        result = get_sig_marker(0.15, **custom_config)
        assert result == "++"  # Matches 0.2

        result = get_sig_marker(0.5, **custom_config)
        assert result == "ns"  # Not significant
