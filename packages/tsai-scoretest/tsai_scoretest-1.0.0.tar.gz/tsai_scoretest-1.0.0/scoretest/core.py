"""
Core implementation of the Score Test for First-Order Autoregressive Model 
with Heteroscedasticity.

This module implements the score test proposed by Tsai (1986) in Biometrika.

Reference:
    Tsai, C.-L. (1986). Score test for the first-order autoregressive model with
    heteroscedasticity. Biometrika, 73(2), 455-460.

Mathematical Framework:
----------------------
Basic Model (Equation 2.1):
    y_t = x_t'β + u_t    (t = 1, ..., T)

AR(1) Error Process (Equation 2.2):
    u_t = ρu_{t-1} + e_t  (t = 2, ..., T), with u_1 = e_1

Heteroscedasticity (Equation 2.3):
    var(e_t) = w_t σ² = w(z_t, λ)σ²

Null Hypothesis:
    H_0: ρ = 0 and λ = λ*  (no autocorrelation and homoscedasticity)

Score Test Statistic (Equation 2.4):
    S = S_1 + S_2

    S_1 = (Tρ̂)² / (T - 1)           [Tests ρ = 0]
    S_2 = V'D̄(D̄'D̄)⁻¹D̄'V           [Tests λ = λ*]

where:
    ρ̂ = Σ'ê_t ê_{t-1} / Σê_t²      (Equation 2.5)
    V = T×1 vector with element ê_t²/σ̂²
    ê_t = y_t - x_t'β̂
    σ̂² = Σê_t²/T
    D = T×q matrix with tth row ∂w(z_t, λ)/∂λ_j at λ = λ*
    D̄ = D - 11'D/T                  (centered D matrix)

    Σ' denotes summation over t = 2, ..., T
    Σ denotes summation over t = 1, ..., T

Asymptotic Distributions:
    S_1 ~ χ²(1)
    S_2 ~ χ²(q)
    S ~ χ²(q + 1)
"""

import numpy as np
from scipy import stats
from scipy.linalg import inv, pinv
from dataclasses import dataclass
from typing import Optional, Callable, Tuple, Union
import warnings


