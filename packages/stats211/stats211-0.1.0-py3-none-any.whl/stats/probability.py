"""
Probability calculations using Central Limit Theorem
"""

from math import sqrt
from scipy.stats import norm
from .utils import print_cyan, print_white, print_yellow, print_red

# ============================================================================
# PROBABILITY CALCULATIONS (CLT)
# ============================================================================

def prob_mean_in_range(mu, sigma, n, lower, upper):
    """
    Probability that sample mean falls in range using CLT
    
    P(lower < x̄ < upper) when sampling from population with mean μ, std σ
    """
    print_yellow(f"⚠ Using Central Limit Theorem")
    print_yellow(f"⚠ Population: μ = {mu}, σ = {sigma}")
    print_yellow(f"⚠ Sample size: n = {n}")
    
    if n < 30:
        print_red(f"WARNING: n = {n} < 30. CLT approximation may be poor unless population is normal.")
    
    se = sigma / sqrt(n)
    print_cyan(f"Standard error: SE = σ/√n = {sigma}/√{n} = {se}")
    
    z_lower = (lower - mu) / se
    z_upper = (upper - mu) / se
    
    print_cyan(f"z_lower = ({lower} - {mu}) / {se} = {z_lower}")
    print_cyan(f"z_upper = ({upper} - {mu}) / {se} = {z_upper}")
    
    prob = norm.cdf(z_upper) - norm.cdf(z_lower)
    
    print_white(f"P({lower} < x̄ < {upper}) = {prob}")
    
    return prob

def prob_proportion_in_range(p, n, lower, upper):
    """
    Probability that sample proportion falls in range using CLT
    
    P(lower < p̂ < upper) when sampling from population with proportion p
    """
    print_yellow(f"⚠ Using Central Limit Theorem for proportions")
    print_yellow(f"⚠ Population proportion: p = {p}")
    print_yellow(f"⚠ Sample size: n = {n}")
    
    if n * p < 10 or n * (1-p) < 10:
        print_red(f"WARNING: np={n*p} or n(1-p)={n*(1-p)} < 10. Normal approximation may be poor.")
    
    se = sqrt(p * (1 - p) / n)
    print_cyan(f"Standard error: SE = √[p(1-p)/n] = √[{p}×{1-p}/{n}] = {se}")
    
    z_lower = (lower - p) / se
    z_upper = (upper - p) / se
    
    print_cyan(f"z_lower = ({lower} - {p}) / {se} = {z_lower}")
    print_cyan(f"z_upper = ({upper} - {p}) / {se} = {z_upper}")
    
    prob = norm.cdf(z_upper) - norm.cdf(z_lower)
    
    print_white(f"P({lower} < p̂ < {upper}) = {prob}")
    
    return prob

def prob_normal_in_range(mu, sigma, lower, upper):
    """
    Probability for normal distribution
    
    P(lower < X < upper) for X ~ N(μ, σ²)
    """
    print_yellow(f"⚠ Normal distribution: μ = {mu}, σ = {sigma}")
    
    z_lower = (lower - mu) / sigma
    z_upper = (upper - mu) / sigma
    
    print_cyan(f"z_lower = ({lower} - {mu}) / {sigma} = {z_lower}")
    print_cyan(f"z_upper = ({upper} - {mu}) / {sigma} = {z_upper}")
    
    prob = norm.cdf(z_upper) - norm.cdf(z_lower)
    
    print_white(f"P({lower} < X < {upper}) = {prob}")
    
    return prob

