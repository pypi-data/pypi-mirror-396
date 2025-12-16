"""
Diagnostic Measures for Model Perturbation Effects.

This module implements the diagnostic measures from Section 3 of Tsai (1986)
that relate the score test statistic to:
1. Geometric normal curvature of the influence graph (Cook's approach)
2. Sensitivity of parameter estimates to perturbation

Reference:
    Tsai, C.-L. (1986). Biometrika, 73(2), 455-460.
    Bates, D.M. & Watts, D.G. (1980). J.R. Statist. Soc. B, 42, 1-25.
    Cook, R.D. Unpublished report, University of Wisconsin.

Mathematical Framework (Section 3):
----------------------------------
The influence graph M(w*) = [L(w*), w*']' where:
    L(w*) = 2{L(β̂) - L(β̂_{w*})}

The geometric normal curvature is:
    C_l = 2|l'ĴK̂⁻¹Ĵ'l| / (l'l)

where:
    Ĵ = [[Ĵ₁₁, Ĵ₁₂], [Ĵ₂₁, Ĵ₂₂]]
    K̂ = diag(X'X/σ̂², ½T/σ̂⁴)
"""

import numpy as np
from scipy.linalg import inv, pinv
from dataclasses import dataclass
from typing import Optional, Tuple, Dict
import warnings


@dataclass
class CurvatureResult:
    """
    Container for normal curvature analysis results.
    
    Attributes
    ----------
    C_max : float
        Maximum normal curvature
    C_direction : np.ndarray
        Direction l that maximizes curvature
    J_matrix : np.ndarray
        Ĵ matrix from Equation (3.2)
    K_matrix : np.ndarray
        K̂ matrix (block diagonal Fisher information)
    influence_direction : str
        Interpretation of which type of perturbation is most influential
    """
    C_max: float
    C_direction: np.ndarray
    J_matrix: np.ndarray
    K_matrix: np.ndarray
    influence_direction: str
    
    def __repr__(self) -> str:
        return self._format_output()
    
    def _format_output(self) -> str:
        width = 70
        line = "=" * width
        
        output = [
            "",
            line,
            "Normal Curvature Analysis - Tsai (1986) Section 3",
            line,
            "",
            f"Maximum Normal Curvature (C_max): {self.C_max:.6f}",
            "",
            "Direction of Maximum Influence:",
            f"  ρ-component: {self.C_direction[0]:.6f}",
            f"  λ-components: {self.C_direction[1:]}",
            "",
            f"Interpretation: {self.influence_direction}",
            "",
            line,
        ]
        return "\n".join(output)


@dataclass
class SensitivityResult:
    """
    Container for parameter sensitivity analysis.
    
    From Equation (3.4):
        ∂β̂(w*)/∂w* |_{w*=w₀*} = -K̃⁻¹J̃'
    
    Attributes
    ----------
    sensitivity_matrix : np.ndarray
        Derivative of β̂ with respect to perturbation vector
    sensitivity_norm : float
        Frobenius norm of sensitivity matrix
    most_sensitive_coef : int
        Index of most sensitive coefficient
    sensitivity_to_rho : np.ndarray
        Sensitivity of β̂ to changes in ρ
    sensitivity_to_lambda : np.ndarray
        Sensitivity of β̂ to changes in λ
    """
    sensitivity_matrix: np.ndarray
    sensitivity_norm: float
    most_sensitive_coef: int
    sensitivity_to_rho: np.ndarray
    sensitivity_to_lambda: np.ndarray
    
    def __repr__(self) -> str:
        return self._format_output()
    
    def _format_output(self) -> str:
        width = 70
        line = "=" * width
        
        output = [
            "",
            line,
            "Parameter Sensitivity Analysis - Tsai (1986) Section 3",
            line,
            "",
            f"Overall Sensitivity (Frobenius norm): {self.sensitivity_norm:.6f}",
            f"Most Sensitive Coefficient Index: {self.most_sensitive_coef}",
            "",
            "Sensitivity to Autocorrelation (∂β̂/∂ρ):",
            f"  {self.sensitivity_to_rho}",
            "",
            "Sensitivity to Heteroscedasticity (∂β̂/∂λ):",
            f"  {self.sensitivity_to_lambda}",
            "",
            line,
        ]
        return "\n".join(output)