@dataclass
class ScoreTestResult:
    """
    Container for Score Test results following Tsai (1986).
    
    Attributes
    ----------
    S : float
        Joint score test statistic S = S_1 + S_2 (Equation 2.4)
    S1 : float
        Score test statistic for autocorrelation, (Tρ̂)²/(T-1)
    S2 : float
        Score test statistic for heteroscedasticity, V'D̄(D̄'D̄)⁻¹D̄'V
    p_value : float
        P-value for the joint test S ~ χ²(q+1)
    p_value_S1 : float
        P-value for S_1 ~ χ²(1)
    p_value_S2 : float
        P-value for S_2 ~ χ²(q)
    df_S1 : int
        Degrees of freedom for S_1 (always 1)
    df_S2 : int
        Degrees of freedom for S_2 (equals q)
    df_total : int
        Degrees of freedom for S (equals q + 1)
    rho_hat : float
        Estimated autocorrelation coefficient ρ̂ (Equation 2.5)
    sigma2_hat : float
        Estimated error variance σ̂²
    T : int
        Sample size
    q : int
        Number of heteroscedasticity parameters
    residuals : np.ndarray
        OLS residuals ê_t
    """
    S: float
    S1: float
    S2: float
    p_value: float
    p_value_S1: float
    p_value_S2: float
    df_S1: int
    df_S2: int
    df_total: int
    rho_hat: float
    sigma2_hat: float
    T: int
    q: int
    residuals: np.ndarray
    
    def __repr__(self) -> str:
        return self._format_output()
    
    def _format_output(self) -> str:
        """Format output for publication-quality display."""
        width = 70
        line = "=" * width
        thin_line = "-" * width
        
        output = [
            "",
            line,
            "Score Test for AR(1) Model with Heteroscedasticity",
            "Tsai (1986) - Biometrika, 73(2), 455-460",
            line,
            "",
            f"Sample Size (T): {self.T}",
            f"Heteroscedasticity Parameters (q): {self.q}",
            "",
            thin_line,
            "Estimated Parameters Under H₀",
            thin_line,
            f"  Autocorrelation (ρ̂):      {self.rho_hat:12.6f}",
            f"  Error Variance (σ̂²):      {self.sigma2_hat:12.6f}",
            "",
            thin_line,
            "Score Test Statistics",
            thin_line,
            "",
            "  Test Component         Statistic    df      P-value    Decision",
            "  " + "-" * 62,
            f"  S₁ (Autocorrelation)   {self.S1:10.4f}     {self.df_S1}    {self.p_value_S1:8.4f}    {'***' if self.p_value_S1 < 0.01 else '**' if self.p_value_S1 < 0.05 else '*' if self.p_value_S1 < 0.10 else ''}",
            f"  S₂ (Heteroscedast.)    {self.S2:10.4f}     {self.df_S2}    {self.p_value_S2:8.4f}    {'***' if self.p_value_S2 < 0.01 else '**' if self.p_value_S2 < 0.05 else '*' if self.p_value_S2 < 0.10 else ''}",
            "  " + "-" * 62,
            f"  S (Joint Test)         {self.S:10.4f}     {self.df_total}    {self.p_value:8.4f}    {'***' if self.p_value < 0.01 else '**' if self.p_value < 0.05 else '*' if self.p_value < 0.10 else ''}",
            "",
            "  Significance codes: *** p<0.01, ** p<0.05, * p<0.10",
            "",
            thin_line,
            "Hypothesis Testing",
            thin_line,
            f"  H₀: ρ = 0 and λ = λ* (No autocorrelation and homoscedasticity)",
            f"  H₁: ρ ≠ 0 or λ ≠ λ* (Presence of autocorrelation or heteroscedasticity)",
            "",
            f"  Decision at α = 0.05: {'Reject H₀' if self.p_value < 0.05 else 'Fail to Reject H₀'}",
            "",
            line,
            "Reference: Tsai, C.-L. (1986). Biometrika, 73(2), 455-460.",
            line,
            ""
        ]
        return "\n".join(output)
    
    def summary(self) -> str:
        """Return publication-ready summary."""
        return self._format_output()
    
    def to_dict(self) -> dict:
        """Convert results to dictionary for export."""
        return {
            "S": self.S,
            "S1": self.S1,
            "S2": self.S2,
            "p_value": self.p_value,
            "p_value_S1": self.p_value_S1,
            "p_value_S2": self.p_value_S2,
            "df_S1": self.df_S1,
            "df_S2": self.df_S2,
            "df_total": self.df_total,
            "rho_hat": self.rho_hat,
            "sigma2_hat": self.sigma2_hat,
            "T": self.T,
            "q": self.q
        }


