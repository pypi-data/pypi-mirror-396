"""
Test Suite for the ScoreTest Package.

This module contains comprehensive tests to verify the correctness
of the implementation against the Tsai (1986) paper.

Tests include:
1. Basic functionality tests
2. Known value tests (comparing with theoretical results)
3. Asymptotic distribution tests
4. Robustness tests
5. Edge case tests
"""

import numpy as np
from scipy import stats
import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scoretest import (
    TsaiScoreTest,
    score_test_autocorrelation,
    score_test_heteroscedasticity,
    score_test_joint,
    simulate_critical_values,
    normal_curvature,
    parameter_sensitivity,
    ols_residuals,
    compute_rho_hat,
    compute_variance_vector,
)
from scoretest.weight_functions import (
    exponential_weight,
    linear_weight,
    compute_weight_derivatives,
)


class TestOLSResiduals:
    """Tests for OLS residuals computation."""
    
    def test_residuals_sum_to_zero_with_intercept(self):
        """Residuals should sum to zero when intercept is included."""
        np.random.seed(42)
        T = 100
        X = np.column_stack([np.ones(T), np.random.randn(T)])
        y = X @ [1, 0.5] + np.random.randn(T)
        
        residuals = ols_residuals(y, X)
        assert np.abs(np.sum(residuals)) < 1e-10
    
    def test_residuals_orthogonal_to_X(self):
        """Residuals should be orthogonal to design matrix."""
        np.random.seed(42)
        T = 100
        X = np.column_stack([np.ones(T), np.random.randn(T), np.random.randn(T)])
        y = X @ [1, 0.5, -0.3] + np.random.randn(T)
        
        residuals = ols_residuals(y, X)
        orthogonality = X.T @ residuals
        
        for val in orthogonality:
            assert np.abs(val) < 1e-10
    
    def test_return_all_option(self):
        """Test that return_all returns all quantities."""
        np.random.seed(42)
        T = 50
        X = np.column_stack([np.ones(T), np.random.randn(T)])
        y = X @ [1, 0.5] + np.random.randn(T)
        
        result = ols_residuals(y, X, return_all=True)
        assert len(result) == 3
        
        residuals, beta_hat, sigma2_hat = result
        assert len(residuals) == T
        assert len(beta_hat) == 2
        assert sigma2_hat > 0


class TestRhoHat:
    """Tests for autocorrelation coefficient estimation."""
    
    def test_rho_hat_bounds(self):
        """ρ̂ should be between -1 and 1."""
        np.random.seed(42)
        residuals = np.random.randn(100)
        
        rho_hat = compute_rho_hat(residuals)
        assert -1 <= rho_hat <= 1
    
    def test_rho_hat_iid_near_zero(self):
        """For i.i.d. residuals, ρ̂ should be near zero."""
        np.random.seed(42)
        residuals = np.random.randn(1000)
        
        rho_hat = compute_rho_hat(residuals)
        # Should be close to zero for large sample
        assert np.abs(rho_hat) < 0.1
    
    def test_rho_hat_ar1_consistent(self):
        """ρ̂ should be consistent for AR(1) process."""
        np.random.seed(42)
        T = 1000
        true_rho = 0.7
        
        residuals = np.zeros(T)
        residuals[0] = np.random.randn()
        for t in range(1, T):
            residuals[t] = true_rho * residuals[t-1] + np.random.randn()
        
        rho_hat = compute_rho_hat(residuals)
        # Should be reasonably close to true value
        assert np.abs(rho_hat - true_rho) < 0.1


class TestScoreTestS1:
    """Tests for S_1 statistic (autocorrelation test)."""
    
    def test_s1_nonnegative(self):
        """S_1 should always be non-negative."""
        np.random.seed(42)
        T = 100
        X = np.column_stack([np.ones(T), np.random.randn(T)])
        y = X @ [1, 0.5] + np.random.randn(T)
        
        S1, _ = score_test_autocorrelation(y, X)
        assert S1 >= 0
    
    def test_s1_formula(self):
        """Verify S_1 = (Tρ̂)²/(T-1)."""
        np.random.seed(42)
        T = 100
        X = np.column_stack([np.ones(T), np.random.randn(T)])
        y = X @ [1, 0.5] + np.random.randn(T)
        
        S1, _, rho_hat = score_test_autocorrelation(y, X, return_rho=True)
        
        expected_S1 = (T * rho_hat)**2 / (T - 1)
        assert np.abs(S1 - expected_S1) < 1e-10
    
    def test_s1_asymptotic_distribution(self):
        """S_1 should follow χ²(1) under H_0 asymptotically."""
        np.random.seed(42)
        n_sim = 1000
        T = 200
        S1_values = []
        
        for _ in range(n_sim):
            X = np.column_stack([np.ones(T), np.random.randn(T)])
            y = X @ [1, 0.5] + np.random.randn(T)  # No autocorrelation
            S1, _ = score_test_autocorrelation(y, X)
            S1_values.append(S1)
        
        # Kolmogorov-Smirnov test against χ²(1)
        _, p_value = stats.kstest(S1_values, 'chi2', args=(1,))
        # Should not reject that S_1 ~ χ²(1)
        assert p_value > 0.01


