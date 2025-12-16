#!/usr/bin/env python
"""
Command Line Interface for pattingalloang Aizawa Attractor Analyzer.

Usage:
    pattingalloang case1              # Standard attractor
    pattingalloang case2              # High resolution
    pattingalloang case3              # Long trajectory
    pattingalloang case4              # Parameter variation
    pattingalloang case5              # Multi-trajectory
    pattingalloang case6              # Butterfly wings
    pattingalloang case7              # Chaotic spiral
    pattingalloang --all              # Run all cases
    pattingalloang case1 --gpu        # Use GPU acceleration
    pattingalloang --config path.txt  # Custom config
"""

import argparse
import sys
from pathlib import Path
import numpy as np

from .core.attractor import AizawaSystem
from .core.integrator import AizawaSolver
from .core.metrics import compute_all_metrics, compute_lyapunov_spectrum_timeseries
from .io.config_manager import ConfigManager
from .io.data_handler import DataHandler
from .visualization.animator import Animator
from .utils.logger import SimulationLogger
from .utils.timer import Timer


def print_header():
    """Print ASCII art header."""
    print("\n" + "=" * 70)
    print(" " * 15 + "pattingalloang: Aizawa Attractor Analyzer")
    print(" " * 25 + "Version 0.0.2")
    print("=" * 70)
    print("\n  JAX-Accelerated Chaotic Dynamics Analysis")
    print("  Lyapunov Exponents | Fractal Dimensions | Strange Attractors")
    print("  License: MIT")
    print("=" * 70 + "\n")


def normalize_scenario_name(scenario_name: str) -> str:
    """Convert scenario name to clean filename format."""
    clean = scenario_name.lower()
    clean = clean.replace(' - ', '_')
    clean = clean.replace('-', '_')
    clean = clean.replace(' ', '_')
    
    while '__' in clean:
        clean = clean.replace('__', '_')
    
    if clean.startswith('case_'):
        parts = clean.split('_')
        if len(parts) >= 2 and parts[1].isdigit():
            case_num = parts[1]
            rest = '_'.join(parts[2:])
            clean = f"case{case_num}_{rest}"
    
    clean = clean.rstrip('_')
    return clean


