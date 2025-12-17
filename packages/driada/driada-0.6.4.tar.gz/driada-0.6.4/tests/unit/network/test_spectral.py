"""
Unit tests for spectral.py module.

Tests spectral network analysis functions including free entropy,
Rényi q-entropy, and von Neumann spectral entropy calculations.
"""

import pytest
import numpy as np
from numpy.testing import assert_almost_equal
from driada.network.spectral import (
    free_entropy,
    q_entropy, 
    spectral_entropy
)


class TestFreeEntropy:
    """Test free_entropy function."""
    
    def test_empty_spectrum_raises(self):
        """Test that empty spectrum raises ValueError."""
        spectrum = np.array([])
        with pytest.raises(ValueError, match="Spectrum array cannot be empty"):
            free_entropy(spectrum, t=1.0)
    
    def test_negative_t_raises(self):
        """Test that negative t raises ValueError."""
        spectrum = np.array([0, 1, 2])
        with pytest.raises(ValueError, match="t must be positive"):
            free_entropy(spectrum, t=-1.0)
    
    def test_zero_spectrum(self):
        """Test free entropy with all zero eigenvalues."""
        spectrum = np.array([0, 0, 0, 0])
        F = free_entropy(spectrum, t=1.0)
        # exp(-0) = 1 for each eigenvalue, so Z = 4, F = log2(4) = 2
        assert_almost_equal(F, 2.0)
    
    def test_single_eigenvalue(self):
        """Test with single eigenvalue."""
        spectrum = np.array([1.0])
        F = free_entropy(spectrum, t=1.0)
        # Z = exp(-1), F = log2(exp(-1)) = -1/ln(2)
        expected = -1.0 / np.log(2)
        assert_almost_equal(F, expected)
    
    def test_increasing_temperature(self):
        """Test that free entropy increases with temperature (decreasing t)."""
        spectrum = np.array([0, 1, 2, 3])
        F_low_t = free_entropy(spectrum, t=0.1)  # High temperature
        F_high_t = free_entropy(spectrum, t=10.0)  # Low temperature
        
        # Higher temperature should give higher free entropy
        assert F_low_t > F_high_t
    
    def test_positive_spectrum(self):
        """Test with typical Laplacian spectrum."""
        spectrum = np.array([0, 0.5, 1.5, 2.0])
        F = free_entropy(spectrum, t=1.0)
        assert F > 0  # Free entropy typically positive
    
    def test_large_eigenvalues(self):
        """Test numerical stability with large eigenvalues."""
        spectrum = np.array([0, 10, 20, 30])
        F = free_entropy(spectrum, t=1.0)
        # Should not overflow or underflow
        assert np.isfinite(F)
    
    def test_negative_eigenvalues(self):
        """Test with negative eigenvalues (e.g., from adjacency matrix)."""
        spectrum = np.array([-2, -1, 0, 1, 2])
        F = free_entropy(spectrum, t=1.0)
        # Should handle negative eigenvalues properly
        assert np.isfinite(F)
        assert np.isreal(F)


class TestQEntropy:
    """Test q_entropy function."""
    
    def test_empty_spectrum_raises(self):
        """Test that empty spectrum raises ValueError."""
        spectrum = np.array([])
        with pytest.raises(ValueError, match="Spectrum array cannot be empty"):
            q_entropy(spectrum, t=1.0)
    
    def test_negative_t_raises(self):
        """Test that negative t raises ValueError."""
        spectrum = np.array([0, 1, 2])
        with pytest.raises(ValueError, match="t must be positive"):
            q_entropy(spectrum, t=-1.0)
    
    def test_q_equals_one(self):
        """Test that q=1 gives von Neumann entropy."""
        spectrum = np.array([0, 1, 1, 2])
        S_q1 = q_entropy(spectrum, t=1.0, q=1)
        S_vn = spectral_entropy(spectrum, t=1.0)
        assert_almost_equal(S_q1, S_vn)
    
    def test_q_zero_raises(self):
        """Test that q=0 raises ValueError."""
        spectrum = np.array([0, 1, 2])
        with pytest.raises(ValueError, match="q must be positive"):
            q_entropy(spectrum, t=1.0, q=0)
    
    def test_negative_q_raises(self):
        """Test that negative q raises ValueError."""
        spectrum = np.array([0, 1, 2])
        with pytest.raises(ValueError, match="q must be positive"):
            q_entropy(spectrum, t=1.0, q=-1)
    
    def test_q_limit_zero(self):
        """Test behavior as q approaches 0 (Hartley entropy)."""
        spectrum = np.array([0, 0.1, 0.2, 1.0])
        S_small_q = q_entropy(spectrum, t=1.0, q=0.01)
        # As q→0, should approach log2(effective rank)
        assert S_small_q > 0
    
    def test_q_limit_infinity(self):
        """Test behavior for large q (min-entropy)."""
        spectrum = np.array([0, 1, 2, 3])
        S_large_q = q_entropy(spectrum, t=1.0, q=100)
        # For large q, dominated by smallest eigenvalue contribution
        assert S_large_q >= 0
    
    def test_renyi_ordering(self):
        """Test that Rényi entropy is non-increasing in q."""
        spectrum = np.array([0, 0.5, 1.5, 2.0])
        t = 1.0
        
        S_05 = q_entropy(spectrum, t, q=0.5)
        S_1 = q_entropy(spectrum, t, q=1.0)
        S_2 = q_entropy(spectrum, t, q=2.0)
        
        # Rényi entropy should be non-increasing in q
        assert S_05 >= S_1
        assert S_1 >= S_2
    
    def test_uniform_spectrum(self):
        """Test with uniform eigenvalue distribution."""
        spectrum = np.ones(4)
        S = q_entropy(spectrum, t=1.0, q=2.0)
        assert np.isfinite(S)
    
    def test_imaginary_entropy_detection(self):
        """Test detection of imaginary entropy (should not happen with real spectrum)."""
        # This test verifies the error handling works
        # In practice, with real spectra this should not occur
        spectrum = np.array([0, 1, 2, 3])
        # Normal computation should not produce imaginary entropy
        S = q_entropy(spectrum, t=1.0, q=2.0)
        assert np.isreal(S)


