"""
Advanced Examples for the scoretest Package
==========================================

This module contains advanced examples demonstrating the full capabilities
of the scoretest package for real-world econometric applications.

Reference:
    Tsai, C.-L. (1986). Score test for the first-order autoregressive model
    with heteroscedasticity. Biometrika, 73(2), 455-460.
"""

import numpy as np
from scipy import stats

# Import the scoretest package
import sys
sys.path.insert(0, '..')
from scoretest import (
    TsaiScoreTest, 
    score_test_joint, 
    score_test_autocorrelation,
    score_test_heteroscedasticity
)
from scoretest.diagnostics import normal_curvature, parameter_sensitivity
from scoretest.simulation import simulate_critical_values, simulate_power
from scoretest.weight_functions import (
    exponential_weight, 
    linear_weight, 
    power_weight
)


def example_1_comprehensive_analysis():
    """
    Example 1: Comprehensive Model Diagnostics
    
    Demonstrates a complete workflow for testing both autocorrelation
    and heteroscedasticity in a regression model with interpretation.
    """
    print("=" * 70)
    print("Example 1: Comprehensive Model Diagnostics")
    print("=" * 70)
    
    # Simulate economic data: investment equation
    np.random.seed(12345)
    T = 150
    
    # Regressors: constant, output, capital stock
    output = 100 + 3 * np.arange(T) + 10 * np.random.randn(T)
    capital = 50 + 2 * np.arange(T) + 5 * np.random.randn(T)
    
    X = np.column_stack([
        np.ones(T),      # Constant
        output,          # Output
        capital          # Capital stock
    ])
    
    # True model: Investment = β₀ + β₁·Output + β₂·Capital + u
    beta_true = np.array([10.0, 0.3, 0.1])
    
    # Generate AR(1) errors with heteroscedasticity
    rho_true = 0.4
    sigma_base = 5.0
    
    # Heteroscedasticity: variance increases with output
    het_factor = np.sqrt(1 + 0.01 * (output - output.min()))
    
    e = np.zeros(T)
    e[0] = het_factor[0] * sigma_base * np.random.randn()
    for t in range(1, T):
        e[t] = rho_true * e[t-1] + het_factor[t] * sigma_base * np.random.randn()
    
    y = X @ beta_true + e
    
    # Heteroscedasticity variables: output and its square
    Z = np.column_stack([output, output**2])
    
    # Perform the score test
    result = score_test_joint(y, X, Z)
    print(result)
    
    # Additional diagnostics
    print("\n" + "-" * 70)
    print("Normal Curvature Analysis (Equation 3.2)")
    print("-" * 70)
    curvature = normal_curvature(y, X, Z)
    print(f"Maximum curvature C_max: {curvature.C_max:.4f}")
    print(f"Direction of maximum influence: {curvature.l_max}")
    
    print("\n" + "-" * 70)
    print("Parameter Sensitivity Analysis (Equation 3.4)")
    print("-" * 70)
    sensitivity = parameter_sensitivity(y, X, Z)
    print(f"Sensitivity matrix shape: {sensitivity.sensitivity_matrix.shape}")
    print("Sensitivity norms for each coefficient:")
    param_names = ['Intercept', 'Output', 'Capital']
    for i, name in enumerate(param_names):
        print(f"  {name}: {sensitivity.sensitivity_norms[i]:.4f}")
    
    print()


def example_2_finite_sample_critical_values():
    """
    Example 2: Finite-Sample Critical Values
    
    Monte Carlo simulation to obtain critical values for small samples.
    """
    print("=" * 70)
    print("Example 2: Finite-Sample Critical Values via Monte Carlo")
    print("=" * 70)
    
    # Parameters
    T = 30  # Small sample
    p = 2   # Intercept + one regressor
    q = 1   # One heteroscedasticity variable
    n_sims = 5000
    
    print(f"\nSimulating {n_sims} replications for T={T}, p={p}, q={q}...")
    
    cv_results = simulate_critical_values(
        T=T, p=p, q=q,
        n_simulations=n_sims,
        alpha_levels=[0.01, 0.05, 0.10],
        seed=42
    )
    
    print("\nResults:")
    print("-" * 70)
    print("\nEmpirical Critical Values:")
    for alpha, cvs in cv_results.critical_values.items():
        print(f"\n  α = {alpha}:")
        print(f"    S (joint):    {cvs['S']:.4f}")
        print(f"    S₁ (autocorr): {cvs['S1']:.4f}")
        print(f"    S₂ (heterosc): {cvs['S2']:.4f}")
    
    print("\n\nAsymptotic Critical Values (χ² distribution):")
    for alpha, cvs in cv_results.asymptotic_cv.items():
        print(f"\n  α = {alpha}:")
        print(f"    S (df={q+1}):  {cvs['S']:.4f}")
        print(f"    S₁ (df=1):    {cvs['S1']:.4f}")
        print(f"    S₂ (df={q}):    {cvs['S2']:.4f}")
    
    print("\n\nEmpirical Size at Nominal Levels:")
    for alpha, sizes in cv_results.empirical_sizes.items():
        print(f"\n  Nominal α = {alpha}:")
        print(f"    S:  {sizes['S']:.4f}")
        print(f"    S₁: {sizes['S1']:.4f}")
        print(f"    S₂: {sizes['S2']:.4f}")
    
    print()