class TsaiScoreTest:
    """
    Score Test for the First-Order Autoregressive Model with Heteroscedasticity.
    
    Implementation of the score test proposed by Tsai (1986) for simultaneous
    testing of independence (ρ = 0) and homoscedasticity (λ = λ*) in the 
    first-order autoregressive model.
    
    Parameters
    ----------
    y : array-like of shape (T,)
        Response variable observations.
    X : array-like of shape (T, p)
        Design matrix of regressors.
    Z : array-like of shape (T, q), optional
        Variables associated with heteroscedasticity. If None, uses linear
        heteroscedasticity with Z = [1, 2, ..., T]'.
    weight_func : callable, optional
        Weight function w(z_t, λ) for heteroscedasticity. Default is exponential.
    weight_deriv : callable, optional
        Derivative ∂w(z_t, λ)/∂λ evaluated at λ = λ*. Default uses numerical.
        
    Attributes
    ----------
    result : ScoreTestResult
        Container with all test results after calling fit().
        
    Examples
    --------
    >>> import numpy as np
    >>> from scoretest import TsaiScoreTest
    >>> 
    >>> # Generate sample data
    >>> np.random.seed(42)
    >>> T = 100
    >>> X = np.column_stack([np.ones(T), np.random.randn(T)])
    >>> beta = np.array([1.0, 0.5])
    >>> y = X @ beta + np.random.randn(T)
    >>> 
    >>> # Perform the score test
    >>> test = TsaiScoreTest(y, X)
    >>> result = test.fit()
    >>> print(result)
    
    References
    ----------
    Tsai, C.-L. (1986). Score test for the first-order autoregressive model 
        with heteroscedasticity. Biometrika, 73(2), 455-460.
    Cook, R.D. & Weisberg, S. (1983). Diagnostics for heteroscedasticity 
        in regression. Biometrika, 70(1), 1-10.
    """
    
    def __init__(
        self,
        y: np.ndarray,
        X: np.ndarray,
        Z: Optional[np.ndarray] = None,
        weight_func: Optional[Callable] = None,
        weight_deriv: Optional[Callable] = None
    ):
        # Convert inputs to numpy arrays
        self.y = np.asarray(y).flatten()
        self.X = np.asarray(X)
        
        # Ensure X is 2D
        if self.X.ndim == 1:
            self.X = self.X.reshape(-1, 1)
        
        self.T = len(self.y)
        self.p = self.X.shape[1]
        
        # Validate dimensions
        if self.X.shape[0] != self.T:
            raise ValueError(f"X has {self.X.shape[0]} rows but y has {self.T} elements")
        
        # Set up heteroscedasticity variables Z
        if Z is None:
            # Default: use time index for linear heteroscedasticity
            self.Z = np.arange(1, self.T + 1).reshape(-1, 1)
        else:
            self.Z = np.asarray(Z)
            if self.Z.ndim == 1:
                self.Z = self.Z.reshape(-1, 1)
        
        self.q = self.Z.shape[1]
        
        if self.Z.shape[0] != self.T:
            raise ValueError(f"Z has {self.Z.shape[0]} rows but y has {self.T} elements")
        
        # Set weight function and derivative
        # Default: exponential weight w(z, λ) = exp(λ'z) with λ* = 0
        # At λ = 0: w = 1 and ∂w/∂λ = z
        self.weight_func = weight_func
        self.weight_deriv = weight_deriv
        
        self.result = None
        self._residuals = None
        self._beta_hat = None
        self._sigma2_hat = None
        
    def _compute_ols(self) -> Tuple[np.ndarray, np.ndarray, float]:
        """
        Compute OLS estimates under the null hypothesis.
        
        Under H_0: ρ = 0 and λ = λ*, the MLE of β is the OLS estimator:
            β̂ = (X'X)⁻¹X'y
            ê = y - Xβ̂
            σ̂² = Σê_t²/T
            
        Returns
        -------
        beta_hat : np.ndarray
            OLS estimate of β
        residuals : np.ndarray  
            OLS residuals ê_t
        sigma2_hat : float
            MLE of error variance σ̂²
        """
        # OLS estimation: β̂ = (X'X)⁻¹X'y
        XtX = self.X.T @ self.X
        XtX_inv = inv(XtX)
        beta_hat = XtX_inv @ (self.X.T @ self.y)
        
        # Residuals: ê = y - Xβ̂
        residuals = self.y - self.X @ beta_hat
        
        # MLE variance: σ̂² = Σê²/T (not T-p for MLE)
        sigma2_hat = np.sum(residuals**2) / self.T
        
        return beta_hat, residuals, sigma2_hat
    
    def _compute_rho_hat(self, residuals: np.ndarray) -> float:
        """
        Compute the autocorrelation coefficient estimate ρ̂.
        
        From Equation (2.5):
            ρ̂ = Σ'ê_t ê_{t-1} / Σê_t²
            
        where Σ' is summation over t = 2, ..., T
        and Σ is summation over t = 1, ..., T
        
        Parameters
        ----------
        residuals : np.ndarray
            OLS residuals ê_t
            
        Returns
        -------
        rho_hat : float
            Estimated autocorrelation coefficient
        """
        # Σ'ê_t ê_{t-1} for t = 2, ..., T
        numerator = np.sum(residuals[1:] * residuals[:-1])
        
        # Σê_t² for t = 1, ..., T
        denominator = np.sum(residuals**2)
        
        rho_hat = numerator / denominator
        
        return rho_hat
    
    def _compute_S1(self, rho_hat: float) -> float:
        """
        Compute S_1 statistic for testing autocorrelation.
        
        From Equation (2.4):
            S_1 = (Tρ̂)² / (T - 1)
            
        Under H_0: ρ = 0, S_1 ~ χ²(1)
        
        Parameters
        ----------
        rho_hat : float
            Estimated autocorrelation coefficient
            
        Returns
        -------
        S1 : float
            Score test statistic for autocorrelation
        """
        S1 = (self.T * rho_hat)**2 / (self.T - 1)
        return S1
    
    def _compute_D_matrix(self) -> np.ndarray:
        """
        Compute the D matrix of weight function derivatives.
        
        D is a T × q matrix with the tth row equal to:
            ∂w(z_t, λ)/∂λ_j evaluated at λ = λ*
            
        For the default exponential weight function w(z, λ) = exp(λ'z):
            At λ* = 0: ∂w/∂λ = z_t
            
        Returns
        -------
        D : np.ndarray of shape (T, q)
            Matrix of weight function derivatives
        """
        if self.weight_deriv is not None:
            # Use user-provided derivative function
            D = np.zeros((self.T, self.q))
            for t in range(self.T):
                D[t, :] = self.weight_deriv(self.Z[t, :])
        else:
            # Default: exponential weight w = exp(λ'z), so ∂w/∂λ|_{λ=0} = z
            # This follows Cook & Weisberg (1983)
            D = self.Z.copy()
        
        return D
    
    def _compute_D_bar(self, D: np.ndarray) -> np.ndarray:
        """
        Compute the centered D matrix D̄.
        
        From the paper:
            D̄ = D - 11'D/T
            
        where 1 is a T × 1 vector of ones.
        
        This centers each column of D by subtracting its mean.
        
        Parameters
        ----------
        D : np.ndarray of shape (T, q)
            Matrix of weight function derivatives
            
        Returns
        -------
        D_bar : np.ndarray of shape (T, q)
            Centered D matrix
        """
        # 11'D/T = mean of each column replicated T times
        D_bar = D - np.mean(D, axis=0)
        return D_bar
    
    def _compute_V(self, residuals: np.ndarray, sigma2_hat: float) -> np.ndarray:
        """
        Compute the V vector for heteroscedasticity testing.
        
        V is a T × 1 vector with element ê_t²/σ̂²
        
        Parameters
        ----------
        residuals : np.ndarray
            OLS residuals ê_t
        sigma2_hat : float
            Estimated error variance σ̂²
            
        Returns
        -------
        V : np.ndarray of shape (T,)
            Vector of squared standardized residuals
        """
        V = residuals**2 / sigma2_hat
        return V
    
    def _compute_S2(self, V: np.ndarray, D_bar: np.ndarray) -> float:
        """
        Compute S_2 statistic for testing heteroscedasticity.
        
        From Equation (2.4):
            S_2 = V'D̄(D̄'D̄)⁻¹D̄'V
            
        This is equivalent to T×R² from regressing V on D̄, times 1/2
        (following Cook & Weisberg, 1983).
        
        Under H_0: λ = λ*, S_2 ~ χ²(q)
        
        Parameters
        ----------
        V : np.ndarray of shape (T,)
            Vector of squared standardized residuals
        D_bar : np.ndarray of shape (T, q)
            Centered D matrix
            
        Returns
        -------
        S2 : float
            Score test statistic for heteroscedasticity
        """
        # Compute D̄'D̄
        DtD = D_bar.T @ D_bar
        
        # Check for singularity
        if np.linalg.cond(DtD) > 1e10:
            warnings.warn("D̄'D̄ is near-singular. Using pseudo-inverse.")
            DtD_inv = pinv(DtD)
        else:
            DtD_inv = inv(DtD)
        
        # S_2 = V'D̄(D̄'D̄)⁻¹D̄'V
        # More efficiently: let u = D̄'V, then S_2 = u'(D̄'D̄)⁻¹u
        DtV = D_bar.T @ V
        S2 = DtV.T @ DtD_inv @ DtV
        
        # Scale factor: Following the Appendix of Tsai (1986), 
        # the score test for heteroscedasticity uses 1/2 scaling
        S2 = 0.5 * S2
        
        return S2
    
    def fit(self) -> ScoreTestResult:
        """
        Perform the score test for AR(1) with heteroscedasticity.
        
        Computes the joint score test statistic S = S_1 + S_2 and its
        components for testing H_0: ρ = 0 and λ = λ*.
        
        Returns
        -------
        result : ScoreTestResult
            Object containing all test statistics, p-values, and diagnostics.
        """
        # Step 1: Compute OLS estimates under H_0
        self._beta_hat, self._residuals, self._sigma2_hat = self._compute_ols()
        
        # Step 2: Compute ρ̂ (Equation 2.5)
        rho_hat = self._compute_rho_hat(self._residuals)
        
        # Step 3: Compute S_1 for testing autocorrelation
        S1 = self._compute_S1(rho_hat)
        
        # Step 4: Compute D matrix and centered D̄
        D = self._compute_D_matrix()
        D_bar = self._compute_D_bar(D)
        
        # Step 5: Compute V vector
        V = self._compute_V(self._residuals, self._sigma2_hat)
        
        # Step 6: Compute S_2 for testing heteroscedasticity
        S2 = self._compute_S2(V, D_bar)
        
        # Step 7: Compute joint statistic S = S_1 + S_2
        S = S1 + S2
        
        # Step 8: Compute p-values from chi-squared distributions
        p_value_S1 = 1 - stats.chi2.cdf(S1, df=1)
        p_value_S2 = 1 - stats.chi2.cdf(S2, df=self.q)
        p_value = 1 - stats.chi2.cdf(S, df=self.q + 1)
        
        # Store and return results
        self.result = ScoreTestResult(
            S=S,
            S1=S1,
            S2=S2,
            p_value=p_value,
            p_value_S1=p_value_S1,
            p_value_S2=p_value_S2,
            df_S1=1,
            df_S2=self.q,
            df_total=self.q + 1,
            rho_hat=rho_hat,
            sigma2_hat=self._sigma2_hat,
            T=self.T,
            q=self.q,
            residuals=self._residuals
        )
        
        return self.result
    
    @property
    def beta_hat(self) -> np.ndarray:
        """OLS estimate of regression coefficients."""
        if self._beta_hat is None:
            self.fit()
        return self._beta_hat
    
    @property  
    def residuals(self) -> np.ndarray:
        """OLS residuals."""
        if self._residuals is None:
            self.fit()
        return self._residuals


