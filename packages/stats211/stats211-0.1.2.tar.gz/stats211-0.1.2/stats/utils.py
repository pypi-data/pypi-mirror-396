"""
Utility functions for statistics module
- Color printing utilities
- File I/O operations
"""

import pandas as pd
import inspect

# ============================================================================
# COLOR PRINTING UTILITIES
# ============================================================================

def print_red(s): 
    """Print warning in red"""
    print(f'\033[31m{s}\033[0m')

def print_yellow(s): 
    """Print reminder in yellow"""
    print(f'\033[33m{s}\033[0m')

def print_white(s): 
    """Print answer in white (bold)"""
    print(f'\033[1m{s}\033[0m')

def print_cyan(s):
    """Print intermediate values in cyan"""
    print(f'\033[36m{s}\033[0m')

# ============================================================================
# FILE I/O
# ============================================================================

def load_data(path, col=0):
    """Load data from CSV file"""
    df = pd.read_csv(path)
    data = df[df.columns[col]].tolist()
    print_cyan(f"Loaded {len(data)} values from column {col}")
    return data

# ============================================================================
# HELP FUNCTION
# ============================================================================

def stats_help(filter_str=None):
    """
    Display all available functions in the stats package.
    
    Parameters:
    - filter_str (optional): If provided, only show functions containing this string in their name,
                            and display their full function signatures with arguments.
    
    Examples:
        stats_help()                    # List all function names
        stats_help('mean')              # Show all functions with 'mean' in name + their arguments
        stats_help('confidence')        # Show all functions with 'confidence' in name + their arguments
    """
    # Import __all__ to get the list of exported functions
    from . import __all__
    
    # Import modules to get functions
    from . import descriptive, standard_error, critical_values, confidence_intervals
    from . import sample_size, hypothesis_testing, two_sample, regression
    from . import probability, inverse
    
    # Build function dictionary, only including functions in __all__
    func_dict = {}
    
    # Utils
    if 'print_red' in __all__:
        func_dict['print_red'] = print_red
    if 'print_yellow' in __all__:
        func_dict['print_yellow'] = print_yellow
    if 'print_white' in __all__:
        func_dict['print_white'] = print_white
    if 'print_cyan' in __all__:
        func_dict['print_cyan'] = print_cyan
    if 'load_data' in __all__:
        func_dict['load_data'] = load_data
    
    # Import from each module, only if in __all__
    for module in [descriptive, standard_error, critical_values, confidence_intervals,
                   sample_size, hypothesis_testing, two_sample, regression,
                   probability, inverse]:
        for name in __all__:
            if name not in func_dict and hasattr(module, name):
                obj = getattr(module, name)
                if callable(obj):
                    func_dict[name] = obj
    
    # Filter functions if filter_str is provided
    if filter_str:
        filtered_funcs = {name: func for name, func in func_dict.items() 
                         if filter_str.lower() in name.lower()}
        
        if not filtered_funcs:
            print_yellow(f"No functions found containing '{filter_str}'")
            return
        
        print_cyan(f"\nFunctions containing '{filter_str}':\n")
        for name, func in sorted(filtered_funcs.items()):
            try:
                sig = inspect.signature(func)
                print_white(f"{name}{sig}")
            except:
                print_white(f"{name}(...)")
        print()
    else:
        # Print all function names grouped by category
        categories = {
            'Utils': ['print_red', 'print_yellow', 'print_white', 'print_cyan', 'load_data'],
            'Descriptive': ['x_to_z', 'z_to_x', 'z_to_percentile', 'percentile_to_z', 
                          'get_mean', 'get_std', 'get_variance'],
            'Standard Error': ['se_proportion', 'se_mean', 'se_difference_proportions', 
                             'se_difference_means'],
            'Critical Values': ['critical_value', 'critical_test_statistic'],
            'Confidence Intervals': ['ci_mean', 'ci_proportion'],
            'Sample Size': ['sample_size_proportion', 'sample_size_mean',
                          'margin_from_sample_size_proportion', 'margin_from_sample_size_mean'],
            'Hypothesis Testing': ['test_mean', 'test_proportion'],
            'Two-Sample': ['test_two_proportions', 'test_two_means'],
            'Regression': ['slope_test', 'slope_test_statistic', 'linregress_ci', 'linregress_predict',
                          'linregress_ci_data', 'linregress_predict_data'],
            'Probability': ['prob_mean_in_range', 'prob_proportion_in_range', 'prob_normal_in_range',
                          'compute_sampling_distribution_params', 'compute_sampling_distribution_proportion_params',
                          'prob_normal_less_than', 'prob_normal_greater_than', 'prob_normal_between'],
            'Inverse': ['solve_xbar_from_ci', 'solve_margin_from_ci', 'solve_critical_from_margin',
                       'solve_alpha_from_critical', 'solve_p_from_test_stat', 'p_to_stat', 'quantile_normal']
        }
        
        print_cyan("\nAvailable functions in stats package:\n")
        for category, funcs in categories.items():
            available_funcs = [f for f in funcs if f in func_dict]
            if available_funcs:
                print_yellow(f"{category}:")
                for func_name in sorted(available_funcs):
                    print_white(f"  {func_name}")
                print()
