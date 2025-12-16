"""
Aizawa Attractor System Definition.

The Aizawa attractor is a three-dimensional chaotic dynamical system
discovered by Yoji Aizawa, exhibiting beautiful butterfly-like structures.

Governing equations:
    dx/dt = (z - b)x - dy
    dy/dt = dx + (z - b)y
    dz/dt = c + az - z³/3 - (x² + y²)(1 + ez) + fzx³

References:
    Aizawa, Y. (1982). Global aspects of the dissipative dynamical systems.
    Sprott, J. C. (2010). Elegant Chaos: Algebraically Simple Chaotic Flows.
"""

import numpy as np
from typing import Tuple, Optional, Union, List
from dataclasses import dataclass


@dataclass
class AizawaParams:
    """Container for Aizawa attractor parameters."""
    a: float = 0.95
    b: float = 0.7
    c: float = 0.6
    d: float = 3.5
    e: float = 0.25
    f: float = 0.1
    
    def to_tuple(self) -> Tuple[float, ...]:
        """Convert to tuple for JAX compatibility."""
        return (self.a, self.b, self.c, self.d, self.e, self.f)
    
    def to_array(self) -> np.ndarray:
        """Convert to numpy array."""
        return np.array([self.a, self.b, self.c, self.d, self.e, self.f])


class AizawaSystem:
    """
    Aizawa Strange Attractor System.
    
    A three-dimensional chaotic dynamical system with rich structure
    and beautiful butterfly-like geometry.
    
    Attributes:
        params: AizawaParams containing system parameters
        a, b, c, d, e, f: Individual parameter accessors
    
    Example:
        >>> system = AizawaSystem(a=0.95, b=0.7, c=0.6, d=3.5, e=0.25, f=0.1)
        >>> print(system)
        AizawaSystem(a=0.95, b=0.70, c=0.60, d=3.50, e=0.25, f=0.10)
    """
    
    def __init__(
        self,
        a: float = 0.95,
        b: float = 0.7,
        c: float = 0.6,
        d: float = 3.5,
        e: float = 0.25,
        f: float = 0.1,
    ):
        """
        Initialize Aizawa system with parameters.
        
        Args:
            a: Linear growth rate in z equation (default: 0.95)
            b: Offset parameter for x,y coupling (default: 0.7)
            c: Constant forcing term (default: 0.6)
            d: Rotation coupling strength (default: 3.5)
            e: Nonlinear coupling coefficient (default: 0.25)
            f: Cubic coupling coefficient (default: 0.1)
        """
        self.params = AizawaParams(a=a, b=b, c=c, d=d, e=e, f=f)
    
    @property
    def a(self) -> float:
        return self.params.a
    
    @property
    def b(self) -> float:
        return self.params.b
    
    @property
    def c(self) -> float:
        return self.params.c
    
    @property
    def d(self) -> float:
        return self.params.d
    
    @property
    def e(self) -> float:
        return self.params.e
    
    @property
    def f(self) -> float:
        return self.params.f
    
    def derivatives(self, state: np.ndarray) -> np.ndarray:
        """
        Compute derivatives at given state (NumPy version).
        
        Args:
            state: Array [x, y, z]
        
        Returns:
            Array [dx/dt, dy/dt, dz/dt]
        """
        x, y, z = state
        a, b, c, d, e, f = self.params.to_tuple()
        
        dx = (z - b) * x - d * y
        dy = d * x + (z - b) * y
        dz = c + a * z - (z**3 / 3) - (x**2 + y**2) * (1 + e * z) + f * z * x**3
        
        return np.array([dx, dy, dz])
    
    def jacobian(self, state: np.ndarray) -> np.ndarray:
        """
        Compute Jacobian matrix at given state.
        
        Args:
            state: Array [x, y, z]
        
        Returns:
            3x3 Jacobian matrix
        """
        x, y, z = state
        a, b, c, d, e, f = self.params.to_tuple()
        
        J = np.array([
            [z - b, -d, x],
            [d, z - b, y],
            [-2*x*(1 + e*z) + 3*f*z*x**2, -2*y*(1 + e*z), 
             a - z**2 - e*(x**2 + y**2) + f*x**3]
        ])
        return J
    
    def get_default_initial_conditions(self) -> List[np.ndarray]:
        """
        Get standard initial conditions for visualization.
        
        Returns:
            List of initial state arrays
        """
        return [
            np.array([0.1, 0.0, 0.0]),
            np.array([0.1, 0.1, 0.0]),
            np.array([-0.1, 0.0, 0.1]),
            np.array([0.0, 0.1, 0.1]),
        ]
    
    def __repr__(self) -> str:
        return (
            f"AizawaSystem(a={self.a:.2f}, b={self.b:.2f}, c={self.c:.2f}, "
            f"d={self.d:.2f}, e={self.e:.2f}, f={self.f:.2f})"
        )
    
    def __str__(self) -> str:
        return self.__repr__()
    
    def describe(self) -> str:
        """Return detailed description of the system."""
        return f"""
Aizawa Strange Attractor
========================
Parameters:
  a = {self.a:.4f}  (linear growth rate)
  b = {self.b:.4f}  (offset parameter)
  c = {self.c:.4f}  (constant forcing)
  d = {self.d:.4f}  (rotation coupling)
  e = {self.e:.4f}  (nonlinear coupling)
  f = {self.f:.4f}  (cubic coupling)

Equations:
  dx/dt = (z - b)x - dy
  dy/dt = dx + (z - b)y
  dz/dt = c + az - z³/3 - (x² + y²)(1 + ez) + fzx³
"""
