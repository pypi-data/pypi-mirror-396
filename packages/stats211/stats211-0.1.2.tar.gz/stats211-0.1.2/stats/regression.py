"""
Linear regression functions
"""

from scipy import stats
from scipy.stats import t
import numpy as np
from .critical_values import critical_value
from .utils import print_cyan, print_white, print_yellow

# ============================================================================
# LINEAR REGRESSION
# ============================================================================

def slope_test(beta, se_beta, n, alpha=0.05, tail='two'):
    """
    Test for regression slope coefficient
    
    H0: β = 0
    H1: depends on tail
    
    Returns: (test_statistic, p_value, critical_value, reject)
    """
    print_yellow(f"⚠ Test for slope coefficient")
    print_yellow(f"⚠ H0: β = 0")
    
    if tail == 'two':
        print_yellow(f"⚠ H1: β ≠ 0")
    elif tail == 'right':
        print_yellow(f"⚠ H1: β > 0")
    elif tail == 'left':
        print_yellow(f"⚠ H1: β < 0")
    
    df = n - 2
    print_cyan(f"Degrees of freedom: df = n - 2 = {df}")
    
    t_stat = beta / se_beta
    print_cyan(f"Test statistic = β / SE(β) = {beta} / {se_beta}")
    print_white(f"Test statistic: t = {t_stat}")
    
    # P-value
    if tail == 'two':
        p_value = 2 * (1 - t.cdf(abs(t_stat), df))
    elif tail == 'right':
        p_value = 1 - t.cdf(t_stat, df)
    else:  # left
        p_value = t.cdf(t_stat, df)
    
    print_white(f"P-value = {p_value}")
    
    # Critical value
    t_crit = critical_value(alpha, 't', df=df, tail=tail)
    
    # Decision
    reject = p_value < alpha
    if reject:
        print_white(f"Decision: REJECT H0")
    else:
        print_white(f"Decision: FAIL TO REJECT H0")
    
    return t_stat, p_value, t_crit, reject

def slope_test_statistic(slope_estimate, slope_standard_error, sample_size, alpha=None):
    """
    Legacy function - compute test statistic for regression slope
    """
    if alpha is None:
        t_stat = slope_estimate / slope_standard_error
        print_white(f"Test statistic: {t_stat}")
        return t_stat
    else:
        return slope_test(slope_estimate, slope_standard_error, sample_size, alpha=alpha, tail='two')

def linregress_ci_data(x, y, alpha=0.05):
    """
    Calculate confidence interval for regression slope and mean response
    
    Parameters:
    - x: independent variable values
    - y: dependent variable values
    - alpha: significance level (default 0.05 for 95% CI)
    
    Returns:
    - slope_ci: tuple (lower, upper) for slope confidence interval
    - func: function that takes x and returns (lower, upper) CI bounds for mean response at that x
    """
    print_yellow(f"⚠ Linear regression confidence intervals")
    print_yellow(f"⚠ Confidence level: {(1-alpha)*100}%, α = {alpha}")
    
    # Fit regression
    slope, intercept, r, p, std_err = stats.linregress(x, y)
    
    x = np.asarray(x)
    n = len(x)
    
    print_cyan(f"Regression: ŷ = {intercept} + {slope}x")
    print_cyan(f"Sample size: n = {n}")
    print_cyan(f"Slope standard error: SE(β) = {std_err}")
    
    df = n - 2
    print_cyan(f"Degrees of freedom: df = n - 2 = {df}")
    
    t_crit = critical_value(alpha, 't', df=df, tail='two')
    
    # Slope confidence interval
    slope_lower = slope - t_crit * std_err
    slope_upper = slope + t_crit * std_err
    slope_ci = (slope_lower, slope_upper)
    
    print_cyan(f"Slope CI: β ± t* × SE(β) = {slope} ± {t_crit} × {std_err}")
    print_white(f"{(1-alpha)*100}% CI for slope: ({slope_lower}, {slope_upper})")
    
    # Function to compute CI bounds using slope CI (simplified bounding approach)
    def func(x_val):
        """Returns CI bounds for mean response at x_val using slope CI bounds"""
        lower_bound = intercept + x_val * slope_ci[0]
        upper_bound = intercept + x_val * slope_ci[1]
        return (float(lower_bound), float(upper_bound))
    
    print_yellow(f"⚠ Function returned computes CI bounds using slope CI at any x")
    
    return slope_ci, func

def linregress_ci(slope, se_slope, n, confidence=0.95):
    """
    Calculate confidence interval for regression slope
    
    Parameters:
    - slope: regression slope coefficient
    - se_slope: standard error of the slope
    - n: sample size
    - confidence: confidence level (default 0.95 for 95% CI)
    
    Returns:
    - slope_ci: tuple (lower, upper) for slope confidence interval
    """
    alpha = 1 - confidence
    
    print_yellow(f"⚠ Linear regression slope confidence interval")
    print_yellow(f"⚠ Confidence level: {confidence*100}%, α = {alpha}")
    
    print_cyan(f"Slope: β = {slope}")
    print_cyan(f"Standard error: SE(β) = {se_slope}")
    print_cyan(f"Sample size: n = {n}")
    
    df = n - 2
    print_cyan(f"Degrees of freedom: df = n - 2 = {df}")
    
    t_crit = critical_value(alpha, 't', df=df, tail='two')
    
    # Slope confidence interval
    slope_lower = slope - t_crit * se_slope
    slope_upper = slope + t_crit * se_slope
    slope_ci = (slope_lower, slope_upper)
    
    print_cyan(f"Slope CI: β ± t* × SE(β) = {slope} ± {t_crit} × {se_slope}")
    print_white(f"{confidence*100}% CI for slope: ({slope_lower}, {slope_upper})")
    
    return slope_ci

