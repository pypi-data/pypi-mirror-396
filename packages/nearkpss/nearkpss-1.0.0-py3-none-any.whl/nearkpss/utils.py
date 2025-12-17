"""
Utility functions for the Modified KPSS test.

This module contains helper functions used in the implementation of the
Modified KPSS test for near integration (Harris et al., 2007).
"""

import numpy as np
from typing import Tuple, Optional


def gls_transform(y: np.ndarray, c_bar: float) -> np.ndarray:
    """
    Apply GLS-type transformation to the data.
    
    This implements the quasi-differencing transformation:
        y_t - ρ_{c̄,T} * y_{t-1}
    
    where ρ_{c̄,T} = 1 - c̄/T as defined in equation (2) of the paper.
    
    Parameters
    ----------
    y : np.ndarray
        The time series data of length T.
    c_bar : float
        The hypothesized local-to-unity parameter (c̄ > 0).
        
    Returns
    -------
    np.ndarray
        Transformed series of length T-1 (for t = 2, ..., T).
        
    Notes
    -----
    Following the paper notation:
        ρ_{c̄,T} = 1 - c̄ * T^{-1}
        
    The transformation removes the near unit root under H0: c ≥ c̄ > 0.
    
    References
    ----------
    Harris, D., Leybourne, S., & McCabe, B. (2007), Section 2, p. 357.
    """
    T = len(y)
    rho_c_bar = 1.0 - c_bar / T
    
    # y_t - ρ_{c̄,T} * y_{t-1} for t = 2, ..., T
    y_transformed = y[1:] - rho_c_bar * y[:-1]
    
    return y_transformed


def gls_transform_trend(y: np.ndarray, c_bar: float) -> np.ndarray:
    """
    Apply GLS-type transformation with trend detrending.
    
    For the trend case, we use OLS detrending of the GLS-transformed data
    as described in Note 1 of the paper.
    
    Parameters
    ----------
    y : np.ndarray
        The time series data of length T.
    c_bar : float
        The hypothesized local-to-unity parameter (c̄ > 0).
        
    Returns
    -------
    np.ndarray
        OLS detrended transformed series of length T-1.
        
    Notes
    -----
    From Note 1 (p. 363): "If (2) also includes a linear trend term, 
    the modified statistic is formed from the OLS detrended 
    y_t - ρ_{c̄,T} * y_{t-1}, t = 2,...,T."
    """
    T = len(y)
    rho_c_bar = 1.0 - c_bar / T
    
    # GLS transform
    y_transformed = y[1:] - rho_c_bar * y[:-1]
    
    # OLS detrending: regress on constant and trend
    T_new = len(y_transformed)
    time_index = np.arange(1, T_new + 1)
    X = np.column_stack([np.ones(T_new), time_index])
    
    # OLS coefficients
    beta = np.linalg.lstsq(X, y_transformed, rcond=None)[0]
    
    # Residuals
    y_detrended = y_transformed - X @ beta
    
    return y_detrended


def compute_residuals(y_transformed: np.ndarray, detrend: str = "c") -> np.ndarray:
    """
    Compute OLS residuals from the transformed series.
    
    This implements the demeaning (or detrending) step described in the paper:
        r_{c̄,t} = (y_t - ρ_{c̄,T} * y_{t-1}) - m_{c̄}
    
    where m_{c̄} is the OLS estimator defined as:
        m_{c̄} = Σ_{t=2}^T (y_t - ρ_{c̄,T} * y_{t-1}) / (T - 1)
    
    Parameters
    ----------
    y_transformed : np.ndarray
        The GLS-transformed series.
    detrend : str, optional
        Detrending specification:
        - "c" : Demean only (constant)
        - "ct" : Demean and detrend (constant + trend)
        Default is "c".
        
    Returns
    -------
    np.ndarray
        OLS residuals r_{c̄,t}.
        
    References
    ----------
    Harris, D., Leybourne, S., & McCabe, B. (2007), Section 2, p. 357.
    """
    T = len(y_transformed)
    
    if detrend == "c":
        # Demean only: m_{c̄} = mean of transformed series
        # From paper: m_{c̄} = Σ(y_t - ρ_{c̄,T} * y_{t-1}) / (T-1)
        m_c_bar = np.sum(y_transformed) / T
        residuals = y_transformed - m_c_bar
    elif detrend == "ct":
        # Demean and detrend
        time_index = np.arange(1, T + 1)
        X = np.column_stack([np.ones(T), time_index])
        beta = np.linalg.lstsq(X, y_transformed, rcond=None)[0]
        residuals = y_transformed - X @ beta
    else:
        raise ValueError(f"Invalid detrend option: {detrend}. Use 'c' or 'ct'.")
    
    return residuals


