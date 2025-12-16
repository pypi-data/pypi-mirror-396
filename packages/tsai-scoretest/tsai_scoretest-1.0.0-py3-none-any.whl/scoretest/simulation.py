"""
Monte Carlo Simulation for Critical Values.

This module provides simulation-based methods to compute critical values
and verify the asymptotic distribution of the score test statistics
from Tsai (1986).

Under the null hypothesis H_0: ρ = 0 and λ = λ*:
    S_1 ~ χ²(1)
    S_2 ~ χ²(q)
    S = S_1 + S_2 ~ χ²(q + 1)

The simulations generate data under H_0 and compute empirical distributions
of the test statistics for finite sample sizes.

Reference:
    Tsai, C.-L. (1986). Biometrika, 73(2), 455-460.
"""

import numpy as np
from scipy import stats
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple, Union
import warnings
from concurrent.futures import ProcessPoolExecutor, as_completed
import time


@dataclass
class SimulationResults:
    """
    Container for Monte Carlo simulation results.
    
    Attributes
    ----------
    n_simulations : int
        Number of Monte Carlo replications
    sample_size : int
        Sample size T used in simulations
    q : int
        Number of heteroscedasticity parameters
    
    S_statistics : np.ndarray
        Simulated joint test statistics S
    S1_statistics : np.ndarray
        Simulated autocorrelation test statistics S_1
    S2_statistics : np.ndarray
        Simulated heteroscedasticity test statistics S_2
    
    critical_values_S : dict
        Critical values for S at various significance levels
    critical_values_S1 : dict
        Critical values for S_1 at various significance levels
    critical_values_S2 : dict
        Critical values for S_2 at various significance levels
    
    rejection_rates : dict
        Empirical rejection rates at theoretical critical values
    
    computation_time : float
        Total computation time in seconds
    """
    n_simulations: int
    sample_size: int
    q: int
    
    S_statistics: np.ndarray
    S1_statistics: np.ndarray
    S2_statistics: np.ndarray
    
    critical_values_S: Dict[float, float]
    critical_values_S1: Dict[float, float]
    critical_values_S2: Dict[float, float]
    
    rejection_rates: Dict[str, Dict[float, float]]
    
    computation_time: float
    
    def __repr__(self) -> str:
        return self._format_output()
    
    def _format_output(self) -> str:
        """Format output for publication-quality display."""
        width = 75
        line = "=" * width
        thin_line = "-" * width
        
        output = [
            "",
            line,
            "Monte Carlo Simulation Results for Tsai (1986) Score Test",
            line,
            "",
            f"Number of Simulations: {self.n_simulations:,}",
            f"Sample Size (T): {self.sample_size}",
            f"Heteroscedasticity Parameters (q): {self.q}",
            f"Computation Time: {self.computation_time:.2f} seconds",
            "",
            thin_line,
            "Empirical Critical Values",
            thin_line,
            "",
            "  Significance Level    S (df={:d})    S₁ (df=1)    S₂ (df={:d})".format(
                self.q + 1, self.q),
            "  " + "-" * 65,
        ]
        
        for alpha in sorted(self.critical_values_S.keys(), reverse=True):
            output.append(
                f"  α = {alpha:5.3f}           {self.critical_values_S[alpha]:8.4f}     "
                f"{self.critical_values_S1[alpha]:8.4f}     {self.critical_values_S2[alpha]:8.4f}"
            )
        
        output.extend([
            "",
            thin_line,
            "Comparison with Asymptotic χ² Critical Values",
            thin_line,
            "",
            "  Significance Level    Empirical    Asymptotic    Difference",
            "  " + "-" * 60,
        ])
        
        for alpha in sorted(self.critical_values_S.keys(), reverse=True):
            asymp_cv = stats.chi2.ppf(1 - alpha, self.q + 1)
            emp_cv = self.critical_values_S[alpha]
            diff = emp_cv - asymp_cv
            output.append(
                f"  α = {alpha:5.3f} (S)        {emp_cv:8.4f}      {asymp_cv:8.4f}       "
                f"{diff:+7.4f}"
            )
        
        output.extend([
            "",
            thin_line,
            "Empirical Rejection Rates at Asymptotic Critical Values",
            thin_line,
            "",
            "  Nominal Level    S Rate    S₁ Rate    S₂ Rate",
            "  " + "-" * 50,
        ])
        
        for alpha in sorted(self.rejection_rates["S"].keys(), reverse=True):
            output.append(
                f"  α = {alpha:5.3f}        {self.rejection_rates['S'][alpha]:6.4f}     "
                f"{self.rejection_rates['S1'][alpha]:6.4f}      {self.rejection_rates['S2'][alpha]:6.4f}"
            )
        
        output.extend([
            "",
            thin_line,
            "Summary Statistics of Test Statistics",
            thin_line,
            "",
            "  Statistic    Mean      Std Dev    Skewness    Kurtosis",
            "  " + "-" * 55,
            f"  S           {np.mean(self.S_statistics):8.4f}   {np.std(self.S_statistics):8.4f}    "
            f"{stats.skew(self.S_statistics):8.4f}    {stats.kurtosis(self.S_statistics):8.4f}",
            f"  S₁          {np.mean(self.S1_statistics):8.4f}   {np.std(self.S1_statistics):8.4f}    "
            f"{stats.skew(self.S1_statistics):8.4f}    {stats.kurtosis(self.S1_statistics):8.4f}",
            f"  S₂          {np.mean(self.S2_statistics):8.4f}   {np.std(self.S2_statistics):8.4f}    "
            f"{stats.skew(self.S2_statistics):8.4f}    {stats.kurtosis(self.S2_statistics):8.4f}",
            "",
            "  Theoretical (χ²):",
            f"  χ²({self.q+1})        {self.q+1:8.4f}   {np.sqrt(2*(self.q+1)):8.4f}    "
            f"{np.sqrt(8/(self.q+1)):8.4f}    {12/(self.q+1):8.4f}",
            "",
            line,
        ]
        )
        
        return "\n".join(output)
    
    def summary(self) -> str:
        """Return publication-ready summary."""
        return self._format_output()
    
    def to_latex_table(self) -> str:
        """Generate LaTeX table of critical values."""
        lines = [
            r"\begin{table}[htbp]",
            r"\centering",
            r"\caption{Monte Carlo Critical Values for Tsai (1986) Score Test}",
            r"\label{tab:critical_values}",
            r"\begin{tabular}{lccc}",
            r"\toprule",
            r"Significance Level & $S$ (df={}) & $S_1$ (df=1) & $S_2$ (df={}) \\".format(
                self.q + 1, self.q),
            r"\midrule",
        ]
        
        for alpha in sorted(self.critical_values_S.keys(), reverse=True):
            lines.append(
                r"$\alpha = {:.3f}$ & {:.4f} & {:.4f} & {:.4f} \\".format(
                    alpha,
                    self.critical_values_S[alpha],
                    self.critical_values_S1[alpha],
                    self.critical_values_S2[alpha]
                )
            )
        
        lines.extend([
            r"\bottomrule",
            r"\end{tabular}",
            r"\begin{tablenotes}",
            r"\small",
            r"\item Notes: Based on {:,} Monte Carlo simulations with $T = {}$.".format(
                self.n_simulations, self.sample_size),
            r"\end{tablenotes}",
            r"\end{table}",
        ])
        
        return "\n".join(lines)


