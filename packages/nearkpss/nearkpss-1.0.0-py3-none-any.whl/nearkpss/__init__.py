"""
nearkpss: Modified KPSS Tests for Near Integration
===================================================

A Python implementation of the Modified KPSS test for near integration
as proposed by Harris, Leybourne, and McCabe (2007).

Reference
---------
Harris, D., Leybourne, S., & McCabe, B. (2007). Modified KPSS Tests for 
Near Integration. Econometric Theory, 23(2), 355-363.
DOI: 10.1017/S0266466607070156

Author: Dr Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/modifiedkpss

"""

__version__ = "1.0.0"
__author__ = "Dr Merwan Roudane"
__email__ = "merwanroudane920@gmail.com"

from .mkpss import (
    ModifiedKPSS,
    modified_kpss_test,
    standard_kpss_test,
)
from .critical_values import (
    CriticalValues,
    get_critical_values,
    simulate_critical_values,
)
from .long_run_variance import (
    long_run_variance,
    newey_west_bandwidth,
    quadratic_spectral_kernel,
    bartlett_kernel,
    parzen_kernel,
)
from .utils import (
    gls_transform,
    compute_residuals,
    compute_partial_sums,
)

__all__ = [
    # Main test class and functions
    "ModifiedKPSS",
    "modified_kpss_test",
    "standard_kpss_test",
    # Critical values
    "CriticalValues",
    "get_critical_values",
    "simulate_critical_values",
    # Long-run variance
    "long_run_variance",
    "newey_west_bandwidth",
    "quadratic_spectral_kernel",
    "bartlett_kernel",
    "parzen_kernel",
    # Utilities
    "gls_transform",
    "compute_residuals",
    "compute_partial_sums",
]