class TestScoreTestS2:
    """Tests for S_2 statistic (heteroscedasticity test)."""
    
    def test_s2_nonnegative(self):
        """S_2 should always be non-negative."""
        np.random.seed(42)
        T = 100
        X = np.column_stack([np.ones(T), np.random.randn(T)])
        Z = np.arange(1, T + 1).reshape(-1, 1)
        y = X @ [1, 0.5] + np.random.randn(T)
        
        S2, _, _ = score_test_heteroscedasticity(y, X, Z)
        assert S2 >= 0
    
    def test_s2_asymptotic_distribution(self):
        """S_2 should follow χ²(q) under H_0 asymptotically."""
        np.random.seed(42)
        n_sim = 500
        T = 200
        q = 1
        S2_values = []
        
        for _ in range(n_sim):
            X = np.column_stack([np.ones(T), np.random.randn(T)])
            Z = np.arange(1, T + 1).reshape(-1, 1)
            y = X @ [1, 0.5] + np.random.randn(T)  # Homoscedastic
            S2, _, _ = score_test_heteroscedasticity(y, X, Z)
            S2_values.append(S2)
        
        # Kolmogorov-Smirnov test against χ²(q)
        _, p_value = stats.kstest(S2_values, 'chi2', args=(q,))
        assert p_value > 0.01


class TestJointScoreTest:
    """Tests for joint score test S = S_1 + S_2."""
    
    def test_s_equals_s1_plus_s2(self):
        """S should equal S_1 + S_2."""
        np.random.seed(42)
        T = 100
        X = np.column_stack([np.ones(T), np.random.randn(T)])
        y = X @ [1, 0.5] + np.random.randn(T)
        
        result = score_test_joint(y, X)
        
        assert np.abs(result.S - (result.S1 + result.S2)) < 1e-10
    
    def test_degrees_of_freedom(self):
        """Verify degrees of freedom are correct."""
        np.random.seed(42)
        T = 100
        q = 2
        X = np.column_stack([np.ones(T), np.random.randn(T)])
        Z = np.column_stack([np.arange(1, T + 1), np.arange(1, T + 1)**2])
        y = X @ [1, 0.5] + np.random.randn(T)
        
        result = score_test_joint(y, X, Z)
        
        assert result.df_S1 == 1
        assert result.df_S2 == q
        assert result.df_total == q + 1
    
    def test_p_values_valid(self):
        """P-values should be between 0 and 1."""
        np.random.seed(42)
        T = 100
        X = np.column_stack([np.ones(T), np.random.randn(T)])
        y = X @ [1, 0.5] + np.random.randn(T)
        
        result = score_test_joint(y, X)
        
        assert 0 <= result.p_value <= 1
        assert 0 <= result.p_value_S1 <= 1
        assert 0 <= result.p_value_S2 <= 1


class TestTsaiScoreTestClass:
    """Tests for the main TsaiScoreTest class."""
    
    def test_initialization(self):
        """Test proper initialization of TsaiScoreTest."""
        np.random.seed(42)
        T = 100
        X = np.column_stack([np.ones(T), np.random.randn(T)])
        y = X @ [1, 0.5] + np.random.randn(T)
        
        test = TsaiScoreTest(y, X)
        assert test.T == T
        assert test.p == 2
        assert test.q == 1  # Default Z is time trend
    
    def test_fit_returns_result(self):
        """Test that fit() returns ScoreTestResult."""
        np.random.seed(42)
        T = 100
        X = np.column_stack([np.ones(T), np.random.randn(T)])
        y = X @ [1, 0.5] + np.random.randn(T)
        
        test = TsaiScoreTest(y, X)
        result = test.fit()
        
        assert result is not None
        assert hasattr(result, 'S')
        assert hasattr(result, 'S1')
        assert hasattr(result, 'S2')
    
    def test_result_summary(self):
        """Test that summary() produces output."""
        np.random.seed(42)
        T = 100
        X = np.column_stack([np.ones(T), np.random.randn(T)])
        y = X @ [1, 0.5] + np.random.randn(T)
        
        result = score_test_joint(y, X)
        summary = result.summary()
        
        assert len(summary) > 0
        assert "Tsai (1986)" in summary
    
    def test_to_dict(self):
        """Test dictionary export."""
        np.random.seed(42)
        T = 100
        X = np.column_stack([np.ones(T), np.random.randn(T)])
        y = X @ [1, 0.5] + np.random.randn(T)
        
        result = score_test_joint(y, X)
        d = result.to_dict()
        
        assert 'S' in d
        assert 'S1' in d
        assert 'S2' in d
        assert 'p_value' in d


