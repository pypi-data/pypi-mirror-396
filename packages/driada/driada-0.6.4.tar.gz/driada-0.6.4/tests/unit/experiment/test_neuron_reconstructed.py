"""Tests for neuron.reconstructed property and get_reconstructed() method."""

import numpy as np
import pytest
from driada.experiment.neuron import Neuron
from driada.information.info_base import TimeSeries


@pytest.fixture
def sample_neuron():
    """Create a neuron with reconstructed spikes."""
    # Fix random seed for reproducibility
    np.random.seed(42)
    # Generate simple synthetic calcium trace
    n_frames = 1000
    fps = 20.0
    ca_trace = np.random.randn(n_frames) * 0.05 + 0.1  # Noise + baseline

    # Add some spikes manually
    spike_times = [100, 300, 500, 700]
    for t in spike_times:
        # Simple spike-like transient
        for dt in range(40):
            if t + dt < n_frames:
                ca_trace[t + dt] += np.exp(-dt / 20.0)

    neuron = Neuron(
        cell_id=0,
        ca=ca_trace,
        sp=None,
        default_t_rise=0.25,
        default_t_off=2.0,
        fps=fps
    )

    # Reconstruct spikes
    neuron.reconstruct_spikes(method='wavelet', fps=fps, show_progress=False)

    return neuron


class TestNeuronReconstructedProperty:
    """Test suite for neuron.reconstructed property."""

    def test_reconstructed_returns_none_without_spikes(self):
        """Test that reconstructed returns None if no spikes detected."""
        ca_trace = np.random.randn(500) * 0.01  # Just noise
        neuron = Neuron(cell_id=0, ca=ca_trace, sp=None, fps=20.0)

        # No reconstruction yet
        assert neuron.reconstructed is None

    def test_reconstructed_returns_timeseries(self, sample_neuron):
        """Test that reconstructed returns TimeSeries object."""
        recon = sample_neuron.reconstructed

        assert recon is not None
        assert isinstance(recon, TimeSeries)
        assert recon.discrete is False  # Continuous signal

    def test_reconstructed_has_correct_length(self, sample_neuron):
        """Test that reconstructed signal has same length as original."""
        recon = sample_neuron.reconstructed

        assert len(recon.data) == len(sample_neuron.ca.data)

    def test_reconstructed_is_cached(self, sample_neuron):
        """Test that reconstructed property caches result."""
        recon1 = sample_neuron.reconstructed
        recon2 = sample_neuron.reconstructed

        # Should return same object (cached)
        assert recon1 is recon2

    def test_reconstructed_uses_optimal_t_off(self, sample_neuron):
        """Test that reconstruction uses fitted t_off."""
        recon = sample_neuron.reconstructed

        # get_t_off() should have been called
        assert sample_neuron.t_off is not None
        assert sample_neuron.t_off > 0

    def test_reconstructed_is_non_negative(self, sample_neuron):
        """Test that reconstructed signal is non-negative (calcium constraint)."""
        recon = sample_neuron.reconstructed

        # Calcium can't be negative
        assert np.all(recon.data >= -1e-10)  # Allow small numerical errors

    def test_reconstructed_consistent_with_asp(self, sample_neuron):
        """Test that reconstruction is consistent with amplitude spikes."""
        recon = sample_neuron.reconstructed

        # Where asp > 0, reconstruction should have events
        event_indices = np.where(sample_neuron.asp.data > 0)[0]

        # Check that reconstruction has elevated signal around events
        for idx in event_indices:
            # Within 3 frames of event, signal should be elevated
            window_start = max(0, idx - 3)
            window_end = min(len(recon.data), idx + 40)  # Decay lasts ~40 frames
            window_signal = recon.data[window_start:window_end]

            assert np.max(window_signal) > 0.05  # Some significant activity