def score_test_autocorrelation(
    y: np.ndarray, 
    X: np.ndarray,
    return_rho: bool = False
) -> Union[Tuple[float, float], Tuple[float, float, float]]:
    """
    Score test for first-order autocorrelation only.
    
    Tests H_0: ρ = 0 in the AR(1) model assuming homoscedasticity.
    
    Parameters
    ----------
    y : array-like of shape (T,)
        Response variable.
    X : array-like of shape (T, p)
        Design matrix.
    return_rho : bool, default=False
        If True, also return the estimated ρ̂.
        
    Returns
    -------
    S1 : float
        Score test statistic S_1 = (Tρ̂)²/(T-1)
    p_value : float
        P-value from χ²(1) distribution.
    rho_hat : float, optional
        Estimated autocorrelation (only if return_rho=True).
        
    Examples
    --------
    >>> import numpy as np
    >>> from scoretest import score_test_autocorrelation
    >>> 
    >>> np.random.seed(42)
    >>> T = 100
    >>> X = np.column_stack([np.ones(T), np.random.randn(T)])
    >>> y = X @ [1, 0.5] + np.random.randn(T)
    >>> 
    >>> S1, pval = score_test_autocorrelation(y, X)
    >>> print(f"S1 = {S1:.4f}, p-value = {pval:.4f}")
    """
    test = TsaiScoreTest(y, X, Z=np.ones((len(y), 1)))
    result = test.fit()
    
    if return_rho:
        return result.S1, result.p_value_S1, result.rho_hat
    return result.S1, result.p_value_S1


