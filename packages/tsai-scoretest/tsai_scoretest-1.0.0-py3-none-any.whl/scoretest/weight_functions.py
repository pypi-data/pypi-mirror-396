"""
Weight Functions for Heteroscedasticity Specifications.

This module provides various weight functions w(z_t, λ) that model
heteroscedasticity in the AR(1) model following Tsai (1986).

The variance structure is:
    var(e_t) = w(z_t, λ)σ²

where:
    - z_t = (z_{t1}, ..., z_{tq})' is a known vector
    - λ = (λ_1, ..., λ_q)' is the parameter vector
    - There exists a unique λ* such that w(z_t, λ*) = 1 for all t

Common Weight Functions:
-----------------------
1. Exponential: w(z, λ) = exp(λ'z)
   - λ* = 0
   - ∂w/∂λ|_{λ=0} = z
   - Used by Cook & Weisberg (1983)

2. Linear: w(z, λ) = 1 + λ'z  
   - λ* = 0
   - ∂w/∂λ|_{λ=0} = z
   - Simple linear heteroscedasticity

3. Power: w(z, λ) = |z|^{2λ}
   - λ* = 0
   - Multiplicative heteroscedasticity

References:
    Tsai, C.-L. (1986). Biometrika, 73(2), 455-460.
    Cook, R.D. & Weisberg, S. (1983). Biometrika, 70(1), 1-10.
"""

import numpy as np
from typing import Callable, Tuple, Optional, Union
from dataclasses import dataclass


@dataclass
class WeightFunction:
    """
    Container for weight function specification.
    
    Attributes
    ----------
    w : callable
        Weight function w(z, λ)
    dw : callable
        Derivative ∂w/∂λ
    d2w : callable, optional
        Second derivative ∂²w/∂λ∂λ' for modified score test
    lambda_star : np.ndarray
        Value of λ* such that w(z, λ*) = 1
    name : str
        Name of the weight function
    """
    w: Callable
    dw: Callable
    d2w: Optional[Callable]
    lambda_star: np.ndarray
    name: str


def exponential_weight(q: int = 1) -> WeightFunction:
    """
    Exponential weight function w(z, λ) = exp(λ'z).
    
    This is the default weight function following Cook & Weisberg (1983).
    
    At λ = λ* = 0:
        w(z, 0) = 1
        ∂w/∂λ|_{λ=0} = z
        ∂²w/∂λ∂λ'|_{λ=0} = zz'
        
    Parameters
    ----------
    q : int, default=1
        Dimension of λ (number of heteroscedasticity parameters).
        
    Returns
    -------
    weight : WeightFunction
        Weight function specification.
        
    Examples
    --------
    >>> from scoretest.weight_functions import exponential_weight
    >>> 
    >>> wf = exponential_weight(q=2)
    >>> z = np.array([1.0, 2.0])
    >>> lam = np.array([0.0, 0.0])
    >>> print(wf.w(z, lam))  # Should be 1.0
    >>> print(wf.dw(z, lam))  # Should be [1.0, 2.0]
    """
    def w(z: np.ndarray, lam: np.ndarray) -> float:
        """w(z, λ) = exp(λ'z)"""
        z = np.asarray(z).flatten()
        lam = np.asarray(lam).flatten()
        return np.exp(np.dot(lam, z))
    
    def dw(z: np.ndarray, lam: np.ndarray) -> np.ndarray:
        """∂w/∂λ = z * exp(λ'z)"""
        z = np.asarray(z).flatten()
        lam = np.asarray(lam).flatten()
        return z * np.exp(np.dot(lam, z))
    
    def d2w(z: np.ndarray, lam: np.ndarray) -> np.ndarray:
        """∂²w/∂λ∂λ' = zz' * exp(λ'z)"""
        z = np.asarray(z).flatten().reshape(-1, 1)
        lam = np.asarray(lam).flatten()
        return (z @ z.T) * np.exp(np.dot(lam.flatten(), z.flatten()))
    
    return WeightFunction(
        w=w,
        dw=dw,
        d2w=d2w,
        lambda_star=np.zeros(q),
        name="Exponential"
    )


