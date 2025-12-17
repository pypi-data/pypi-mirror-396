"""
Statistics module - provides comprehensive statistical functions

This module is organized into sub-modules:
- utils: Color printing and file I/O
- descriptive: Basic statistics and z-score conversions
- standard_error: Standard error calculations
- critical_values: Critical value functions
- confidence_intervals: Confidence interval calculations
- sample_size: Sample size calculations
- hypothesis_testing: Single-sample hypothesis tests
- two_sample: Two-sample hypothesis tests
- regression: Linear regression functions
- probability: Probability calculations (CLT)
- inverse: Inverse calculations

All functions are imported here. Use:
    from stats211 import *
"""

# Import all functions to maintain backward compatibility
from .utils import (
    print_red, print_yellow, print_white, print_cyan,
    load_data, stats_help
)

from .descriptive import (
    x_to_z, z_to_x, z_to_percentile, percentile_to_z,
    get_mean, get_std, get_variance
)

from .standard_error import (
    se_proportion, se_mean,
    se_difference_proportions, se_difference_means
)

from .critical_values import (
    critical_value, critical_test_statistic
)

from .confidence_intervals import (
    ci_mean, ci_proportion
)

from .sample_size import (
    sample_size_proportion, sample_size_mean,
    margin_from_sample_size_proportion, margin_from_sample_size_mean
)

from .hypothesis_testing import (
    test_mean, test_proportion
)

from .two_sample import (
    test_two_proportions, test_two_means
)

from .regression import (
    slope_test, slope_test_statistic,
    linregress_ci, linregress_predict,
    linregress_ci_data, linregress_predict_data
)

from .probability import (
    prob_mean_in_range, prob_proportion_in_range, prob_normal_in_range,
    compute_sampling_distribution_params, compute_sampling_distribution_proportion_params,
    prob_normal_less_than, prob_normal_greater_than, prob_normal_between
)

from .inverse import (
    solve_xbar_from_ci, solve_margin_from_ci,
    solve_critical_from_margin, solve_alpha_from_critical,
    solve_p_from_test_stat, p_to_stat, quantile_normal
)

# All functions exported for use with: from stats211 import *
__all__ = [
    # Utils
    'print_red', 'print_yellow', 'print_white', 'print_cyan', 'load_data', 'stats_help',
    # Descriptive
    'x_to_z', 'z_to_x', 'z_to_percentile', 'percentile_to_z',
    'get_mean', 'get_std', 'get_variance',
    # Standard error
    'se_proportion', 'se_mean', 'se_difference_proportions', 'se_difference_means',
    # Critical values
    'critical_value', 'critical_test_statistic',
    # Confidence intervals
    'ci_mean', 'ci_proportion',
    # Sample size
    'sample_size_proportion', 'sample_size_mean',
    'margin_from_sample_size_proportion', 'margin_from_sample_size_mean',
    # Hypothesis testing
    'test_mean', 'test_proportion',
    # Two-sample
    'test_two_proportions', 'test_two_means',
    # Regression
    'slope_test', 'slope_test_statistic', 'linregress_ci', 'linregress_predict',
    'linregress_ci_data', 'linregress_predict_data',
    # Probability
    'prob_mean_in_range', 'prob_proportion_in_range', 'prob_normal_in_range',
    'compute_sampling_distribution_params', 'compute_sampling_distribution_proportion_params',
    'prob_normal_less_than', 'prob_normal_greater_than', 'prob_normal_between',
    # Inverse
    'solve_xbar_from_ci', 'solve_margin_from_ci', 'solve_critical_from_margin',
    'solve_alpha_from_critical', 'solve_p_from_test_stat', 'p_to_stat', 'quantile_normal',
]