def example_3_power_analysis():
    """
    Example 3: Power Analysis
    
    Examine how power varies with the strength of autocorrelation.
    """
    print("=" * 70)
    print("Example 3: Power Analysis")
    print("=" * 70)
    
    T = 100
    p = 2
    q = 1
    n_sims = 1000
    alpha = 0.05
    
    rho_values = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    
    print(f"\nComputing power for various ρ values (T={T}, α={alpha})...")
    print("-" * 70)
    
    power_results = simulate_power(
        T=T, p=p, q=q,
        rho_values=rho_values,
        n_simulations=n_sims,
        alpha=alpha,
        seed=42
    )
    
    print("\n    ρ      Power(S)   Power(S₁)   Power(S₂)")
    print("  " + "-" * 45)
    for i, rho in enumerate(rho_values):
        print(f"  {rho:5.2f}    {power_results.power_S[i]:7.3f}    {power_results.power_S1[i]:8.3f}    {power_results.power_S2[i]:8.3f}")
    
    print("\nNote: Power of S₂ should remain approximately equal to α")
    print("(since we're only varying autocorrelation, not heteroscedasticity)")
    print()


def example_4_comparison_with_durbin_watson():
    """
    Example 4: Comparison with Durbin-Watson Test
    
    Compare the score test with the traditional Durbin-Watson test.
    """
    print("=" * 70)
    print("Example 4: Comparison with Durbin-Watson Test")
    print("=" * 70)
    
    from scoretest.utils import durbin_watson_statistic, breusch_godfrey_statistic
    
    np.random.seed(2024)
    T = 100
    
    # Generate data with moderate autocorrelation
    rho = 0.35
    X = np.column_stack([np.ones(T), np.random.randn(T)])
    beta = np.array([1.0, 2.0])
    
    # AR(1) errors
    e = np.zeros(T)
    e[0] = np.random.randn()
    for t in range(1, T):
        e[t] = rho * e[t-1] + np.random.randn()
    
    y = X @ beta + e
    
    # Score test
    result = score_test_joint(y, X)
    
    # OLS residuals
    beta_hat = np.linalg.lstsq(X, y, rcond=None)[0]
    residuals = y - X @ beta_hat
    
    # Durbin-Watson
    dw = durbin_watson_statistic(residuals)
    
    # Breusch-Godfrey
    bg_stat, bg_pval = breusch_godfrey_statistic(y, X, order=1)
    
    print(f"\nTrue autocorrelation: ρ = {rho}")
    print("-" * 70)
    print("\nTest Results:")
    print(f"  Tsai Score Test (S₁):       {result.S1:8.4f}  (p = {result.p_value_S1:.4f})")
    print(f"  Durbin-Watson:              {dw:8.4f}")
    print(f"  Breusch-Godfrey LM:         {bg_stat:8.4f}  (p = {bg_pval:.4f})")
    print(f"\n  Estimated ρ̂:                {result.rho_hat:8.4f}")
    
    print("\nInterpretation:")
    print("  DW ≈ 2(1 - ρ̂) under AR(1), so expected DW =", f"{2*(1-result.rho_hat):.4f}")
    print("  DW < 2 suggests positive autocorrelation")
    print()


def example_5_heteroscedasticity_patterns():
    """
    Example 5: Different Heteroscedasticity Patterns
    
    Test for various forms of heteroscedasticity.
    """
    print("=" * 70)
    print("Example 5: Testing Different Heteroscedasticity Patterns")
    print("=" * 70)
    
    np.random.seed(999)
    T = 200
    X = np.column_stack([np.ones(T), np.random.randn(T)])
    beta = np.array([1.0, 2.0])
    
    patterns = {
        'None (Homoscedastic)': lambda t: 1.0,
        'Linear in time': lambda t: np.sqrt(1 + 0.02 * t),
        'Quadratic in time': lambda t: np.sqrt(1 + 0.0002 * t**2),
        'Exponential in time': lambda t: np.exp(0.01 * t),
        'Periodic (business cycle)': lambda t: np.sqrt(1 + 0.5 * np.sin(2 * np.pi * t / 40))
    }
    
    print("-" * 70)
    print(f"{'Pattern':<25} {'S₂':>10} {'p-value':>10} {'Decision':>15}")
    print("-" * 70)
    
    for name, var_func in patterns.items():
        # Generate heteroscedastic errors
        e = np.array([var_func(t) * np.random.randn() for t in range(T)])
        y = X @ beta + e
        
        # Use time as heteroscedasticity variable
        Z = np.arange(1, T + 1).reshape(-1, 1)
        
        result = score_test_joint(y, X, Z)
        decision = 'Reject H₀' if result.p_value_S2 < 0.05 else 'Fail to Reject'
        
        print(f"  {name:<23} {result.S2:10.4f} {result.p_value_S2:10.4f} {decision:>15}")
    
    print()