class TestWeightFunctions:
    """Tests for weight function implementations."""
    
    def test_exponential_weight_at_lambda_star(self):
        """Exponential weight should be 1 at λ* = 0."""
        wf = exponential_weight(q=2)
        z = np.array([1.0, 2.0])
        
        w_val = wf.w(z, wf.lambda_star)
        assert np.abs(w_val - 1.0) < 1e-10
    
    def test_exponential_derivative_at_lambda_star(self):
        """∂w/∂λ should equal z at λ* = 0."""
        wf = exponential_weight(q=2)
        z = np.array([1.0, 2.0])
        
        dw_val = wf.dw(z, wf.lambda_star)
        np.testing.assert_array_almost_equal(dw_val, z)
    
    def test_linear_weight_at_lambda_star(self):
        """Linear weight should be 1 at λ* = 0."""
        wf = linear_weight(q=2)
        z = np.array([1.0, 2.0])
        
        w_val = wf.w(z, wf.lambda_star)
        assert np.abs(w_val - 1.0) < 1e-10


class TestDiagnostics:
    """Tests for diagnostic functions."""
    
    def test_normal_curvature_positive(self):
        """Maximum curvature should be non-negative."""
        np.random.seed(42)
        T = 100
        X = np.column_stack([np.ones(T), np.random.randn(T)])
        y = X @ [1, 0.5] + np.random.randn(T)
        
        result = normal_curvature(y, X)
        assert result.C_max >= 0
    
    def test_parameter_sensitivity_dimensions(self):
        """Sensitivity matrix should have correct dimensions."""
        np.random.seed(42)
        T = 100
        p = 3
        q = 2
        X = np.column_stack([np.ones(T)] + [np.random.randn(T) for _ in range(p-1)])
        Z = np.column_stack([np.arange(1, T + 1)**j for j in range(1, q + 1)])
        y = X @ np.ones(p) + np.random.randn(T)
        
        result = parameter_sensitivity(y, X, Z)
        
        assert result.sensitivity_matrix.shape == (p, q + 1)
        assert len(result.sensitivity_to_rho) == p
        assert result.sensitivity_to_lambda.shape == (p, q)


class TestPowerAnalysis:
    """Tests for power against alternatives."""
    
    def test_power_increases_with_autocorrelation(self):
        """Power of S_1 should increase with |ρ|."""
        np.random.seed(42)
        n_sim = 200
        T = 100
        alpha = 0.05
        cv = stats.chi2.ppf(1 - alpha, 1)
        
        rho_values = [0, 0.3, 0.5]
        rejection_rates = []
        
        for rho in rho_values:
            rejections = 0
            for _ in range(n_sim):
                X = np.column_stack([np.ones(T), np.random.randn(T)])
                
                # Generate AR(1) errors
                e = np.zeros(T)
                e[0] = np.random.randn()
                for t in range(1, T):
                    e[t] = rho * e[t-1] + np.random.randn()
                
                y = X @ [1, 0.5] + e
                S1, _ = score_test_autocorrelation(y, X)
                
                if S1 > cv:
                    rejections += 1
            
            rejection_rates.append(rejections / n_sim)
        
        # Power should increase (or stay same) with |ρ|
        assert rejection_rates[1] >= rejection_rates[0] - 0.05
        assert rejection_rates[2] >= rejection_rates[1] - 0.05


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_minimum_sample_size(self):
        """Test with minimum viable sample size."""
        np.random.seed(42)
        T = 10
        X = np.column_stack([np.ones(T), np.random.randn(T)])
        y = X @ [1, 0.5] + np.random.randn(T)
        
        # Should not raise error
        result = score_test_joint(y, X)
        assert result is not None
    
    def test_single_regressor(self):
        """Test with only intercept."""
        np.random.seed(42)
        T = 50
        X = np.ones((T, 1))
        y = 1.0 + np.random.randn(T)
        
        result = score_test_joint(y, X)
        assert result is not None
    
    def test_dimension_mismatch_error(self):
        """Test error on dimension mismatch."""
        np.random.seed(42)
        T = 100
        X = np.random.randn(T + 1, 2)  # Wrong dimension
        y = np.random.randn(T)
        
        with pytest.raises(ValueError):
            TsaiScoreTest(y, X)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