def _single_simulation(
    args: Tuple[int, int, int, int, Optional[int]]
) -> Tuple[float, float, float]:
    """
    Run a single simulation replication.
    
    This is a helper function for parallel execution.
    """
    T, p, q, seed, _ = args
    
    # Set seed for reproducibility
    rng = np.random.RandomState(seed)
    
    # Generate data under H_0: ρ = 0, λ = λ* (homoscedastic, no autocorrelation)
    X = np.column_stack([np.ones(T)] + [rng.randn(T) for _ in range(p - 1)])
    beta = rng.randn(p)
    e = rng.randn(T)  # i.i.d. N(0,1) errors
    y = X @ beta + e
    
    # Compute OLS residuals
    XtX_inv = np.linalg.inv(X.T @ X)
    beta_hat = XtX_inv @ (X.T @ y)
    residuals = y - X @ beta_hat
    sigma2_hat = np.sum(residuals**2) / T
    
    # Compute ρ̂ (Equation 2.5)
    rho_hat = np.sum(residuals[1:] * residuals[:-1]) / np.sum(residuals**2)
    
    # Compute S_1 (Equation 2.4)
    S1 = (T * rho_hat)**2 / (T - 1)
    
    # Create Z matrix (time trend for heteroscedasticity)
    Z = np.column_stack([np.arange(1, T + 1)**j for j in range(1, q + 1)])
    
    # Compute D and D̄
    D = Z.copy()  # For exponential weight, ∂w/∂λ|_{λ=0} = z
    D_bar = D - np.mean(D, axis=0)
    
    # Compute V
    V = residuals**2 / sigma2_hat
    
    # Compute S_2
    DtD = D_bar.T @ D_bar
    try:
        DtD_inv = np.linalg.inv(DtD)
    except np.linalg.LinAlgError:
        DtD_inv = np.linalg.pinv(DtD)
    
    DtV = D_bar.T @ V
    S2 = 0.5 * (DtV.T @ DtD_inv @ DtV)
    
    # Joint statistic
    S = S1 + S2
    
    return S, S1, S2