def score_test_heteroscedasticity(
    y: np.ndarray,
    X: np.ndarray,
    Z: np.ndarray
) -> Tuple[float, float, int]:
    """
    Score test for heteroscedasticity only.
    
    Tests H_0: λ = λ* (homoscedasticity) assuming no autocorrelation.
    This is equivalent to the Cook-Weisberg (1983) test.
    
    Parameters
    ----------
    y : array-like of shape (T,)
        Response variable.
    X : array-like of shape (T, p)
        Design matrix.
    Z : array-like of shape (T, q)
        Variables associated with heteroscedasticity.
        
    Returns
    -------
    S2 : float
        Score test statistic S_2 = V'D̄(D̄'D̄)⁻¹D̄'V
    p_value : float
        P-value from χ²(q) distribution.
    df : int
        Degrees of freedom (q).
        
    Examples
    --------
    >>> import numpy as np
    >>> from scoretest import score_test_heteroscedasticity
    >>> 
    >>> np.random.seed(42)
    >>> T = 100
    >>> X = np.column_stack([np.ones(T), np.random.randn(T)])
    >>> Z = np.arange(1, T + 1).reshape(-1, 1)  # Time trend
    >>> y = X @ [1, 0.5] + np.random.randn(T)
    >>> 
    >>> S2, pval, df = score_test_heteroscedasticity(y, X, Z)
    >>> print(f"S2 = {S2:.4f}, p-value = {pval:.4f}, df = {df}")
    
    References
    ----------
    Cook, R.D. & Weisberg, S. (1983). Diagnostics for heteroscedasticity 
        in regression. Biometrika, 70(1), 1-10.
    """
    test = TsaiScoreTest(y, X, Z=Z)
    result = test.fit()
    
    return result.S2, result.p_value_S2, result.df_S2


