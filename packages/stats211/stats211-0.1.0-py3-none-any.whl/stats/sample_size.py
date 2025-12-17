"""
Sample size calculations
"""

from math import sqrt, ceil
from .standard_error import se_proportion
from .critical_values import critical_value
from .utils import print_cyan, print_white, print_yellow

# ============================================================================
# SAMPLE SIZE CALCULATIONS
# ============================================================================

def sample_size_proportion(margin, p=0.5, confidence=0.95, distribution='z'):
    """
    Calculate required sample size for proportion CI with given margin of error
    """
    alpha = 1 - confidence
    
    if p != 0.5:
        print_yellow(f"⚠ Using p = {p}. For conservative estimate, use p = 0.5")
    
    print_yellow(f"⚠ Desired margin of error: {margin}")
    print_yellow(f"⚠ Confidence level: {confidence*100}%")
    
    crit = critical_value(alpha, distribution, df=1000 if distribution=='t' else None, tail='two')
    
    n = (crit**2 * p * (1-p)) / (margin**2)
    n_rounded = ceil(n)
    
    print_cyan(f"n = (z*)² × p(1-p) / E²")
    print_cyan(f"n = {crit}² × {p}×{1-p} / {margin}²")
    print_cyan(f"n = {n}")
    print_white(f"Required sample size: n = {n_rounded}")
    
    return n_rounded

def sample_size_mean(margin, sigma, confidence=0.95, distribution='z'):
    """
    Calculate required sample size for mean CI with given margin of error
    Requires known or estimated population standard deviation
    """
    alpha = 1 - confidence
    
    print_yellow(f"⚠ Desired margin of error: {margin}")
    print_yellow(f"⚠ Population std dev (σ): {sigma}")
    print_yellow(f"⚠ Confidence level: {confidence*100}%")
    
    crit = critical_value(alpha, distribution, df=1000 if distribution=='t' else None, tail='two')
    
    n = (crit * sigma / margin)**2
    n_rounded = ceil(n)
    
    print_cyan(f"n = (z* × σ / E)²")
    print_cyan(f"n = ({crit} × {sigma} / {margin})²")
    print_cyan(f"n = {n}")
    print_white(f"Required sample size: n = {n_rounded}")
    
    return n_rounded

# Inverse: solve for margin given sample size
def margin_from_sample_size_proportion(n, p=0.5, confidence=0.95, distribution='z'):
    """Calculate achievable margin of error given sample size for proportion"""
    alpha = 1 - confidence
    
    print_yellow(f"⚠ Sample size: n = {n}")
    print_yellow(f"⚠ Proportion: p = {p}")
    
    crit = critical_value(alpha, distribution, df=1000 if distribution=='t' else None, tail='two')
    se = se_proportion(p, n)
    margin = crit * se
    
    print_white(f"Achievable margin of error: E = {margin}")
    return margin

def margin_from_sample_size_mean(n, sigma, confidence=0.95, distribution='z'):
    """Calculate achievable margin of error given sample size for mean"""
    alpha = 1 - confidence
    
    print_yellow(f"⚠ Sample size: n = {n}")
    print_yellow(f"⚠ Population std dev: σ = {sigma}")
    
    crit = critical_value(alpha, distribution, df=1000 if distribution=='t' else None, tail='two')
    se = sigma / sqrt(n)
    margin = crit * se
    
    print_cyan(f"SE = σ/√n = {sigma}/√{n} = {se}")
    print_cyan(f"Margin = critical_value × SE = {crit} × {se}")
    print_white(f"Achievable margin of error: E = {margin}")
    return margin