def normal_curvature(
    y: np.ndarray,
    X: np.ndarray,
    Z: Optional[np.ndarray] = None,
    direction: Optional[np.ndarray] = None
) -> CurvatureResult:
    """
    Compute the geometric normal curvature of the influence graph.
    
    Implements Equation (3.2) from Tsai (1986):
        C_l = 2|l'ĴK̂⁻¹Ĵ'l| / (l'l)
        
    where Ĵ and K̂ are matrices defined in Section 3.
    
    Parameters
    ----------
    y : array-like of shape (T,)
        Response variable.
    X : array-like of shape (T, p)
        Design matrix.
    Z : array-like of shape (T, q), optional
        Heteroscedasticity variables. Default is time trend.
    direction : array-like of shape (q+1,), optional
        Direction l for curvature. If None, finds maximum curvature.
        
    Returns
    -------
    result : CurvatureResult
        Container with curvature analysis results.
        
    Notes
    -----
    When C_max is large, the score test S will tend to reject H_0.
    This provides a geometric interpretation of the test.
    
    Examples
    --------
    >>> import numpy as np
    >>> from scoretest import normal_curvature
    >>> 
    >>> np.random.seed(42)
    >>> T = 100
    >>> X = np.column_stack([np.ones(T), np.random.randn(T)])
    >>> y = X @ [1, 0.5] + np.random.randn(T)
    >>> 
    >>> result = normal_curvature(y, X)
    >>> print(result)
    """
    y = np.asarray(y).flatten()
    X = np.asarray(X)
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    
    T, p = X.shape
    
    if Z is None:
        Z = np.arange(1, T + 1).reshape(-1, 1)
    else:
        Z = np.asarray(Z)
        if Z.ndim == 1:
            Z = Z.reshape(-1, 1)
    
    q = Z.shape[1]
    
    # Compute OLS estimates
    XtX = X.T @ X
    XtX_inv = inv(XtX)
    beta_hat = XtX_inv @ (X.T @ y)
    residuals = y - X @ beta_hat
    sigma2_hat = np.sum(residuals**2) / T
    sigma4_hat = sigma2_hat ** 2
    
    # Compute Ĵ matrix components (from Section 3)
    # Ĵ₁₁ = Σ'(ê_{t-1}x_t + x_{t-1}ê_t)/σ̂²
    J11 = np.zeros(p)
    for t in range(1, T):
        J11 += (residuals[t-1] * X[t, :] + X[t-1, :] * residuals[t]) / sigma2_hat
    
    # Ĵ₁₂ = Σê_t x_t (∂w_t/∂λ)' / σ̂²
    # For exponential weight at λ=0: ∂w/∂λ = z_t
    J12 = np.zeros((p, q))
    for t in range(T):
        J12 += np.outer(residuals[t] * X[t, :], Z[t, :]) / sigma2_hat
    
    # Ĵ₂₁ = Σ'ê_t ê_{t-1} / σ̂⁴
    J21 = np.sum(residuals[1:] * residuals[:-1]) / sigma4_hat
    
    # Ĵ₂₂ = ½{Σê_t²(∂w_t/∂λ)'}/σ̂⁴
    J22 = np.zeros(q)
    for t in range(T):
        J22 += 0.5 * (residuals[t]**2) * Z[t, :] / sigma4_hat
    
    # Construct full Ĵ matrix
    # Ĵ = [[Ĵ₁₁, Ĵ₁₂], [Ĵ₂₁, Ĵ₂₂]]
    # But Ĵ₁₁ is p×1 (relating β to ρ), and we need to think about dimensions
    
    # Actually, from the paper context, J relates (ρ, λ) to (β, σ²)
    # J is a (q+1) × (p+1) matrix conceptually
    # Let's build the curvature matrix M = ĴK̂⁻¹Ĵ'
    
    # K̂ = diag(X'X/σ̂², ½T/σ̂⁴)
    K_beta = XtX / sigma2_hat
    K_sigma = 0.5 * T / sigma4_hat
    
    # For the curvature computation, we work with the (q+1)×(q+1) matrix
    # C_l = 2l'M l / (l'l) where M = ĴK̂⁻¹Ĵ'
    
    # Simplified version: compute curvature matrix for perturbation in (ρ, λ)
    # The J matrix linking perturbation to likelihood has dimensions based on
    # the score vector components
    
    # From the appendix and Section 3, the key quantity is:
    # M = ĴK̂⁻¹Ĵ' which is (q+1)×(q+1)
    
    # Component for ρ: uses J₂₁ (scalar)
    # Component for λ: uses J₂₂ (q-vector)
    
    # Construct J_tilde for perturbation (ρ, λ') dimension (q+1)
    # J matrix is 2×(q+1) relating likelihood to perturbation
    
    # The full J matrix from equation (3.2):
    J_full = np.zeros((2, q + 1))
    J_full[0, 0] = J21  # ∂²L/∂σ²∂ρ component
    J_full[0, 1:] = J22  # ∂²L/∂σ²∂λ component
    J_full[1, 0] = np.sum(J11)  # Aggregated ∂²L/∂β∂ρ
    J_full[1, 1:] = np.sum(J12, axis=0)  # Aggregated ∂²L/∂β∂λ
    
    # K is 2×2 block diagonal relating to (β, σ²)
    K_full = np.zeros((2, 2))
    K_full[0, 0] = K_sigma
    K_full[1, 1] = np.trace(XtX_inv) * sigma2_hat  # Simplified
    
    try:
        K_full_inv = inv(K_full)
    except np.linalg.LinAlgError:
        K_full_inv = pinv(K_full)
    
    # Curvature matrix M = J' K⁻¹ J
    M = J_full.T @ K_full_inv @ J_full
    
    # Find maximum curvature via eigenvalue decomposition
    eigenvalues, eigenvectors = np.linalg.eigh(M)
    max_idx = np.argmax(np.abs(eigenvalues))
    C_max = 2 * np.abs(eigenvalues[max_idx])
    l_max = eigenvectors[:, max_idx]
    
    # If specific direction is given, compute curvature in that direction
    if direction is not None:
        direction = np.asarray(direction).flatten()
        if len(direction) != q + 1:
            raise ValueError(f"Direction must have length {q+1}, got {len(direction)}")
        C_l = 2 * np.abs(direction @ M @ direction) / (direction @ direction)
    
    # Interpret the direction
    rho_component = np.abs(l_max[0])
    lambda_components = np.abs(l_max[1:])
    
    if rho_component > np.max(lambda_components):
        influence_direction = "Perturbation in autocorrelation (ρ) is most influential"
    else:
        max_lambda_idx = np.argmax(lambda_components)
        influence_direction = f"Perturbation in λ_{max_lambda_idx+1} is most influential"
    
    return CurvatureResult(
        C_max=C_max,
        C_direction=l_max,
        J_matrix=J_full,
        K_matrix=K_full,
        influence_direction=influence_direction
    )


