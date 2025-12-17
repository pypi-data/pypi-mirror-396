"""
Unit tests for FFT-based convolution in Neuron.get_restored_calcium().

This test suite verifies that the FFT-based implementation produces
identical results to the naive convolution implementation.
"""

import numpy as np
import pytest
from scipy.signal import fftconvolve

from driada.experiment.neuron import Neuron


class TestFFTConvolution:
    """Test FFT convolution implementation in get_restored_calcium."""

    def naive_convolution_reference(self, sp, t_rise, t_off):
        """Reference implementation using naive convolution for comparison.

        Uses same kernel length (500) as FFT version for fair comparison.
        """
        x = np.arange(500)
        spform = Neuron.spike_form(x, t_rise=t_rise, t_off=t_off)
        conv = np.convolve(sp, spform)
        return conv[:len(sp)]

    def test_single_spike(self):
        """Test reconstruction of a single spike."""
        sp = np.zeros(100)
        sp[50] = 1.0
        t_rise, t_off = 5.0, 40.0

        result_fft = Neuron.get_restored_calcium(sp, t_rise, t_off)
        result_naive = self.naive_convolution_reference(sp, t_rise, t_off)

        # Results should be nearly identical (within numerical precision)
        np.testing.assert_allclose(result_fft, result_naive, rtol=1e-10, atol=1e-10)

    def test_multiple_spikes(self):
        """Test reconstruction with multiple spikes."""
        sp = np.zeros(200)
        sp[50] = 1.0
        sp[100] = 1.5
        sp[150] = 0.8
        t_rise, t_off = 5.0, 40.0

        result_fft = Neuron.get_restored_calcium(sp, t_rise, t_off)
        result_naive = self.naive_convolution_reference(sp, t_rise, t_off)

        np.testing.assert_allclose(result_fft, result_naive, rtol=1e-10, atol=1e-10)

    def test_amplitude_weighted_spikes(self):
        """Test with amplitude-weighted spike train (dF/F values)."""
        sp = np.zeros(150)
        sp[30] = 0.5
        sp[60] = 1.2
        sp[90] = 0.3
        sp[120] = 0.9
        t_rise, t_off = 4.0, 35.0

        result_fft = Neuron.get_restored_calcium(sp, t_rise, t_off)
        result_naive = self.naive_convolution_reference(sp, t_rise, t_off)

        np.testing.assert_allclose(result_fft, result_naive, rtol=1e-10, atol=1e-10)

    def test_fast_kinetics(self):
        """Test with fast calcium kinetics (small time constants)."""
        sp = np.zeros(100)
        sp[40] = 1.0
        sp[60] = 1.0
        t_rise, t_off = 2.0, 15.0  # Fast kinetics

        result_fft = Neuron.get_restored_calcium(sp, t_rise, t_off)
        result_naive = self.naive_convolution_reference(sp, t_rise, t_off)

        np.testing.assert_allclose(result_fft, result_naive, rtol=1e-10, atol=1e-10)

    def test_slow_kinetics(self):
        """Test with slow calcium kinetics (large time constants)."""
        sp = np.zeros(500)
        sp[100] = 1.0
        sp[300] = 1.0
        t_rise, t_off = 10.0, 80.0  # Slow kinetics

        result_fft = Neuron.get_restored_calcium(sp, t_rise, t_off)
        result_naive = self.naive_convolution_reference(sp, t_rise, t_off)

        np.testing.assert_allclose(result_fft, result_naive, rtol=1e-10, atol=1e-10)

    def test_long_signal(self):
        """Test with long signal (10,000 frames)."""
        np.random.seed(42)
        sp = np.zeros(10000)
        # Add random spikes
        spike_indices = np.random.choice(10000, size=50, replace=False)
        sp[spike_indices] = np.random.uniform(0.5, 1.5, size=50)

        t_rise, t_off = 5.0, 40.0

        result_fft = Neuron.get_restored_calcium(sp, t_rise, t_off)
        result_naive = self.naive_convolution_reference(sp, t_rise, t_off)

        np.testing.assert_allclose(result_fft, result_naive, rtol=1e-10, atol=1e-10)

    def test_no_spikes(self):
        """Test with zero spike train (all zeros)."""
        sp = np.zeros(100)
        t_rise, t_off = 5.0, 40.0

        result = Neuron.get_restored_calcium(sp, t_rise, t_off)

        # Should be all zeros
        np.testing.assert_array_equal(result, np.zeros(100))

    def test_output_length_matches_input(self):
        """Test that output length exactly matches input length."""
        for length in [50, 100, 500, 1000, 5000]:
            sp = np.zeros(length)
            sp[length // 2] = 1.0
            t_rise, t_off = 5.0, 40.0

            result = Neuron.get_restored_calcium(sp, t_rise, t_off)

            assert len(result) == length, f"Output length {len(result)} != input length {length}"

    def test_dense_spike_train(self):
        """Test with very dense spike train."""
        sp = np.random.uniform(0, 0.5, size=200)  # Many small spikes
        t_rise, t_off = 5.0, 40.0

        result_fft = Neuron.get_restored_calcium(sp, t_rise, t_off)
        result_naive = self.naive_convolution_reference(sp, t_rise, t_off)

        np.testing.assert_allclose(result_fft, result_naive, rtol=1e-9, atol=1e-9)

    def test_different_parameter_combinations(self):
        """Test various combinations of t_rise and t_off."""
        sp = np.zeros(200)
        sp[50] = 1.0
        sp[100] = 1.0
        sp[150] = 1.0

        param_combinations = [
            (3.0, 20.0),
            (5.0, 40.0),
            (8.0, 60.0),
            (2.0, 15.0),
            (10.0, 100.0),
        ]

        for t_rise, t_off in param_combinations:
            result_fft = Neuron.get_restored_calcium(sp, t_rise, t_off)
            result_naive = self.naive_convolution_reference(sp, t_rise, t_off)

            np.testing.assert_allclose(
                result_fft, result_naive, rtol=1e-10, atol=1e-10,
                err_msg=f"Failed for t_rise={t_rise}, t_off={t_off}"
            )

    def test_early_spike(self):
        """Test spike at beginning of signal."""
        sp = np.zeros(100)
        sp[0] = 1.0
        t_rise, t_off = 5.0, 40.0

        result_fft = Neuron.get_restored_calcium(sp, t_rise, t_off)
        result_naive = self.naive_convolution_reference(sp, t_rise, t_off)

        np.testing.assert_allclose(result_fft, result_naive, rtol=1e-10, atol=1e-10)

    def test_late_spike(self):
        """Test spike at end of signal."""
        sp = np.zeros(100)
        sp[99] = 1.0
        t_rise, t_off = 5.0, 40.0

        result_fft = Neuron.get_restored_calcium(sp, t_rise, t_off)
        result_naive = self.naive_convolution_reference(sp, t_rise, t_off)

        np.testing.assert_allclose(result_fft, result_naive, rtol=1e-10, atol=1e-10)

    def test_error_handling_empty_array(self):
        """Test that empty array raises ValueError."""
        sp = np.array([])
        t_rise, t_off = 5.0, 40.0

        with pytest.raises(ValueError, match="Spike train cannot be empty"):
            Neuron.get_restored_calcium(sp, t_rise, t_off)

    def test_error_handling_invalid_parameters(self):
        """Test that invalid parameters raise ValueError."""
        sp = np.zeros(100)
        sp[50] = 1.0

        # Negative t_rise
        with pytest.raises(ValueError):
            Neuron.get_restored_calcium(sp, -5.0, 40.0)

        # Zero t_rise
        with pytest.raises(ValueError):
            Neuron.get_restored_calcium(sp, 0.0, 40.0)

        # Negative t_off
        with pytest.raises(ValueError):
            Neuron.get_restored_calcium(sp, 5.0, -40.0)

        # Zero t_off
        with pytest.raises(ValueError):
            Neuron.get_restored_calcium(sp, 5.0, 0.0)

    def test_performance_improvement(self):
        """Verify that FFT convolution is faster than naive (smoke test)."""
        import time

        # Create large signal
        sp = np.zeros(10000)
        spike_indices = np.random.choice(10000, size=100, replace=False)
        sp[spike_indices] = 1.0
        t_rise, t_off = 5.0, 40.0

        # Time FFT version
        start_fft = time.perf_counter()
        for _ in range(10):
            _ = Neuron.get_restored_calcium(sp, t_rise, t_off)
        time_fft = time.perf_counter() - start_fft

        # Time naive version
        start_naive = time.perf_counter()
        for _ in range(10):
            _ = self.naive_convolution_reference(sp, t_rise, t_off)
        time_naive = time.perf_counter() - start_naive

        # FFT should be significantly faster (at least 2x)
        speedup = time_naive / time_fft
        assert speedup > 2.0, f"FFT speedup {speedup:.1f}x is less than 2x"

    def test_real_calcium_imaging_scenario(self):
        """Test with realistic calcium imaging parameters."""
        # Simulate 5 minutes of recording at 20 Hz
        duration_frames = 5 * 60 * 20  # 6000 frames
        sp = np.zeros(duration_frames)

        # Add realistic spike pattern (irregular firing)
        spike_times = [100, 250, 380, 500, 720, 950, 1100, 1300, 1550, 1800,
                      2000, 2300, 2600, 2900, 3200, 3500, 3800, 4100, 4400, 4700]
        for t in spike_times:
            if t < duration_frames:
                # Amplitude varies (realistic dF/F)
                sp[t] = np.random.uniform(0.3, 1.2)

        # GCaMP6f parameters (typical)
        t_rise_frames = 0.25 * 20  # 0.25 sec * 20 fps = 5 frames
        t_off_frames = 2.0 * 20    # 2.0 sec * 20 fps = 40 frames

        result_fft = Neuron.get_restored_calcium(sp, t_rise_frames, t_off_frames)
        result_naive = self.naive_convolution_reference(sp, t_rise_frames, t_off_frames)

        np.testing.assert_allclose(result_fft, result_naive, rtol=1e-10, atol=1e-10)

        # Verify peak amplitudes are reasonable
        assert np.max(result_fft) > 0.3, "Peak amplitude too low"
        assert np.max(result_fft) < 1.5, "Peak amplitude unreasonably high"


class TestKernelLength:
    """Test that reduced kernel length (500 vs 1000) is sufficient."""

    def test_kernel_length_500_sufficient_for_typical_kinetics(self):
        """Verify 500-frame kernel is sufficient for typical GCaMP parameters."""
        # GCaMP6f: t_off = 40 frames → 5× = 200 frames (well within 500)
        # Test realistic kinetics where 5×t_off < 500

        sp = np.zeros(300)
        sp[50] = 1.0

        # Test typical GCaMP6f/6s parameters (t_off ≤ 40 frames = 2 seconds @ 20Hz)
        for t_off in [20, 30, 40]:
            t_rise = t_off / 8  # Typical ratio
            result = Neuron.get_restored_calcium(sp, t_rise, t_off)

            # Verify signal shows significant calcium transient
            peak_region = result[50:50+int(2*t_off)]
            assert np.max(peak_region) > 0.5, f"Peak too low for t_off={t_off}"

            # Verify signal decays to reasonable levels
            # For t_off=40, decay at 50+200=250, signal should be low
            if 50 + int(5 * t_off) < len(result):
                decay_point = 50 + int(5 * t_off)
                # After 5× decay time, signal should be <10% of peak
                assert result[decay_point] < 0.1 * np.max(peak_region), \
                    f"Insufficient decay for t_off={t_off}"

    def test_very_slow_kinetics_edge_case(self):
        """Test edge case with very slow kinetics (t_off=100 frames)."""
        sp = np.zeros(600)
        sp[100] = 1.0
        t_rise, t_off = 12.0, 100.0  # Very slow

        result = Neuron.get_restored_calcium(sp, t_rise, t_off)

        # Signal should still reconstruct properly
        assert np.max(result) > 0.5, "Peak reconstruction too low"
        assert result[100] < result[100 + int(t_rise)], "Peak not after rise time"
