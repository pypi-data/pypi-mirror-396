"""
pattingalloang: JAX-Accelerated Aizawa Attractor Analysis

A high-performance Python library for simulating and analyzing the Aizawa
strange attractor with comprehensive chaos metrics.

The Aizawa attractor is a three-dimensional chaotic dynamical system:
    dx/dt = (z - b)x - dy
    dy/dt = dx + (z - b)y  
    dz/dt = c + az - z³/3 - (x² + y²)(1 + ez) + fzx³

Features:
    - JAX GPU/CPU acceleration for fast integration
    - Comprehensive chaos metrics (Lyapunov exponents, dimensions, entropy)
    - Beautiful dark-themed visualizations
    - Multiple output formats (CSV, NetCDF, PNG, GIF)

Example:
    >>> from pattingalloang import AizawaSystem, AizawaSolver
    >>> system = AizawaSystem()
    >>> solver = AizawaSolver(dt=0.01)
    >>> result = solver.solve(system, n_steps=80000)
    >>> print(f"Trajectory shape: {result['trajectory'].shape}")

Author: Sandy H. S. Herho
Email: sandy.herho@email.ucr.edu
License: MIT
"""

__version__ = "0.0.2"
__author__ = "Sandy H. S. Herho"
__email__ = "sandy.herho@email.ucr.edu"
__license__ = "MIT"

from .core.attractor import AizawaSystem
from .core.integrator import AizawaSolver
from .core.metrics import (
    compute_lyapunov_exponents,
    compute_correlation_dimension,
    compute_kaplan_yorke_dimension,
    compute_kolmogorov_sinai_entropy,
    compute_recurrence_metrics,
    compute_average_mutual_information,
    compute_all_metrics,
    compute_metrics_timeseries,
)
from .io.config_manager import ConfigManager
from .io.data_handler import DataHandler

__all__ = [
    # Core classes
    "AizawaSystem",
    "AizawaSolver",
    # Config and data
    "ConfigManager",
    "DataHandler",
    # Metrics functions
    "compute_lyapunov_exponents",
    "compute_correlation_dimension",
    "compute_kaplan_yorke_dimension",
    "compute_kolmogorov_sinai_entropy",
    "compute_recurrence_metrics",
    "compute_average_mutual_information",
    "compute_all_metrics",
    "compute_metrics_timeseries",
]