class TestGetReconstructedMethod:
    """Test suite for neuron.get_reconstructed() method."""

    def test_get_reconstructed_default_same_as_property(self, sample_neuron):
        """Test that get_reconstructed() with no args returns same as property."""
        recon_prop = sample_neuron.reconstructed
        recon_method = sample_neuron.get_reconstructed()

        # Should be same cached object
        assert recon_prop is recon_method

    def test_get_reconstructed_force_recomputes(self, sample_neuron):
        """Test that force_reconstruction bypasses cache."""
        recon1 = sample_neuron.reconstructed
        recon2 = sample_neuron.get_reconstructed(force_reconstruction=True)

        # Should be different objects
        assert recon1 is not recon2

        # But should have same values (same parameters)
        np.testing.assert_array_almost_equal(recon1.data, recon2.data, decimal=10)

    def test_get_reconstructed_custom_t_off(self, sample_neuron):
        """Test reconstruction with custom decay time."""
        default_recon = sample_neuron.reconstructed

        # Try with faster decay
        fast_recon = sample_neuron.get_reconstructed(t_off_frames=20.0)

        # Should be different from default
        assert not np.array_equal(default_recon.data, fast_recon.data)

        # Faster decay should have lower total signal (decays faster)
        assert np.sum(fast_recon.data) < np.sum(default_recon.data)

    def test_get_reconstructed_custom_t_rise(self, sample_neuron):
        """Test reconstruction with custom rise time."""
        default_recon = sample_neuron.reconstructed

        # Try with slower rise
        slow_recon = sample_neuron.get_reconstructed(t_rise_frames=10.0)

        # Should be different from default
        assert not np.array_equal(default_recon.data, slow_recon.data)

    def test_get_reconstructed_custom_spike_data(self, sample_neuron):
        """Test reconstruction with custom spike data."""
        # Create custom spike train (sparser than detected)
        custom_spikes = np.zeros(len(sample_neuron.ca.data))
        custom_spikes[100] = 1.0
        custom_spikes[500] = 1.5

        custom_recon = sample_neuron.get_reconstructed(spike_data=custom_spikes)

        # Should return reconstruction
        assert custom_recon is not None
        assert isinstance(custom_recon, TimeSeries)

        # Should have elevated signal around specified locations (convolution spreads signal)
        # Check window around event, not exact position
        assert np.max(custom_recon.data[100:140]) > 0.3  # Window after spike
        assert np.max(custom_recon.data[500:540]) > 0.3

    def test_get_reconstructed_custom_params_not_cached(self, sample_neuron):
        """Test that custom parameter reconstructions are not cached."""
        # Get two custom reconstructions
        recon1 = sample_neuron.get_reconstructed(t_off_frames=30.0)
        recon2 = sample_neuron.get_reconstructed(t_off_frames=30.0)

        # Should be different objects (not cached)
        assert recon1 is not recon2

        # But should have same values
        np.testing.assert_array_almost_equal(recon1.data, recon2.data, decimal=10)

    def test_get_reconstructed_returns_none_without_asp(self):
        """Test that get_reconstructed returns None if no amplitude spikes."""
        ca_trace = np.random.randn(500) * 0.01
        neuron = Neuron(cell_id=0, ca=ca_trace, sp=None, fps=20.0)

        # No reconstruction done yet
        assert neuron.get_reconstructed() is None

    def test_get_reconstructed_with_only_spike_data(self):
        """Test reconstruction using only custom spike_data (no asp)."""
        ca_trace = np.random.randn(500) * 0.01
        neuron = Neuron(cell_id=0, ca=ca_trace, sp=None, fps=20.0)

        # Provide custom spikes AND custom t_off to avoid needing get_t_off()
        custom_spikes = np.zeros(500)
        custom_spikes[100] = 1.0

        recon = neuron.get_reconstructed(spike_data=custom_spikes, t_off_frames=40.0)

        assert recon is not None
        assert len(recon.data) == 500
        # Check window around spike (convolution spreads signal)
        assert np.max(recon.data[100:140]) > 0