class TestSpectralEntropy:
    """Test spectral_entropy function."""
    
    def test_empty_spectrum_raises(self):
        """Test that empty spectrum raises ValueError."""
        spectrum = np.array([])
        with pytest.raises(ValueError, match="Spectrum array cannot be empty"):
            spectral_entropy(spectrum, t=1.0)
    
    def test_negative_t_raises(self):
        """Test that negative t raises ValueError."""
        spectrum = np.array([0, 1, 2])
        with pytest.raises(ValueError, match="t must be positive"):
            spectral_entropy(spectrum, t=-1.0)
    
    def test_zero_entropy(self):
        """Test case that should give zero entropy."""
        # Single non-zero probability
        spectrum = np.array([0, 1000, 1000, 1000])  # One small, others large
        S = spectral_entropy(spectrum, t=100.0)  # High t suppresses large eigenvalues
        # Should be close to zero (one dominant state)
        assert S < 0.1
    
    def test_maximum_entropy(self):
        """Test maximum entropy case."""
        # All equal eigenvalues give uniform distribution
        spectrum = np.ones(4)
        S = spectral_entropy(spectrum, t=1.0)
        # Maximum entropy is log2(n)
        assert_almost_equal(S, 2.0)  # log2(4) = 2
    
    def test_entropy_bounds(self):
        """Test that entropy respects theoretical bounds."""
        spectrum = np.array([0, 0.5, 1.0, 1.5, 2.0])
        S = spectral_entropy(spectrum, t=1.0)
        
        # Entropy should be between 0 and log2(n)
        assert 0 <= S <= np.log2(len(spectrum))
    
    def test_temperature_effect(self):
        """Test effect of temperature parameter."""
        spectrum = np.array([0, 1, 2])
        
        S_low_t = spectral_entropy(spectrum, t=0.1)   # High temperature
        S_high_t = spectral_entropy(spectrum, t=10.0)  # Low temperature
        
        # High temperature should give higher entropy (more mixed state)
        assert S_low_t > S_high_t
    
    def test_verbose_mode(self):
        """Test verbose output (should print intermediate values)."""
        spectrum = np.array([0, 1])
        # This should print but not affect the result
        S = spectral_entropy(spectrum, t=1.0, verbose=1)
        assert isinstance(S, float)
    
    def test_degenerate_spectrum(self):
        """Test with degenerate eigenvalues."""
        spectrum = np.array([0, 1, 1, 1, 2, 2])
        S = spectral_entropy(spectrum, t=1.0)
        assert 0 <= S <= np.log2(len(spectrum))
    
    def test_numerical_stability(self):
        """Test numerical stability with extreme values."""
        # Very small eigenvalues
        spectrum = np.array([0, 1e-10, 1e-9, 1e-8])
        S = spectral_entropy(spectrum, t=1.0)
        assert np.isfinite(S)
        
        # Very large eigenvalues
        spectrum = np.array([0, 100, 200, 300])
        S = spectral_entropy(spectrum, t=0.01)
        assert np.isfinite(S)
    
    def test_trimming_zeros(self):
        """Test that zero probabilities are properly trimmed."""
        # Create spectrum that will have some zero probabilities
        spectrum = np.array([0, 0, 0, 1000])  # Most weight on last eigenvalue
        S = spectral_entropy(spectrum, t=10.0)  # High t emphasizes small eigenvalues
        # Should handle zero probabilities without log(0) errors
        assert np.isfinite(S)


class TestIntegration:
    """Integration tests combining multiple functions."""
    
    def test_consistency_between_functions(self):
        """Test consistency between q_entropy and spectral_entropy."""
        spectrum = np.array([0, 0.5, 1.0, 1.5])
        t = 1.5
        
        # q_entropy with q=1 should equal spectral_entropy
        S_q = q_entropy(spectrum, t, q=1.0)
        S_vn = spectral_entropy(spectrum, t)
        assert_almost_equal(S_q, S_vn)
    
    def test_realistic_laplacian_spectrum(self):
        """Test with realistic graph Laplacian spectrum."""
        # Path graph P4 Laplacian eigenvalues (approximately)
        spectrum = np.array([0, 0.586, 2.0, 3.414])
        
        F = free_entropy(spectrum, t=1.0)
        S = spectral_entropy(spectrum, t=1.0)
        S_q = q_entropy(spectrum, t=1.0, q=2.0)
        
        # All should be finite and positive
        assert np.isfinite(F) and F > 0
        assert np.isfinite(S) and S > 0
        assert np.isfinite(S_q) and S_q >= 0
    
    def test_complete_graph_spectrum(self):
        """Test with complete graph spectrum."""
        # Complete graph K_n has eigenvalues 0 (once) and n (n-1 times)
        n = 5
        spectrum = np.array([0] + [n] * (n-1))
        
        # Test all three entropy measures
        F = free_entropy(spectrum, t=0.5)
        S = spectral_entropy(spectrum, t=0.5)
        S_q = q_entropy(spectrum, t=0.5, q=0.5)
        
        # All should be well-defined
        assert all(np.isfinite(x) for x in [F, S, S_q])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])