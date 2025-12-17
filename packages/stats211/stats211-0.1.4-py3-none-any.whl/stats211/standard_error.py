"""
Standard error calculations
"""

from math import sqrt
from .utils import print_cyan, print_white, print_yellow, print_red

# ============================================================================
# STANDARD ERROR CALCULATIONS
# ============================================================================

def se_proportion(p, n):
    """Standard error for a proportion"""
    print_yellow(f"⚠ Assumes: population proportion p = {p}")
    se = sqrt(p * (1 - p) / n)
    print_cyan(f"SE = √[p(1-p)/n] = √[{p}×{1-p}/{n}]")
    print_white(f"SE = {se}")
    return se

def se_mean(s, n):
    """Standard error for a mean"""
    se = s / sqrt(n)
    print_cyan(f"SE = s / √n = {s} / √{n}")
    print_white(f"SE = {se}")
    return se

def se_difference_proportions(p1, n1, p2, n2, pooled=False, p_pool=None):
    """Standard error for difference in proportions"""
    if pooled:
        if p_pool is None:
            print_red("ERROR: pooled=True requires p_pool parameter")
            return None
        print_yellow(f"⚠ Using pooled SE (for hypothesis testing)")
        se = sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))
        print_cyan(f"SE_pooled = √[p_pool(1-p_pool)(1/n1 + 1/n2)]")
        print_cyan(f"SE_pooled = √[{p_pool}×{1-p_pool}×(1/{n1} + 1/{n2})]")
    else:
        print_yellow(f"⚠ Using unpooled SE (for confidence intervals)")
        se = sqrt(p1*(1-p1)/n1 + p2*(1-p2)/n2)
        print_cyan(f"SE = √[p1(1-p1)/n1 + p2(1-p2)/n2]")
        print_cyan(f"SE = √[{p1}×{1-p1}/{n1} + {p2}×{1-p2}/{n2}]")
    print_white(f"SE = {se}")
    return se

def se_difference_means(s1, n1, s2, n2, equal_var=False):
    """Standard error for difference in means"""
    if equal_var:
        print_yellow(f"⚠ Assuming equal population variances")
        # Pooled variance
        sp2 = ((n1-1)*s1**2 + (n2-1)*s2**2) / (n1 + n2 - 2)
        print_cyan(f"Pooled variance: sp² = [(n1-1)s1² + (n2-1)s2²] / (n1+n2-2)")
        print_cyan(f"sp² = [({n1}-1)×{s1**2} + ({n2}-1)×{s2**2}] / {n1+n2-2}")
        print_cyan(f"sp² = {sp2}")
        se = sqrt(sp2 * (1/n1 + 1/n2))
        print_cyan(f"SE = √[sp²(1/n1 + 1/n2)] = √[{sp2}×(1/{n1} + 1/{n2})]")
    else:
        print_yellow(f"⚠ Using Welch's approximation (unequal variances)")
        se = sqrt(s1**2/n1 + s2**2/n2)
        print_cyan(f"SE = √[s1²/n1 + s2²/n2] = √[{s1**2}/{n1} + {s2**2}/{n2}]")
    print_white(f"SE = {se}")
    return se

