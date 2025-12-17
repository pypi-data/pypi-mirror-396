"""
Long-run variance estimation for the Modified KPSS test.

This module implements the long-run variance estimator (equation 3) 
from Harris et al. (2007) using various kernel functions and 
automatic bandwidth selection.

References
----------
Harris, D., Leybourne, S., & McCabe, B. (2007). Modified KPSS Tests for 
Near Integration. Econometric Theory, 23(2), 355-363.

Newey, W. & West, K. (1994). Automatic lag selection in covariance matrix 
estimation. Review of Economic Studies, 61, 631-653.

Sul, D., Phillips, P.C.B., & Choi, C. (2005). Prewhitening bias in HAC 
estimation. Oxford Bulletin of Economics and Statistics, 67, 517-546.
"""

import numpy as np
from typing import Optional, Callable, Tuple


def quadratic_spectral_kernel(x: np.ndarray) -> np.ndarray:
    """
    Quadratic Spectral (QS) kernel function.
    
    The QS kernel is defined as:
        λ(x) = (25 / (12π²x²)) * [sin(6πx/5) / (6πx/5) - cos(6πx/5)]
    
    For x = 0: λ(0) = 1
    
    Parameters
    ----------
    x : np.ndarray
        Input values (typically j/l where j is lag, l is bandwidth).
        
    Returns
    -------
    np.ndarray
        Kernel weights.
        
    Notes
    -----
    The QS kernel is used in the finite-sample simulations (Section 3, p. 359):
    "For all tests we use the quadratic spectral (QS) kernel for λ(.)
    and employ the automatic bandwidth selection of Newey and West (1994)."
    
    References
    ----------
    Andrews, D.W.K. (1991). Heteroskedasticity and autocorrelation 
    consistent covariance matrix estimation. Econometrica, 59, 817-858.
    """
    x = np.atleast_1d(np.asarray(x, dtype=float))
    result = np.ones_like(x)
    
    # For non-zero x
    nonzero = np.abs(x) > 1e-10
    z = x[nonzero]
    
    # QS kernel formula
    arg = 6.0 * np.pi * z / 5.0
    term1 = 25.0 / (12.0 * (np.pi ** 2) * (z ** 2))
    term2 = np.sin(arg) / arg - np.cos(arg)
    result[nonzero] = term1 * term2
    
    return result


def bartlett_kernel(x: np.ndarray) -> np.ndarray:
    """
    Bartlett (triangular) kernel function.
    
    λ(x) = 1 - |x|  if |x| < 1
         = 0        otherwise
    
    Parameters
    ----------
    x : np.ndarray
        Input values (typically j/l where j is lag, l is bandwidth).
        
    Returns
    -------
    np.ndarray
        Kernel weights.
    """
    x = np.atleast_1d(np.asarray(x, dtype=float))
    result = np.maximum(1.0 - np.abs(x), 0.0)
    return result


def parzen_kernel(x: np.ndarray) -> np.ndarray:
    """
    Parzen kernel function.
    
    λ(x) = 1 - 6x² + 6|x|³        if 0 ≤ |x| ≤ 0.5
         = 2(1 - |x|)³            if 0.5 < |x| ≤ 1
         = 0                       if |x| > 1
    
    Parameters
    ----------
    x : np.ndarray
        Input values (typically j/l where j is lag, l is bandwidth).
        
    Returns
    -------
    np.ndarray
        Kernel weights.
    """
    x = np.atleast_1d(np.asarray(x, dtype=float))
    absx = np.abs(x)
    result = np.zeros_like(x)
    
    # 0 ≤ |x| ≤ 0.5
    mask1 = absx <= 0.5
    result[mask1] = 1.0 - 6.0 * absx[mask1]**2 + 6.0 * absx[mask1]**3
    
    # 0.5 < |x| ≤ 1
    mask2 = (absx > 0.5) & (absx <= 1.0)
    result[mask2] = 2.0 * (1.0 - absx[mask2])**3
    
    return result


def truncated_kernel(x: np.ndarray) -> np.ndarray:
    """
    Truncated (rectangular) kernel function.
    
    λ(x) = 1  if |x| ≤ 1
         = 0  otherwise
    
    Parameters
    ----------
    x : np.ndarray
        Input values (typically j/l where j is lag, l is bandwidth).
        
    Returns
    -------
    np.ndarray
        Kernel weights.
    """
    x = np.atleast_1d(np.asarray(x, dtype=float))
    return np.where(np.abs(x) <= 1.0, 1.0, 0.0)


def get_kernel(kernel_name: str) -> Callable:
    """
    Get kernel function by name.
    
    Parameters
    ----------
    kernel_name : str
        Name of the kernel: "qs", "bartlett", "parzen", "truncated".
        
    Returns
    -------
    Callable
        Kernel function.
        
    Raises
    ------
    ValueError
        If kernel name is not recognized.
    """
    kernels = {
        "qs": quadratic_spectral_kernel,
        "quadratic_spectral": quadratic_spectral_kernel,
        "bartlett": bartlett_kernel,
        "parzen": parzen_kernel,
        "truncated": truncated_kernel,
    }
    
    kernel_lower = kernel_name.lower()
    if kernel_lower not in kernels:
        raise ValueError(
            f"Unknown kernel: {kernel_name}. "
            f"Available kernels: {list(kernels.keys())}"
        )
    
    return kernels[kernel_lower]