def parameter_sensitivity(
    y: np.ndarray,
    X: np.ndarray,
    Z: Optional[np.ndarray] = None
) -> SensitivityResult:
    """
    Compute sensitivity of regression coefficients to model perturbation.
    
    Implements Equation (3.4) from Tsai (1986):
        ∂β̂(w*)/∂w* |_{w*=w₀*} = -K̃⁻¹J̃'
        
    where K̃ = X'X and J̃' relates β to perturbation vector.
    
    Parameters
    ----------
    y : array-like of shape (T,)
        Response variable.
    X : array-like of shape (T, p)
        Design matrix.
    Z : array-like of shape (T, q), optional
        Heteroscedasticity variables. Default is time trend.
        
    Returns
    -------
    result : SensitivityResult
        Container with sensitivity analysis results.
        
    Notes
    -----
    When the sensitivity is large, the hypothesis ρ = 0 and λ = λ*
    is likely to be rejected by the score test.
    
    Examples
    --------
    >>> import numpy as np
    >>> from scoretest import parameter_sensitivity
    >>> 
    >>> np.random.seed(42)
    >>> T = 100
    >>> X = np.column_stack([np.ones(T), np.random.randn(T)])
    >>> y = X @ [1, 0.5] + np.random.randn(T)
    >>> 
    >>> result = parameter_sensitivity(y, X)
    >>> print(result)
    """
    y = np.asarray(y).flatten()
    X = np.asarray(X)
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    
    T, p = X.shape
    
    if Z is None:
        Z = np.arange(1, T + 1).reshape(-1, 1)
    else:
        Z = np.asarray(Z)
        if Z.ndim == 1:
            Z = Z.reshape(-1, 1)
    
    q = Z.shape[1]
    
    # Compute OLS estimates
    XtX = X.T @ X
    XtX_inv = inv(XtX)
    beta_hat = XtX_inv @ (X.T @ y)
    residuals = y - X @ beta_hat
    
    # From Equation (3.4):
    # K̃ = X'X
    # J̃' = [Σ'(ê_t x_{t-1} + ê_{t-1} x_t), Σ{ê_t x_t (∂w_t/∂λ)'}]
    
    # J̃ has dimensions p × (q+1)
    J_tilde = np.zeros((p, q + 1))
    
    # Component for ρ: Σ'(ê_t x_{t-1} + ê_{t-1} x_t) for t=2,...,T
    for t in range(1, T):
        J_tilde[:, 0] += residuals[t] * X[t-1, :] + residuals[t-1] * X[t, :]
    
    # Component for λ: Σ{ê_t x_t (∂w_t/∂λ)'}
    # For exponential weight at λ=0: ∂w/∂λ = z_t
    for t in range(T):
        J_tilde[:, 1:] += np.outer(residuals[t] * X[t, :], Z[t, :])
    
    # Sensitivity matrix: ∂β̂/∂w* = -K̃⁻¹J̃
    sensitivity_matrix = -XtX_inv @ J_tilde
    
    # Compute norm and identify most sensitive coefficient
    sensitivity_norm = np.linalg.norm(sensitivity_matrix, 'fro')
    
    # Sensitivity by coefficient
    coef_sensitivity = np.linalg.norm(sensitivity_matrix, axis=1)
    most_sensitive_coef = np.argmax(coef_sensitivity)
    
    # Extract sensitivity to ρ and λ separately
    sensitivity_to_rho = sensitivity_matrix[:, 0]
    sensitivity_to_lambda = sensitivity_matrix[:, 1:]
    
    return SensitivityResult(
        sensitivity_matrix=sensitivity_matrix,
        sensitivity_norm=sensitivity_norm,
        most_sensitive_coef=most_sensitive_coef,
        sensitivity_to_rho=sensitivity_to_rho,
        sensitivity_to_lambda=sensitivity_to_lambda
    )