def run_scenario(
    config: dict,
    output_dir: str = "outputs",
    verbose: bool = True,
    use_gpu: bool = False
):
    """Run a complete Aizawa attractor simulation scenario."""
    
    scenario_name = config.get('scenario_name', 'simulation')
    clean_name = normalize_scenario_name(scenario_name)
    
    # Override GPU setting from command line
    if use_gpu:
        config['use_gpu'] = True
    
    if verbose:
        print(f"\n{'=' * 70}")
        print(f"SCENARIO: {scenario_name}")
        print(f"{'=' * 70}")
    
    logger = SimulationLogger(clean_name, "logs", verbose)
    timer = Timer()
    timer.start("total")
    
    try:
        logger.log_parameters(config)
        
        # [1/8] Initialize system
        with timer.time_section("system_init"):
            if verbose:
                print("\n[1/8] Initializing Aizawa system...")
            
            system = AizawaSystem(
                a=config.get('a', 0.95),
                b=config.get('b', 0.7),
                c=config.get('c', 0.6),
                d=config.get('d', 3.5),
                e=config.get('e', 0.25),
                f=config.get('f', 0.1),
            )
            
            if verbose:
                print(f"      {system}")
        
        # [2/8] Initialize solver
        with timer.time_section("solver_init"):
            if verbose:
                print("\n[2/8] Initializing JAX solver...")
            
            solver = AizawaSolver(
                dt=config.get('dt', 0.01),
                use_gpu=config.get('use_gpu', False)
            )
            
            if verbose:
                print(f"      dt={solver.dt}, Backend={solver.backend}")
        
        # Check if multi-trajectory
        multi_trajectory = config.get('multi_trajectory', False)
        initial_conditions = config.get('initial_conditions', None)
        
        # [3/8] Run simulation
        with timer.time_section("simulation"):
            if verbose:
                print("\n[3/8] Running integration...")
            
            if multi_trajectory and initial_conditions is not None:
                result = solver.solve_batch(
                    system=system,
                    n_steps=config.get('n_steps', 80000),
                    initial_conditions=initial_conditions,
                    transient_steps=config.get('transient_steps', 5000),
                    verbose=verbose
                )
                # Use first trajectory for metrics
                main_traj = result['trajectories'][0]
            else:
                initial_state = np.array([
                    config.get('initial_x', 0.1),
                    config.get('initial_y', 0.0),
                    config.get('initial_z', 0.0),
                ])
                
                result = solver.solve(
                    system=system,
                    n_steps=config.get('n_steps', 80000),
                    initial_state=initial_state,
                    transient_steps=config.get('transient_steps', 5000),
                    verbose=verbose
                )
                main_traj = result['trajectory']
            
            logger.log_results(result)
        
        # [4/8] Compute chaos metrics
        metrics = None
        if config.get('compute_metrics', True):
            with timer.time_section("metrics"):
                if verbose:
                    print("\n[4/8] Computing chaos metrics...")
                
                # Compute Lyapunov exponents via separate integration
                lyap_result = solver.solve_with_lyapunov(
                    system=system,
                    n_steps=min(config.get('n_steps', 80000), 50000),
                    verbose=verbose
                )
                
                # Compute all metrics
                metrics = compute_all_metrics(
                    trajectory=main_traj,
                    time_array=result['time'],
                    params=system.params.to_tuple(),
                    dt=solver.dt,
                    log_diags=lyap_result['log_diags'],
                    verbose=verbose
                )
                
                logger.log_metrics(metrics)
                
                if verbose:
                    print(f"\n      Largest Lyapunov exponent: {metrics.get('lyapunov_1', 0):.4f}")
                    print(f"      Kaplan-Yorke dimension: {metrics.get('kaplan_yorke_dim', 0):.4f}")
                    print(f"      Correlation dimension: {metrics.get('correlation_dim', 0):.4f}")
                    
                    if metrics.get('is_chaotic', False):
                        print(f"      Status: CHAOTIC (λ₁ > 0)")
                    else:
                        print(f"      Status: NON-CHAOTIC")
        else:
            if verbose:
                print("\n[4/8] Skipping chaos metrics (disabled)")
        
        # [5/8] Save CSV data
        if config.get('save_csv', True):
            with timer.time_section("csv_save"):
                if verbose:
                    print("\n[5/8] Saving CSV data...")
                
                csv_dir = Path(output_dir) / "csv"
                csv_dir.mkdir(parents=True, exist_ok=True)
                
                # Trajectory
                if not multi_trajectory:
                    traj_file = csv_dir / f"{clean_name}_trajectory.csv"
                    DataHandler.save_trajectory_csv(traj_file, result)
                    if verbose:
                        print(f"      Saved: {traj_file}")
                
                # Metrics
                if metrics is not None:
                    metrics_file = csv_dir / f"{clean_name}_chaos_metrics.csv"
                    DataHandler.save_metrics_csv(metrics_file, metrics)
                    if verbose:
                        print(f"      Saved: {metrics_file}")
        
        # [6/8] Save NetCDF
        if config.get('save_netcdf', True):
            with timer.time_section("netcdf_save"):
                if verbose:
                    print("\n[6/8] Saving NetCDF data...")
                
                nc_dir = Path(output_dir) / "netcdf"
                nc_dir.mkdir(parents=True, exist_ok=True)
                
                nc_file = nc_dir / f"{clean_name}.nc"
                
                if multi_trajectory:
                    DataHandler.save_multi_trajectory_netcdf(nc_file, result, config)
                else:
                    DataHandler.save_netcdf(nc_file, result, config, metrics)
                
                if verbose:
                    print(f"      Saved: {nc_file}")
        
        # [7/8] Generate visualizations
        with timer.time_section("visualization"):
            if verbose:
                print("\n[7/8] Generating visualizations...")
            
            animator = Animator(
                fps=config.get('animation_fps', 30),
                dpi=config.get('png_dpi', 150)
            )
            
            if config.get('save_png', True):
                with timer.time_section("png_save"):
                    if verbose:
                        print("      Creating static plots...")
                    
                    fig_dir = Path(output_dir) / "figs"
                    fig_dir.mkdir(parents=True, exist_ok=True)
                    
                    png_file = fig_dir / f"{clean_name}_summary.png"
                    animator.create_static_plot(
                        result, png_file, scenario_name, metrics,
                        multi_trajectory=multi_trajectory
                    )
                    
                    if verbose:
                        print(f"      Saved: {png_file}")
            
            if config.get('save_gif', True):
                with timer.time_section("gif_save"):
                    if verbose:
                        print("      Creating animation...")
                    
                    gif_dir = Path(output_dir) / "gifs"
                    gif_dir.mkdir(parents=True, exist_ok=True)
                    
                    gif_file = gif_dir / f"{clean_name}_animation.gif"
                    animator.create_animation(
                        result, gif_file, scenario_name,
                        n_frames=config.get('animation_frames', 180),
                        duration_seconds=config.get('animation_duration', 15.0),
                        multi_trajectory=multi_trajectory
                    )
                    
                    if verbose:
                        print(f"      Saved: {gif_file}")
        
        timer.stop("total")
        logger.log_timing(timer.get_times())
        
        # [8/8] Summary
        sim_time = timer.times.get('simulation', 0)
        metrics_time = timer.times.get('metrics', 0)
        total_time = timer.times.get('total', 0)
        
        if verbose:
            print(f"\n[8/8] SIMULATION COMPLETED")
            print(f"{'=' * 70}")
            
            if metrics is not None:
                print(f"  Lyapunov exponents: [{metrics.get('lyapunov_1', 0):.4f}, "
                      f"{metrics.get('lyapunov_2', 0):.4f}, {metrics.get('lyapunov_3', 0):.4f}]")
                print(f"  Kaplan-Yorke dimension: {metrics.get('kaplan_yorke_dim', 0):.4f}")
                print(f"  Correlation dimension: {metrics.get('correlation_dim', 0):.4f}")
            
            print(f"  Integration time: {sim_time:.2f} s")
            if metrics_time > 0:
                print(f"  Metrics computation: {metrics_time:.2f} s")
            print(f"  Total time: {total_time:.2f} s")
            
            if logger.warnings:
                print(f"  Warnings: {len(logger.warnings)}")
            if logger.errors:
                print(f"  Errors: {len(logger.errors)}")
            
            print(f"{'=' * 70}\n")
    
    except Exception as e:
        logger.error(f"Simulation failed: {str(e)}")
        
        if verbose:
            print(f"\n{'=' * 70}")
            print(f"SIMULATION FAILED")
            print(f"  Error: {str(e)}")
            print(f"{'=' * 70}\n")
        
        raise
    
    finally:
        logger.finalize()


