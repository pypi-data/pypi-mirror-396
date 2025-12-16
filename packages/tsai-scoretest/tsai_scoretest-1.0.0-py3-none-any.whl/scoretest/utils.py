"""
Utility Functions for Score Test Computations.

This module provides helper functions for computing OLS residuals,
autocorrelation estimates, and other quantities needed for the
score test from Tsai (1986).
"""

import numpy as np
from scipy.linalg import inv
from typing import Tuple, Optional, Union


def ols_residuals(
    y: np.ndarray,
    X: np.ndarray,
    return_all: bool = False
) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray, float]]:
    """
    Compute OLS residuals.
    
    Under the null hypothesis H_0: ρ = 0 and λ = λ*, the MLE of β
    is the OLS estimator.
    
    Parameters
    ----------
    y : array-like of shape (T,)
        Response variable.
    X : array-like of shape (T, p)
        Design matrix.
    return_all : bool, default=False
        If True, also return β̂ and σ̂².
        
    Returns
    -------
    residuals : np.ndarray of shape (T,)
        OLS residuals ê_t = y_t - x_t'β̂
    beta_hat : np.ndarray, optional
        OLS coefficient estimates (only if return_all=True)
    sigma2_hat : float, optional
        MLE of error variance (only if return_all=True)
        
    Examples
    --------
    >>> import numpy as np
    >>> from scoretest.utils import ols_residuals
    >>> 
    >>> np.random.seed(42)
    >>> T = 100
    >>> X = np.column_stack([np.ones(T), np.random.randn(T)])
    >>> y = X @ [1, 0.5] + np.random.randn(T)
    >>> 
    >>> residuals = ols_residuals(y, X)
    >>> print(f"Sum of residuals: {np.sum(residuals):.6f}")  # Should be ~0
    """
    y = np.asarray(y).flatten()
    X = np.asarray(X)
    
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    
    T = len(y)
    
    # OLS: β̂ = (X'X)⁻¹X'y
    XtX = X.T @ X
    XtX_inv = inv(XtX)
    beta_hat = XtX_inv @ (X.T @ y)
    
    # Residuals: ê = y - Xβ̂
    residuals = y - X @ beta_hat
    
    # MLE variance: σ̂² = Σê²/T
    sigma2_hat = np.sum(residuals**2) / T
    
    if return_all:
        return residuals, beta_hat, sigma2_hat
    return residuals


def compute_rho_hat(residuals: np.ndarray) -> float:
    """
    Compute the autocorrelation coefficient estimate ρ̂.
    
    From Equation (2.5) of Tsai (1986):
        ρ̂ = Σ'ê_t ê_{t-1} / Σê_t²
        
    where:
        Σ' is summation over t = 2, ..., T
        Σ is summation over t = 1, ..., T
    
    Parameters
    ----------
    residuals : array-like of shape (T,)
        OLS residuals.
        
    Returns
    -------
    rho_hat : float
        Estimated first-order autocorrelation coefficient.
        
    Examples
    --------
    >>> import numpy as np
    >>> from scoretest.utils import compute_rho_hat
    >>> 
    >>> # Simulate AR(1) residuals
    >>> np.random.seed(42)
    >>> T = 100
    >>> rho = 0.5
    >>> residuals = np.zeros(T)
    >>> residuals[0] = np.random.randn()
    >>> for t in range(1, T):
    ...     residuals[t] = rho * residuals[t-1] + np.random.randn()
    >>> 
    >>> rho_hat = compute_rho_hat(residuals)
    >>> print(f"True ρ: {rho}, Estimated ρ̂: {rho_hat:.4f}")
    """
    residuals = np.asarray(residuals).flatten()
    
    # Σ'ê_t ê_{t-1} for t = 2, ..., T
    numerator = np.sum(residuals[1:] * residuals[:-1])
    
    # Σê_t² for t = 1, ..., T
    denominator = np.sum(residuals**2)
    
    rho_hat = numerator / denominator
    
    return rho_hat


def compute_variance_vector(
    residuals: np.ndarray,
    sigma2_hat: Optional[float] = None
) -> np.ndarray:
    """
    Compute the V vector for heteroscedasticity testing.
    
    V is a T × 1 vector with element ê_t²/σ̂².
    
    Parameters
    ----------
    residuals : array-like of shape (T,)
        OLS residuals.
    sigma2_hat : float, optional
        Error variance estimate. If None, computed as MLE.
        
    Returns
    -------
    V : np.ndarray of shape (T,)
        Vector of squared standardized residuals.
        
    Examples
    --------
    >>> import numpy as np
    >>> from scoretest.utils import compute_variance_vector
    >>> 
    >>> residuals = np.random.randn(100)
    >>> V = compute_variance_vector(residuals)
    >>> print(f"Mean of V: {np.mean(V):.4f}")  # Should be ~1 under H0
    """
    residuals = np.asarray(residuals).flatten()
    T = len(residuals)
    
    if sigma2_hat is None:
        sigma2_hat = np.sum(residuals**2) / T
    
    V = residuals**2 / sigma2_hat
    
    return V


def durbin_watson_statistic(residuals: np.ndarray) -> float:
    """
    Compute the Durbin-Watson statistic for comparison.
    
    DW = Σ(ê_t - ê_{t-1})² / Σê_t²
    
    The DW statistic is related to ρ̂ by: DW ≈ 2(1 - ρ̂)
    
    Parameters
    ----------
    residuals : array-like of shape (T,)
        OLS residuals.
        
    Returns
    -------
    dw : float
        Durbin-Watson test statistic.
        
    References
    ----------
    Durbin, J. & Watson, G.S. (1950, 1951, 1971). Biometrika.
    """
    residuals = np.asarray(residuals).flatten()
    
    # Σ(ê_t - ê_{t-1})² for t = 2, ..., T
    diff_sq = np.sum((residuals[1:] - residuals[:-1])**2)
    
    # Σê_t²
    sum_sq = np.sum(residuals**2)
    
    dw = diff_sq / sum_sq
    
    return dw


