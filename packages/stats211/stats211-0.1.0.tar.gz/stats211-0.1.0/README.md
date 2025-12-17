# Stats Package

A comprehensive Python package for statistical analysis, providing functions for hypothesis testing, confidence intervals, regression analysis, and more.

## Features

- **Descriptive Statistics**: Basic statistics, z-score conversions, and percentile calculations
- **Standard Error Calculations**: For means, proportions, and their differences
- **Critical Values**: Calculate critical values for hypothesis testing
- **Confidence Intervals**: For means and proportions
- **Sample Size Calculations**: Determine required sample sizes for studies
- **Hypothesis Testing**: Single-sample and two-sample tests for means and proportions
- **Regression Analysis**: Linear regression with confidence intervals and predictions
- **Probability Calculations**: Central Limit Theorem applications
- **Inverse Calculations**: Solve for various statistical parameters

## Installation

```bash
pip install stats-package
```

## Quick Start

```python
from stats import *

# Hypothesis testing
test_mean(0, 3.1, 1.3, 18)

# Confidence intervals
ci_mean(3.1, 1.3, 18, 0.95)

# Two-sample tests
test_two_means(1610, 129.8, 18.906, 1929, 127.07, 21.975, equal_var=True, alpha=0.13)

# Sample size calculations
sample_size_mean(0.9, 11.71, 0.84)

# Get help
stats_help()
```

## Module Organization

The package is organized into the following modules:

- `utils`: Color printing and file I/O utilities
- `descriptive`: Basic statistics and z-score conversions
- `standard_error`: Standard error calculations
- `critical_values`: Critical value functions
- `confidence_intervals`: Confidence interval calculations
- `sample_size`: Sample size calculations
- `hypothesis_testing`: Single-sample hypothesis tests
- `two_sample`: Two-sample hypothesis tests
- `regression`: Linear regression functions
- `probability`: Probability calculations (CLT)
- `inverse`: Inverse calculations

## Usage Examples

### Hypothesis Testing

```python
from stats import test_mean, test_proportion

# Test a mean
test_mean(0, 3.1, 1.3, 18)

# Test a proportion
test_proportion(0.03, 0.04, 500, tail='right')
```

### Confidence Intervals

```python
from stats import ci_mean, ci_proportion

# Confidence interval for mean
ci_mean(3.1, 1.3, 18, 0.95)

# Confidence interval for proportion
ci_proportion(0.5, 100, 0.95)
```

### Two-Sample Tests

```python
from stats import test_two_means, test_two_proportions

# Two-sample t-test
test_two_means(1610, 129.8, 18.906, 1929, 127.07, 21.975, equal_var=True, alpha=0.13)

# Two-sample proportion test
test_two_proportions(314, 59, 319, 101)
```

### Regression Analysis

```python
from stats import slope_test, linregress_ci

# Test slope
slope_test(1.57, 0.606, 170, 0.05, 'two')

# Confidence interval for regression
linregress_ci(slope, se_slope, n, confidence=0.95)
```

## Requirements

- Python >= 3.8
- numpy >= 1.20.0
- pandas >= 1.3.0
- scipy >= 1.7.0

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Isaac Lagoy