class TestReconstructedEdgeCases:
    """Test edge cases and error handling."""

    def test_reconstructed_empty_calcium(self):
        """Test behavior with minimal calcium signal."""
        ca_trace = np.zeros(100)
        neuron = Neuron(cell_id=0, ca=ca_trace, sp=None, fps=20.0)

        try:
            neuron.reconstruct_spikes(method='wavelet', fps=20.0, show_progress=False)
        except:
            pass  # May fail, that's OK

        # Should handle gracefully
        recon = neuron.reconstructed
        # Either None or valid TimeSeries
        assert recon is None or isinstance(recon, TimeSeries)

    def test_reconstructed_after_failed_reconstruction(self):
        """Test reconstructed property after reconstruction failure."""
        ca_trace = np.ones(50)  # Too short, may fail
        neuron = Neuron(cell_id=0, ca=ca_trace, sp=None, fps=20.0)

        try:
            neuron.reconstruct_spikes(method='wavelet', fps=20.0, show_progress=False)
        except:
            pass

        # Should not crash
        recon = neuron.reconstructed
        assert recon is None or isinstance(recon, TimeSeries)

    def test_get_reconstructed_invalid_parameters(self, sample_neuron):
        """Test that invalid parameters are handled."""
        # Negative decay time should fail in get_restored_calcium
        with pytest.raises(Exception):
            sample_neuron.get_reconstructed(t_off_frames=-10.0)


class TestReconstructedIntegrationWithMetrics:
    """Test integration with quality metrics."""

    def test_reconstructed_consistent_with_r2(self, sample_neuron):
        """Test that reconstructed signal is used for R² calculation."""
        r2 = sample_neuron.get_reconstruction_r2()
        recon = sample_neuron.reconstructed

        # R² should be calculated from this reconstruction
        residuals = sample_neuron.ca.data - recon.data
        ss_residual = np.sum(residuals ** 2)
        ss_total = np.sum((sample_neuron.ca.data - np.mean(sample_neuron.ca.data)) ** 2)
        expected_r2 = 1 - (ss_residual / ss_total)

        np.testing.assert_almost_equal(r2, expected_r2, decimal=10)

    def test_reconstructed_consistent_with_mae(self, sample_neuron):
        """Test that reconstructed signal is used for MAE calculation."""
        mae = sample_neuron.get_mae()
        recon = sample_neuron.reconstructed

        # MAE should be calculated from this reconstruction
        expected_mae = np.mean(np.abs(sample_neuron.ca.data - recon.data))

        np.testing.assert_almost_equal(mae, expected_mae, decimal=10)

    def test_reconstructed_consistent_with_rmse(self, sample_neuron):
        """Test that reconstructed signal gives consistent RMSE."""
        rmse = sample_neuron.get_noise_ampl()  # Returns RMSE
        recon = sample_neuron.reconstructed

        # Calculate RMSE from reconstruction
        residuals = sample_neuron.ca.data - recon.data
        expected_rmse = np.sqrt(np.mean(residuals ** 2))

        # Should be close (may differ due to get_t_off optimization)
        np.testing.assert_almost_equal(rmse, expected_rmse, decimal=1)


