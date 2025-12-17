"""
Descriptive statistics and z-score conversions
- Basic statistics from data
- Z-score conversions
"""

from scipy.stats import norm, tmean
import numpy as np
from .utils import print_cyan, print_white

# ============================================================================
# Z-SCORE CONVERSIONS
# ============================================================================

def x_to_z(x, mu, sigma):
    """Convert raw score to z-score"""
    z = (x - mu) / sigma
    print_cyan(f"z = (x - μ) / σ = ({x} - {mu}) / {sigma}")
    print_white(f"z = {z}")
    return z

def z_to_x(z, mu, sigma):
    """Convert z-score to raw score"""
    x = z * sigma + mu
    print_cyan(f"x = z × σ + μ = {z} × {sigma} + {mu}")
    print_white(f"x = {x}")
    return x

def z_to_percentile(z):
    """Convert z-score to percentile"""
    percentile = norm.cdf(z) * 100
    print_cyan(f"Percentile = Φ(z) × 100 = Φ({z}) × 100")
    print_white(f"Percentile = {percentile}%")
    return percentile

def percentile_to_z(percentile):
    """Convert percentile to z-score"""
    z = norm.ppf(percentile / 100)
    print_cyan(f"z = Φ⁻¹(percentile/100) = Φ⁻¹({percentile}/100)")
    print_white(f"z = {z}")
    return z

# ============================================================================
# BASIC STATISTICS FROM DATA
# ============================================================================

def get_mean(values):
    """Calculate sample mean"""
    xbar = tmean(values)
    print_cyan(f"Sample mean (x̄) calculated from {len(values)} values")
    print_white(f"x̄ = {xbar}")
    return xbar

def get_std(values):
    """Calculate sample standard deviation (with Bessel's correction)"""
    s = np.std(values, ddof=1)
    print_cyan(f"Sample standard deviation (s) with n-1 correction")
    print_white(f"s = {s}")
    return s

def get_variance(values):
    """Calculate sample variance"""
    s2 = np.var(values, ddof=1)
    print_cyan(f"Sample variance (s²) with n-1 correction")
    print_white(f"s² = {s2}")
    return s2