def compute_partial_sums(residuals: np.ndarray) -> np.ndarray:
    """
    Compute partial sums of the residuals.
    
    This computes S_t = Σ_{i=2}^t r_{c̄,i} for t = 2, ..., T.
    
    Parameters
    ----------
    residuals : np.ndarray
        The OLS residuals r_{c̄,t}.
        
    Returns
    -------
    np.ndarray
        Partial sums S_t.
        
    Notes
    -----
    The partial sums are used in the KPSS statistic:
        S^μ(c̄) = T^{-2} * Σ_{t=2}^T S_t^2 / ω̂_{c̄}^2
    
    References
    ----------
    Harris, D., Leybourne, S., & McCabe, B. (2007), Section 2, p. 357.
    """
    return np.cumsum(residuals)


def compute_kpss_statistic(residuals: np.ndarray, 
                           long_run_variance: float) -> float:
    """
    Compute the KPSS test statistic.
    
    This implements:
        S^μ(c̄) = [T^{-2} * Σ_{t=2}^T (Σ_{i=2}^t r_{c̄,i})^2] / ω̂_{c̄}^2
    
    Parameters
    ----------
    residuals : np.ndarray
        The OLS residuals r_{c̄,t}.
    long_run_variance : float
        The long-run variance estimate ω̂_{c̄}^2.
        
    Returns
    -------
    float
        The KPSS test statistic S^μ(c̄).
        
    Raises
    ------
    ValueError
        If long_run_variance is not positive.
        
    References
    ----------
    Harris, D., Leybourne, S., & McCabe, B. (2007), Section 2, p. 357.
    """
    if long_run_variance <= 0:
        raise ValueError("Long-run variance must be positive.")
    
    T = len(residuals)
    
    # Compute partial sums: S_t = Σ_{i=1}^t r_{c̄,i}
    partial_sums = compute_partial_sums(residuals)
    
    # Compute statistic: S^μ(c̄) = T^{-2} * Σ S_t^2 / ω̂^2
    numerator = np.sum(partial_sums ** 2) / (T ** 2)
    statistic = numerator / long_run_variance
    
    return statistic


def simulate_near_integrated_process(T: int, 
                                     c: float,
                                     alpha: float = 1.0,
                                     mu: float = 0.0,
                                     sigma: float = 1.0,
                                     seed: Optional[int] = None) -> np.ndarray:
    """
    Simulate a near-integrated process as in the DGP (2) of the paper.
    
    The DGP is:
        y_t = μ + w_t,  t = 1, ..., T
        w_t = ρ_{c,T} * w_{t-1} + v_t,  t = 2, ..., T
        w_1 = ξ
    
    where:
        ρ_{c,T} = 1 - c/T
        ξ = α * ω / sqrt(1 - ρ_{c,T}^2)  for c > 0
    
    Parameters
    ----------
    T : int
        Sample size.
    c : float
        Local-to-unity parameter (c ≥ 0).
        c = 0 gives a unit root, c > 0 gives near-integrated process.
    alpha : float, optional
        Initial value scaling parameter. Default is 1.0.
    mu : float, optional
        Mean/intercept. Default is 0.0.
    sigma : float, optional
        Innovation standard deviation. Default is 1.0.
    seed : int, optional
        Random seed for reproducibility.
        
    Returns
    -------
    np.ndarray
        Simulated series y_t of length T.
        
    References
    ----------
    Harris, D., Leybourne, S., & McCabe, B. (2007), Section 2, equations (2).
    Müller, U. & Elliott, G. (2003), for the initial value specification.
    """
    if seed is not None:
        np.random.seed(seed)
    
    rho = 1.0 - c / T
    
    # Generate innovations v_t ~ N(0, σ^2)
    v = np.random.normal(0, sigma, T)
    
    # Initialize w
    w = np.zeros(T)
    
    # Set initial value w_1 = ξ = α * σ / sqrt(1 - ρ^2) for c > 0
    # For c = 0 (unit root), we set w_1 = 0 (or could use v[0])
    if c > 0:
        # ξ = α * ω / sqrt(1 - ρ_{c,T}^2)
        # For i.i.d. innovations, ω = σ
        var_factor = 1.0 - rho ** 2
        if var_factor > 0:
            w[0] = alpha * sigma / np.sqrt(var_factor)
        else:
            w[0] = 0.0
    else:
        w[0] = v[0]
    
    # Generate the process: w_t = ρ * w_{t-1} + v_t
    for t in range(1, T):
        w[t] = rho * w[t-1] + v[t]
    
    # Add mean: y_t = μ + w_t
    y = mu + w
    
    return y


