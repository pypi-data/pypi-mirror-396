"""
Legacy stats.py file - maintained for backward compatibility

This file now imports all functions from the organized sub-modules.
All functionality remains the same, but the code is now better organized.

For backward compatibility, this file re-exports everything.
You can continue using: from stats.stats import *
"""

# Import everything from the new organized modules
from .utils import *
from .descriptive import *
from .standard_error import *
from .critical_values import *
from .confidence_intervals import *
from .sample_size import *
from .hypothesis_testing import *
from .two_sample import *
from .regression import *
from .probability import *
from .inverse import *

# This file maintains backward compatibility with:
#   from stats.stats import *
#   from stats import * (if __init__.py is set up correctly)