def linear_weight(q: int = 1) -> WeightFunction:
    """
    Linear weight function w(z, λ) = 1 + λ'z.
    
    At λ = λ* = 0:
        w(z, 0) = 1
        ∂w/∂λ|_{λ=0} = z
        ∂²w/∂λ∂λ'|_{λ=0} = 0
        
    Note: This requires constraints to ensure w > 0.
    
    Parameters
    ----------
    q : int, default=1
        Dimension of λ.
        
    Returns
    -------
    weight : WeightFunction
        Weight function specification.
    """
    def w(z: np.ndarray, lam: np.ndarray) -> float:
        """w(z, λ) = 1 + λ'z"""
        z = np.asarray(z).flatten()
        lam = np.asarray(lam).flatten()
        return 1.0 + np.dot(lam, z)
    
    def dw(z: np.ndarray, lam: np.ndarray) -> np.ndarray:
        """∂w/∂λ = z"""
        return np.asarray(z).flatten()
    
    def d2w(z: np.ndarray, lam: np.ndarray) -> np.ndarray:
        """∂²w/∂λ∂λ' = 0"""
        z = np.asarray(z).flatten()
        return np.zeros((len(z), len(z)))
    
    return WeightFunction(
        w=w,
        dw=dw,
        d2w=d2w,
        lambda_star=np.zeros(q),
        name="Linear"
    )


def power_weight(base_positive: bool = True) -> WeightFunction:
    """
    Power weight function w(z, λ) = |z|^{2λ} for scalar z.
    
    This models multiplicative heteroscedasticity where variance
    is proportional to a power of z.
    
    At λ = λ* = 0:
        w(z, 0) = 1
        ∂w/∂λ|_{λ=0} = 2*log|z|
        
    Parameters
    ----------
    base_positive : bool, default=True
        If True, assumes z > 0 (no absolute value needed).
        
    Returns
    -------
    weight : WeightFunction
        Weight function specification.
        
    Examples
    --------
    >>> from scoretest.weight_functions import power_weight
    >>> 
    >>> wf = power_weight()
    >>> z = np.array([2.0])  # scalar
    >>> lam = np.array([0.0])
    >>> print(wf.w(z, lam))  # Should be 1.0
    """
    def w(z: np.ndarray, lam: np.ndarray) -> float:
        """w(z, λ) = |z|^{2λ}"""
        z_val = np.abs(np.asarray(z).flatten()[0])
        lam_val = np.asarray(lam).flatten()[0]
        if z_val <= 0:
            return 1.0
        return z_val ** (2 * lam_val)
    
    def dw(z: np.ndarray, lam: np.ndarray) -> np.ndarray:
        """∂w/∂λ = 2*log|z| * |z|^{2λ}"""
        z_val = np.abs(np.asarray(z).flatten()[0])
        lam_val = np.asarray(lam).flatten()[0]
        if z_val <= 0:
            return np.array([0.0])
        return np.array([2 * np.log(z_val) * (z_val ** (2 * lam_val))])
    
    def d2w(z: np.ndarray, lam: np.ndarray) -> np.ndarray:
        """∂²w/∂λ² = 4*(log|z|)² * |z|^{2λ}"""
        z_val = np.abs(np.asarray(z).flatten()[0])
        lam_val = np.asarray(lam).flatten()[0]
        if z_val <= 0:
            return np.array([[0.0]])
        return np.array([[4 * (np.log(z_val)**2) * (z_val ** (2 * lam_val))]])
    
    return WeightFunction(
        w=w,
        dw=dw,
        d2w=d2w,
        lambda_star=np.zeros(1),
        name="Power"
    )


def compute_weight_derivatives(
    Z: np.ndarray,
    weight_func: Optional[WeightFunction] = None
) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """
    Compute the D matrix of weight function derivatives.
    
    Computes ∂w(z_t, λ)/∂λ evaluated at λ = λ* for each observation.
    
    Parameters
    ----------
    Z : np.ndarray of shape (T, q)
        Matrix of heteroscedasticity variables.
    weight_func : WeightFunction, optional
        Weight function specification. Default is exponential.
        
    Returns
    -------
    D : np.ndarray of shape (T, q)
        Matrix with tth row = ∂w(z_t, λ)/∂λ|_{λ=λ*}
    D2 : np.ndarray of shape (T, q, q), optional
        Array of second derivatives if available.
        
    Examples
    --------
    >>> import numpy as np
    >>> from scoretest.weight_functions import compute_weight_derivatives
    >>> 
    >>> Z = np.random.randn(100, 2)
    >>> D, D2 = compute_weight_derivatives(Z)
    >>> print(D.shape)  # (100, 2)
    """
    Z = np.asarray(Z)
    if Z.ndim == 1:
        Z = Z.reshape(-1, 1)
    
    T, q = Z.shape
    
    if weight_func is None:
        weight_func = exponential_weight(q)
    
    lambda_star = weight_func.lambda_star
    
    # Compute first derivatives
    D = np.zeros((T, q))
    for t in range(T):
        D[t, :] = weight_func.dw(Z[t, :], lambda_star)
    
    # Compute second derivatives if available
    D2 = None
    if weight_func.d2w is not None:
        D2 = np.zeros((T, q, q))
        for t in range(T):
            D2[t, :, :] = weight_func.d2w(Z[t, :], lambda_star)
    
    return D, D2