def simulate_critical_values(
    sample_size: int = 100,
    q: int = 1,
    n_simulations: int = 10000,
    p: int = 2,
    significance_levels: Optional[List[float]] = None,
    seed: Optional[int] = None,
    n_jobs: int = 1,
    verbose: bool = True
) -> SimulationResults:
    """
    Simulate critical values for the Tsai (1986) score test.
    
    Generates data under H_0 (no autocorrelation, homoscedasticity) and
    computes empirical distributions of S, S_1, and S_2.
    
    Parameters
    ----------
    sample_size : int, default=100
        Sample size T for each simulation.
    q : int, default=1
        Number of heteroscedasticity parameters.
    n_simulations : int, default=10000
        Number of Monte Carlo replications.
    p : int, default=2
        Number of regression coefficients (including intercept).
    significance_levels : list of float, optional
        Significance levels for critical values. 
        Default is [0.01, 0.05, 0.10].
    seed : int, optional
        Random seed for reproducibility.
    n_jobs : int, default=1
        Number of parallel jobs. Use -1 for all cores.
    verbose : bool, default=True
        Print progress messages.
        
    Returns
    -------
    results : SimulationResults
        Container with all simulation results.
        
    Examples
    --------
    >>> from scoretest import simulate_critical_values
    >>> 
    >>> # Run simulation
    >>> results = simulate_critical_values(
    ...     sample_size=100,
    ...     q=1,
    ...     n_simulations=10000,
    ...     seed=42
    ... )
    >>> print(results)
    >>> 
    >>> # Get critical value for α = 0.05
    >>> cv_05 = results.critical_values_S[0.05]
    >>> print(f"Critical value at α=0.05: {cv_05:.4f}")
    
    Notes
    -----
    Under H_0, the asymptotic distributions are:
        S_1 ~ χ²(1)
        S_2 ~ χ²(q)  
        S ~ χ²(q + 1)
    
    The simulation verifies these asymptotic results and provides
    finite-sample critical values.
    """
    if significance_levels is None:
        significance_levels = [0.01, 0.05, 0.10]
    
    if seed is not None:
        np.random.seed(seed)
    
    start_time = time.time()
    
    if verbose:
        print(f"Running {n_simulations:,} Monte Carlo simulations...")
        print(f"Sample size T = {sample_size}, q = {q}, p = {p}")
    
    # Generate seeds for each simulation
    seeds = np.random.randint(0, 2**31 - 1, size=n_simulations)
    
    # Prepare arguments for parallel execution
    args_list = [(sample_size, p, q, seeds[i], i) for i in range(n_simulations)]
    
    # Run simulations
    S_stats = np.zeros(n_simulations)
    S1_stats = np.zeros(n_simulations)
    S2_stats = np.zeros(n_simulations)
    
    if n_jobs == 1:
        # Sequential execution
        for i, args in enumerate(args_list):
            S_stats[i], S1_stats[i], S2_stats[i] = _single_simulation(args)
            
            if verbose and (i + 1) % (n_simulations // 10) == 0:
                pct = 100 * (i + 1) / n_simulations
                print(f"  Progress: {pct:.0f}%")
    else:
        # Parallel execution
        if n_jobs == -1:
            import os
            n_jobs = os.cpu_count()
        
        with ProcessPoolExecutor(max_workers=n_jobs) as executor:
            futures = {executor.submit(_single_simulation, args): i 
                      for i, args in enumerate(args_list)}
            
            completed = 0
            for future in as_completed(futures):
                i = futures[future]
                S_stats[i], S1_stats[i], S2_stats[i] = future.result()
                completed += 1
                
                if verbose and completed % (n_simulations // 10) == 0:
                    pct = 100 * completed / n_simulations
                    print(f"  Progress: {pct:.0f}%")
    
    # Compute empirical critical values
    critical_values_S = {}
    critical_values_S1 = {}
    critical_values_S2 = {}
    
    for alpha in significance_levels:
        critical_values_S[alpha] = np.percentile(S_stats, 100 * (1 - alpha))
        critical_values_S1[alpha] = np.percentile(S1_stats, 100 * (1 - alpha))
        critical_values_S2[alpha] = np.percentile(S2_stats, 100 * (1 - alpha))
    
    # Compute rejection rates at asymptotic critical values
    rejection_rates = {"S": {}, "S1": {}, "S2": {}}
    
    for alpha in significance_levels:
        # Asymptotic critical values
        cv_S = stats.chi2.ppf(1 - alpha, q + 1)
        cv_S1 = stats.chi2.ppf(1 - alpha, 1)
        cv_S2 = stats.chi2.ppf(1 - alpha, q)
        
        # Empirical rejection rates
        rejection_rates["S"][alpha] = np.mean(S_stats > cv_S)
        rejection_rates["S1"][alpha] = np.mean(S1_stats > cv_S1)
        rejection_rates["S2"][alpha] = np.mean(S2_stats > cv_S2)
    
    computation_time = time.time() - start_time
    
    if verbose:
        print(f"Simulation completed in {computation_time:.2f} seconds")
    
    return SimulationResults(
        n_simulations=n_simulations,
        sample_size=sample_size,
        q=q,
        S_statistics=S_stats,
        S1_statistics=S1_stats,
        S2_statistics=S2_stats,
        critical_values_S=critical_values_S,
        critical_values_S1=critical_values_S1,
        critical_values_S2=critical_values_S2,
        rejection_rates=rejection_rates,
        computation_time=computation_time
    )


def simulate_power(
    sample_size: int = 100,
    rho_values: Optional[List[float]] = None,
    lambda_values: Optional[List[float]] = None,
    q: int = 1,
    n_simulations: int = 1000,
    p: int = 2,
    alpha: float = 0.05,
    seed: Optional[int] = None,
    verbose: bool = True
) -> Dict[str, np.ndarray]:
    """
    Simulate power of the score test under alternatives.
    
    Parameters
    ----------
    sample_size : int, default=100
        Sample size T.
    rho_values : list of float, optional
        Values of ρ for power against autocorrelation.
        Default is [0, 0.1, 0.2, 0.3, 0.4, 0.5].
    lambda_values : list of float, optional
        Values of λ for power against heteroscedasticity.
        Default is [0, 0.1, 0.2, 0.3, 0.4, 0.5].
    q : int, default=1
        Number of heteroscedasticity parameters.
    n_simulations : int, default=1000
        Number of Monte Carlo replications.
    p : int, default=2
        Number of regression coefficients.
    alpha : float, default=0.05
        Significance level.
    seed : int, optional
        Random seed.
    verbose : bool, default=True
        Print progress messages.
        
    Returns
    -------
    results : dict
        Dictionary with power curves for S, S_1, and S_2.
    """
    if rho_values is None:
        rho_values = [0, 0.1, 0.2, 0.3, 0.4, 0.5]
    if lambda_values is None:
        lambda_values = [0, 0.1, 0.2, 0.3, 0.4, 0.5]
    
    if seed is not None:
        np.random.seed(seed)
    
    # Critical values from asymptotic distributions
    cv_S = stats.chi2.ppf(1 - alpha, q + 1)
    cv_S1 = stats.chi2.ppf(1 - alpha, 1)
    cv_S2 = stats.chi2.ppf(1 - alpha, q)
    
    T = sample_size
    
    # Power against autocorrelation (ρ ≠ 0)
    power_S1 = np.zeros(len(rho_values))
    power_S_rho = np.zeros(len(rho_values))
    
    if verbose:
        print("Computing power against autocorrelation...")
    
    for i, rho in enumerate(rho_values):
        rejections_S1 = 0
        rejections_S = 0
        
        for _ in range(n_simulations):
            # Generate X
            X = np.column_stack([np.ones(T)] + [np.random.randn(T) for _ in range(p - 1)])
            beta = np.zeros(p)
            
            # Generate AR(1) errors with autocorrelation ρ
            e = np.zeros(T)
            e[0] = np.random.randn()
            for t in range(1, T):
                e[t] = rho * e[t-1] + np.random.randn()
            
            y = X @ beta + e
            
            # Compute test statistics
            XtX_inv = np.linalg.inv(X.T @ X)
            beta_hat = XtX_inv @ (X.T @ y)
            residuals = y - X @ beta_hat
            sigma2_hat = np.sum(residuals**2) / T
            
            rho_hat = np.sum(residuals[1:] * residuals[:-1]) / np.sum(residuals**2)
            S1 = (T * rho_hat)**2 / (T - 1)
            
            Z = np.arange(1, T + 1).reshape(-1, 1)
            D = Z.copy()
            D_bar = D - np.mean(D, axis=0)
            V = residuals**2 / sigma2_hat
            DtD_inv = np.linalg.inv(D_bar.T @ D_bar)
            DtV = D_bar.T @ V
            S2 = 0.5 * (DtV.T @ DtD_inv @ DtV)
            S = S1 + S2
            
            if S1 > cv_S1:
                rejections_S1 += 1
            if S > cv_S:
                rejections_S += 1
        
        power_S1[i] = rejections_S1 / n_simulations
        power_S_rho[i] = rejections_S / n_simulations
    
    # Power against heteroscedasticity (λ ≠ 0)
    power_S2 = np.zeros(len(lambda_values))
    power_S_lambda = np.zeros(len(lambda_values))
    
    if verbose:
        print("Computing power against heteroscedasticity...")
    
    for i, lam in enumerate(lambda_values):
        rejections_S2 = 0
        rejections_S = 0
        
        for _ in range(n_simulations):
            # Generate X
            X = np.column_stack([np.ones(T)] + [np.random.randn(T) for _ in range(p - 1)])
            beta = np.zeros(p)
            
            # Generate heteroscedastic errors: var(e_t) = exp(λ * t/T)
            t_scaled = np.arange(1, T + 1) / T
            variances = np.exp(lam * t_scaled)
            e = np.random.randn(T) * np.sqrt(variances)
            
            y = X @ beta + e
            
            # Compute test statistics
            XtX_inv = np.linalg.inv(X.T @ X)
            beta_hat = XtX_inv @ (X.T @ y)
            residuals = y - X @ beta_hat
            sigma2_hat = np.sum(residuals**2) / T
            
            rho_hat = np.sum(residuals[1:] * residuals[:-1]) / np.sum(residuals**2)
            S1 = (T * rho_hat)**2 / (T - 1)
            
            Z = np.arange(1, T + 1).reshape(-1, 1)
            D = Z.copy()
            D_bar = D - np.mean(D, axis=0)
            V = residuals**2 / sigma2_hat
            DtD_inv = np.linalg.inv(D_bar.T @ D_bar)
            DtV = D_bar.T @ V
            S2 = 0.5 * (DtV.T @ DtD_inv @ DtV)
            S = S1 + S2
            
            if S2 > cv_S2:
                rejections_S2 += 1
            if S > cv_S:
                rejections_S += 1
        
        power_S2[i] = rejections_S2 / n_simulations
        power_S_lambda[i] = rejections_S / n_simulations
    
    return {
        "rho_values": np.array(rho_values),
        "lambda_values": np.array(lambda_values),
        "power_S1": power_S1,
        "power_S_rho": power_S_rho,
        "power_S2": power_S2,
        "power_S_lambda": power_S_lambda
    }