def example_6_publication_quality_output():
    """
    Example 6: Publication-Quality Output
    
    Generate output suitable for academic publications.
    """
    print("=" * 70)
    print("Example 6: Publication-Quality Output")
    print("=" * 70)
    
    np.random.seed(42)
    T = 250
    
    # Generate realistic economic data
    time_trend = np.arange(T)
    X = np.column_stack([
        np.ones(T),
        100 + 0.5 * time_trend + 5 * np.random.randn(T),  # GDP
        50 + 0.3 * time_trend + 3 * np.random.randn(T),   # Investment
    ])
    
    beta = np.array([10.0, 0.5, 0.3])
    
    # AR(1) heteroscedastic errors
    rho = 0.3
    e = np.zeros(T)
    for t in range(T):
        het = np.sqrt(1 + 0.01 * t)
        if t == 0:
            e[t] = het * np.random.randn()
        else:
            e[t] = rho * e[t-1] + het * np.random.randn()
    
    y = X @ beta + e
    
    # Time as heteroscedasticity variable
    Z = time_trend.reshape(-1, 1)
    
    # Perform test
    result = score_test_joint(y, X, Z)
    
    # Print publication-quality summary
    print(result.summary())
    
    # Export to dictionary for tables
    print("\nResults as dictionary (for programmatic access):")
    results_dict = result.to_dict()
    for key, value in results_dict.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.6f}")
        else:
            print(f"  {key}: {value}")
    
    # LaTeX-ready output
    print("\n" + "-" * 70)
    print("LaTeX-Ready Table Row:")
    print("-" * 70)
    latex_row = (
        f"S = ${result.S:.3f}$ & "
        f"S_1 = ${result.S1:.3f}$ & "
        f"S_2 = ${result.S2:.3f}$ & "
        f"p = ${result.p_value:.4f}$ \\\\"
    )
    print(latex_row)
    print()


def example_7_multiple_weight_functions():
    """
    Example 7: Comparing Different Weight Functions
    
    Test using different specifications for the weight function.
    """
    print("=" * 70)
    print("Example 7: Comparing Different Weight Function Specifications")
    print("=" * 70)
    
    np.random.seed(7777)
    T = 150
    
    X = np.column_stack([np.ones(T), np.random.randn(T)])
    beta = np.array([1.0, 2.0])
    
    # Generate heteroscedastic errors (exponential pattern)
    het = np.exp(0.02 * np.arange(T))
    e = np.sqrt(het) * np.random.randn(T)
    y = X @ beta + e
    
    Z = np.arange(1, T + 1).reshape(-1, 1)
    
    # Test with different weight functions
    weight_funcs = {
        'Exponential (default)': exponential_weight(),
        'Linear': linear_weight(),
        'Power': power_weight(),
    }
    
    print("-" * 70)
    print(f"{'Weight Function':<25} {'S':>10} {'S₂':>10} {'p-value(S₂)':>12}")
    print("-" * 70)
    
    for name, wf in weight_funcs.items():
        test = TsaiScoreTest(y, X, Z, weight_deriv=wf.derivative_at_lambda_star)
        result = test.fit()
        print(f"  {name:<23} {result.S:10.4f} {result.S2:10.4f} {result.p_value_S2:12.4f}")
    
    print("\nNote: Results may differ based on the assumed form of heteroscedasticity")
    print()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("SCORETEST PACKAGE - ADVANCED EXAMPLES")
    print("Tsai (1986) Score Test for AR(1) with Heteroscedasticity")
    print("=" * 70 + "\n")
    
    # Run all examples
    example_1_comprehensive_analysis()
    example_2_finite_sample_critical_values()
    example_3_power_analysis()
    example_4_comparison_with_durbin_watson()
    example_5_heteroscedasticity_patterns()
    example_6_publication_quality_output()
    example_7_multiple_weight_functions()
    
    print("=" * 70)
    print("All examples completed successfully!")
    print("=" * 70)