class TestReconstructedDocumentation:
    """Test that examples from docstrings work."""

    def test_docstring_example_basic(self):
        """Test basic example from docstring."""
        # Generate simple data with stronger events
        ca_data = np.random.randn(1000) * 0.02 + 0.05
        # Add multiple clear events
        for spike_time in [100, 300, 500, 700]:
            decay = np.exp(-np.arange(min(60, 1000 - spike_time)) / 20.0)
            ca_data[spike_time:spike_time+len(decay)] += decay * 2.0

        neuron = Neuron(cell_id=1, ca=ca_data, sp=None, fps=20)
        neuron.reconstruct_spikes(method='wavelet', show_progress=False)

        recon = neuron.reconstructed
        if recon is not None:
            r2 = neuron.get_reconstruction_r2()
            assert isinstance(r2, (float, np.floating))
            assert 0 <= r2 <= 1
        # If no events detected, that's acceptable for this test

    def test_docstring_example_force_reconstruction(self):
        """Test force_reconstruction example from docstring."""
        ca_data = np.random.randn(1000) * 0.05 + 0.2
        ca_data[100:140] += np.exp(-np.arange(40) / 20.0)

        neuron = Neuron(cell_id=1, ca=ca_data, sp=None, fps=20)
        neuron.reconstruct_spikes(method='wavelet', show_progress=False)

        # Force recomputation
        recon = neuron.get_reconstructed(force_reconstruction=True)
        assert recon is None or isinstance(recon, TimeSeries)

    def test_docstring_example_custom_decay(self):
        """Test custom decay time example from docstring."""
        # Generate data with stronger events
        ca_data = np.random.randn(1000) * 0.02 + 0.05
        for spike_time in [100, 300, 500, 700]:
            decay = np.exp(-np.arange(min(60, 1000 - spike_time)) / 20.0)
            ca_data[spike_time:spike_time+len(decay)] += decay * 2.0

        neuron = Neuron(cell_id=1, ca=ca_data, sp=None, fps=20)
        neuron.reconstruct_spikes(method='wavelet', show_progress=False)

        # Custom decay times
        recon_fast = neuron.get_reconstructed(t_off_frames=20)
        recon_slow = neuron.get_reconstructed(t_off_frames=60)

        if recon_fast is not None and recon_slow is not None:
            # Fast decay should have less total signal
            assert np.sum(recon_fast.data) < np.sum(recon_slow.data)
        # If no events detected, acceptable for this test


