"""
Comprehensive Chaos Metrics for Aizawa Attractor Analysis.

Implements rigorous measures for quantifying chaotic dynamics:
    - Lyapunov Exponents (full spectrum via QR method)
    - Kaplan-Yorke / Lyapunov Dimension
    - Correlation Dimension (Grassberger-Procaccia)
    - Kolmogorov-Sinai Entropy
    - Recurrence Quantification Analysis
    - Average Mutual Information
    - Embedding Dimension Estimation

References:
    Kantz, H., & Schreiber, T. (2004). Nonlinear Time Series Analysis.
    Ott, E. (2002). Chaos in Dynamical Systems.
    Sprott, J. C. (2003). Chaos and Time-Series Analysis.
"""

import numpy as np
from typing import Dict, Tuple, Optional, List
from scipy.spatial import cKDTree
from scipy.stats import entropy as scipy_entropy
from tqdm import tqdm


def compute_lyapunov_exponents(
    log_diags: np.ndarray,
    dt: float,
    transient_fraction: float = 0.2
) -> np.ndarray:
    """
    Compute Lyapunov exponents from QR decomposition log diagonals.
    
    The Lyapunov exponents characterize the average exponential rates
    of divergence or convergence of nearby trajectories.
    
    Args:
        log_diags: Array of log(|R_ii|) from QR decomposition (n_steps, 3)
        dt: Integration time step
        transient_fraction: Fraction of initial data to discard
    
    Returns:
        Array of 3 Lyapunov exponents in descending order
    """
    n_steps = len(log_diags)
    transient = int(n_steps * transient_fraction)
    
    # Use only post-transient data
    log_diags_steady = log_diags[transient:]
    total_time = len(log_diags_steady) * dt
    
    if total_time == 0:
        return np.array([np.nan, np.nan, np.nan])
    
    # Sum log values and divide by time
    lyapunov = np.sum(log_diags_steady, axis=0) / total_time
    
    # Sort in descending order
    return np.sort(lyapunov)[::-1]


