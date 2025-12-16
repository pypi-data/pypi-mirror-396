"""
JAX-Accelerated Integrator for Aizawa Attractor.

Implements high-performance numerical integration using JAX with
optional GPU acceleration. Uses 4th-order Runge-Kutta method with
lax.scan for efficient trajectory computation.

Features:
    - JIT-compiled integration kernels
    - GPU/CPU backend selection
    - Batch trajectory computation with vmap
    - Jacobian tracking for Lyapunov exponents

References:
    Kantz, H., & Schreiber, T. (2004). Nonlinear Time Series Analysis.
"""

import os
from typing import Dict, Any, Optional, List, Tuple, Union
from functools import partial

import numpy as np
from tqdm import tqdm

# Configure JAX before import
def _configure_jax(use_gpu: bool = False):
    """Configure JAX backend before first use."""
    if use_gpu:
        os.environ['JAX_PLATFORM_NAME'] = 'gpu'
    else:
        os.environ['JAX_PLATFORM_NAME'] = 'cpu'

# Import JAX
import jax
import jax.numpy as jnp
from jax import jit, lax, vmap

from .attractor import AizawaSystem


# ============================================================================
# JAX-COMPILED INTEGRATION KERNELS
# ============================================================================

@jit
def _aizawa_derivatives(state: jnp.ndarray, params: jnp.ndarray) -> jnp.ndarray:
    """
    Compute Aizawa attractor derivatives (JIT-compiled).
    
    Args:
        state: Array [x, y, z]
        params: Array [a, b, c, d, e, f]
    
    Returns:
        Array [dx, dy, dz]
    """
    x, y, z = state[0], state[1], state[2]
    a, b, c, d, e, f = params[0], params[1], params[2], params[3], params[4], params[5]
    
    dx = (z - b) * x - d * y
    dy = d * x + (z - b) * y
    dz = c + a * z - (z**3 / 3) - (x**2 + y**2) * (1 + e * z) + f * z * x**3
    
    return jnp.array([dx, dy, dz])


@jit
def _rk4_step(state: jnp.ndarray, params: jnp.ndarray, dt: float) -> jnp.ndarray:
    """
    Single RK4 integration step (JIT-compiled).
    
    Args:
        state: Current state [x, y, z]
        params: System parameters [a, b, c, d, e, f]
        dt: Time step
    
    Returns:
        Next state [x, y, z]
    """
    k1 = _aizawa_derivatives(state, params)
    k2 = _aizawa_derivatives(state + 0.5 * dt * k1, params)
    k3 = _aizawa_derivatives(state + 0.5 * dt * k2, params)
    k4 = _aizawa_derivatives(state + dt * k3, params)
    
    return state + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)


@partial(jit, static_argnums=(0,))
def _integrate_trajectory(
    n_steps: int,
    dt: float,
    initial_state: jnp.ndarray,
    params: jnp.ndarray
) -> jnp.ndarray:
    """
    Integrate full trajectory using lax.scan (JIT-compiled).
    
    Args:
        n_steps: Number of integration steps
        dt: Time step
        initial_state: Initial [x, y, z]
        params: System parameters
    
    Returns:
        Trajectory array of shape (n_steps, 3)
    """
    def scan_fn(state, _):
        next_state = _rk4_step(state, params, dt)
        return next_state, next_state
    
    _, trajectory = lax.scan(scan_fn, initial_state, None, length=n_steps-1)
    
    # Prepend initial state
    trajectory = jnp.concatenate([initial_state[None, :], trajectory], axis=0)
    return trajectory


@partial(jit, static_argnums=(0,))
def _integrate_batch(
    n_steps: int,
    dt: float,
    initial_states: jnp.ndarray,
    params: jnp.ndarray
) -> jnp.ndarray:
    """
    Integrate multiple trajectories in parallel using vmap.
    
    Args:
        n_steps: Number of integration steps
        dt: Time step
        initial_states: Initial conditions array (n_traj, 3)
        params: System parameters
    
    Returns:
        Trajectories array (n_traj, n_steps, 3)
    """
    batched_integrate = vmap(
        lambda ic: _integrate_trajectory(n_steps, dt, ic, params)
    )
    return batched_integrate(initial_states)


@jit
def _jacobian_aizawa(state: jnp.ndarray, params: jnp.ndarray) -> jnp.ndarray:
    """
    Compute Jacobian matrix at given state (JIT-compiled).
    
    Args:
        state: Array [x, y, z]
        params: Array [a, b, c, d, e, f]
    
    Returns:
        3x3 Jacobian matrix
    """
    x, y, z = state[0], state[1], state[2]
    a, b, c, d, e, f = params[0], params[1], params[2], params[3], params[4], params[5]
    
    J = jnp.array([
        [z - b, -d, x],
        [d, z - b, y],
        [-2*x*(1 + e*z) + 3*f*z*x**2, 
         -2*y*(1 + e*z), 
         a - z**2 - e*(x**2 + y**2) + f*x**3]
    ])
    return J