def score_test_joint(
    y: np.ndarray,
    X: np.ndarray,
    Z: Optional[np.ndarray] = None
) -> ScoreTestResult:
    """
    Joint score test for autocorrelation and heteroscedasticity.
    
    Tests H_0: ρ = 0 and λ = λ* (no autocorrelation and homoscedasticity)
    vs H_1: ρ ≠ 0 or λ ≠ λ* (presence of autocorrelation or heteroscedasticity).
    
    This is the main test proposed by Tsai (1986).
    
    Parameters
    ----------
    y : array-like of shape (T,)
        Response variable.
    X : array-like of shape (T, p)
        Design matrix.
    Z : array-like of shape (T, q), optional
        Variables for heteroscedasticity. Default is time trend.
        
    Returns
    -------
    result : ScoreTestResult
        Complete test results with S, S_1, S_2, p-values, and diagnostics.
        
    Examples
    --------
    >>> import numpy as np
    >>> from scoretest import score_test_joint
    >>> 
    >>> np.random.seed(42)
    >>> T = 100
    >>> X = np.column_stack([np.ones(T), np.random.randn(T)])
    >>> y = X @ [1, 0.5] + np.random.randn(T)
    >>> 
    >>> result = score_test_joint(y, X)
    >>> print(result)
    
    See Also
    --------
    TsaiScoreTest : Class-based interface with more options.
    score_test_autocorrelation : Test for autocorrelation only.
    score_test_heteroscedasticity : Test for heteroscedasticity only.
    """
    test = TsaiScoreTest(y, X, Z=Z)
    return test.fit()