def compute_lyapunov_spectrum_timeseries(
    log_diags: np.ndarray,
    dt: float,
    window_size: int = 1000
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute running Lyapunov exponents over time.
    
    Args:
        log_diags: Array of log diagonals
        dt: Time step
        window_size: Rolling window size
    
    Returns:
        Tuple of (time_array, lyapunov_array) where lyapunov_array is (n, 3)
    """
    n_steps = len(log_diags)
    n_windows = n_steps - window_size + 1
    
    if n_windows <= 0:
        return np.array([0.0]), np.zeros((1, 3))
    
    lyap_series = np.zeros((n_windows, 3))
    time_series = np.zeros(n_windows)
    
    for i in range(n_windows):
        window = log_diags[i:i+window_size]
        lyap_series[i] = np.sum(window, axis=0) / (window_size * dt)
        time_series[i] = (i + window_size // 2) * dt
    
    # Sort each row in descending order
    lyap_series = -np.sort(-lyap_series, axis=1)
    
    return time_series, lyap_series


def compute_kaplan_yorke_dimension(lyapunov_exponents: np.ndarray) -> float:
    """
    Compute Kaplan-Yorke (Lyapunov) dimension.
    
    D_KY = j + (λ₁ + λ₂ + ... + λⱼ) / |λⱼ₊₁|
    
    where j is the largest index for which the sum is non-negative.
    
    Args:
        lyapunov_exponents: Array of Lyapunov exponents (descending order)
    
    Returns:
        Kaplan-Yorke dimension
    """
    lyap = np.sort(lyapunov_exponents)[::-1]
    
    cumsum = 0.0
    j = 0
    
    for i, le in enumerate(lyap):
        if cumsum + le >= 0:
            cumsum += le
            j = i
        else:
            break
    
    # Compute dimension
    if j < len(lyap) - 1 and abs(lyap[j + 1]) > 1e-10:
        d_ky = (j + 1) + cumsum / abs(lyap[j + 1])
    else:
        d_ky = j + 1
    
    return float(d_ky)


def compute_kolmogorov_sinai_entropy(lyapunov_exponents: np.ndarray) -> float:
    """
    Compute Kolmogorov-Sinai entropy from Lyapunov exponents.
    
    The KS entropy is the sum of positive Lyapunov exponents,
    representing the rate of information production.
    
    h_KS = Σ λᵢ for λᵢ > 0
    
    Args:
        lyapunov_exponents: Array of Lyapunov exponents
    
    Returns:
        Kolmogorov-Sinai entropy
    """
    positive_exponents = lyapunov_exponents[lyapunov_exponents > 0]
    return float(np.sum(positive_exponents))


def compute_correlation_dimension(
    trajectory: np.ndarray,
    n_samples: int = 5000,
    r_min_percentile: float = 1.0,
    r_max_percentile: float = 30.0,
    n_r_values: int = 20
) -> Tuple[float, float, np.ndarray, np.ndarray]:
    """
    Estimate correlation dimension using Grassberger-Procaccia algorithm.
    
    The correlation dimension D₂ is estimated from the scaling:
    C(r) ~ r^D₂ as r → 0
    
    Args:
        trajectory: Trajectory array (n_points, 3)
        n_samples: Number of reference points to use
        r_min_percentile: Percentile for minimum r
        r_max_percentile: Percentile for maximum r
        n_r_values: Number of r values for scaling analysis
    
    Returns:
        Tuple of (dimension, r_squared, r_values, C_values)
    """
    n_points = len(trajectory)
    
    # Subsample for computational efficiency
    if n_points > n_samples:
        indices = np.random.choice(n_points, n_samples, replace=False)
        sample = trajectory[indices]
    else:
        sample = trajectory
    
    n = len(sample)
    
    # Compute pairwise distances using vectorized operations
    diff = sample[:, np.newaxis, :] - sample[np.newaxis, :, :]
    distances = np.sqrt(np.sum(diff**2, axis=-1))
    
    # Get upper triangle (unique pairs)
    upper_indices = np.triu_indices(n, k=1)
    unique_distances = distances[upper_indices]
    unique_distances = unique_distances[unique_distances > 0]
    
    if len(unique_distances) < 100:
        return np.nan, np.nan, np.array([]), np.array([])
    
    # Determine r range
    r_min = np.percentile(unique_distances, r_min_percentile)
    r_max = np.percentile(unique_distances, r_max_percentile)
    
    if r_min <= 0 or r_max <= r_min:
        return np.nan, np.nan, np.array([]), np.array([])
    
    r_values = np.logspace(np.log10(r_min), np.log10(r_max), n_r_values)
    
    # Compute correlation sum for each r
    n_pairs = len(unique_distances)
    C_values = np.array([np.sum(unique_distances < r) / n_pairs for r in r_values])
    
    # Filter valid points for linear regression
    valid = C_values > 0
    if np.sum(valid) < 5:
        return np.nan, np.nan, r_values, C_values
    
    log_r = np.log(r_values[valid])
    log_C = np.log(C_values[valid])
    
    # Use middle scaling region for fit
    n_valid = len(log_r)
    start_idx = n_valid // 4
    end_idx = 3 * n_valid // 4
    
    if end_idx - start_idx < 3:
        start_idx = 0
        end_idx = n_valid
    
    # Linear regression
    coeffs = np.polyfit(log_r[start_idx:end_idx], log_C[start_idx:end_idx], 1)
    
    # R-squared
    y_pred = coeffs[0] * log_r[start_idx:end_idx] + coeffs[1]
    ss_res = np.sum((log_C[start_idx:end_idx] - y_pred)**2)
    ss_tot = np.sum((log_C[start_idx:end_idx] - np.mean(log_C[start_idx:end_idx]))**2)
    r_squared = 1 - ss_res / (ss_tot + 1e-10)
    
    return float(coeffs[0]), float(r_squared), r_values, C_values


def compute_recurrence_metrics(
    trajectory: np.ndarray,
    threshold_percentile: float = 10.0,
    n_samples: int = 3000
) -> Dict[str, float]:
    """
    Compute Recurrence Quantification Analysis metrics.
    
    RQA provides measures of determinism and recurrence patterns
    in the attractor.
    
    Args:
        trajectory: Trajectory array (n_points, 3)
        threshold_percentile: Percentile for recurrence threshold
        n_samples: Number of points to use
    
    Returns:
        Dictionary with RQA metrics
    """
    n_points = len(trajectory)
    
    # Subsample if needed
    if n_points > n_samples:
        indices = np.random.choice(n_points, n_samples, replace=False)
        indices.sort()
        sample = trajectory[indices]
    else:
        sample = trajectory
    
    n = len(sample)
    
    # Compute distance matrix
    diff = sample[:, np.newaxis, :] - sample[np.newaxis, :, :]
    distances = np.sqrt(np.sum(diff**2, axis=-1))
    
    # Set threshold
    upper_distances = distances[np.triu_indices(n, k=1)]
    threshold = np.percentile(upper_distances, threshold_percentile)
    
    # Recurrence matrix (excluding diagonal)
    R = (distances < threshold).astype(int)
    np.fill_diagonal(R, 0)
    
    # Recurrence Rate (RR)
    n_recurrences = np.sum(R)
    rr = n_recurrences / (n * (n - 1))
    
    # Determinism (DET) - fraction of recurrent points in diagonal lines
    # Count diagonal lines of length >= 2
    det_sum = 0
    for k in range(-n+2, n-1):
        if k == 0:
            continue
        diag = np.diag(R, k)
        # Count consecutive ones
        in_line = False
        line_length = 0
        for val in diag:
            if val == 1:
                line_length += 1
                in_line = True
            else:
                if in_line and line_length >= 2:
                    det_sum += line_length
                line_length = 0
                in_line = False
        if in_line and line_length >= 2:
            det_sum += line_length
    
    determinism = det_sum / (n_recurrences + 1e-10)
    
    # Average diagonal line length (L)
    line_lengths = []
    for k in range(-n+2, n-1):
        if k == 0:
            continue
        diag = np.diag(R, k)
        in_line = False
        line_length = 0
        for val in diag:
            if val == 1:
                line_length += 1
                in_line = True
            else:
                if in_line and line_length >= 2:
                    line_lengths.append(line_length)
                line_length = 0
                in_line = False
        if in_line and line_length >= 2:
            line_lengths.append(line_length)
    
    avg_line_length = np.mean(line_lengths) if line_lengths else 0.0
    max_line_length = np.max(line_lengths) if line_lengths else 0
    
    # Entropy of diagonal line length distribution
    if line_lengths:
        unique, counts = np.unique(line_lengths, return_counts=True)
        probs = counts / np.sum(counts)
        line_entropy = scipy_entropy(probs)
    else:
        line_entropy = 0.0
    
    return {
        'recurrence_rate': float(rr),
        'determinism': float(determinism),
        'avg_diagonal_line': float(avg_line_length),
        'max_diagonal_line': int(max_line_length),
        'diagonal_entropy': float(line_entropy),
        'threshold': float(threshold),
    }


def compute_average_mutual_information(
    time_series: np.ndarray,
    max_lag: int = 50,
    n_bins: int = 16
) -> Tuple[np.ndarray, np.ndarray, int]:
    """
    Compute Average Mutual Information for embedding delay selection.
    
    AMI measures nonlinear correlation between time series and its
    delayed version. First minimum suggests optimal embedding delay.
    
    Args:
        time_series: 1D time series
        max_lag: Maximum lag to compute
        n_bins: Number of bins for histogram
    
    Returns:
        Tuple of (lags, AMI values, optimal_lag)
    """
    n = len(time_series)
    lags = np.arange(0, min(max_lag, n // 4) + 1)
    ami_values = np.zeros(len(lags))
    
    # Bin edges
    edges = np.linspace(np.min(time_series), np.max(time_series), n_bins + 1)
    
    for i, lag in enumerate(lags):
        if lag == 0:
            ami_values[i] = 1.0  # Maximum at zero lag
            continue
        
        x1 = time_series[:-lag]
        x2 = time_series[lag:]
        
        # 2D histogram
        hist_2d, _, _ = np.histogram2d(x1, x2, bins=edges)
        
        # Normalize to probability
        p_joint = hist_2d / np.sum(hist_2d)
        p_x1 = np.sum(p_joint, axis=1)
        p_x2 = np.sum(p_joint, axis=0)
        
        # Compute mutual information
        mi = 0.0
        for j in range(n_bins):
            for k in range(n_bins):
                if p_joint[j, k] > 0 and p_x1[j] > 0 and p_x2[k] > 0:
                    mi += p_joint[j, k] * np.log(p_joint[j, k] / (p_x1[j] * p_x2[k]))
        
        ami_values[i] = mi
    
    # Find first local minimum
    optimal_lag = 1
    for i in range(1, len(ami_values) - 1):
        if ami_values[i] < ami_values[i-1] and ami_values[i] < ami_values[i+1]:
            optimal_lag = int(lags[i])
            break
    
    return lags, ami_values, optimal_lag


def compute_false_nearest_neighbors(
    time_series: np.ndarray,
    max_dim: int = 10,
    delay: int = 1,
    threshold: float = 15.0
) -> Tuple[np.ndarray, np.ndarray, int]:
    """
    Estimate embedding dimension using False Nearest Neighbors.
    
    Args:
        time_series: 1D time series
        max_dim: Maximum embedding dimension to test
        delay: Embedding delay
        threshold: FNN threshold ratio
    
    Returns:
        Tuple of (dimensions, FNN percentages, optimal dimension)
    """
    n = len(time_series)
    dims = np.arange(1, max_dim + 1)
    fnn_ratios = np.zeros(len(dims))
    
    for i, dim in enumerate(dims):
        # Create embedding
        m = n - (dim + 1) * delay
        if m < 10:
            fnn_ratios[i] = np.nan
            continue
        
        # Current dimension embedding
        embedded = np.zeros((m, dim))
        for d in range(dim):
            embedded[:, d] = time_series[d * delay:d * delay + m]
        
        # Build KD-tree
        tree = cKDTree(embedded)
        
        # Count false neighbors
        n_false = 0
        n_total = 0
        
        for j in range(min(1000, m)):  # Sample for efficiency
            # Find nearest neighbor
            dists, indices = tree.query(embedded[j], k=2)
            
            if dists[1] < 1e-10:
                continue
            
            nn_idx = indices[1]
            
            # Check distance in next dimension
            if nn_idx < m - delay and j < m - delay:
                next_dist = abs(time_series[(dim) * delay + j] - 
                              time_series[(dim) * delay + nn_idx])
                
                ratio = next_dist / (dists[1] + 1e-10)
                
                if ratio > threshold:
                    n_false += 1
                n_total += 1
        
        fnn_ratios[i] = n_false / (n_total + 1e-10) * 100
    
    # Find optimal dimension (FNN drops below 1%)
    optimal_dim = max_dim
    for i, ratio in enumerate(fnn_ratios):
        if not np.isnan(ratio) and ratio < 1.0:
            optimal_dim = dims[i]
            break
    
    return dims, fnn_ratios, int(optimal_dim)


def compute_attractor_statistics(trajectory: np.ndarray) -> Dict[str, float]:
    """
    Compute basic attractor statistics.
    
    Args:
        trajectory: Trajectory array (n_points, 3)
    
    Returns:
        Dictionary of statistics
    """
    x, y, z = trajectory[:, 0], trajectory[:, 1], trajectory[:, 2]
    
    return {
        'x_min': float(np.min(x)),
        'x_max': float(np.max(x)),
        'x_mean': float(np.mean(x)),
        'x_std': float(np.std(x)),
        'y_min': float(np.min(y)),
        'y_max': float(np.max(y)),
        'y_mean': float(np.mean(y)),
        'y_std': float(np.std(y)),
        'z_min': float(np.min(z)),
        'z_max': float(np.max(z)),
        'z_mean': float(np.mean(z)),
        'z_std': float(np.std(z)),
        'x_range': float(np.max(x) - np.min(x)),
        'y_range': float(np.max(y) - np.min(y)),
        'z_range': float(np.max(z) - np.min(z)),
        'bounding_volume': float((np.max(x) - np.min(x)) * 
                                 (np.max(y) - np.min(y)) * 
                                 (np.max(z) - np.min(z))),
    }


def compute_all_metrics(
    trajectory: np.ndarray,
    time_array: np.ndarray,
    params: tuple,
    dt: float,
    log_diags: Optional[np.ndarray] = None,
    verbose: bool = True
) -> Dict[str, any]:
    """
    Compute all chaos metrics for a trajectory.
    
    Args:
        trajectory: Trajectory array (n_points, 3)
        time_array: Time array
        params: System parameters tuple (a, b, c, d, e, f)
        dt: Time step
        log_diags: Optional pre-computed log diagonals
        verbose: Print progress
    
    Returns:
        Comprehensive dictionary of all metrics
    """
    results = {}
    
    # Basic statistics
    if verbose:
        print("      Computing attractor statistics...")
    stats = compute_attractor_statistics(trajectory)
    results.update(stats)
    
    # Lyapunov exponents (if log_diags provided)
    if log_diags is not None:
        if verbose:
            print("      Computing Lyapunov exponents...")
        lyap = compute_lyapunov_exponents(log_diags, dt)
        results['lyapunov_1'] = float(lyap[0])
        results['lyapunov_2'] = float(lyap[1])
        results['lyapunov_3'] = float(lyap[2])
        results['lyapunov_sum'] = float(np.sum(lyap))
        
        # Kaplan-Yorke dimension
        results['kaplan_yorke_dim'] = compute_kaplan_yorke_dimension(lyap)
        
        # KS entropy
        results['ks_entropy'] = compute_kolmogorov_sinai_entropy(lyap)
        
        # Is chaotic?
        results['is_chaotic'] = bool(lyap[0] > 0)
    
    # Correlation dimension
    if verbose:
        print("      Computing correlation dimension...")
    corr_dim, corr_r2, _, _ = compute_correlation_dimension(trajectory)
    results['correlation_dim'] = corr_dim
    results['correlation_dim_r2'] = corr_r2
    
    # Recurrence metrics
    if verbose:
        print("      Computing recurrence metrics...")
    rqa = compute_recurrence_metrics(trajectory)
    results.update({f'rqa_{k}': v for k, v in rqa.items()})
    
    # AMI for x-component
    if verbose:
        print("      Computing average mutual information...")
    _, _, optimal_delay = compute_average_mutual_information(trajectory[:, 0])
    results['optimal_embedding_delay'] = optimal_delay
    
    # Add parameters
    results['param_a'] = float(params[0])
    results['param_b'] = float(params[1])
    results['param_c'] = float(params[2])
    results['param_d'] = float(params[3])
    results['param_e'] = float(params[4])
    results['param_f'] = float(params[5])
    results['dt'] = float(dt)
    results['n_points'] = len(trajectory)
    
    return results


def compute_metrics_timeseries(
    trajectory: np.ndarray,
    time_array: np.ndarray,
    params: tuple,
    dt: float,
    window_size: int = 5000,
    step_size: int = 1000,
    verbose: bool = True
) -> Dict[str, np.ndarray]:
    """
    Compute sliding-window metrics over trajectory.
    
    Args:
        trajectory: Trajectory array
        time_array: Time array
        params: System parameters
        dt: Time step
        window_size: Window size for local metrics
        step_size: Step between windows
        verbose: Print progress
    
    Returns:
        Dictionary with time series of metrics
    """
    n_points = len(trajectory)
    n_windows = (n_points - window_size) // step_size + 1
    
    if n_windows <= 0:
        n_windows = 1
        window_size = n_points
        step_size = n_points
    
    results = {
        'time_windows': np.zeros(n_windows),
        'correlation_dim': np.zeros(n_windows),
        'recurrence_rate': np.zeros(n_windows),
        'determinism': np.zeros(n_windows),
    }
    
    iterator = tqdm(
        range(n_windows),
        desc="      Computing windowed metrics",
        disable=not verbose,
        ncols=70
    )
    
    for i in iterator:
        start = i * step_size
        end = start + window_size
        window = trajectory[start:end]
        
        results['time_windows'][i] = time_array[start + window_size // 2]
        
        # Correlation dimension
        corr_dim, _, _, _ = compute_correlation_dimension(window, n_samples=2000)
        results['correlation_dim'][i] = corr_dim
        
        # RQA metrics
        rqa = compute_recurrence_metrics(window, n_samples=1500)
        results['recurrence_rate'][i] = rqa['recurrence_rate']
        results['determinism'][i] = rqa['determinism']
    
    return results