@partial(jit, static_argnums=(0,))
def _integrate_with_jacobian(
    n_steps: int,
    dt: float,
    initial_state: jnp.ndarray,
    params: jnp.ndarray
) -> Tuple[jnp.ndarray, jnp.ndarray]:
    """
    Integrate trajectory with tangent vectors for Lyapunov computation.
    
    Uses QR decomposition at each step for numerical stability.
    
    Args:
        n_steps: Number of steps
        dt: Time step
        initial_state: Initial [x, y, z]
        params: System parameters
    
    Returns:
        Tuple of (trajectory, log_diagonals) for Lyapunov calculation
    """
    def scan_fn(carry, _):
        state, Q = carry
        
        # Evolve state
        next_state = _rk4_step(state, params, dt)
        
        # Evolve tangent vectors using Jacobian
        J = _jacobian_aizawa(state, params)
        Q_new = Q + dt * (J @ Q)
        
        # QR decomposition for numerical stability
        Q_new, R = jnp.linalg.qr(Q_new)
        
        # Log of diagonal elements for Lyapunov exponents
        log_diag = jnp.log(jnp.abs(jnp.diag(R)) + 1e-10)
        
        return (next_state, Q_new), (next_state, log_diag)
    
    # Initialize with identity matrix for tangent vectors
    Q0 = jnp.eye(3)
    initial_carry = (initial_state, Q0)
    
    _, (trajectory, log_diags) = lax.scan(
        scan_fn, initial_carry, None, length=n_steps-1
    )
    
    trajectory = jnp.concatenate([initial_state[None, :], trajectory], axis=0)
    
    return trajectory, log_diags


# ============================================================================
# SOLVER CLASS
# ============================================================================

