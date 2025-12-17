"""
Inverse calculations - solve for parameters given results
"""

from scipy.stats import norm, t
from .utils import print_cyan, print_white, print_yellow, print_red

# ============================================================================
# INVERSE CALCULATIONS
# ============================================================================

def solve_xbar_from_ci(lower, upper, s, n, confidence=0.95, distribution='t'):
    """
    Given CI bounds, solve for the sample mean x̄
    """
    xbar = (lower + upper) / 2
    print_cyan(f"x̄ = (lower + upper) / 2 = ({lower} + {upper}) / 2")
    print_white(f"x̄ = {xbar}")
    return xbar

def solve_margin_from_ci(lower, upper):
    """
    Given CI bounds, solve for margin of error
    """
    margin = (upper - lower) / 2
    print_cyan(f"Margin = (upper - lower) / 2 = ({upper} - {lower}) / 2")
    print_white(f"Margin = {margin}")
    return margin

def solve_critical_from_margin(margin, se):
    """
    Given margin of error and SE, solve for critical value
    """
    crit = margin / se
    print_cyan(f"Critical value = Margin / SE = {margin} / {se}")
    print_white(f"Critical value = {crit}")
    return crit

def solve_alpha_from_critical(crit, distribution='z', df=None, tail='two'):
    """
    Given critical value, solve for alpha
    """
    if distribution == 't' and df is None:
        print_red("ERROR: t-distribution requires df parameter")
        return None
    
    print_yellow(f"⚠ Distribution: {distribution}, tail: {tail}")
    
    if distribution == 'z':
        if tail == 'two':
            alpha = 2 * (1 - norm.cdf(abs(crit)))
        elif tail == 'right':
            alpha = 1 - norm.cdf(crit)
        elif tail == 'left':
            alpha = norm.cdf(crit)
    elif distribution == 't':
        if tail == 'two':
            alpha = 2 * (1 - t.cdf(abs(crit), df))
        elif tail == 'right':
            alpha = 1 - t.cdf(crit, df)
        elif tail == 'left':
            alpha = t.cdf(crit, df)
    
    print_white(f"α = {alpha}")
    return alpha

def solve_p_from_test_stat(test_stat, n, distribution='t', tail='two'):
    """
    Given test statistic, solve for p-value
    """
    print_yellow(f"⚠ Test statistic: {test_stat}")
    print_yellow(f"⚠ Distribution: {distribution}, tail: {tail}")
    
    if distribution == 'z':
        dist = norm()
        df = None
    else:
        df = n - 1
        print_cyan(f"Degrees of freedom: df = {df}")
        dist = t(df=df)
    
    if tail == 'two':
        p_value = 2 * (1 - dist.cdf(abs(test_stat)))
    elif tail == 'right':
        p_value = 1 - dist.cdf(test_stat)
    else:  # left
        p_value = dist.cdf(test_stat)
    
    print_white(f"P-value = {p_value}")
    return p_value

def p_to_stat(p, df=None, tail='two', distribution='t'):
    """
    Convert p-value to z or t statistic (inverse of solve_p_from_test_stat)
    
    Parameters:
    - p: p-value
    - df: degrees of freedom (required for t-distribution)
    - tail: 'two', 'left', or 'right'
    - distribution: 'z' or 't'
    
    Returns:
    - statistic corresponding to p-value
    """
    print_yellow(f"⚠ P-value: {p}")
    print_yellow(f"⚠ Distribution: {distribution}, tail: {tail}")
    
    if distribution == 'z':
        if tail == 'two':
            stat = norm.ppf(1 - p/2)
            print_cyan(f"z = Φ⁻¹(1 - p/2) = Φ⁻¹(1 - {p}/2)")
        elif tail == 'right':
            stat = norm.ppf(1 - p)
            print_cyan(f"z = Φ⁻¹(1 - p) = Φ⁻¹(1 - {p})")
        elif tail == 'left':
            stat = norm.ppf(p)
            print_cyan(f"z = Φ⁻¹(p) = Φ⁻¹({p})")
        else:
            print_red("ERROR: tail must be 'two', 'left', or 'right'")
            raise ValueError("tail must be 'two', 'left', or 'right'")
            
    elif distribution == 't':
        if df is None:
            print_red("ERROR: df must be specified for t-distribution")
            raise ValueError("df must be specified for t-distribution")
        print_cyan(f"Degrees of freedom: df = {df}")
        if tail == 'two':
            stat = t.ppf(1 - p/2, df)
            print_cyan(f"t = t⁻¹(1 - p/2, df={df}) = t⁻¹(1 - {p}/2, {df})")
        elif tail == 'right':
            stat = t.ppf(1 - p, df)
            print_cyan(f"t = t⁻¹(1 - p, df={df}) = t⁻¹(1 - {p}, {df})")
        elif tail == 'left':
            stat = t.ppf(p, df)
            print_cyan(f"t = t⁻¹(p, df={df}) = t⁻¹({p}, {df})")
        else:
            print_red("ERROR: tail must be 'two', 'left', or 'right'")
            raise ValueError("tail must be 'two', 'left', or 'right'")
    else:
        print_red("ERROR: distribution must be 'z' or 't'")
        raise ValueError("distribution must be 'z' or 't'")
    
    print_white(f"Test statistic = {stat}")
    return stat

def quantile_normal(p, mu, sigma):
    """
    Find the quantile (inverse CDF) of a normal distribution
    
    Finds x such that P(X ≤ x) = p for X ~ N(μ, σ²)
    
    Parameters
    ----------
    p : float
        Probability (0 <= p <= 1)
    mu : float
        Mean of the normal distribution
    sigma : float
        Standard deviation of the normal distribution
    
    Returns
    -------
    float
        The quantile value x such that P(X ≤ x) = p
    """
    if not (0 <= p <= 1):
        print_red("ERROR: p must be between 0 and 1")
        raise ValueError("p must be between 0 and 1")
    
    if sigma < 0:
        print_red("ERROR: sigma must be non-negative")
        raise ValueError("sigma must be non-negative")
    
    print_yellow(f"⚠ Normal distribution: μ = {mu}, σ = {sigma}")
    print_yellow(f"⚠ Finding x such that P(X ≤ x) = {p}")
    
    x = norm.ppf(p, mu, sigma)
    print_cyan(f"x = Φ⁻¹({p}, μ={mu}, σ={sigma})")
    print_white(f"x = {x}")
    
    return x

