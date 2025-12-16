"""Comprehensive simulation logger for Aizawa attractor analysis."""

import logging
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


class SimulationLogger:
    """Logger for Aizawa simulations with detailed diagnostics."""
    
    def __init__(
        self,
        scenario_name: str,
        log_dir: str = "logs",
        verbose: bool = True
    ):
        """
        Initialize simulation logger.
        
        Args:
            scenario_name: Scenario name (for log filename)
            log_dir: Directory for log files
            verbose: Print messages to console
        """
        self.scenario_name = scenario_name
        self.log_dir = Path(log_dir)
        self.verbose = verbose
        
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / f"{scenario_name}.log"
        
        self.logger = self._setup_logger()
        self.warnings: List[str] = []
        self.errors: List[str] = []
    
    def _setup_logger(self) -> logging.Logger:
        """Configure Python logging."""
        logger = logging.getLogger(f"pattingalloang_{self.scenario_name}")
        logger.setLevel(logging.DEBUG)
        logger.handlers = []
        
        handler = logging.FileHandler(self.log_file, mode='w')
        handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        return logger
    
    def info(self, msg: str):
        """Log informational message."""
        self.logger.info(msg)
    
    def warning(self, msg: str):
        """Log warning message."""
        self.logger.warning(msg)
        self.warnings.append(msg)
        
        if self.verbose:
            print(f"  WARNING: {msg}")
    
    def error(self, msg: str):
        """Log error message."""
        self.logger.error(msg)
        self.errors.append(msg)
        
        if self.verbose:
            print(f"  ERROR: {msg}")
    
    def log_parameters(self, config: Dict[str, Any]):
        """Log all simulation parameters."""
        self.info("=" * 70)
        self.info("AIZAWA ATTRACTOR SIMULATION")
        self.info(f"Scenario: {config.get('scenario_name', 'Unknown')}")
        self.info("=" * 70)
        self.info("")
        
        self.info("SYSTEM PARAMETERS:")
        self.info(f"  a = {config.get('a', 0.95)}")
        self.info(f"  b = {config.get('b', 0.7)}")
        self.info(f"  c = {config.get('c', 0.6)}")
        self.info(f"  d = {config.get('d', 3.5)}")
        self.info(f"  e = {config.get('e', 0.25)}")
        self.info(f"  f = {config.get('f', 0.1)}")
        
        self.info("")
        self.info("SIMULATION PARAMETERS:")
        self.info(f"  dt = {config.get('dt', 0.01)}")
        self.info(f"  n_steps = {config.get('n_steps', 80000)}")
        self.info(f"  transient_steps = {config.get('transient_steps', 5000)}")
        self.info(f"  use_gpu = {config.get('use_gpu', False)}")
        
        self.info("")
        self.info("INITIAL CONDITIONS:")
        self.info(f"  x0 = {config.get('initial_x', 0.1)}")
        self.info(f"  y0 = {config.get('initial_y', 0.0)}")
        self.info(f"  z0 = {config.get('initial_z', 0.0)}")
        
        self.info("=" * 70)
        self.info("")
    
    def log_results(self, result: Dict[str, Any]):
        """Log simulation results."""
        self.info("=" * 70)
        self.info("SIMULATION RESULTS:")
        self.info("=" * 70)
        self.info("")
        
        self.info(f"Trajectory points: {len(result['time'])}")
        self.info(f"Backend: {result.get('backend', 'unknown')}")
        
        bounds = result.get('bounds', {})
        if bounds:
            self.info("")
            self.info("ATTRACTOR BOUNDS:")
            self.info(f"  x: [{bounds.get('x_min', 0):.4f}, {bounds.get('x_max', 0):.4f}]")
            self.info(f"  y: [{bounds.get('y_min', 0):.4f}, {bounds.get('y_max', 0):.4f}]")
            self.info(f"  z: [{bounds.get('z_min', 0):.4f}, {bounds.get('z_max', 0):.4f}]")
        
        self.info("=" * 70)
        self.info("")
    
    def log_metrics(self, metrics: Dict[str, Any]):
        """Log chaos metrics."""
        self.info("=" * 70)
        self.info("CHAOS METRICS:")
        self.info("=" * 70)
        self.info("")
        
        # Lyapunov exponents
        if 'lyapunov_1' in metrics:
            self.info("LYAPUNOV EXPONENTS:")
            self.info(f"  λ₁ = {metrics['lyapunov_1']:.6f}")
            self.info(f"  λ₂ = {metrics['lyapunov_2']:.6f}")
            self.info(f"  λ₃ = {metrics['lyapunov_3']:.6f}")
            self.info(f"  Sum = {metrics.get('lyapunov_sum', 0):.6f}")
            self.info("")
            
            self.info("DERIVED DIMENSIONS:")
            self.info(f"  Kaplan-Yorke dimension = {metrics.get('kaplan_yorke_dim', 0):.4f}")
            self.info(f"  KS entropy = {metrics.get('ks_entropy', 0):.6f}")
            self.info(f"  Is chaotic = {metrics.get('is_chaotic', False)}")
        
        if 'correlation_dim' in metrics:
            self.info("")
            self.info("CORRELATION DIMENSION:")
            self.info(f"  D₂ = {metrics['correlation_dim']:.4f}")
            self.info(f"  R² = {metrics.get('correlation_dim_r2', 0):.4f}")
        
        if 'rqa_recurrence_rate' in metrics:
            self.info("")
            self.info("RECURRENCE QUANTIFICATION:")
            self.info(f"  Recurrence rate = {metrics['rqa_recurrence_rate']:.4f}")
            self.info(f"  Determinism = {metrics.get('rqa_determinism', 0):.4f}")
        
        self.info("=" * 70)
        self.info("")
    
    def log_timing(self, timing: Dict[str, float]):
        """Log timing breakdown."""
        self.info("=" * 70)
        self.info("TIMING BREAKDOWN:")
        self.info("=" * 70)
        
        for key, value in sorted(timing.items()):
            if key != 'total':
                self.info(f"  {key}: {value:.3f} s")
        
        self.info(f"  {'-' * 40}")
        total_time = timing.get('total', sum(timing.values()))
        self.info(f"  TOTAL: {total_time:.3f} s")
        
        self.info("=" * 70)
        self.info("")
    
    def finalize(self):
        """Write final summary."""
        self.info("=" * 70)
        self.info("SIMULATION SUMMARY:")
        self.info("=" * 70)
        self.info("")
        
        if self.errors:
            self.info(f"ERRORS: {len(self.errors)}")
            for i, err in enumerate(self.errors, 1):
                self.info(f"  {i}. {err}")
        else:
            self.info("ERRORS: None")
        
        self.info("")
        
        if self.warnings:
            self.info(f"WARNINGS: {len(self.warnings)}")
            for i, warn in enumerate(self.warnings, 1):
                self.info(f"  {i}. {warn}")
        else:
            self.info("WARNINGS: None")
        
        self.info("")
        self.info(f"Log file: {self.log_file}")
        self.info("=" * 70)
        self.info(f"Simulation completed: {self.scenario_name}")
        self.info(f"Timestamp: {datetime.now().isoformat()}")
        self.info("=" * 70)
