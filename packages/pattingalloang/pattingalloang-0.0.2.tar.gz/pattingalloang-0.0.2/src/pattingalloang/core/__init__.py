"""Core solver components for Aizawa attractor analysis."""

from .attractor import AizawaSystem, AizawaParams
from .integrator import AizawaSolver
from .metrics import (
    compute_lyapunov_exponents,
    compute_lyapunov_spectrum_timeseries,
    compute_kaplan_yorke_dimension,
    compute_kolmogorov_sinai_entropy,
    compute_correlation_dimension,
    compute_recurrence_metrics,
    compute_average_mutual_information,
    compute_false_nearest_neighbors,
    compute_attractor_statistics,
    compute_all_metrics,
    compute_metrics_timeseries,
)

__all__ = [
    "AizawaSystem",
    "AizawaParams",
    "AizawaSolver",
    "compute_lyapunov_exponents",
    "compute_lyapunov_spectrum_timeseries",
    "compute_kaplan_yorke_dimension",
    "compute_kolmogorov_sinai_entropy",
    "compute_correlation_dimension",
    "compute_recurrence_metrics",
    "compute_average_mutual_information",
    "compute_false_nearest_neighbors",
    "compute_attractor_statistics",
    "compute_all_metrics",
    "compute_metrics_timeseries",
]
