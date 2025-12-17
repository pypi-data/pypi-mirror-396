"""
Probability calculations using Central Limit Theorem
"""

from math import sqrt
import numpy as np
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

# ============================================================================
# SAMPLING DISTRIBUTION PARAMETERS
# ============================================================================

def compute_sampling_distribution_params(mu, sigma, n, kind="mean"):
    """
    Compute the CLT-based sampling distribution parameters.

    Parameters
    ----------
    mu : float
        Population mean
    sigma : float
        Population standard deviation
    n : int
        Sample size (must be >= 1)
    kind : {"mean", "total"}
        Type of sampling distribution

    Returns
    -------
    dict
        Dictionary containing:
        - mean: expected value
        - stdev: standard deviation (standard error if mean)
        - distribution: scipy.stats normal distribution object
    """
    print_yellow(f"⚠ Computing sampling distribution parameters")
    print_yellow(f"⚠ Population: μ = {mu}, σ = {sigma}")
    print_yellow(f"⚠ Sample size: n = {n}")
    print_yellow(f"⚠ Distribution type: {kind}")

    if n <= 0:
        print_red("ERROR: n must be a positive integer")
        raise ValueError("n must be a positive integer")

    if sigma < 0:
        print_red("ERROR: sigma must be non-negative")
        raise ValueError("sigma must be non-negative")

    if kind == "mean":
        mean = mu
        stdev = sigma / np.sqrt(n)
        print_cyan(f"Mean of sampling distribution: μ_x̄ = μ = {mean}")
        print_cyan(f"Standard error: SE = σ/√n = {sigma}/√{n} = {stdev}")

    elif kind == "total":
        mean = n * mu
        stdev = sigma * np.sqrt(n)
        print_cyan(f"Mean of sampling distribution: μ_total = n × μ = {n} × {mu} = {mean}")
        print_cyan(f"Standard deviation: σ_total = σ × √n = {sigma} × √{n} = {stdev}")

    else:
        print_red(f"ERROR: kind must be 'mean' or 'total'")
        raise ValueError("kind must be 'mean' or 'total'")

    dist = norm(loc=mean, scale=stdev)
    print_white(f"Sampling distribution: N(μ = {mean}, σ = {stdev})")

    return {
        "mean": mean,
        "stdev": stdev,
        "distribution": dist
    }

def compute_sampling_distribution_proportion_params(p, n, kind="proportion"):
    """
    Compute the CLT-based sampling distribution for proportions.

    Parameters
    ----------
    p : float
        Population proportion (0 <= p <= 1)
    n : int
        Number of trials
    kind : {"proportion", "count"}
        Type of sampling distribution

    Returns
    -------
    dict
        Dictionary containing:
        - mean: expected value
        - stdev: standard deviation
        - distribution: scipy.stats normal distribution object
    """
    print_yellow(f"⚠ Computing sampling distribution parameters for proportions")
    print_yellow(f"⚠ Population proportion: p = {p}")
    print_yellow(f"⚠ Sample size: n = {n}")
    print_yellow(f"⚠ Distribution type: {kind}")

    if not (0 <= p <= 1):
        print_red("ERROR: p must be between 0 and 1")
        raise ValueError("p must be between 0 and 1")

    if n <= 0:
        print_red("ERROR: n must be a positive integer")
        raise ValueError("n must be a positive integer")

    if n * p < 10 or n * (1-p) < 10:
        print_red(f"WARNING: np={n*p} or n(1-p)={n*(1-p)} < 10. Normal approximation may be poor.")

    if kind == "proportion":
        mean = p
        stdev = np.sqrt(p * (1 - p) / n)
        print_cyan(f"Mean of sampling distribution: μ_p̂ = p = {mean}")
        print_cyan(f"Standard error: SE = √[p(1-p)/n] = √[{p}×{1-p}/{n}] = {stdev}")

    elif kind == "count":
        mean = n * p
        stdev = np.sqrt(n * p * (1 - p))
        print_cyan(f"Mean of sampling distribution: μ_count = n × p = {n} × {p} = {mean}")
        print_cyan(f"Standard deviation: σ_count = √[np(1-p)] = √[{n}×{p}×{1-p}] = {stdev}")

    else:
        print_red(f"ERROR: kind must be 'proportion' or 'count'")
        raise ValueError("kind must be 'proportion' or 'count'")

    dist = norm(loc=mean, scale=stdev)
    print_white(f"Sampling distribution: N(μ = {mean}, σ = {stdev})")

    return {
        "mean": mean,
        "stdev": stdev,
        "distribution": dist
    }

# ============================================================================
# NORMAL DISTRIBUTION PROBABILITIES
# ============================================================================

def prob_normal_less_than(x, mu, sigma):
    """
    Probability that a normal random variable is less than x
    
    P(X < x) for X ~ N(μ, σ²)
    
    Parameters
    ----------
    x : float
        Upper bound
    mu : float
        Mean of the normal distribution
    sigma : float
        Standard deviation of the normal distribution
    
    Returns
    -------
    float
        Probability P(X < x)
    """
    print_yellow(f"⚠ Normal distribution: μ = {mu}, σ = {sigma}")
    print_yellow(f"⚠ Finding: P(X < {x})")
    
    z = (x - mu) / sigma
    print_cyan(f"z = (x - μ) / σ = ({x} - {mu}) / {sigma} = {z}")
    
    prob = norm.cdf(x, mu, sigma)
    print_white(f"P(X < {x}) = {prob}")
    
    return prob

def prob_normal_greater_than(x, mu, sigma):
    """
    Probability that a normal random variable is greater than x
    
    P(X > x) for X ~ N(μ, σ²)
    
    Parameters
    ----------
    x : float
        Lower bound
    mu : float
        Mean of the normal distribution
    sigma : float
        Standard deviation of the normal distribution
    
    Returns
    -------
    float
        Probability P(X > x)
    """
    print_yellow(f"⚠ Normal distribution: μ = {mu}, σ = {sigma}")
    print_yellow(f"⚠ Finding: P(X > {x})")
    
    z = (x - mu) / sigma
    print_cyan(f"z = (x - μ) / σ = ({x} - {mu}) / {sigma} = {z}")
    
    prob = 1 - norm.cdf(x, mu, sigma)
    print_white(f"P(X > {x}) = {prob}")
    
    return prob

def prob_normal_between(x1, x2, mu, sigma):
    """
    Probability that a normal random variable is between x1 and x2
    
    P(x1 < X < x2) for X ~ N(μ, σ²)
    
    Parameters
    ----------
    x1 : float
        Lower bound
    x2 : float
        Upper bound
    mu : float
        Mean of the normal distribution
    sigma : float
        Standard deviation of the normal distribution
    
    Returns
    -------
    float
        Probability P(x1 < X < x2)
    """
    print_yellow(f"⚠ Normal distribution: μ = {mu}, σ = {sigma}")
    print_yellow(f"⚠ Finding: P({x1} < X < {x2})")
    
    z1 = (x1 - mu) / sigma
    z2 = (x2 - mu) / sigma
    print_cyan(f"z1 = (x1 - μ) / σ = ({x1} - {mu}) / {sigma} = {z1}")
    print_cyan(f"z2 = (x2 - μ) / σ = ({x2} - {mu}) / {sigma} = {z2}")
    
    prob = norm.cdf(x2, mu, sigma) - norm.cdf(x1, mu, sigma)
    print_white(f"P({x1} < X < {x2}) = {prob}")
    
    return prob