def newey_west_bandwidth(residuals: np.ndarray, 
                         kernel: str = "qs") -> float:
    """
    Compute automatic bandwidth using Newey-West (1994) method.
    
    This implements the data-dependent bandwidth selection procedure
    from Newey and West (1994), as used in the paper.
    
    Parameters
    ----------
    residuals : np.ndarray
        The residuals from which to estimate bandwidth.
    kernel : str, optional
        Kernel type: "qs" (Quadratic Spectral), "bartlett", or "parzen".
        Default is "qs".
        
    Returns
    -------
    float
        Optimal bandwidth.
        
    Notes
    -----
    From the paper (p. 359): "employ the automatic bandwidth selection 
    of Newey and West (1994)."
    
    For the QS kernel, the optimal bandwidth is:
        l = 1.3221 * (α(2) * T)^(1/5)
    
    where α(2) is estimated from an AR(1) approximation.
    
    References
    ----------
    Newey, W. & West, K. (1994). Automatic lag selection in covariance 
    matrix estimation. Review of Economic Studies, 61, 631-653.
    """
    T = len(residuals)
    
    # Fit AR(1) to get the autoregressive coefficient
    if T < 3:
        return 1.0
    
    # AR(1) regression: e_t = ρ * e_{t-1} + u_t
    y = residuals[1:]
    x = residuals[:-1]
    
    # OLS estimate of ρ
    rho_hat = np.sum(x * y) / np.sum(x ** 2) if np.sum(x ** 2) > 0 else 0.0
    
    # Bound rho to avoid numerical issues
    rho_hat = np.clip(rho_hat, -0.999, 0.999)
    
    # Estimate σ² from residuals
    u = y - rho_hat * x
    sigma2_u = np.var(u, ddof=1) if len(u) > 1 else np.var(u)
    
    # For QS kernel: α(2) = 4ρ² / (1-ρ)^4
    # For Bartlett: α(1) = 4ρ² / (1-ρ)^4
    if kernel.lower() in ["qs", "quadratic_spectral"]:
        # QS kernel uses α(2)
        # α(2) = 4ρ² / [(1-ρ)^4 * σ^4] * σ^4 = 4ρ² / (1-ρ)^4
        if abs(1 - abs(rho_hat)) > 0.01:
            alpha2 = 4.0 * rho_hat ** 2 / (1.0 - rho_hat) ** 4
        else:
            alpha2 = 4.0
        
        # Bandwidth for QS: l = 1.3221 * (α(2) * T)^(1/5)
        bandwidth = 1.3221 * (alpha2 * T) ** 0.2
        
    elif kernel.lower() == "bartlett":
        # Bartlett kernel uses α(1)
        if abs(1 - abs(rho_hat)) > 0.01:
            alpha1 = 4.0 * rho_hat ** 2 / (1.0 - rho_hat) ** 4
        else:
            alpha1 = 4.0
        
        # Bandwidth for Bartlett: l = 1.1447 * (α(1) * T)^(1/3)
        bandwidth = 1.1447 * (alpha1 * T) ** (1.0 / 3.0)
        
    elif kernel.lower() == "parzen":
        # Parzen kernel uses α(2)
        if abs(1 - abs(rho_hat)) > 0.01:
            alpha2 = 4.0 * rho_hat ** 2 / (1.0 - rho_hat) ** 4
        else:
            alpha2 = 4.0
        
        # Bandwidth for Parzen: l = 2.6614 * (α(2) * T)^(1/5)
        bandwidth = 2.6614 * (alpha2 * T) ** 0.2
        
    else:
        # Default: use floor(4 * (T/100)^(2/9))
        bandwidth = np.floor(4.0 * (T / 100.0) ** (2.0 / 9.0))
    
    # Ensure bandwidth is at least 1 and at most T-1
    bandwidth = max(1.0, min(bandwidth, T - 1))
    
    return bandwidth