def main():
    """Main entry point for command-line interface."""
    parser = argparse.ArgumentParser(
        description='pattingalloang: Aizawa Attractor Analyzer',
        epilog='Example: pattingalloang case1 --gpu'
    )
    
    parser.add_argument(
        'case',
        nargs='?',
        choices=['case1', 'case2', 'case3', 'case4', 'case5', 'case6', 'case7'],
        help='Test case to run (case1-7)'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Path to custom configuration file'
    )
    
    parser.add_argument(
        '--all', '-a',
        action='store_true',
        help='Run all test cases sequentially'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        default='outputs',
        help='Output directory for results (default: outputs)'
    )
    
    parser.add_argument(
        '--gpu',
        action='store_true',
        help='Use GPU acceleration (requires JAX with CUDA)'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Quiet mode (minimal output)'
    )
    
    parser.add_argument(
        '--no-gif',
        action='store_true',
        help='Skip GIF animation generation'
    )
    
    parser.add_argument(
        '--no-metrics',
        action='store_true',
        help='Skip chaos metrics computation'
    )
    
    args = parser.parse_args()
    verbose = not args.quiet
    
    if verbose:
        print_header()
    
    # Custom config
    if args.config:
        config = ConfigManager.load(args.config)
        if args.no_gif:
            config['save_gif'] = False
        if args.no_metrics:
            config['compute_metrics'] = False
        run_scenario(config, args.output_dir, verbose, args.gpu)
    
    # All cases
    elif args.all:
        configs_dir = Path(__file__).parent.parent.parent / 'configs'
        
        # Try installed package location
        if not configs_dir.exists():
            configs_dir = Path(__file__).parent.parent.parent.parent / 'configs'
        
        config_files = sorted(configs_dir.glob('case*.txt'))
        
        if not config_files:
            print("ERROR: No configuration files found in configs/")
            print(f"Searched in: {configs_dir}")
            sys.exit(1)
        
        for i, cfg_file in enumerate(config_files, 1):
            if verbose:
                print(f"\n[Case {i}/{len(config_files)}] Running {cfg_file.stem}...")
            
            config = ConfigManager.load(str(cfg_file))
            if args.no_gif:
                config['save_gif'] = False
            if args.no_metrics:
                config['compute_metrics'] = False
            run_scenario(config, args.output_dir, verbose, args.gpu)
    
    # Single case
    elif args.case:
        case_map = {
            'case1': 'case1_standard',
            'case2': 'case2_high_resolution',
            'case3': 'case3_long_trajectory',
            'case4': 'case4_parameter_variation',
            'case5': 'case5_multi_trajectory',
            'case6': 'case6_butterfly_wings',
            'case7': 'case7_chaotic_spiral',
        }
        
        cfg_name = case_map[args.case]
        
        # Search for config in various locations
        search_paths = [
            Path(__file__).parent.parent.parent / 'configs',
            Path(__file__).parent.parent.parent.parent / 'configs',
            Path.cwd() / 'configs',
        ]
        
        cfg_file = None
        for search_path in search_paths:
            potential_file = search_path / f'{cfg_name}.txt'
            if potential_file.exists():
                cfg_file = potential_file
                break
        
        if cfg_file is not None:
            config = ConfigManager.load(str(cfg_file))
            if args.no_gif:
                config['save_gif'] = False
            if args.no_metrics:
                config['compute_metrics'] = False
            run_scenario(config, args.output_dir, verbose, args.gpu)
        else:
            print(f"ERROR: Configuration file not found: {cfg_name}.txt")
            print(f"Searched in: {[str(p) for p in search_paths]}")
            sys.exit(1)
    
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == '__main__':
    main()