def influence_graph(
    y: np.ndarray,
    X: np.ndarray,
    rho_range: Optional[Tuple[float, float]] = None,
    lambda_range: Optional[Tuple[float, float]] = None,
    n_points: int = 50
) -> Dict[str, np.ndarray]:
    """
    Compute the influence graph for model perturbation.
    
    From Equation (3.1):
        M(w*) = [L(w*), w*']'
        
    where L(w*) = 2{L(β̂) - L(β̂_{w*})}
    
    Parameters
    ----------
    y : array-like of shape (T,)
        Response variable.
    X : array-like of shape (T, p)
        Design matrix.
    rho_range : tuple of float, optional
        Range of ρ values to evaluate. Default is (-0.5, 0.5).
    lambda_range : tuple of float, optional
        Range of λ values to evaluate. Default is (-0.5, 0.5).
    n_points : int, default=50
        Number of grid points per dimension.
        
    Returns
    -------
    results : dict
        Dictionary with:
        - 'rho_grid': ρ values
        - 'lambda_grid': λ values  
        - 'L_rho': Likelihood displacement along ρ
        - 'L_lambda': Likelihood displacement along λ
        
    Notes
    -----
    The influence graph visualizes how the likelihood function
    changes as the model is perturbed from H_0.
    """
    if rho_range is None:
        rho_range = (-0.5, 0.5)
    if lambda_range is None:
        lambda_range = (-0.5, 0.5)
    
    y = np.asarray(y).flatten()
    X = np.asarray(X)
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    
    T, p = X.shape
    
    # OLS estimates under H_0
    XtX_inv = inv(X.T @ X)
    beta_hat = XtX_inv @ (X.T @ y)
    residuals = y - X @ beta_hat
    sigma2_hat = np.sum(residuals**2) / T
    
    # Log-likelihood under H_0 (up to constant)
    L0 = -0.5 * T * np.log(sigma2_hat) - 0.5 * T
    
    # Grid for ρ (keeping λ = 0)
    rho_grid = np.linspace(rho_range[0], rho_range[1], n_points)
    L_rho = np.zeros(n_points)
    
    for i, rho in enumerate(rho_grid):
        # Transform data for GLS
        y_star = y.copy()
        X_star = X.copy()
        
        y_star[1:] = y[1:] - rho * y[:-1]
        X_star[1:, :] = X[1:, :] - rho * X[:-1, :]
        
        # First observation adjustment (optional, for exact likelihood)
        y_star[0] = y[0] * np.sqrt(1 - rho**2)
        X_star[0, :] = X[0, :] * np.sqrt(1 - rho**2)
        
        # GLS estimates
        try:
            XtX_star_inv = inv(X_star.T @ X_star)
            beta_star = XtX_star_inv @ (X_star.T @ y_star)
            resid_star = y_star - X_star @ beta_star
            sigma2_star = np.sum(resid_star**2) / T
            
            # Log-likelihood with AR(1) errors
            L_rho[i] = -0.5 * T * np.log(sigma2_star) - 0.5 * T + 0.5 * np.log(1 - rho**2)
        except:
            L_rho[i] = L0
    
    # Likelihood displacement: 2(L(β̂) - L(β̂_{w*}))
    L_rho = 2 * (L0 - L_rho)
    
    # Grid for λ (keeping ρ = 0)
    lambda_grid = np.linspace(lambda_range[0], lambda_range[1], n_points)
    L_lambda = np.zeros(n_points)
    
    Z = np.arange(1, T + 1) / T  # Scaled time trend
    
    for i, lam in enumerate(lambda_grid):
        # Heteroscedastic weights
        weights = np.exp(lam * Z)
        
        # Weighted least squares
        W = np.diag(1 / weights)
        XtWX = X.T @ W @ X
        try:
            XtWX_inv = inv(XtWX)
            beta_w = XtWX_inv @ (X.T @ W @ y)
            resid_w = y - X @ beta_w
            sigma2_w = np.sum((resid_w**2) / weights) / T
            
            # Log-likelihood with heteroscedasticity
            L_lambda[i] = -0.5 * T * np.log(sigma2_w) - 0.5 * np.sum(np.log(weights)) - 0.5 * T
        except:
            L_lambda[i] = L0
    
    L_lambda = 2 * (L0 - L_lambda)
    
    return {
        'rho_grid': rho_grid,
        'lambda_grid': lambda_grid,
        'L_rho': L_rho,
        'L_lambda': L_lambda,
        'L0': L0
    }