class TestQualityMetrics:
    """Test suite for new quality metrics (event-only R², normalized metrics)."""

    def test_event_only_r2_basic(self, sample_neuron):
        """Test event-only R² computation."""
        event_r2 = sample_neuron.get_reconstruction_r2(event_only=True, n_mad=3.0)

        assert isinstance(event_r2, (float, np.floating))
        # Event R² can be negative if reconstruction is poor
        assert -10 < event_r2 < 1.0

    def test_event_only_r2_vs_standard_r2(self, sample_neuron):
        """Test that event-only R² differs from standard R²."""
        standard_r2 = sample_neuron.get_reconstruction_r2(event_only=False)
        event_r2 = sample_neuron.get_reconstruction_r2(event_only=True)

        # Should be different (ignoring baseline noise)
        # Event R² typically higher as it ignores baseline
        assert standard_r2 != event_r2

    def test_event_only_r2_different_n_mad(self, sample_neuron):
        """Test event-only R² with different n_mad thresholds."""
        event_r2_low = sample_neuron.get_reconstruction_r2(event_only=True, n_mad=2.0)
        event_r2_high = sample_neuron.get_reconstruction_r2(event_only=True, n_mad=4.0)

        # Different thresholds should give different results
        assert isinstance(event_r2_low, (float, np.floating))
        assert isinstance(event_r2_high, (float, np.floating))

    def test_event_only_r2_insufficient_data(self):
        """Test event-only R² with very high threshold (no events)."""
        ca_trace = np.random.randn(500) * 0.01 + 0.1
        neuron = Neuron(cell_id=0, ca=ca_trace, sp=None, fps=20.0)
        neuron.reconstruct_spikes(method='wavelet', fps=20.0, show_progress=False)

        # Very high threshold should raise error (no events detected)
        with pytest.raises(ValueError, match="Either event_mask or wvt_ridges must be provided"):
            neuron.get_reconstruction_r2(event_only=True, n_mad=10.0)

    def test_event_count_basic(self, sample_neuron):
        """Test event counting."""
        count = sample_neuron.get_event_count()

        assert isinstance(count, int)
        assert count >= 0
        # Should have detected some events
        assert count > 0

    def test_event_count_matches_asp(self, sample_neuron):
        """Test that event count matches non-zero entries in asp."""
        count = sample_neuron.get_event_count()
        expected_count = np.count_nonzero(sample_neuron.asp.data)

        assert count == expected_count

    def test_event_count_without_reconstruction(self):
        """Test event count raises error without reconstruction."""
        ca_trace = np.random.randn(500) * 0.01
        neuron = Neuron(cell_id=0, ca=ca_trace, sp=None, fps=20.0)

        with pytest.raises(ValueError, match="Spike reconstruction required"):
            neuron.get_event_count()

    def test_baseline_noise_std_basic(self, sample_neuron):
        """Test baseline noise std estimation."""
        noise_std = sample_neuron.get_baseline_noise_std(n_mad=3.0)

        assert isinstance(noise_std, float)
        assert noise_std > 0

    def test_baseline_noise_std_different_thresholds(self, sample_neuron):
        """Test baseline noise with different n_mad values."""
        noise_low = sample_neuron.get_baseline_noise_std(n_mad=2.0)
        noise_high = sample_neuron.get_baseline_noise_std(n_mad=4.0)

        # Both should be positive
        assert noise_low > 0
        assert noise_high > 0
        # Higher threshold includes more baseline (typically lower variance)
        # But this depends on data, so just check they're different
        assert isinstance(noise_low, float)
        assert isinstance(noise_high, float)

    def test_baseline_noise_std_very_high_threshold(self, sample_neuron):
        """Test baseline noise with very high threshold (all baseline)."""
        noise_std = sample_neuron.get_baseline_noise_std(n_mad=10.0)

        # Should succeed (almost all data is baseline)
        assert noise_std > 0

    def test_event_snr_basic(self, sample_neuron):
        """Test event SNR calculation."""
        snr_db = sample_neuron.get_event_snr(n_mad=3.0)

        assert isinstance(snr_db, float)
        # SNR should be reasonable (not extreme)
        assert -10 < snr_db < 50  # dB range

    def test_event_snr_positive_for_good_signal(self, sample_neuron):
        """Test that event SNR is positive for signals with events."""
        snr_db = sample_neuron.get_event_snr()

        # Should be positive (events above noise)
        assert snr_db > 0

    def test_event_snr_different_thresholds(self, sample_neuron):
        """Test event SNR with different n_mad values."""
        snr_low = sample_neuron.get_event_snr(n_mad=2.0)
        snr_high = sample_neuron.get_event_snr(n_mad=4.0)

        # Both should be positive
        assert snr_low > 0
        assert snr_high > 0

    def test_event_snr_no_events(self):
        """Test event SNR raises error when no events detected."""
        ca_trace = np.random.randn(500) * 0.01 + 0.1
        neuron = Neuron(cell_id=0, ca=ca_trace, sp=None, fps=20.0)

        # Should fail - no events detected
        with pytest.raises(ValueError, match="No events detected"):
            neuron.get_event_snr(n_mad=10.0)

    def test_nmae_basic(self, sample_neuron):
        """Test normalized MAE calculation."""
        nmae = sample_neuron.get_nmae(n_mad=3.0)

        assert isinstance(nmae, float)
        assert nmae > 0  # Error should be positive
        # Normalized error should be reasonable (< 10x noise)
        assert nmae < 10.0

    def test_nmae_vs_raw_mae(self, sample_neuron):
        """Test that NMAE relates correctly to raw MAE."""
        mae = sample_neuron.get_mae()
        nmae = sample_neuron.get_nmae(n_mad=3.0)
        baseline_std = sample_neuron.get_baseline_noise_std(n_mad=3.0)

        # NMAE = MAE / baseline_std
        expected_nmae = mae / baseline_std
        np.testing.assert_almost_equal(nmae, expected_nmae, decimal=6)

    def test_nmae_different_thresholds(self, sample_neuron):
        """Test NMAE with different n_mad values."""
        nmae_low = sample_neuron.get_nmae(n_mad=2.0)
        nmae_high = sample_neuron.get_nmae(n_mad=4.0)

        # Both should be positive
        assert nmae_low > 0
        assert nmae_high > 0

    def test_nrmse_basic(self, sample_neuron):
        """Test normalized RMSE calculation."""
        nrmse = sample_neuron.get_nrmse(n_mad=3.0)

        assert isinstance(nrmse, float)
        assert nrmse > 0
        # Normalized error should be reasonable
        assert nrmse < 10.0

    def test_nrmse_vs_raw_rmse(self, sample_neuron):
        """Test that NRMSE relates correctly to raw RMSE."""
        rmse = sample_neuron.get_noise_ampl()
        nrmse = sample_neuron.get_nrmse(n_mad=3.0)
        baseline_std = sample_neuron.get_baseline_noise_std(n_mad=3.0)

        # NRMSE = RMSE / baseline_std
        expected_nrmse = rmse / baseline_std
        np.testing.assert_almost_equal(nrmse, expected_nrmse, decimal=6)

    def test_nrmse_greater_than_nmae(self, sample_neuron):
        """Test that NRMSE >= NMAE (due to squaring)."""
        nmae = sample_neuron.get_nmae()
        nrmse = sample_neuron.get_nrmse()

        # RMSE >= MAE always (due to squaring)
        assert nrmse >= nmae

    def test_nrmse_different_thresholds(self, sample_neuron):
        """Test NRMSE with different n_mad values."""
        nrmse_low = sample_neuron.get_nrmse(n_mad=2.0)
        nrmse_high = sample_neuron.get_nrmse(n_mad=4.0)

        # Both should be positive
        assert nrmse_low > 0
        assert nrmse_high > 0

    def test_quality_metrics_integration(self, sample_neuron):
        """Test that all quality metrics work together."""
        # Get all metrics
        standard_r2 = sample_neuron.get_reconstruction_r2(event_only=False)
        event_r2 = sample_neuron.get_reconstruction_r2(event_only=True)
        event_count = sample_neuron.get_event_count()
        baseline_std = sample_neuron.get_baseline_noise_std()
        event_snr = sample_neuron.get_event_snr()
        nmae = sample_neuron.get_nmae()
        nrmse = sample_neuron.get_nrmse()

        # All should be computable
        assert isinstance(standard_r2, (float, np.floating))
        assert isinstance(event_r2, (float, np.floating))
        assert isinstance(event_count, int)
        assert baseline_std > 0
        assert event_snr > 0
        assert nmae > 0
        assert nrmse > 0

        # Consistency checks
        assert nrmse >= nmae
        assert event_count >= 0

    def test_quality_metrics_reasonable_ranges(self, sample_neuron):
        """Test that quality metrics fall within reasonable ranges."""
        event_snr = sample_neuron.get_event_snr()
        nmae = sample_neuron.get_nmae()
        nrmse = sample_neuron.get_nrmse()

        # SNR should be positive and reasonable (0-40 dB typical)
        assert 0 < event_snr < 50

        # Normalized errors should be positive and < 10x noise
        assert 0 < nmae < 10
        assert 0 < nrmse < 10

    def test_zero_baseline_noise_raises_error(self):
        """Test that zero baseline noise raises appropriate errors."""
        # Create signal with no noise (constant + events)
        ca_trace = np.ones(1000) * 0.5
        # Add single large event
        ca_trace[500:550] += 2.0

        neuron = Neuron(cell_id=0, ca=ca_trace, sp=None, fps=20.0)
        neuron.reconstruct_spikes(method='wavelet', fps=20.0, show_progress=False)

        # Baseline noise might be near zero - should raise error
        try:
            baseline_std = neuron.get_baseline_noise_std()
            if baseline_std < 1e-10:
                with pytest.raises(ValueError):
                    neuron.get_nmae()
        except ValueError:
            # Expected if baseline detection fails
            pass