def breusch_godfrey_statistic(
    y: np.ndarray,
    X: np.ndarray,
    order: int = 1
) -> Tuple[float, float, int]:
    """
    Compute Breusch-Godfrey LM test statistic for autocorrelation.
    
    This is an alternative to the score test for autocorrelation
    that allows for higher-order serial correlation.
    
    Parameters
    ----------
    y : array-like of shape (T,)
        Response variable.
    X : array-like of shape (T, p)
        Design matrix.
    order : int, default=1
        Order of autocorrelation to test.
        
    Returns
    -------
    LM : float
        Breusch-Godfrey LM statistic.
    p_value : float
        P-value from χ²(order) distribution.
    df : int
        Degrees of freedom.
        
    References
    ----------
    Breusch, T.S. (1978). Econometrica, 46, 1251-1271.
    Godfrey, L.G. (1978). Econometrica, 46, 1293-1301.
    """
    from scipy import stats
    
    y = np.asarray(y).flatten()
    X = np.asarray(X)
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    
    T = len(y)
    
    # Get OLS residuals
    residuals = ols_residuals(y, X)
    
    # Create lagged residuals matrix
    Z_lags = np.zeros((T, order))
    for i in range(order):
        Z_lags[i+1:, i] = residuals[:-(i+1)]
    
    # Auxiliary regression: ê on X and lagged residuals
    X_aug = np.hstack([X, Z_lags])
    
    # Regression of ê on X_aug
    XtX = X_aug.T @ X_aug
    try:
        XtX_inv = inv(XtX)
        beta_aug = XtX_inv @ (X_aug.T @ residuals)
        resid_aux = residuals - X_aug @ beta_aug
        
        # R² from auxiliary regression
        SSR = np.sum(resid_aux**2)
        SST = np.sum(residuals**2)
        R2 = 1 - SSR / SST
        
        # LM = T × R²
        LM = T * R2
    except np.linalg.LinAlgError:
        LM = 0.0
    
    p_value = 1 - stats.chi2.cdf(LM, df=order)
    
    return LM, p_value, order


def center_matrix(D: np.ndarray) -> np.ndarray:
    """
    Center a matrix by subtracting column means.
    
    Computes D̄ = D - 11'D/T as in Tsai (1986).
    
    Parameters
    ----------
    D : np.ndarray of shape (T, q)
        Matrix to center.
        
    Returns
    -------
    D_bar : np.ndarray of shape (T, q)
        Centered matrix.
    """
    return D - np.mean(D, axis=0)


def validate_inputs(
    y: np.ndarray,
    X: np.ndarray,
    Z: Optional[np.ndarray] = None
) -> Tuple[np.ndarray, np.ndarray, Optional[np.ndarray]]:
    """
    Validate and format input arrays.
    
    Parameters
    ----------
    y : array-like
        Response variable.
    X : array-like
        Design matrix.
    Z : array-like, optional
        Heteroscedasticity variables.
        
    Returns
    -------
    y : np.ndarray of shape (T,)
        Validated response.
    X : np.ndarray of shape (T, p)
        Validated design matrix.
    Z : np.ndarray or None
        Validated Z matrix.
        
    Raises
    ------
    ValueError
        If dimensions are inconsistent.
    """
    y = np.asarray(y).flatten()
    X = np.asarray(X)
    
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    
    T = len(y)
    
    if X.shape[0] != T:
        raise ValueError(f"X has {X.shape[0]} rows but y has {T} elements")
    
    if Z is not None:
        Z = np.asarray(Z)
        if Z.ndim == 1:
            Z = Z.reshape(-1, 1)
        if Z.shape[0] != T:
            raise ValueError(f"Z has {Z.shape[0]} rows but y has {T} elements")
    
    return y, X, Z


def summary_statistics(y: np.ndarray, X: np.ndarray) -> dict:
    """
    Compute summary statistics for the regression.
    
    Parameters
    ----------
    y : array-like
        Response variable.
    X : array-like
        Design matrix.
        
    Returns
    -------
    stats : dict
        Dictionary with summary statistics.
    """
    y = np.asarray(y).flatten()
    X = np.asarray(X)
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    
    T, p = X.shape
    
    residuals, beta_hat, sigma2_hat = ols_residuals(y, X, return_all=True)
    rho_hat = compute_rho_hat(residuals)
    dw = durbin_watson_statistic(residuals)
    
    # R-squared
    y_mean = np.mean(y)
    SST = np.sum((y - y_mean)**2)
    SSR = np.sum(residuals**2)
    R2 = 1 - SSR / SST
    
    # Adjusted R-squared
    R2_adj = 1 - (1 - R2) * (T - 1) / (T - p)
    
    return {
        'T': T,
        'p': p,
        'beta_hat': beta_hat,
        'sigma2_hat': sigma2_hat,
        'sigma_hat': np.sqrt(sigma2_hat),
        'rho_hat': rho_hat,
        'R2': R2,
        'R2_adj': R2_adj,
        'durbin_watson': dw,
        'residual_mean': np.mean(residuals),
        'residual_std': np.std(residuals),
        'y_mean': y_mean,
        'y_std': np.std(y)
    }
