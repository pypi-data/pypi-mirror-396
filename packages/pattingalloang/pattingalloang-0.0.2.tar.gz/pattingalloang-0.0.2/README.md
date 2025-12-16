# `pattingalloang`: A JAX-Accelerated Framework for the Aizawa Strange Attractor

[![DOI](https://zenodo.org/badge/1112665838.svg)](https://doi.org/10.5281/zenodo.17891089)
[![Tests](https://github.com/sandyherho/pattingalloang/actions/workflows/tests.yml/badge.svg)](https://github.com/sandyherho/pattingalloang/actions/workflows/tests.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/pattingalloang.svg)](https://pypi.org/project/pattingalloang/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[![JAX](https://img.shields.io/badge/JAX-%23FF6F00.svg?logo=google&logoColor=white)](https://github.com/google/jax)
[![NumPy](https://img.shields.io/badge/NumPy-%23013243.svg?logo=numpy&logoColor=white)](https://numpy.org/)
[![SciPy](https://img.shields.io/badge/SciPy-%230C55A5.svg?logo=scipy&logoColor=white)](https://scipy.org/)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-%23ffffff.svg?logo=Matplotlib&logoColor=black)](https://matplotlib.org/)
[![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![netCDF4](https://img.shields.io/badge/netCDF4-%23004B87.svg)](https://unidata.github.io/netcdf4-python/)

JAX-accelerated Python library for simulating and analyzing the Aizawa strange attractor with comprehensive chaos metrics.


> *This library is named after **Karaeng Pattingalloang III** (1600–1654), an eminent scholar-statesman of the Gowa-Tallo Sultanate in South Sulawesi, Indonesia. Serving as Grand Vizier from 1639 until his death, Pattingalloang was renowned throughout the early modern maritime world for his exceptional intellectual pursuits. Contemporary European accounts document his mastery of multiple languages, his extensive library of Western scientific and cartographic works, and his sophisticated engagement with mathematics, astronomy, and natural philosophy. His scholarly reputation earned him the epithet "Father of Makassar" among European observers. This library honors his legacy as a patron of cross-cultural scientific exchange during the Age of Exploration.*

<p align="center">
  <img src="https://github.com/sandyherho/pattingalloang/blob/main/.assets/anim.gif" alt="Aizawa Attractor Animation" width="600">
</p>

## Governing Equations

$$\dot{x} = (z - b)x - dy$$

$$\dot{y} = dx + (z - b)y$$

$$\dot{z} = c + az - \frac{z^3}{3} - (x^2 + y^2)(1 + ez) + fzx^3$$

**Standard Parameters:** $a=0.95$, $b=0.7$, $c=0.6$, $d=3.5$, $e=0.25$, $f=0.1$

## Installation

```bash
pip install pattingalloang          # From PyPI
pip install jax[cuda12]             # Optional: GPU support
```

## Quick Start

**CLI:**
```bash
pattingalloang case1              # Standard Aizawa
pattingalloang --all              # Run all 7 cases
pattingalloang case1 --gpu        # GPU acceleration
```

**Python API:**
```python
from pattingalloang import AizawaSystem, AizawaSolver, compute_all_metrics

system = AizawaSystem(a=0.95, b=0.7, c=0.6, d=3.5, e=0.25, f=0.1)
solver = AizawaSolver(dt=0.01, use_gpu=False)
result = solver.solve(system, n_steps=80000, initial_state=[0.1, 0.0, 0.0])

lyap_result = solver.solve_with_lyapunov(system, n_steps=30000)
metrics = compute_all_metrics(result['trajectory'], result['time'], 
                              system.params.to_tuple(), dt=0.01,
                              log_diags=lyap_result['log_diags'])

print(f"λ₁={metrics['lyapunov_1']:.4f}, D_KY={metrics['kaplan_yorke_dim']:.4f}")
```

## Test Cases

| Case | Description | Steps | Focus |
|:----:|:------------|------:|:------|
| 1 | Standard Aizawa | 80K | Classic butterfly structure |
| 2 | High Resolution | 150K | Fine attractor detail |
| 3 | Long Trajectory | 300K | Accurate chaos metrics |
| 4 | Parameter Variation | 80K | Effect of parameter changes |
| 5 | Multi-Trajectory | 80K | Sensitivity to initial conditions |
| 6 | Butterfly Wings | 120K | Wing structure emphasis |
| 7 | Chaotic Spiral | 100K | Spiral-like dynamics |

## Chaos Metrics

| Metric | Description |
|:-------|:------------|
| **Lyapunov Exponents** | Rate of trajectory divergence ($\lambda_1 > 0$ → chaos) |
| **Kaplan-Yorke Dimension** | Fractal dimension from Lyapunov spectrum |
| **Correlation Dimension** | Grassberger-Procaccia attractor complexity |
| **KS Entropy** | Information production rate ($\sum \lambda_i$ for $\lambda_i > 0$) |
| **Recurrence Rate** | Fraction of recurrent points |
| **Determinism** | Predictability from recurrence plot |

## Output Files

- **CSV:** `*_trajectory.csv`, `*_chaos_metrics.csv`
- **NetCDF:** CF-compliant with all variables and metadata
- **PNG:** High-resolution static visualizations
- **GIF:** Animated 3D rotation

## License

MIT © Sandy H. S. Herho

## Citation

```bibtex
@software{herho2025_pattingalloang,
  title   = {{\texttt{pattingalloang}: A JAX-Accelerated Framework for the Aizawa Strange Attractor}},
  author  = {Herho, Sandy H. S.},
  year    = {2025},
  url     = {https://github.com/sandyherho/pattingalloang}
}
```