def simulate_near_integrated_ma(T: int, 
                                c: float,
                                theta: float = 0.0,
                                alpha: float = 1.0,
                                mu: float = 0.0,
                                sigma: float = 1.0,
                                seed: Optional[int] = None) -> np.ndarray:
    """
    Simulate a near-integrated process with MA(1) innovations.
    
    The DGP is:
        y_t = μ + w_t,  t = 1, ..., T
        w_t = ρ_{c,T} * w_{t-1} + v_t,  t = 2, ..., T
        v_t = ε_t - θ * ε_{t-1}  (MA(1) innovations)
    
    This is used in the finite-sample simulations of Table 1 in the paper.
    
    Parameters
    ----------
    T : int
        Sample size.
    c : float
        Local-to-unity parameter (c ≥ 0).
    theta : float, optional
        MA(1) parameter. Default is 0.0 (i.i.d. innovations).
    alpha : float, optional
        Initial value scaling parameter. Default is 1.0.
    mu : float, optional
        Mean/intercept. Default is 0.0.
    sigma : float, optional
        Innovation standard deviation. Default is 1.0.
    seed : int, optional
        Random seed for reproducibility.
        
    Returns
    -------
    np.ndarray
        Simulated series y_t of length T.
        
    Notes
    -----
    From Table 1 (p. 359): "v_t = ε_t - θ * ε_{t-1}"
    
    The long-run variance of v_t is:
        ω^2 = σ^2 * (1 - θ)^2
    
    References
    ----------
    Harris, D., Leybourne, S., & McCabe, B. (2007), Section 3, Table 1.
    """
    if seed is not None:
        np.random.seed(seed)
    
    rho = 1.0 - c / T
    
    # Generate i.i.d. innovations ε_t ~ N(0, σ^2)
    # Need T+1 to generate MA(1)
    epsilon = np.random.normal(0, sigma, T + 1)
    
    # MA(1) innovations: v_t = ε_t - θ * ε_{t-1}
    v = epsilon[1:] - theta * epsilon[:-1]
    
    # Long-run variance of MA(1): ω^2 = σ^2 * (1 - θ)^2
    omega = sigma * np.abs(1 - theta)
    
    # Initialize w
    w = np.zeros(T)
    
    # Set initial value w_1 = ξ = α * ω / sqrt(1 - ρ^2) for c > 0
    if c > 0:
        var_factor = 1.0 - rho ** 2
        if var_factor > 0:
            w[0] = alpha * omega / np.sqrt(var_factor)
        else:
            w[0] = 0.0
    else:
        w[0] = v[0]
    
    # Generate the process: w_t = ρ * w_{t-1} + v_t
    for t in range(1, T):
        w[t] = rho * w[t-1] + v[t]
    
    # Add mean: y_t = μ + w_t
    y = mu + w
    
    return y
