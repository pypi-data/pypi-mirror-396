"""
Confidence interval calculations
"""

from .standard_error import se_mean, se_proportion
from .critical_values import critical_value
from .utils import print_cyan, print_white, print_yellow, print_red

# ============================================================================
# CONFIDENCE INTERVALS
# ============================================================================

def ci_mean(xbar, s, n, confidence=0.95, distribution='t'):
    """
    Confidence interval for population mean
    
    Returns: (lower, upper, margin, critical_value)
    """
    alpha = 1 - confidence
    
    print_yellow(f"⚠ Confidence level: {confidence*100}%, α = {alpha}")
    
    if distribution == 'z':
        if n < 30:
            print_red(f"WARNING: Using z with n={n} < 30. Consider using t-distribution.")
        print_yellow(f"⚠ Assumes: population is normal OR n ≥ 30")
        df = None
    else:
        print_yellow(f"⚠ Assumes: population is normal or n is large")
        df = n - 1
        print_cyan(f"Degrees of freedom: df = n - 1 = {df}")
    
    se = se_mean(s, n)
    crit = critical_value(alpha, distribution, df, tail='two')
    margin = crit * se
    
    print_cyan(f"Margin of error: E = critical_value × SE = {crit} × {se}")
    print_cyan(f"E = {margin}")
    
    lower = xbar - margin
    upper = xbar + margin
    
    print_white(f"{confidence*100}% CI: ({lower}, {upper})")
    
    return lower, upper, margin, crit

def ci_proportion(p, n, confidence=0.95, distribution='z'):
    """
    Confidence interval for population proportion
    
    Returns: (lower, upper, margin, critical_value)
    """
    alpha = 1 - confidence
    
    print_yellow(f"⚠ Confidence level: {confidence*100}%, α = {alpha}")
    
    if distribution == 't':
        print_yellow("⚠ Unusual to use t-distribution for proportions")
        df = n - 1
    else:
        print_yellow(f"⚠ Assumes: np ≥ 10 AND n(1-p) ≥ 10")
        if n * p < 10 or n * (1-p) < 10:
            print_red(f"WARNING: np={n*p} or n(1-p)={n*(1-p)} < 10. Normal approximation may be poor.")
        df = None
    
    se = se_proportion(p, n)
    crit = critical_value(alpha, distribution, df, tail='two')
    margin = crit * se
    
    print_cyan(f"Margin of error: E = critical_value × SE = {crit} × {se}")
    print_cyan(f"E = {margin}")
    
    lower = p - margin
    upper = p + margin
    
    # Check bounds
    if lower < 0 or upper > 1:
        print_red(f"WARNING: CI bounds outside [0,1]. Lower={lower}, Upper={upper}")
    
    print_white(f"{confidence*100}% CI: ({lower}, {upper})")
    
    return lower, upper, margin, crit

