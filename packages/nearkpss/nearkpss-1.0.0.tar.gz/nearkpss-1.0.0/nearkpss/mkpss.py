"""
Modified KPSS Test for Near Integration.

This module implements the Modified KPSS test proposed by Harris, Leybourne, 
and McCabe (2007) for testing the null hypothesis of near integration against 
a unit root alternative.

The key innovation is applying the KPSS test to the filtered series 
w_t - (1 - c̄/T)w_{t-1}, which removes the near unit root under H0, 
resulting in controlled asymptotic size.

References
----------
Harris, D., Leybourne, S., & McCabe, B. (2007). Modified KPSS Tests for 
Near Integration. Econometric Theory, 23(2), 355-363.
DOI: 10.1017/S0266466607070156

Author: Dr Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/modifiedkpss
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple, Union
import warnings

from .utils import (
    gls_transform,
    compute_residuals,
    compute_partial_sums,
    compute_kpss_statistic,
)
from .long_run_variance import (
    long_run_variance,
    newey_west_bandwidth,
)
from .critical_values import (
    get_critical_values,
    compute_p_value,
    CriticalValues,
    STANDARD_KPSS_CRITICAL_VALUES,
)


@dataclass
class ModifiedKPSSResult:
    """
    Results from the Modified KPSS test.
    
    Attributes
    ----------
    statistic : float
        The test statistic S^μ(c̄).
    p_value : float
        P-value from the asymptotic distribution (if computed).
    critical_values : CriticalValues
        Critical values at 1%, 5%, and 10% significance levels.
    c_bar : float
        The local-to-unity parameter used for the test.
    bandwidth : float
        The bandwidth used in the long-run variance estimator.
    long_run_variance : float
        The estimated long-run variance ω̂²_{c̄}.
    detrend : str
        The detrending specification used.
    nobs : int
        Number of observations.
    reject_1pct : bool
        Whether the null is rejected at 1% level.
    reject_5pct : bool
        Whether the null is rejected at 5% level.
    reject_10pct : bool
        Whether the null is rejected at 10% level.
    """
    statistic: float
    p_value: float
    critical_values: CriticalValues
    c_bar: float
    bandwidth: float
    long_run_variance: float
    detrend: str
    nobs: int
    reject_1pct: bool
    reject_5pct: bool
    reject_10pct: bool
    
    def __repr__(self) -> str:
        stars = ""
        if self.reject_1pct:
            stars = "***"
        elif self.reject_5pct:
            stars = "**"
        elif self.reject_10pct:
            stars = "*"
        
        result_str = (
            f"\n"
            f"{'='*60}\n"
            f"        Modified KPSS Test for Near Integration\n"
            f"        Harris, Leybourne, and McCabe (2007)\n"
            f"{'='*60}\n\n"
            f"Null Hypothesis: The series is near-integrated (stationary)\n"
            f"                 H₀: c ≥ c̄ = {self.c_bar:.1f}\n"
            f"Alternative:     The series has a unit root (H₁: c = 0)\n\n"
            f"Detrending:      {'Level (constant only)' if self.detrend == 'c' else 'Trend (constant + trend)'}\n"
            f"Observations:    {self.nobs}\n\n"
            f"{'-'*60}\n"
            f"Test Statistic:  {self.statistic:.6f} {stars}\n"
            f"P-value:         {self.p_value:.4f}\n"
            f"{'-'*60}\n\n"
            f"Critical Values:\n"
            f"  1%:   {self.critical_values.cv_1pct:.4f}\n"
            f"  5%:   {self.critical_values.cv_5pct:.4f}\n"
            f"  10%:  {self.critical_values.cv_10pct:.4f}\n\n"
            f"Estimation Details:\n"
            f"  Bandwidth:           {self.bandwidth:.2f}\n"
            f"  Long-run variance:   {self.long_run_variance:.6f}\n\n"
            f"{'='*60}\n"
            f"Conclusion: "
        )
        
        if self.reject_1pct:
            result_str += "Reject H₀ at 1% significance level.\n"
            result_str += "           Evidence of a unit root.\n"
        elif self.reject_5pct:
            result_str += "Reject H₀ at 5% significance level.\n"
            result_str += "           Evidence of a unit root.\n"
        elif self.reject_10pct:
            result_str += "Reject H₀ at 10% significance level.\n"
            result_str += "           Weak evidence of a unit root.\n"
        else:
            result_str += "Cannot reject H₀.\n"
            result_str += "           Series appears near-integrated/stationary.\n"
        
        result_str += f"{'='*60}\n"
        result_str += "\nSignificance codes: *** 1%  ** 5%  * 10%\n"
        
        return result_str
    
    def summary(self) -> str:
        """Return a summary string suitable for publication."""
        return self.__repr__()


class ModifiedKPSS:
    """
    Modified KPSS Test for Near Integration.
    
    This class implements the Modified KPSS test from Harris, Leybourne, 
    and McCabe (2007) for testing near integration against a unit root.
    
    The test is applicable to testing:
        H₀: c ≥ c̄ > 0 (near integration/stationarity)
        H₁: c = 0 (unit root)
    
    where the DGP is:
        y_t = μ + w_t,  t = 1, ..., T
        w_t = ρ_{c,T} * w_{t-1} + v_t,  t = 2, ..., T
        ρ_{c,T} = 1 - c/T
    
    Parameters
    ----------
    c_bar : float, optional
        The hypothesized local-to-unity parameter under H₀. Default is 10.0.
        Following the paper, c̄ = 10 is recommended.
    detrend : str, optional
        Detrending specification:
        - "c": Level (intercept only, tests for level stationarity)
        - "ct": Trend (intercept + trend, tests for trend stationarity)
        Default is "c".
    kernel : str, optional
        Kernel function for long-run variance estimation:
        "qs" (Quadratic Spectral), "bartlett", "parzen", "truncated".
        Default is "qs" (as used in the paper).
    bandwidth : float or None, optional
        Bandwidth for long-run variance estimation. If None, uses automatic
        selection from Newey and West (1994). Default is None.
        
    Attributes
    ----------
    c_bar : float
        Local-to-unity parameter.
    detrend : str
        Detrending specification.
    kernel : str
        Kernel function name.
    bandwidth : float or None
        Bandwidth parameter.
        
    Examples
    --------
    >>> import numpy as np
    >>> from nearkpss import ModifiedKPSS
    >>> 
    >>> # Generate near-integrated data
    >>> np.random.seed(42)
    >>> T = 200
    >>> c = 10  # Near-integrated with c = 10
    >>> rho = 1 - c/T
    >>> y = np.zeros(T)
    >>> for t in range(1, T):
    ...     y[t] = rho * y[t-1] + np.random.normal()
    >>> 
    >>> # Run the Modified KPSS test
    >>> mkpss = ModifiedKPSS(c_bar=10, detrend="c")
    >>> result = mkpss.test(y)
    >>> print(result)
    
    Notes
    -----
    From the paper (p. 356-357):
    "Instead of applying the KPSS test to w_t, we suggest that it be applied 
    instead to the filtered series w_t - (1 - c̄/T)w_{t-1}. This has the effect 
    of removing the near unit root under the null hypothesis, resulting in a 
    KPSS test with controlled asymptotic size."
    
    References
    ----------
    Harris, D., Leybourne, S., & McCabe, B. (2007). Modified KPSS Tests for 
    Near Integration. Econometric Theory, 23(2), 355-363.
    """
    
    def __init__(self,
                 c_bar: float = 10.0,
                 detrend: str = "c",
                 kernel: str = "qs",
                 bandwidth: Optional[float] = None):
        """Initialize the Modified KPSS test."""
        if c_bar <= 0:
            raise ValueError(f"c_bar must be positive, got {c_bar}")
        if detrend not in ["c", "ct"]:
            raise ValueError(f"detrend must be 'c' or 'ct', got {detrend}")
        
        self.c_bar = c_bar
        self.detrend = detrend
        self.kernel = kernel
        self.bandwidth = bandwidth
    
    def test(self,
             y: np.ndarray,
             compute_pvalue: bool = True,
             pvalue_replications: int = 10000) -> ModifiedKPSSResult:
        """
        Perform the Modified KPSS test.
        
        Parameters
        ----------
        y : np.ndarray
            The time series data to test.
        compute_pvalue : bool, optional
            Whether to compute the p-value via simulation. Default is True.
        pvalue_replications : int, optional
            Number of replications for p-value computation. Default is 10000.
            
        Returns
        -------
        ModifiedKPSSResult
            Test results including statistic, p-value, and critical values.
            
        Notes
        -----
        The test procedure follows Section 2 of the paper:
        
        1. Apply GLS transformation: y_t - ρ_{c̄,T} * y_{t-1}
           where ρ_{c̄,T} = 1 - c̄/T
        
        2. Compute OLS mean: m_{c̄} = Σ(y_t - ρ_{c̄,T} * y_{t-1}) / (T-1)
        
        3. Compute residuals: r_{c̄,t} = (y_t - ρ_{c̄,T} * y_{t-1}) - m_{c̄}
        
        4. Compute test statistic:
           S^μ(c̄) = [T^{-2} * Σ(Σ r_{c̄,i})²] / ω̂²_{c̄}
        
        5. Compare with critical values from the standard KPSS distribution
           (valid at the boundary c = c̄ of the null hypothesis).
        """
        y = np.asarray(y, dtype=float)
        T = len(y)
        
        if T < 10:
            raise ValueError(f"Sample size too small: {T}. Need at least 10 observations.")
        
        # Step 1: GLS transformation
        # y_t - ρ_{c̄,T} * y_{t-1} where ρ_{c̄,T} = 1 - c̄/T
        y_transformed = gls_transform(y, self.c_bar)
        
        # Step 2-3: Compute OLS residuals
        residuals = compute_residuals(y_transformed, self.detrend)
        
        # Compute bandwidth if not specified
        if self.bandwidth is None:
            bw = newey_west_bandwidth(residuals, self.kernel)
        else:
            bw = self.bandwidth
        
        # Step 4a: Compute long-run variance ω̂²_{c̄}
        lrv = long_run_variance(residuals, self.kernel, bw)
        
        # Step 4b: Compute test statistic S^μ(c̄)
        statistic = compute_kpss_statistic(residuals, lrv)
        
        # Step 5: Get critical values
        # At the boundary c = c̄, the distribution is standard KPSS
        cv = get_critical_values(self.c_bar, self.detrend)
        
        # Compute p-value if requested
        if compute_pvalue:
            pval = compute_p_value(
                statistic, self.c_bar, self.detrend,
                n_replications=pvalue_replications
            )
        else:
            # Use asymptotic approximation based on standard KPSS
            pval = self._approximate_pvalue(statistic)
        
        # Determine rejection decisions
        reject_1 = statistic > cv.cv_1pct
        reject_5 = statistic > cv.cv_5pct
        reject_10 = statistic > cv.cv_10pct
        
        return ModifiedKPSSResult(
            statistic=statistic,
            p_value=pval,
            critical_values=cv,
            c_bar=self.c_bar,
            bandwidth=bw,
            long_run_variance=lrv,
            detrend=self.detrend,
            nobs=T,
            reject_1pct=reject_1,
            reject_5pct=reject_5,
            reject_10pct=reject_10,
        )
    
    def _approximate_pvalue(self, statistic: float) -> float:
        """
        Approximate p-value using interpolation from critical values.
        
        This is a rough approximation when simulation is not used.
        """
        cv = STANDARD_KPSS_CRITICAL_VALUES[self.detrend]
        
        if statistic <= cv[10]:
            return 0.15  # Very approximate
        elif statistic <= cv[5]:
            return 0.075
        elif statistic <= cv[1]:
            return 0.025
        else:
            return 0.005


def modified_kpss_test(y: np.ndarray,
                       c_bar: float = 10.0,
                       detrend: str = "c",
                       kernel: str = "qs",
                       bandwidth: Optional[float] = None,
                       compute_pvalue: bool = True) -> ModifiedKPSSResult:
    """
    Perform the Modified KPSS test for near integration.
    
    This is a convenience function that wraps the ModifiedKPSS class.
    
    Parameters
    ----------
    y : np.ndarray
        The time series data to test.
    c_bar : float, optional
        Local-to-unity parameter under H₀. Default is 10.0.
    detrend : str, optional
        "c" for level, "ct" for trend. Default is "c".
    kernel : str, optional
        Kernel function. Default is "qs".
    bandwidth : float or None, optional
        Bandwidth parameter. Default is None (automatic).
    compute_pvalue : bool, optional
        Whether to compute p-value. Default is True.
        
    Returns
    -------
    ModifiedKPSSResult
        Test results.
        
    Examples
    --------
    >>> import numpy as np
    >>> from nearkpss import modified_kpss_test
    >>> 
    >>> # Test a near-integrated series
    >>> y = np.cumsum(np.random.normal(size=200))  # Random walk
    >>> result = modified_kpss_test(y, c_bar=10)
    >>> print(f"Statistic: {result.statistic:.4f}")
    >>> print(f"P-value: {result.p_value:.4f}")
    
    See Also
    --------
    ModifiedKPSS : Class-based interface for the test.
    standard_kpss_test : Standard KPSS test without modification.
    """
    test = ModifiedKPSS(c_bar=c_bar, detrend=detrend, kernel=kernel, bandwidth=bandwidth)
    return test.test(y, compute_pvalue=compute_pvalue)


@dataclass
class StandardKPSSResult:
    """
    Results from the standard KPSS test.
    
    Attributes
    ----------
    statistic : float
        The KPSS test statistic.
    critical_values : dict
        Critical values at 1%, 5%, and 10%.
    bandwidth : float
        Bandwidth used.
    long_run_variance : float
        Estimated long-run variance.
    detrend : str
        Detrending specification.
    nobs : int
        Number of observations.
    """
    statistic: float
    critical_values: dict
    bandwidth: float
    long_run_variance: float
    detrend: str
    nobs: int
    
    def __repr__(self) -> str:
        reject_1 = self.statistic > self.critical_values[1]
        reject_5 = self.statistic > self.critical_values[5]
        reject_10 = self.statistic > self.critical_values[10]
        
        stars = ""
        if reject_1:
            stars = "***"
        elif reject_5:
            stars = "**"
        elif reject_10:
            stars = "*"
        
        return (
            f"\n"
            f"{'='*55}\n"
            f"         Standard KPSS Test for Stationarity\n"
            f"       Kwiatkowski, Phillips, Schmidt, Shin (1992)\n"
            f"{'='*55}\n\n"
            f"Null: Series is stationary\n"
            f"Alternative: Series has a unit root\n\n"
            f"Detrending:  {'Level' if self.detrend == 'c' else 'Trend'}\n"
            f"Observations: {self.nobs}\n\n"
            f"{'-'*55}\n"
            f"Test Statistic: {self.statistic:.6f} {stars}\n"
            f"{'-'*55}\n\n"
            f"Critical Values:\n"
            f"  1%:   {self.critical_values[1]:.4f}\n"
            f"  5%:   {self.critical_values[5]:.4f}\n"
            f"  10%:  {self.critical_values[10]:.4f}\n\n"
            f"Bandwidth: {self.bandwidth:.2f}\n"
            f"Long-run variance: {self.long_run_variance:.6f}\n\n"
            f"{'='*55}\n"
            f"Significance codes: *** 1%  ** 5%  * 10%\n"
        )


def standard_kpss_test(y: np.ndarray,
                       detrend: str = "c",
                       kernel: str = "qs",
                       bandwidth: Optional[float] = None) -> StandardKPSSResult:
    """
    Perform the standard KPSS test for stationarity.
    
    This implements the original KPSS test from Kwiatkowski, Phillips, 
    Schmidt, and Shin (1992) for comparison with the Modified KPSS test.
    
    Parameters
    ----------
    y : np.ndarray
        The time series data.
    detrend : str, optional
        "c" for level, "ct" for trend. Default is "c".
    kernel : str, optional
        Kernel function. Default is "qs".
    bandwidth : float or None, optional
        Bandwidth. Default is None (automatic).
        
    Returns
    -------
    StandardKPSSResult
        Test results.
        
    Notes
    -----
    The standard KPSS test tests:
        H₀: Series is stationary (I(0))
        H₁: Series has a unit root (I(1))
    
    Unlike the Modified KPSS test, the standard KPSS test has size distortion
    problems under near-integrated null hypotheses as shown by Müller (2005).
    
    References
    ----------
    Kwiatkowski, D., Phillips, P., Schmidt, P., & Shin, Y. (1992). Testing 
    the null hypothesis of stationarity against the alternative of a unit 
    root. Journal of Econometrics, 54, 159-178.
    """
    y = np.asarray(y, dtype=float)
    T = len(y)
    
    if T < 10:
        raise ValueError(f"Sample size too small: {T}")
    
    # Demean or detrend
    if detrend == "c":
        residuals = y - np.mean(y)
    elif detrend == "ct":
        time_idx = np.arange(1, T + 1)
        X = np.column_stack([np.ones(T), time_idx])
        beta = np.linalg.lstsq(X, y, rcond=None)[0]
        residuals = y - X @ beta
    else:
        raise ValueError(f"detrend must be 'c' or 'ct', got {detrend}")
    
    # Compute bandwidth
    if bandwidth is None:
        bw = newey_west_bandwidth(residuals, kernel)
    else:
        bw = bandwidth
    
    # Compute long-run variance
    lrv = long_run_variance(residuals, kernel, bw)
    
    # Compute KPSS statistic
    partial_sums = compute_partial_sums(residuals)
    numerator = np.sum(partial_sums ** 2) / (T ** 2)
    statistic = numerator / lrv
    
    # Critical values
    cv = STANDARD_KPSS_CRITICAL_VALUES[detrend]
    
    return StandardKPSSResult(
        statistic=statistic,
        critical_values=cv,
        bandwidth=bw,
        long_run_variance=lrv,
        detrend=detrend,
        nobs=T,
    )
