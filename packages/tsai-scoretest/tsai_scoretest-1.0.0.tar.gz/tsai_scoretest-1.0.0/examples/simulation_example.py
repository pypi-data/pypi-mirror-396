"""
Example: Monte Carlo Simulation for Critical Values

This example demonstrates how to use Monte Carlo simulation to:
1. Verify the asymptotic distribution of the score test statistics
2. Compute finite-sample critical values
3. Analyze power against alternatives

Reference:
    Tsai, C.-L. (1986). Score test for the first-order autoregressive model 
    with heteroscedasticity. Biometrika, 73(2), 455-460.
"""

import numpy as np
from scipy import stats
import sys
import os

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scoretest import simulate_critical_values
from scoretest.simulation import simulate_power


def main():
    """Run simulation examples."""
    
    print("=" * 70)
    print("ScoreTest Package - Monte Carlo Simulation Examples")
    print("=" * 70)
    
    # =================================================================
    # Example 1: Simulate critical values
    # =================================================================
    print("\n" + "-" * 70)
    print("Example 1: Simulating Critical Values")
    print("-" * 70)
    
    # Run Monte Carlo simulation
    results = simulate_critical_values(
        sample_size=100,
        q=1,
        n_simulations=5000,
        p=2,
        significance_levels=[0.01, 0.05, 0.10],
        seed=42,
        verbose=True
    )
    
    # Print results
    print(results)
    
    # =================================================================
    # Example 2: Compare with asymptotic critical values
    # =================================================================
    print("\n" + "-" * 70)
    print("Example 2: Asymptotic vs Finite-Sample Critical Values")
    print("-" * 70)
    
    q = 1
    print("\nCritical values for joint test S ~ χ²({})".format(q + 1))
    print("\nα       Asymptotic    Simulated     Difference")
    print("-" * 50)
    
    for alpha in [0.10, 0.05, 0.01]:
        asymp = stats.chi2.ppf(1 - alpha, q + 1)
        simul = results.critical_values_S[alpha]
        diff = simul - asymp
        print(f"{alpha:.2f}      {asymp:8.4f}      {simul:8.4f}      {diff:+7.4f}")
    
    # =================================================================
    # Example 3: Empirical size (rejection rate under H_0)
    # =================================================================
    print("\n" + "-" * 70)
    print("Example 3: Empirical Size at Nominal Levels")
    print("-" * 70)
    
    print("\nRejection rates at asymptotic critical values:")
    print("(Should be close to nominal level under H_0)")
    print("\nNominal    S Rate    S₁ Rate   S₂ Rate")
    print("-" * 45)
    
    for alpha in [0.10, 0.05, 0.01]:
        s_rate = results.rejection_rates['S'][alpha]
        s1_rate = results.rejection_rates['S1'][alpha]
        s2_rate = results.rejection_rates['S2'][alpha]
        print(f"α = {alpha:.2f}    {s_rate:.4f}    {s1_rate:.4f}    {s2_rate:.4f}")
    
    # =================================================================
    # Example 4: Summary statistics of simulated distributions
    # =================================================================
    print("\n" + "-" * 70)
    print("Example 4: Distribution Properties")
    print("-" * 70)
    
    print("\nComparison with theoretical χ² moments:")
    print("\nStatistic    Mean    Variance    (Theoretical)")
    print("-" * 55)
    
    # For χ²(df): E[X] = df, Var(X) = 2*df
    df_S = q + 1
    df_S1 = 1
    df_S2 = q
    
    print(f"S           {np.mean(results.S_statistics):6.3f}    {np.var(results.S_statistics):7.3f}       "
          f"({df_S}, {2*df_S})")
    print(f"S₁          {np.mean(results.S1_statistics):6.3f}    {np.var(results.S1_statistics):7.3f}       "
          f"({df_S1}, {2*df_S1})")
    print(f"S₂          {np.mean(results.S2_statistics):6.3f}    {np.var(results.S2_statistics):7.3f}       "
          f"({df_S2}, {2*df_S2})")
    
    # =================================================================
    # Example 5: Power simulation
    # =================================================================
    print("\n" + "-" * 70)
    print("Example 5: Power Analysis")
    print("-" * 70)
    
    print("\nSimulating power against alternatives...")
    
    power_results = simulate_power(
        sample_size=100,
        rho_values=[0, 0.1, 0.2, 0.3, 0.4, 0.5],
        lambda_values=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
        q=1,
        n_simulations=500,
        alpha=0.05,
        seed=42,
        verbose=True
    )
    
    print("\nPower against autocorrelation (S₁ test):")
    print("ρ        Power")
    print("-" * 25)
    for rho, power in zip(power_results['rho_values'], power_results['power_S1']):
        print(f"{rho:.2f}      {power:.4f}")
    
    print("\nPower against heteroscedasticity (S₂ test):")
    print("λ        Power")
    print("-" * 25)
    for lam, power in zip(power_results['lambda_values'], power_results['power_S2']):
        print(f"{lam:.2f}      {power:.4f}")
    
    # =================================================================
    # Example 6: Generate LaTeX table
    # =================================================================
    print("\n" + "-" * 70)
    print("Example 6: LaTeX Table Output")
    print("-" * 70)
    
    print("\nLaTeX code for critical values table:")
    print(results.to_latex_table())
    
    # =================================================================
    # Example 7: Effect of sample size
    # =================================================================
    print("\n" + "-" * 70)
    print("Example 7: Effect of Sample Size on Critical Values")
    print("-" * 70)
    
    sample_sizes = [50, 100, 200, 500]
    print("\nCritical values for S at α = 0.05 by sample size:")
    print(f"(Asymptotic: {stats.chi2.ppf(0.95, 2):.4f})")
    print("\nT        CV(S)     CV(S₁)    CV(S₂)")
    print("-" * 45)
    
    for T in sample_sizes:
        res = simulate_critical_values(
            sample_size=T,
            q=1,
            n_simulations=2000,
            seed=42,
            verbose=False
        )
        print(f"{T:4d}     {res.critical_values_S[0.05]:.4f}    "
              f"{res.critical_values_S1[0.05]:.4f}    {res.critical_values_S2[0.05]:.4f}")


if __name__ == "__main__":
    main()
