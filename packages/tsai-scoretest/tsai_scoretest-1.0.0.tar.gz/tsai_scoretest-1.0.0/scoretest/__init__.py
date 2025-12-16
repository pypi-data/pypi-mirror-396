"""
ScoreTest: Score Test for the First-Order Autoregressive Model with Heteroscedasticity

A Python implementation of the score test proposed by Tsai (1986) for simultaneous
testing of independence and homoscedasticity in the first-order autoregressive model
with nonconstant variance.

Reference:
    Tsai, C.-L. (1986). Score test for the first-order autoregressive model with
    heteroscedasticity. Biometrika, 73(2), 455-460.

Author: Dr Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/scoretest
"""

__version__ = "1.0.0"
__author__ = "Dr Merwan Roudane"
__email__ = "merwanroudane920@gmail.com"

from .core import (
    TsaiScoreTest,
    score_test_autocorrelation,
    score_test_heteroscedasticity,
    score_test_joint,
)
from .weight_functions import (
    exponential_weight,
    linear_weight,
    power_weight,
    compute_weight_derivatives,
)
from .simulation import (
    simulate_critical_values,
    SimulationResults,
)
from .diagnostics import (
    normal_curvature,
    parameter_sensitivity,
    influence_graph,
)
from .utils import (
    ols_residuals,
    compute_rho_hat,
    compute_variance_vector,
)

__all__ = [
    # Core test functions
    "TsaiScoreTest",
    "score_test_autocorrelation",
    "score_test_heteroscedasticity", 
    "score_test_joint",
    # Weight functions
    "exponential_weight",
    "linear_weight",
    "power_weight",
    "compute_weight_derivatives",
    # Simulation
    "simulate_critical_values",
    "SimulationResults",
    # Diagnostics
    "normal_curvature",
    "parameter_sensitivity",
    "influence_graph",
    # Utilities
    "ols_residuals",
    "compute_rho_hat",
    "compute_variance_vector",
]