class AizawaSolver:
    """
    JAX-Accelerated Solver for Aizawa Attractor.
    
    Provides high-performance numerical integration with optional
    GPU acceleration and comprehensive trajectory analysis.
    
    Attributes:
        dt: Integration time step
        use_gpu: Whether GPU acceleration is enabled
        backend: JAX backend string ('cpu' or 'gpu')
    
    Example:
        >>> solver = AizawaSolver(dt=0.01, use_gpu=False)
        >>> system = AizawaSystem()
        >>> result = solver.solve(system, n_steps=80000)
    """
    
    def __init__(self, dt: float = 0.01, use_gpu: bool = False):
        """
        Initialize solver.
        
        Args:
            dt: Integration time step (default: 0.01)
            use_gpu: Use GPU acceleration if available (default: False)
        """
        self.dt = dt
        self.use_gpu = use_gpu
        
        # Configure JAX backend
        _configure_jax(use_gpu)
        
        self.backend = jax.default_backend()
        self.devices = jax.devices()
    
    def solve(
        self,
        system: AizawaSystem,
        n_steps: int = 80000,
        initial_state: Optional[Union[np.ndarray, List[float]]] = None,
        transient_steps: int = 5000,
        save_interval: int = 1,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Integrate Aizawa system trajectory.
        
        Args:
            system: AizawaSystem instance
            n_steps: Number of integration steps
            initial_state: Initial [x, y, z] (default: [0.1, 0, 0])
            transient_steps: Steps to discard for attractor settling
            save_interval: Save state every N steps
            verbose: Print progress information
        
        Returns:
            Dictionary with trajectory and metadata
        """
        if initial_state is None:
            initial_state = np.array([0.1, 0.0, 0.0])
        else:
            initial_state = np.asarray(initial_state, dtype=np.float64)
        
        # Convert to JAX arrays
        jax_state = jnp.array(initial_state)
        jax_params = jnp.array(system.params.to_tuple())
        
        total_steps = n_steps + transient_steps
        
        if verbose:
            print(f"      Integrating {total_steps:,} steps (dt={self.dt})")
            print(f"      JAX backend: {self.backend}")
            print(f"      Devices: {self.devices}")
        
        # Warmup JIT compilation
        if verbose:
            print("      Compiling JAX kernels...")
        _ = _integrate_trajectory(100, self.dt, jax_state, jax_params)
        jax.block_until_ready(_)
        
        # Main integration
        if verbose:
            print("      Running integration...")
        
        trajectory = _integrate_trajectory(total_steps, self.dt, jax_state, jax_params)
        jax.block_until_ready(trajectory)
        
        # Remove transient and apply save interval
        trajectory = trajectory[transient_steps::save_interval]
        
        # Convert to numpy
        trajectory_np = np.array(trajectory)
        
        # Generate time array
        n_saved = len(trajectory_np)
        time_array = np.arange(n_saved) * self.dt * save_interval
        
        if verbose:
            print(f"      ✓ Integration complete: {n_saved:,} points saved")
        
        # Compute attractor bounds
        mins = np.min(trajectory_np, axis=0)
        maxs = np.max(trajectory_np, axis=0)
        means = np.mean(trajectory_np, axis=0)
        stds = np.std(trajectory_np, axis=0)
        
        return {
            'trajectory': trajectory_np,
            'time': time_array,
            'x': trajectory_np[:, 0],
            'y': trajectory_np[:, 1],
            'z': trajectory_np[:, 2],
            'system': system,
            'dt': self.dt,
            'n_steps': n_steps,
            'transient_steps': transient_steps,
            'save_interval': save_interval,
            'initial_state': initial_state,
            'bounds': {
                'x_min': float(mins[0]), 'x_max': float(maxs[0]),
                'y_min': float(mins[1]), 'y_max': float(maxs[1]),
                'z_min': float(mins[2]), 'z_max': float(maxs[2]),
            },
            'statistics': {
                'x_mean': float(means[0]), 'x_std': float(stds[0]),
                'y_mean': float(means[1]), 'y_std': float(stds[1]),
                'z_mean': float(means[2]), 'z_std': float(stds[2]),
            },
            'backend': self.backend,
        }
    
    def solve_batch(
        self,
        system: AizawaSystem,
        n_steps: int = 80000,
        initial_conditions: Optional[List[np.ndarray]] = None,
        transient_steps: int = 5000,
        save_interval: int = 1,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Integrate multiple trajectories in parallel.
        
        Args:
            system: AizawaSystem instance
            n_steps: Number of integration steps
            initial_conditions: List of initial states
            transient_steps: Steps to discard
            save_interval: Save interval
            verbose: Print progress
        
        Returns:
            Dictionary with trajectories and metadata
        """
        if initial_conditions is None:
            initial_conditions = system.get_default_initial_conditions()
        
        # Convert to JAX array
        jax_ics = jnp.array([np.asarray(ic) for ic in initial_conditions])
        jax_params = jnp.array(system.params.to_tuple())
        
        total_steps = n_steps + transient_steps
        n_traj = len(initial_conditions)
        
        if verbose:
            print(f"      Integrating {n_traj} trajectories × {total_steps:,} steps")
            print(f"      JAX backend: {self.backend}")
        
        # Warmup
        if verbose:
            print("      Compiling batch kernels...")
        _ = _integrate_batch(100, self.dt, jax_ics, jax_params)
        jax.block_until_ready(_)
        
        # Batch integration
        if verbose:
            print("      Running batch integration...")
        
        trajectories = _integrate_batch(total_steps, self.dt, jax_ics, jax_params)
        jax.block_until_ready(trajectories)
        
        # Remove transient and apply save interval
        trajectories = trajectories[:, transient_steps::save_interval, :]
        
        # Convert to numpy
        trajectories_np = np.array(trajectories)
        
        n_saved = trajectories_np.shape[1]
        time_array = np.arange(n_saved) * self.dt * save_interval
        
        if verbose:
            print(f"      ✓ Batch integration complete: {n_traj} × {n_saved:,} points")
        
        return {
            'trajectories': trajectories_np,
            'time': time_array,
            'n_trajectories': n_traj,
            'system': system,
            'dt': self.dt,
            'n_steps': n_steps,
            'initial_conditions': initial_conditions,
            'backend': self.backend,
        }
    
    def solve_with_lyapunov(
        self,
        system: AizawaSystem,
        n_steps: int = 50000,
        initial_state: Optional[np.ndarray] = None,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Integrate with Jacobian tracking for Lyapunov exponents.
        
        Args:
            system: AizawaSystem instance
            n_steps: Number of steps
            initial_state: Initial state
            verbose: Print progress
        
        Returns:
            Dictionary with trajectory and Lyapunov data
        """
        if initial_state is None:
            initial_state = np.array([0.1, 0.0, 0.0])
        
        jax_state = jnp.array(initial_state)
        jax_params = jnp.array(system.params.to_tuple())
        
        if verbose:
            print(f"      Computing Lyapunov exponents ({n_steps:,} steps)...")
        
        # Warmup
        _ = _integrate_with_jacobian(100, self.dt, jax_state, jax_params)
        jax.block_until_ready(_)
        
        # Integration with Jacobian
        trajectory, log_diags = _integrate_with_jacobian(
            n_steps, self.dt, jax_state, jax_params
        )
        jax.block_until_ready(trajectory)
        jax.block_until_ready(log_diags)
        
        trajectory_np = np.array(trajectory)
        log_diags_np = np.array(log_diags)
        
        if verbose:
            print(f"      ✓ Lyapunov integration complete")
        
        return {
            'trajectory': trajectory_np,
            'log_diags': log_diags_np,
            'system': system,
            'dt': self.dt,
            'n_steps': n_steps,
        }
