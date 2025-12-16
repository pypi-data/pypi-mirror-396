"""
Example: Basic Usage of the ScoreTest Package

This example demonstrates the fundamental usage of the score test
from Tsai (1986) for testing autocorrelation and heteroscedasticity
in linear regression models.

Reference:
    Tsai, C.-L. (1986). Score test for the first-order autoregressive model 
    with heteroscedasticity. Biometrika, 73(2), 455-460.
"""

import numpy as np
import sys
import os

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scoretest import (
    TsaiScoreTest,
    score_test_joint,
    score_test_autocorrelation,
    score_test_heteroscedasticity,
)


def main():
    """Run basic examples."""
    
    print("=" * 70)
    print("ScoreTest Package - Basic Usage Examples")
    print("Tsai (1986) Score Test for AR(1) with Heteroscedasticity")
    print("=" * 70)
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # =================================================================
    # Example 1: Test under null hypothesis (no issues)
    # =================================================================
    print("\n" + "=" * 70)
    print("Example 1: Data Generated Under H₀ (No Autocorrelation, Homoscedastic)")
    print("=" * 70)
    
    T = 200  # Sample size
    
    # Generate design matrix
    X = np.column_stack([
        np.ones(T),           # Intercept
        np.random.randn(T),   # Regressor 1
        np.random.randn(T)    # Regressor 2
    ])
    
    # True coefficients
    beta = np.array([1.0, 0.5, -0.3])
    
    # Generate i.i.d. errors (H₀ is true)
    errors = np.random.randn(T)
    
    # Generate response
    y = X @ beta + errors
    
    # Perform the joint score test
    result = score_test_joint(y, X)
    print(result)
    
    # =================================================================
    # Example 2: Test with autocorrelated errors
    # =================================================================
    print("\n" + "=" * 70)
    print("Example 2: Data with AR(1) Errors (ρ = 0.6)")
    print("=" * 70)
    
    rho = 0.6  # True autocorrelation
    
    # Generate AR(1) errors
    ar1_errors = np.zeros(T)
    ar1_errors[0] = np.random.randn()
    for t in range(1, T):
        ar1_errors[t] = rho * ar1_errors[t-1] + np.random.randn()
    
    y_ar1 = X @ beta + ar1_errors
    
    result_ar1 = score_test_joint(y_ar1, X)
    print(result_ar1)
    
    # =================================================================
    # Example 3: Test with heteroscedastic errors
    # =================================================================
    print("\n" + "=" * 70)
    print("Example 3: Data with Heteroscedastic Errors")
    print("=" * 70)
    
    # Variance increases over time: var(e_t) = exp(0.02 * t)
    t_index = np.arange(1, T + 1)
    variances = np.exp(0.02 * t_index)
    hetero_errors = np.random.randn(T) * np.sqrt(variances)
    
    y_hetero = X @ beta + hetero_errors
    
    # Use time index as Z variable
    Z = t_index.reshape(-1, 1)
    
    result_hetero = score_test_joint(y_hetero, X, Z)
    print(result_hetero)
    
    # =================================================================
    # Example 4: Test with both problems
    # =================================================================
    print("\n" + "=" * 70)
    print("Example 4: Data with Both AR(1) and Heteroscedasticity")
    print("=" * 70)
    
    # Generate AR(1) errors with heteroscedasticity
    combined_errors = np.zeros(T)
    combined_errors[0] = np.random.randn() * np.sqrt(variances[0])
    for t in range(1, T):
        innovation = np.random.randn() * np.sqrt(variances[t])
        combined_errors[t] = rho * combined_errors[t-1] + innovation
    
    y_combined = X @ beta + combined_errors
    
    result_combined = score_test_joint(y_combined, X, Z)
    print(result_combined)
    
    # =================================================================
    # Example 5: Using individual test functions
    # =================================================================
    print("\n" + "=" * 70)
    print("Example 5: Using Individual Test Functions")
    print("=" * 70)
    
    # Test for autocorrelation only
    S1, p_S1, rho_hat = score_test_autocorrelation(y_ar1, X, return_rho=True)
    print(f"\nAutocorrelation Test (S₁):")
    print(f"  S₁ = {S1:.4f}")
    print(f"  p-value = {p_S1:.4f}")
    print(f"  ρ̂ = {rho_hat:.4f}")
    
    # Test for heteroscedasticity only
    S2, p_S2, df = score_test_heteroscedasticity(y_hetero, X, Z)
    print(f"\nHeteroscedasticity Test (S₂):")
    print(f"  S₂ = {S2:.4f}")
    print(f"  p-value = {p_S2:.4f}")
    print(f"  df = {df}")
    
    # =================================================================
    # Example 6: Using the class interface
    # =================================================================
    print("\n" + "=" * 70)
    print("Example 6: Using TsaiScoreTest Class")
    print("=" * 70)
    
    test = TsaiScoreTest(y_combined, X, Z)
    result = test.fit()
    
    print(f"\nTest Statistics:")
    print(f"  S (Joint) = {result.S:.4f}, p-value = {result.p_value:.4f}")
    print(f"  S₁ (AR) = {result.S1:.4f}, p-value = {result.p_value_S1:.4f}")
    print(f"  S₂ (Het) = {result.S2:.4f}, p-value = {result.p_value_S2:.4f}")
    print(f"\nEstimated Parameters:")
    print(f"  ρ̂ = {result.rho_hat:.4f}")
    print(f"  σ̂² = {result.sigma2_hat:.4f}")
    print(f"\nOLS Coefficients: {test.beta_hat}")
    
    # Export to dictionary
    print("\nExport to dictionary:")
    print(result.to_dict())


if __name__ == "__main__":
    main()