def create_custom_weight(
    w: Callable[[np.ndarray, np.ndarray], float],
    dw: Callable[[np.ndarray, np.ndarray], np.ndarray],
    lambda_star: np.ndarray,
    d2w: Optional[Callable[[np.ndarray, np.ndarray], np.ndarray]] = None,
    name: str = "Custom"
) -> WeightFunction:
    """
    Create a custom weight function specification.
    
    Parameters
    ----------
    w : callable
        Weight function w(z, λ) -> float
    dw : callable
        First derivative ∂w/∂λ(z, λ) -> array of shape (q,)
    lambda_star : array-like
        Value of λ* such that w(z, λ*) = 1
    d2w : callable, optional
        Second derivative ∂²w/∂λ∂λ'(z, λ) -> array of shape (q, q)
    name : str, default="Custom"
        Name of the weight function
        
    Returns
    -------
    weight : WeightFunction
        Custom weight function specification.
        
    Examples
    --------
    >>> import numpy as np
    >>> from scoretest.weight_functions import create_custom_weight
    >>> 
    >>> # Define a custom quadratic weight function
    >>> def w(z, lam):
    ...     return np.exp(lam[0] * z[0] + lam[1] * z[0]**2)
    >>> 
    >>> def dw(z, lam):
    ...     w_val = np.exp(lam[0] * z[0] + lam[1] * z[0]**2)
    ...     return np.array([z[0] * w_val, z[0]**2 * w_val])
    >>> 
    >>> wf = create_custom_weight(w, dw, np.zeros(2), name="Quadratic")
    """
    return WeightFunction(
        w=w,
        dw=dw,
        d2w=d2w,
        lambda_star=np.asarray(lambda_star),
        name=name
    )


# Common heteroscedasticity specifications from the literature
def breusch_pagan_weight(Z: np.ndarray) -> WeightFunction:
    """
    Weight function for Breusch-Pagan test.
    
    Uses linear specification: var(e_t) = σ²(1 + λ'z_t)
    
    This is equivalent to linear_weight but specifically
    configured for Breusch-Pagan style testing.
    
    Parameters
    ----------
    Z : np.ndarray
        Matrix of heteroscedasticity variables (used to determine q).
        
    Returns
    -------
    weight : WeightFunction
        Breusch-Pagan style weight function.
    """
    Z = np.asarray(Z)
    if Z.ndim == 1:
        q = 1
    else:
        q = Z.shape[1]
    
    wf = linear_weight(q)
    wf.name = "Breusch-Pagan"
    return wf


def white_weight(X: np.ndarray) -> Tuple[WeightFunction, np.ndarray]:
    """
    Weight function for White's heteroscedasticity test.
    
    Uses all regressors, their squares, and cross-products as Z.
    
    Parameters
    ----------
    X : np.ndarray of shape (T, p)
        Design matrix.
        
    Returns
    -------
    weight : WeightFunction
        White-style weight function.
    Z : np.ndarray
        Augmented Z matrix with squares and cross-products.
    """
    X = np.asarray(X)
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    
    T, p = X.shape
    
    # Build Z: regressors, squares, and cross-products
    Z_list = [X]
    
    # Add squares
    for j in range(p):
        Z_list.append(X[:, j:j+1]**2)
    
    # Add cross-products
    for j in range(p):
        for k in range(j+1, p):
            Z_list.append((X[:, j] * X[:, k]).reshape(-1, 1))
    
    Z = np.hstack(Z_list)
    q = Z.shape[1]
    
    wf = exponential_weight(q)
    wf.name = "White"
    
    return wf, Z