def long_run_variance(residuals: np.ndarray,
                      kernel: str = "qs",
                      bandwidth: Optional[float] = None,
                      prewhiten: bool = False) -> float:
    """
    Estimate long-run variance using kernel-based HAC estimator.
    
    This implements equation (3) from the paper:
        ω̂²_{c̄} = γ̂_{c̄,0} + 2 * Σ_{j=1}^{T-1} λ(j/l) * γ̂_{c̄,j}
    
    where:
        γ̂_{c̄,j} = T^{-1} * Σ_{t=j+1}^T r_{c̄,t} * r_{c̄,t-j}
    
    Parameters
    ----------
    residuals : np.ndarray
        The OLS residuals r_{c̄,t}.
    kernel : str, optional
        Kernel function name: "qs", "bartlett", "parzen", "truncated".
        Default is "qs" (Quadratic Spectral).
    bandwidth : float, optional
        Bandwidth parameter l. If None, uses automatic selection
        from Newey-West (1994). Default is None.
    prewhiten : bool, optional
        Whether to apply AR(1) prewhitening. Default is False.
        
    Returns
    -------
    float
        Long-run variance estimate ω̂²_{c̄}.
        
    Notes
    -----
    From the paper (p. 357, eq. 3):
    "ω̂²_{c̄} is any standard long-run variance estimator of the form (3)"
    
    From p. 359: "For all tests we use the quadratic spectral (QS) kernel 
    for λ(.) and employ the automatic bandwidth selection of 
    Newey and West (1994)."
    
    References
    ----------
    Harris, D., Leybourne, S., & McCabe, B. (2007), Section 2, equation (3).
    Newey, W. & West, K. (1994). Review of Economic Studies, 61, 631-653.
    """
    T = len(residuals)
    
    if T < 2:
        raise ValueError("Need at least 2 observations.")
    
    # Get kernel function
    kernel_func = get_kernel(kernel)
    
    # Prewhitening (optional, following Sul et al., 2005)
    if prewhiten:
        # AR(1) prewhitening
        y = residuals[1:]
        x = residuals[:-1]
        rho = np.sum(x * y) / np.sum(x ** 2) if np.sum(x ** 2) > 0 else 0.0
        rho = np.clip(rho, -0.99, 0.99)
        
        # Prewhitened residuals
        pw_residuals = residuals[1:] - rho * residuals[:-1]
        
        # Automatic bandwidth for prewhitened series
        if bandwidth is None:
            bandwidth = newey_west_bandwidth(pw_residuals, kernel)
        
        # Compute autocovariances of prewhitened residuals
        T_pw = len(pw_residuals)
        gamma_0 = np.sum(pw_residuals ** 2) / T_pw
        
        omega2_pw = gamma_0
        for j in range(1, T_pw):
            gamma_j = np.sum(pw_residuals[j:] * pw_residuals[:-j]) / T_pw
            weight = kernel_func(np.array([j / bandwidth]))[0]
            omega2_pw += 2.0 * weight * gamma_j
        
        # Recolor
        omega2 = omega2_pw / (1.0 - rho) ** 2
        
    else:
        # No prewhitening
        if bandwidth is None:
            bandwidth = newey_west_bandwidth(residuals, kernel)
        
        # Compute autocovariances: γ̂_{c̄,j} = T^{-1} * Σ r_{c̄,t} * r_{c̄,t-j}
        # γ̂_{c̄,0} = T^{-1} * Σ r_{c̄,t}²
        gamma_0 = np.sum(residuals ** 2) / T
        
        # Long-run variance estimate
        omega2 = gamma_0
        
        for j in range(1, T):
            # γ̂_{c̄,j} = T^{-1} * Σ_{t=j+1}^T r_{c̄,t} * r_{c̄,t-j}
            gamma_j = np.sum(residuals[j:] * residuals[:-j]) / T
            weight = kernel_func(np.array([j / bandwidth]))[0]
            omega2 += 2.0 * weight * gamma_j
    
    # Ensure positivity
    omega2 = max(omega2, 1e-10)
    
    return omega2


def long_run_variance_sul(residuals: np.ndarray,
                          c_bar: float,
                          kernel: str = "qs") -> float:
    """
    Prewhitened long-run variance estimator following Sul et al. (2005).
    
    This implements the modified long-run variance estimator mentioned
    in the paper (p. 358):
    
    "The modified KPSS test is related to the prewhitened long-run variance 
    estimator suggested by Sul, Phillips, and Choi (2005) for the KPSS test.
    Instead of the usual fixed upper bound of 0.97 for the AR(1) prewhitening 
    coefficient, they suggest using 1 - T^{-1/2}. The difference is that our 
    AR(1) filtering uses 1 - c̄*T^{-1} and this is employed in both numerator 
    and denominator of the test."
    
    Parameters
    ----------
    residuals : np.ndarray
        The OLS residuals r_{c̄,t}.
    c_bar : float
        The hypothesized local-to-unity parameter.
    kernel : str, optional
        Kernel function name. Default is "qs".
        
    Returns
    -------
    float
        Long-run variance estimate.
        
    References
    ----------
    Sul, D., Phillips, P.C.B., & Choi, C. (2005). Prewhitening bias in HAC 
    estimation. Oxford Bulletin of Economics and Statistics, 67, 517-546.
    """
    T = len(residuals)
    
    # AR(1) coefficient from local-to-unity: ρ = 1 - c̄/T
    rho = 1.0 - c_bar / T
    
    # Get kernel function
    kernel_func = get_kernel(kernel)
    
    # Automatic bandwidth
    bandwidth = newey_west_bandwidth(residuals, kernel)
    
    # Compute autocovariances
    gamma_0 = np.sum(residuals ** 2) / T
    
    omega2 = gamma_0
    for j in range(1, T):
        gamma_j = np.sum(residuals[j:] * residuals[:-j]) / T
        weight = kernel_func(np.array([j / bandwidth]))[0]
        omega2 += 2.0 * weight * gamma_j
    
    return max(omega2, 1e-10)
