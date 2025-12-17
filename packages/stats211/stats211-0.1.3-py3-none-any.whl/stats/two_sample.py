"""
Two-sample hypothesis tests
"""

from math import sqrt
from scipy.stats import norm, t
from .standard_error import se_difference_proportions
from .critical_values import critical_value
from .utils import print_cyan, print_white, print_yellow, print_red

# ============================================================================
# TWO-SAMPLE TESTS
# ============================================================================

def test_two_proportions(n1, x1, n2, x2, alpha=0.05, tail='two'):
    """
    Two-sample z-test for proportions
    
    H0: p1 = p2
    H1: depends on tail
    """
    print("=" * 60)
    print("TWO-SAMPLE PROPORTION TEST")
    print("=" * 60)
    
    print_yellow(f"⚠ Test type: {tail}-tailed, α = {alpha}")
    print_yellow(f"⚠ H0: p1 = p2")
    if tail == 'two':
        print_yellow(f"⚠ H1: p1 ≠ p2")
    elif tail == 'right':
        print_yellow(f"⚠ H1: p1 > p2")
    elif tail == 'left':
        print_yellow(f"⚠ H1: p1 < p2")
    
    print_yellow(f"⚠ Assumes: independent samples, normal approximation valid")
    print()
    
    # Sample proportions
    p1 = x1 / n1
    p2 = x2 / n2
    print_cyan(f"Sample 1: n1 = {n1}, x1 = {x1}, p̂1 = {p1}")
    print_cyan(f"Sample 2: n2 = {n2}, x2 = {x2}, p̂2 = {p2}")
    
    diff = p1 - p2
    print_cyan(f"Difference: p̂1 - p̂2 = {diff}")
    print()
    
    # Pooled proportion (for hypothesis test)
    p_pool = (x1 + x2) / (n1 + n2)
    print_cyan(f"Pooled proportion: p̂_pool = (x1+x2)/(n1+n2) = {p_pool}")
    
    # Check assumptions
    if n1*p_pool < 10 or n1*(1-p_pool) < 10 or n2*p_pool < 10 or n2*(1-p_pool) < 10:
        print_red("WARNING: Normal approximation may be poor. Check np and n(1-p) ≥ 10")
    
    # Standard error (pooled, for hypothesis test)
    se_pooled = se_difference_proportions(p1, n1, p2, n2, pooled=True, p_pool=p_pool)
    
    # Test statistic
    z = diff / se_pooled
    print_white(f"Test statistic: z = {z}")
    
    # P-value
    if tail == 'two':
        p_value = 2 * (1 - norm.cdf(abs(z)))
    elif tail == 'right':
        p_value = 1 - norm.cdf(z)
    else:  # left
        p_value = norm.cdf(z)
    
    print_white(f"P-value = {p_value}")
    
    # Critical value
    z_crit = critical_value(alpha, 'z', tail=tail)
    
    # Decision
    reject = p_value < alpha
    if reject:
        print_white(f"Decision: REJECT H0")
    else:
        print_white(f"Decision: FAIL TO REJECT H0")
    
    print()
    
    # Confidence interval (uses unpooled SE)
    print_yellow(f"⚠ {(1-alpha)*100}% Confidence Interval for (p1 - p2):")
    se_unpooled = se_difference_proportions(p1, n1, p2, n2, pooled=False)
    z_ci = critical_value(alpha, 'z', tail='two')
    ci_lower = diff - z_ci * se_unpooled
    ci_upper = diff + z_ci * se_unpooled
    print_white(f"CI: ({ci_lower}, {ci_upper})")
    
    return z, p_value, z_crit, reject

def test_two_means(n1, xbar1, s1, n2, xbar2, s2, alpha=0.05, tail='two', equal_var=False):
    """
    Two-sample t-test for means
    
    H0: μ1 = μ2
    H1: depends on tail
    """
    print("=" * 60)
    print("TWO-SAMPLE MEAN TEST")
    print("=" * 60)
    
    print_yellow(f"⚠ Test type: {tail}-tailed, α = {alpha}")
    print_yellow(f"⚠ H0: μ1 = μ2")
    if tail == 'two':
        print_yellow(f"⚠ H1: μ1 ≠ μ2")
    elif tail == 'right':
        print_yellow(f"⚠ H1: μ1 > μ2")
    elif tail == 'left':
        print_yellow(f"⚠ H1: μ1 < μ2")
    
    if equal_var:
        print_yellow(f"⚠ Assumes: equal population variances, independent samples, normal populations")
    else:
        print_yellow(f"⚠ Assumes: independent samples, normal populations (Welch's test)")
    print()
    
    # Sample summaries
    print_cyan(f"Sample 1: n1 = {n1}, x̄1 = {xbar1}, s1 = {s1}")
    print_cyan(f"Sample 2: n2 = {n2}, x̄2 = {xbar2}, s2 = {s2}")
    
    diff = xbar1 - xbar2
    print_cyan(f"Difference: x̄1 - x̄2 = {diff}")
    print()
    
    # Standard error and degrees of freedom
    if equal_var:
        # Pooled variance
        sp2 = ((n1-1)*s1**2 + (n2-1)*s2**2) / (n1 + n2 - 2)
        print_cyan(f"Pooled variance: sp² = {sp2}")
        se = sqrt(sp2 * (1/n1 + 1/n2))
        print_cyan(f"SE = √[sp²(1/n1 + 1/n2)] = {se}")
        df = n1 + n2 - 2
        print_cyan(f"Degrees of freedom: df = n1 + n2 - 2 = {df}")
    else:
        # Welch's
        se = sqrt(s1**2/n1 + s2**2/n2)
        print_cyan(f"SE = √[s1²/n1 + s2²/n2] = {se}")
        # Welch-Satterthwaite df
        v1 = s1**2 / n1
        v2 = s2**2 / n2
        df = (v1 + v2)**2 / ((v1**2)/(n1-1) + (v2**2)/(n2-1))
        print_cyan(f"Welch-Satterthwaite df = {df}")
    
    # Test statistic
    t_stat = diff / se
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
    
    print()
    
    # Confidence interval
    print_yellow(f"⚠ {(1-alpha)*100}% Confidence Interval for (μ1 - μ2):")
    t_ci = critical_value(alpha, 't', df=df, tail='two')
    ci_lower = diff - t_ci * se
    ci_upper = diff + t_ci * se
    print_white(f"CI: ({ci_lower}, {ci_upper})")
    
    return t_stat, p_value, t_crit, reject