def linregress_predict(slope, intercept, s, x0, xbar, Sxx, n, confidence=0.95):
    """
    Calculate prediction interval for a new response value at x0
    
    Parameters:
    - slope: regression slope coefficient
    - intercept: regression intercept
    - s: residual standard error
    - x0: point at which to predict
    - xbar: mean of x values
    - Sxx: sum of squares Σ(x - x̄)²
    - n: sample size
    - confidence: confidence level (default 0.95 for 95% prediction interval)
    
    Returns:
    - y0_hat: predicted value at x0
    - prediction_interval: tuple (lower, upper) for prediction interval
    """
    alpha = 1 - confidence
    
    print_yellow(f"⚠ Prediction interval for new response")
    print_yellow(f"⚠ Prediction at x0 = {x0}")
    print_yellow(f"⚠ Confidence level: {confidence*100}%, α = {alpha}")
    
    print_cyan(f"Regression: ŷ = {intercept} + {slope}x")
    print_cyan(f"Sample size: n = {n}")
    
    df = n - 2
    print_cyan(f"Degrees of freedom: df = n - 2 = {df}")
    
    t_crit = critical_value(alpha, 't', df=df, tail='two')
    
    print_cyan(f"Mean of x: x̄ = {xbar}")
    print_cyan(f"Sum of squares: Sxx = {Sxx}")
    
    # Predicted value
    y0_hat = intercept + slope * x0
    print_cyan(f"Predicted value: ŷ0 = {intercept} + {slope} × {x0} = {y0_hat}")
    
    # Residual standard error
    print_cyan(f"Residual standard error: s = {s}")
    
    # Prediction interval margin
    margin_term = np.sqrt(1 + 1/n + (x0 - xbar) ** 2 / Sxx)
    margin = t_crit * s * margin_term
    
    print_cyan(f"Margin = t* × s × √[1 + 1/n + (x0 - x̄)²/Sxx]")
    print_cyan(f"Margin = {t_crit} × {s} × √[1 + 1/{n} + ({x0} - {xbar})²/{Sxx}]")
    print_cyan(f"Margin = {margin}")
    
    lower = y0_hat - margin
    upper = y0_hat + margin
    
    print_white(f"Predicted value: {y0_hat}")
    print_white(f"{confidence*100}% Prediction interval: ({lower}, {upper})")
    
    return y0_hat, (lower, upper)

def linregress_predict_data(x, y, x0, alpha=0.05):
    """
    Calculate prediction interval for a new response value at x0
    
    Parameters:
    - x: independent variable values
    - y: dependent variable values
    - x0: point at which to predict
    - alpha: significance level (default 0.05 for 95% prediction interval)
    
    Returns:
    - y0_hat: predicted value at x0
    - prediction_interval: tuple (lower, upper) for prediction interval
    """
    print_yellow(f"⚠ Prediction interval for new response")
    print_yellow(f"⚠ Prediction at x0 = {x0}")
    print_yellow(f"⚠ Confidence level: {(1-alpha)*100}%, α = {alpha}")
    
    # Fit regression
    slope, intercept, r, p, std_err = stats.linregress(x, y)
    
    print_cyan(f"Regression: ŷ = {intercept} + {slope}x")
    
    x = np.asarray(x)
    y = np.asarray(y)
    n = len(x)
    
    print_cyan(f"Sample size: n = {n}")
    
    df = n - 2
    print_cyan(f"Degrees of freedom: df = n - 2 = {df}")
    
    t_crit = critical_value(alpha, 't', df=df, tail='two')
    
    xbar = x.mean()
    print_cyan(f"Mean of x: x̄ = {xbar}")
    
    # Predicted value
    y0_hat = intercept + slope * x0
    print_cyan(f"Predicted value: ŷ0 = {intercept} + {slope} × {x0} = {y0_hat}")
    
    # Fitted values and residuals
    y_hat = intercept + slope * x
    
    # Residual standard error (s)
    s = np.sqrt(np.sum((y - y_hat) ** 2) / df)
    print_cyan(f"Residual standard error: s = √[Σ(y - ŷ)² / df] = {s}")
    
    Sxx = np.sum((x - xbar) ** 2)
    print_cyan(f"Sum of squares: Sxx = Σ(x - x̄)² = {Sxx}")
    
    # Prediction interval margin
    margin_term = np.sqrt(1 + 1/n + (x0 - xbar) ** 2 / Sxx)
    margin = t_crit * s * margin_term
    
    print_cyan(f"Margin = t* × s × √[1 + 1/n + (x0 - x̄)²/Sxx]")
    print_cyan(f"Margin = {t_crit} × {s} × √[1 + 1/{n} + ({x0} - {xbar})²/{Sxx}]")
    print_cyan(f"Margin = {margin}")
    
    lower = y0_hat - margin
    upper = y0_hat + margin
    
    print_white(f"Predicted value: {y0_hat}")
    print_white(f"{(1-alpha)*100}% Prediction interval: ({lower}, {upper})")
    
    return y0_hat, (lower, upper)

