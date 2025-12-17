"""
Critical value calculations
"""

from scipy.stats import norm, t
from scipy import stats
from .utils import print_cyan, print_white, print_yellow, print_red

# ============================================================================
# CRITICAL VALUES
# ============================================================================

def critical_value(alpha, distribution='z', df=None, tail='two'):
    """
    Get critical value for a distribution
    
    Parameters:
    - alpha: significance level
    - distribution: 'z' or 't'
    - df: degrees of freedom (required for t)
    - tail: 'two', 'left', or 'right'
    """
    if distribution == 't' and df is None:
        print_red("ERROR: t-distribution requires df parameter")
        return None
    
    print_yellow(f"⚠ Distribution: {distribution}, α = {alpha}, tail: {tail}")
    
    if distribution == 'z':
        if tail == 'two':
            crit = norm.ppf(1 - alpha/2)
            print_cyan(f"z* = z_(1-α/2) = z_({1-alpha/2})")
        elif tail == 'right':
            crit = norm.ppf(1 - alpha)
            print_cyan(f"z* = z_(1-α) = z_({1-alpha})")
        elif tail == 'left':
            crit = norm.ppf(alpha)
            print_cyan(f"z* = z_(α) = z_({alpha})")
    elif distribution == 't':
        if tail == 'two':
            crit = t.ppf(1 - alpha/2, df)
            print_cyan(f"t* = t_(1-α/2, df={df}) = t_({1-alpha/2}, {df})")
        elif tail == 'right':
            crit = t.ppf(1 - alpha, df)
            print_cyan(f"t* = t_(1-α, df={df}) = t_({1-alpha}, {df})")
        elif tail == 'left':
            crit = t.ppf(alpha, df)
            print_cyan(f"t* = t_(α, df={df}) = t_({alpha}, {df})")
    else:
        print_red(f"ERROR: distribution must be 'z' or 't'")
        return None
    
    print_white(f"Critical value = {crit}")
    return crit

# ============================================================================
# GENERAL CRITICAL VALUE FUNCTION
# ============================================================================

def critical_test_statistic(alpha, test_type, sample_size, tails="two", predictors=1):
    """
    Calculate critical test statistic
    
    Parameters:
    - alpha: significance level
    - test_type: "t", "z", "f", "chi_square"
    - sample_size: number of observations
    - tails: "one" or "two"
    - predictors: number of predictors (for F and t tests)
    """
    test_type = test_type.lower()
    tails = tails.lower()
    
    tail = 'two' if tails == 'two' else 'right'
    
    if test_type == "t":
        df = sample_size - predictors - 1
        return critical_value(alpha, 't', df=df, tail=tail)
    
    elif test_type == "z":
        return critical_value(alpha, 'z', tail=tail)
    
    elif test_type == "f":
        df1 = predictors
        df2 = sample_size - predictors - 1
        print_yellow(f"⚠ F-distribution: df1={df1}, df2={df2}")
        f_crit = stats.f.ppf(1 - alpha, df1, df2)
        print_white(f"F critical value = {f_crit}")
        return f_crit
    
    elif test_type == "chi_square":
        df = sample_size - 1
        print_yellow(f"⚠ χ² distribution: df={df}")
        chi2_crit = stats.chi2.ppf(1 - alpha, df)
        print_white(f"χ² critical value = {chi2_crit}")
        return chi2_crit
    
    else:
        print_red(f"ERROR: Unsupported test type: {test_type}")
        return None

