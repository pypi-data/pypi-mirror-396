"""
Single-sample hypothesis testing
"""

from scipy.stats import norm, t
from .standard_error import se_mean, se_proportion
from .critical_values import critical_value
from .utils import print_cyan, print_white, print_yellow, print_red

# ============================================================================
# HYPOTHESIS TESTING
# ============================================================================

def test_mean(mu0, xbar, s, n, distribution='t', tail='two', alpha=0.05):
    """
    Hypothesis test for population mean
    
    H0: μ = μ0
    H1: depends on tail ('two': μ ≠ μ0, 'right': μ > μ0, 'left': μ < μ0)
    
    Returns: (test_statistic, p_value, critical_value, reject)
    """
    print_yellow(f"⚠ Test type: {tail}-tailed, α = {alpha}")
    print_yellow(f"⚠ H0: μ = {mu0}")
    
    if tail == 'two':
        print_yellow(f"⚠ H1: μ ≠ {mu0}")
    elif tail == 'right':
        print_yellow(f"⚠ H1: μ > {mu0}")
    elif tail == 'left':
        print_yellow(f"⚠ H1: μ < {mu0}")
    
    if distribution == 'z':
        if n < 30:
            print_red(f"WARNING: Using z with n={n} < 30. Consider t-distribution.")
        print_yellow(f"⚠ Assumes: population normal OR n ≥ 30, σ known")
        df = None
        dist = norm()
    else:
        print_yellow(f"⚠ Assumes: population normal or n large")
        df = n - 1
        print_cyan(f"Degrees of freedom: df = n - 1 = {df}")
        dist = t(df=df)
    
    se = se_mean(s, n)
    test_stat = (xbar - mu0) / se
    
    print_cyan(f"Test statistic = (x̄ - μ0) / SE = ({xbar} - {mu0}) / {se}")
    print_white(f"Test statistic = {test_stat}")
    
    # P-value
    if tail == 'two':
        p_value = 2 * (1 - dist.cdf(abs(test_stat)))
    elif tail == 'right':
        p_value = 1 - dist.cdf(test_stat)
    else:  # left
        p_value = dist.cdf(test_stat)
    
    print_white(f"P-value = {p_value}")
    
    # Critical value
    crit = critical_value(alpha, distribution, df, tail)
    
    # Decision
    reject = p_value < alpha
    if reject:
        print_white(f"Decision: REJECT H0 (p-value {p_value} < α {alpha})")
    else:
        print_white(f"Decision: FAIL TO REJECT H0 (p-value {p_value} ≥ α {alpha})")
    
    return test_stat, p_value, crit, reject

def test_proportion(p0, phat, n, distribution='z', tail='two', alpha=0.05):
    """
    Hypothesis test for population proportion
    
    H0: p = p0
    H1: depends on tail
    
    Returns: (test_statistic, p_value, critical_value, reject)
    """
    print_yellow(f"⚠ Test type: {tail}-tailed, α = {alpha}")
    print_yellow(f"⚠ H0: p = {p0}")
    
    if tail == 'two':
        print_yellow(f"⚠ H1: p ≠ {p0}")
    elif tail == 'right':
        print_yellow(f"⚠ H1: p > {p0}")
    elif tail == 'left':
        print_yellow(f"⚠ H1: p < {p0}")
    
    if distribution == 't':
        print_yellow("⚠ Unusual to use t-distribution for proportions")
        df = n - 1
        dist = t(df=df)
    else:
        print_yellow(f"⚠ Assumes: np0 ≥ 10 AND n(1-p0) ≥ 10")
        if n * p0 < 10 or n * (1-p0) < 10:
            print_red(f"WARNING: np0={n*p0} or n(1-p0)={n*(1-p0)} < 10. Normal approximation may be poor.")
        df = None
        dist = norm()
    
    se = se_proportion(p0, n)
    test_stat = (phat - p0) / se
    
    print_cyan(f"Test statistic = (p̂ - p0) / SE = ({phat} - {p0}) / {se}")
    print_white(f"Test statistic = {test_stat}")
    
    # P-value
    if tail == 'two':
        p_value = 2 * (1 - dist.cdf(abs(test_stat)))
    elif tail == 'right':
        p_value = 1 - dist.cdf(test_stat)
    else:  # left
        p_value = dist.cdf(test_stat)
    
    print_white(f"P-value = {p_value}")
    
    # Critical value
    crit = critical_value(alpha, distribution, df, tail)
    
    # Decision
    reject = p_value < alpha
    if reject:
        print_white(f"Decision: REJECT H0 (p-value {p_value} < α {alpha})")
    else:
        print_white(f"Decision: FAIL TO REJECT H0 (p-value {p_value} ≥ α {alpha})")
    
    return test_stat, p_value, crit, reject

def test_paired_mean(xbar1, xbar2, sD, n, tail='two', alpha=0.05):
    """
    Paired t-test via mean difference

    H0: μ_d = 0
    """
    dbar = xbar1 - xbar2
    return test_mean(
        mu0=0,
        xbar=dbar,
        s=sD,
        n=n,
        distribution='t',
        tail=tail,
        alpha=alpha
    )

    