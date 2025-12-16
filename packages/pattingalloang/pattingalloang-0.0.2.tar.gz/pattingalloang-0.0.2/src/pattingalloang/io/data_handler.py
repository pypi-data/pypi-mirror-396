"""Data handler for saving Aizawa attractor results to CSV and NetCDF."""

import numpy as np
import pandas as pd
from netCDF4 import Dataset
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class DataHandler:
    """Handle saving simulation data to various formats."""
    
    @staticmethod
    def save_trajectory_csv(filepath: str, result: Dict[str, Any]):
        """
        Save trajectory to CSV.
        
        Args:
            filepath: Output file path
            result: Simulation result dictionary
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        df = pd.DataFrame({
            'time': result['time'],
            'x': result['x'],
            'y': result['y'],
            'z': result['z'],
        })
        
        df.to_csv(filepath, index=False, float_format='%.8e')
    
    @staticmethod
    def save_metrics_csv(filepath: str, metrics: Dict[str, Any]):
        """
        Save chaos metrics to CSV.
        
        Args:
            filepath: Output file path
            metrics: Metrics dictionary
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Filter to scalar values only
        scalar_metrics = {k: v for k, v in metrics.items() 
                        if isinstance(v, (int, float, bool, str))}
        
        rows = []
        for key, value in sorted(scalar_metrics.items()):
            rows.append({
                'Metric': key,
                'Value': value,
            })
        
        df = pd.DataFrame(rows)
        df.to_csv(filepath, index=False)
    
    @staticmethod
    def save_lyapunov_timeseries_csv(
        filepath: str,
        time_array: np.ndarray,
        lyap_array: np.ndarray
    ):
        """
        Save Lyapunov exponent time series to CSV.
        
        Args:
            filepath: Output file path
            time_array: Time values
            lyap_array: Lyapunov values (n, 3)
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        df = pd.DataFrame({
            'time': time_array,
            'lambda_1': lyap_array[:, 0],
            'lambda_2': lyap_array[:, 1],
            'lambda_3': lyap_array[:, 2],
        })
        
        df.to_csv(filepath, index=False, float_format='%.8e')
    
    @staticmethod
    def save_netcdf(
        filepath: str,
        result: Dict[str, Any],
        config: Dict[str, Any],
        metrics: Optional[Dict[str, Any]] = None
    ):
        """
        Save complete simulation data to NetCDF format.
        
        Creates a CF-compliant NetCDF file with trajectory,
        parameters, and metrics.
        
        Args:
            filepath: Output file path
            result: Simulation result dictionary
            config: Configuration dictionary
            metrics: Optional metrics dictionary
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        trajectory = result['trajectory']
        time_array = result['time']
        n_time = len(time_array)
        
        with Dataset(filepath, 'w', format='NETCDF4') as nc:
            # Dimensions
            nc.createDimension('time', n_time)
            nc.createDimension('spatial', 3)
            
            # Time coordinate
            nc_time = nc.createVariable('time', 'f8', ('time',), zlib=True)
            nc_time[:] = time_array
            nc_time.units = "simulation_time_units"
            nc_time.long_name = "simulation_time"
            nc_time.axis = "T"
            nc_time.standard_name = "time"
            
            # Full trajectory
            nc_traj = nc.createVariable(
                'trajectory', 'f8', ('time', 'spatial'), zlib=True
            )
            nc_traj[:] = trajectory
            nc_traj.units = "dimensionless"
            nc_traj.long_name = "phase_space_trajectory"
            nc_traj.coordinates = "time spatial"
            
            # Individual coordinates
            nc_x = nc.createVariable('x', 'f8', ('time',), zlib=True)
            nc_x[:] = trajectory[:, 0]
            nc_x.units = "dimensionless"
            nc_x.long_name = "x_coordinate"
            nc_x.standard_name = "projection_x_coordinate"
            
            nc_y = nc.createVariable('y', 'f8', ('time',), zlib=True)
            nc_y[:] = trajectory[:, 1]
            nc_y.units = "dimensionless"
            nc_y.long_name = "y_coordinate"
            nc_y.standard_name = "projection_y_coordinate"
            
            nc_z = nc.createVariable('z', 'f8', ('time',), zlib=True)
            nc_z[:] = trajectory[:, 2]
            nc_z.units = "dimensionless"
            nc_z.long_name = "z_coordinate"
            
            # Add chaos metrics if provided
            if metrics is not None:
                # Scalar metrics as attributes or variables
                for key, value in metrics.items():
                    if isinstance(value, (int, float)):
                        nc.setncattr(f'metric_{key}', float(value))
                    elif isinstance(value, bool):
                        nc.setncattr(f'metric_{key}', int(value))
            
            # Global attributes - System parameters
            system = result.get('system')
            if system is not None:
                nc.param_a = float(system.a)
                nc.param_b = float(system.b)
                nc.param_c = float(system.c)
                nc.param_d = float(system.d)
                nc.param_e = float(system.e)
                nc.param_f = float(system.f)
            else:
                nc.param_a = float(config.get('a', 0.95))
                nc.param_b = float(config.get('b', 0.7))
                nc.param_c = float(config.get('c', 0.6))
                nc.param_d = float(config.get('d', 3.5))
                nc.param_e = float(config.get('e', 0.25))
                nc.param_f = float(config.get('f', 0.1))
            
            # Simulation parameters
            nc.dt = float(result.get('dt', config.get('dt', 0.01)))
            nc.n_steps = int(result.get('n_steps', config.get('n_steps', 80000)))
            nc.transient_steps = int(config.get('transient_steps', 5000))
            
            # Initial conditions
            initial = result.get('initial_state', [0.1, 0.0, 0.0])
            nc.initial_x = float(initial[0])
            nc.initial_y = float(initial[1])
            nc.initial_z = float(initial[2])
            
            # Statistics
            bounds = result.get('bounds', {})
            for key, value in bounds.items():
                nc.setncattr(f'bounds_{key}', float(value))
            
            stats = result.get('statistics', {})
            for key, value in stats.items():
                nc.setncattr(f'stats_{key}', float(value))
            
            # CF metadata
            nc.title = "Aizawa Attractor Simulation"
            nc.scenario_name = config.get('scenario_name', 'unknown')
            nc.institution = "pattingalloang"
            nc.source = "pattingalloang v0.1.0"
            nc.history = f"Created {datetime.now().isoformat()}"
            nc.Conventions = "CF-1.8"
            nc.references = "Aizawa, Y. (1982). Global aspects of dissipative dynamical systems."
            
            # Author info
            nc.author = "Sandy H. S. Herho"
            nc.email = "sandy.herho@email.ucr.edu"
            nc.license = "MIT"
    
    @staticmethod
    def save_multi_trajectory_netcdf(
        filepath: str,
        result: Dict[str, Any],
        config: Dict[str, Any]
    ):
        """
        Save multiple trajectories to NetCDF.
        
        Args:
            filepath: Output file path
            result: Batch result dictionary
            config: Configuration dictionary
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        trajectories = result['trajectories']
        time_array = result['time']
        n_traj = result['n_trajectories']
        n_time = len(time_array)
        
        with Dataset(filepath, 'w', format='NETCDF4') as nc:
            # Dimensions
            nc.createDimension('time', n_time)
            nc.createDimension('trajectory_id', n_traj)
            nc.createDimension('spatial', 3)
            
            # Time coordinate
            nc_time = nc.createVariable('time', 'f8', ('time',), zlib=True)
            nc_time[:] = time_array
            nc_time.units = "simulation_time_units"
            nc_time.long_name = "simulation_time"
            
            # Trajectory ID
            nc_traj_id = nc.createVariable('trajectory_id', 'i4', ('trajectory_id',), zlib=True)
            nc_traj_id[:] = np.arange(n_traj)
            nc_traj_id.long_name = "trajectory_index"
            
            # All trajectories
            nc_trajs = nc.createVariable(
                'trajectories', 'f8', ('trajectory_id', 'time', 'spatial'), zlib=True
            )
            nc_trajs[:] = trajectories
            nc_trajs.units = "dimensionless"
            nc_trajs.long_name = "phase_space_trajectories"
            
            # Individual coordinates for each trajectory
            nc_x = nc.createVariable('x', 'f8', ('trajectory_id', 'time'), zlib=True)
            nc_x[:] = trajectories[:, :, 0]
            nc_x.long_name = "x_coordinates"
            
            nc_y = nc.createVariable('y', 'f8', ('trajectory_id', 'time'), zlib=True)
            nc_y[:] = trajectories[:, :, 1]
            nc_y.long_name = "y_coordinates"
            
            nc_z = nc.createVariable('z', 'f8', ('trajectory_id', 'time'), zlib=True)
            nc_z[:] = trajectories[:, :, 2]
            nc_z.long_name = "z_coordinates"
            
            # Metadata
            nc.title = "Aizawa Attractor Multi-Trajectory Simulation"
            nc.n_trajectories = n_traj
            nc.Conventions = "CF-1.8"
            nc.history = f"Created {datetime.now().isoformat()}"
            nc.author = "Sandy H. S. Herho"
            nc.license = "MIT"
