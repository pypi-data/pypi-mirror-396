#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/


from matplotlib.axes import Axes


def add_diagonal_line(ax: Axes, **kwargs) -> Axes:
    """Add a 1:1 line to the plot.

    It's useful for comparing two variables in a scatter plot.

    Args:
        ax:
            The axes to add the line to.
        kwargs:
            Keyword arguments to pass to the plot function.

    Returns:
        The axes with the line added.
    """
    vals = [*ax.get_xlim(), *ax.get_ylim()]
    max_val = max(vals)
    min_val = min(vals)
    ax.plot([min_val, max_val], [min_val, max_val], **kwargs)
    return ax


def get_sig_marker(
    p_val,
    thresholds=None,
    markers=None,
    ns_marker="",
    strict=True,
):
    """Get significance marker based on p-value.

    This function returns a marker string indicating the statistical significance
    level based on the provided p-value. By default, it follows the standard
    convention: *** for p < 0.001, ** for p < 0.01, * for p < 0.05.

    Args:
        p_val:
            The p-value to evaluate. Must be a number between 0 and 1.
        thresholds:
            List of significance thresholds in descending order.
            Default is [0.001, 0.01, 0.05].
        markers:
            List of marker strings corresponding to thresholds.
            Default is ["***", "**", "*"].
        ns_marker:
            Marker to return when p-value is not significant.
            Default is empty string "".
        strict:
            If True, raises ValueError for invalid inputs.
            If False, returns ns_marker for invalid inputs.
            Default is True.

    Returns:
        A string marker indicating significance level, or ns_marker if not
        significant or invalid (when strict=False).

    Raises:
        ValueError:
            If p_val is not a number, is negative, or exceeds 1 (when
            strict=True).
        TypeError:
            If p_val is not a numeric type (when strict=True).

    Examples:
        >>> get_sig_marker(0.0005)
        '***'
        >>> get_sig_marker(0.005)
        '**'
        >>> get_sig_marker(0.03)
        '*'
        >>> get_sig_marker(0.1)
        ''
        >>> get_sig_marker(0.1, ns_marker="ns")
        'ns'
        >>> get_sig_marker(0.15, thresholds=[0.1, 0.2], markers=["+", "-"])
        '+'
    """
    # Input validation
    # Support numpy types as well
    try:
        import numpy as np

        numeric_types = (int, float, np.integer, np.floating)
        has_numpy = True
    except ImportError:
        numeric_types = (int, float)
        has_numpy = False

    if not isinstance(p_val, numeric_types):
        if strict:
            raise TypeError(f"p_val must be a number, got {type(p_val).__name__}")
        return ns_marker

    # Convert numpy types to Python native float for consistent comparison
    # This ensures compatibility across different Python and numpy versions
    if has_numpy and isinstance(p_val, (np.integer, np.floating)):
        p_val = float(p_val)

    if p_val < 0 or p_val > 1:
        if strict:
            raise ValueError(f"p_val must be between 0 and 1, got {p_val}")
        return ns_marker

    # Set default thresholds and markers
    # Thresholds in descending order (most strict to least strict)
    # Markers correspond to thresholds in the same order
    if thresholds is None:
        thresholds = [0.05, 0.01, 0.001]
    if markers is None:
        markers = ["*", "**", "***"]

    # Validate thresholds and markers
    if len(thresholds) != len(markers):
        raise ValueError(
            f"thresholds and markers must have the same length, "
            f"got {len(thresholds)} and {len(markers)}"
        )

    if not all(0 < t <= 1 for t in thresholds):
        raise ValueError(f"All thresholds must be between 0 and 1, got {thresholds}")

    # Check if thresholds are in descending order
    if len(thresholds) > 1:
        if not all(
            thresholds[i] >= thresholds[i + 1] for i in range(len(thresholds) - 1)
        ):
            raise ValueError(
                f"thresholds must be in descending order, got {thresholds}"
            )

    # Find the appropriate marker
    # Check from most strict (last) to least strict (first)
    # Reverse iterate to find the most strict threshold that matches
    for i in range(len(thresholds) - 1, -1, -1):
        if p_val < thresholds[i]:
            return markers[i]

    # Not significant
    return ns_marker