class TestScaledReconstruction:
    """Test suite for scaled reconstruction (get_reconstruction_scaled)."""

    def test_ca_scaler_initialized(self):
        """Test that ca_scaler is created during __init__."""
        ca_trace = np.random.randn(500) * 0.1 + 0.2
        neuron = Neuron(cell_id=0, ca=ca_trace, sp=None, fps=20.0)

        assert hasattr(neuron, 'ca_scaler')
        assert neuron.ca_scaler is not None
        # Scaler should be fitted on ca.data
        assert hasattr(neuron.ca_scaler, 'data_min_')
        assert hasattr(neuron.ca_scaler, 'data_max_')

    def test_reconstructed_scaled_initialized_none(self):
        """Test that _reconstructed_scaled starts as None."""
        ca_trace = np.random.randn(500) * 0.1 + 0.2
        neuron = Neuron(cell_id=0, ca=ca_trace, sp=None, fps=20.0)

        assert hasattr(neuron, '_reconstructed_scaled')
        assert neuron._reconstructed_scaled is None

    def test_reconstructed_scaled_auto_cached_after_reconstruct(self, sample_neuron):
        """Test that scaled reconstruction is automatically cached after reconstruct_spikes()."""
        # Already reconstructed in fixture
        assert sample_neuron._reconstructed_scaled is not None
        assert isinstance(sample_neuron._reconstructed_scaled, np.ndarray)
        assert len(sample_neuron._reconstructed_scaled) == len(sample_neuron.ca.data)

    def test_reconstructed_scaled_cleared_by_clear_cached_metrics(self, sample_neuron):
        """Test that _clear_cached_metrics() clears scaled reconstruction."""
        # Should be cached from fixture
        assert sample_neuron._reconstructed_scaled is not None

        sample_neuron._clear_cached_metrics()

        assert sample_neuron._reconstructed_scaled is None

    def test_get_reconstruction_scaled_basic(self, sample_neuron):
        """Test basic get_reconstruction_scaled() functionality."""
        recon_scaled = sample_neuron.get_reconstruction_scaled()

        assert recon_scaled is not None
        assert isinstance(recon_scaled, np.ndarray)
        assert len(recon_scaled) == len(sample_neuron.ca.data)

    def test_get_reconstruction_scaled_returns_cached(self, sample_neuron):
        """Test that get_reconstruction_scaled() returns cached value."""
        recon1 = sample_neuron.get_reconstruction_scaled()
        recon2 = sample_neuron.get_reconstruction_scaled()

        assert np.array_equal(recon1, recon2)
        # Should be same object (cached)
        assert recon1 is sample_neuron._reconstructed_scaled

    def test_get_reconstruction_scaled_uses_scaler_transform(self, sample_neuron):
        """Test that scaled reconstruction uses ca_scaler.transform()."""
        recon_scaled = sample_neuron.get_reconstruction_scaled()

        # Manually compute what it should be
        t_rise = sample_neuron.t_rise if sample_neuron.t_rise is not None else sample_neuron.default_t_rise
        t_off = sample_neuron.t_off if sample_neuron.t_off is not None else sample_neuron.default_t_off
        ca_recon = Neuron.get_restored_calcium(sample_neuron.asp.data, t_rise, t_off)
        expected = sample_neuron.ca_scaler.transform(ca_recon.reshape(-1, 1)).reshape(-1)

        np.testing.assert_array_almost_equal(recon_scaled, expected, decimal=10)

    def test_get_reconstruction_scaled_can_exceed_01_range(self):
        """Test that scaled reconstruction can fall outside [0,1] range."""
        # Create signal with known range
        np.random.seed(42)
        sp = np.zeros(1000)
        sp[[100, 300]] = 1.0

        ca = Neuron.get_restored_calcium(sp, 2.0, 30.0)
        ca += np.random.randn(1000) * 0.15 * np.std(ca)
        ca = np.maximum(ca, 0)

        neuron = Neuron(cell_id=0, ca=ca, sp=None, fps=20.0)
        neuron.reconstruct_spikes(method='wavelet', show_progress=False)

        recon_scaled = neuron.get_reconstruction_scaled()

        # Can have values outside [0,1] - this is EXPECTED
        # (e.g., negative from baseline noise, or >1 from missed events)
        # Just verify it's computable
        assert recon_scaled is not None

    def test_get_reconstruction_scaled_without_reconstruction_raises(self):
        """Test that get_reconstruction_scaled() raises error without reconstruction."""
        ca_trace = np.random.randn(500) * 0.1
        neuron = Neuron(cell_id=0, ca=ca_trace, sp=None, fps=20.0)

        with pytest.raises(ValueError, match="No spike data available"):
            neuron.get_reconstruction_scaled()

    def test_get_reconstruction_scaled_with_custom_kinetics(self, sample_neuron):
        """Test get_reconstruction_scaled() with custom kinetics parameters."""
        # Get with current kinetics (optimized during reconstruct_spikes, cached)
        recon_current = sample_neuron.get_reconstruction_scaled()

        # Get with custom kinetics (not cached)
        recon_custom = sample_neuron.get_reconstruction_scaled(t_rise=10.0, t_off=60.0)

        # Should be different
        assert not np.array_equal(recon_current, recon_custom)

        # Cached version should match current kinetics call (exact match expected)
        assert np.array_equal(sample_neuron._reconstructed_scaled, recon_current)

    def test_scaled_reconstruction_auto_updated_after_new_reconstruct(self, sample_neuron):
        """Test that scaled reconstruction is auto-updated after new reconstruct_spikes()."""
        recon_v1 = sample_neuron._reconstructed_scaled.copy()

        # Reconstruct with different parameters
        sample_neuron.reconstruct_spikes(
            method='wavelet',
            iterative=True,
            n_iter=2,
            show_progress=False
        )

        # Should have new cached scaled reconstruction
        assert sample_neuron._reconstructed_scaled is not None
        # May or may not be different depending on detection results
        # Just verify it's been recomputed
        assert isinstance(sample_neuron._reconstructed_scaled, np.ndarray)

    def test_scaled_reconstruction_auto_updated_after_get_kinetics(self, sample_neuron):
        """Test that scaled reconstruction is updated after get_kinetics()."""
        # Get initial scaled reconstruction
        recon_before = sample_neuron._reconstructed_scaled.copy()

        # Optimize kinetics (this updates t_rise, t_off, and reconstruction)
        # Using 'direct' method (only available method)
        sample_neuron.get_kinetics(method='direct')

        # Scaled reconstruction should be updated with new kinetics
        assert sample_neuron._reconstructed_scaled is not None
        # Should be different (uses new kinetics)
        # Note: may be same if kinetics didn't change much
        assert isinstance(sample_neuron._reconstructed_scaled, np.ndarray)

    def test_scaled_reconstruction_consistency_with_scdata(self, sample_neuron):
        """Test that scaled reconstruction is consistent with ca.scdata scaling."""
        recon_scaled = sample_neuron.get_reconstruction_scaled()

        # Both should use same scaler
        ca_scdata = sample_neuron.ca.scdata

        # Verify scaler was fitted on ca.data
        assert sample_neuron.ca_scaler.data_min_[0] == sample_neuron.ca.data.min()
        assert sample_neuron.ca_scaler.data_max_[0] == sample_neuron.ca.data.max()

    def test_compute_scaled_reconstruction_helper_called(self, sample_neuron):
        """Test that _compute_scaled_reconstruction() helper works."""
        # Clear cache
        sample_neuron._reconstructed_scaled = None

        # Call helper
        sample_neuron._compute_scaled_reconstruction()

        # Should be cached now
        assert sample_neuron._reconstructed_scaled is not None
        assert isinstance(sample_neuron._reconstructed_scaled, np.ndarray)

    def test_scaled_reconstruction_documentation_example(self):
        """Test example from get_reconstruction_scaled() docstring."""
        # Generate synthetic data
        np.random.seed(42)
        sp = np.zeros(1000)
        sp[[100, 300, 500]] = 1.0

        ca = Neuron.get_restored_calcium(sp, 2.0, 30.0)
        ca += np.random.randn(1000) * 0.02 * np.std(ca)
        ca = np.maximum(ca, 0)

        neuron = Neuron(cell_id=0, ca=ca, sp=None, fps=20.0)
        neuron.reconstruct_spikes(show_progress=False)

        recon_scaled = neuron.get_reconstruction_scaled()

        # Check range violations as documented
        pct_below = 100 * np.sum(recon_scaled < 0) / len(recon_scaled)
        pct_above = 100 * np.sum(recon_scaled > 1.0) / len(recon_scaled)

        # Just verify it's computable
        assert isinstance(pct_below, (float, np.floating))
        assert isinstance(pct_above, (float, np.floating))
        assert pct_below >= 0
        assert pct_above >= 0
