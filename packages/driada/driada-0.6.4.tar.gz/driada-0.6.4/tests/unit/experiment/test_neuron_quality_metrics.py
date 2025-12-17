"""Tests for signal quality metrics in Neuron class.

Tests new quality assessment methods:
- get_reconstruction_r2()
- get_snr_reconstruction()
- get_mae()
"""

import numpy as np
import pytest
from driada.experiment.neuron import Neuron
from driada.utils.neural import generate_pseudo_calcium_signal


# Global test signal parameters
# Wavelet analysis requires longer signals for reliable detection
TEST_DURATION = 100.0  # seconds - sufficient for wavelet analysis
TEST_SAMPLING_RATE = 20.0  # Hz
TEST_FPS = 20
TEST_RISE_TIME = 0.25  # seconds - typical for GCaMP
TEST_DECAY_TIME = 2.0  # seconds - GCaMP6f decay time
TEST_EVENT_RATE = 0.1  # Hz - sparse firing (optimal for wavelet detection)
TEST_KERNEL = 'double_exponential'  # matches Neuron model


@pytest.fixture
def high_quality_signal():
    """Generate high-quality test signal (reused across tests)."""
    np.random.seed(1000)
    return generate_pseudo_calcium_signal(
        duration=TEST_DURATION,
        sampling_rate=TEST_SAMPLING_RATE,
        event_rate=TEST_EVENT_RATE,
        amplitude_range=(1.0, 3.0),  # Strong events
        decay_time=TEST_DECAY_TIME,
        noise_std=0.01,  # Low noise
        rise_time=TEST_RISE_TIME,
        kernel=TEST_KERNEL
    )


@pytest.fixture
def moderate_quality_signal():
    """Generate moderate-quality test signal (reused across tests)."""
    np.random.seed(1000)
    return generate_pseudo_calcium_signal(
        duration=TEST_DURATION,
        sampling_rate=TEST_SAMPLING_RATE,
        event_rate=TEST_EVENT_RATE,
        amplitude_range=(0.5, 2.0),  # Mixed amplitudes
        decay_time=TEST_DECAY_TIME,
        noise_std=0.1,  # Moderate noise
        rise_time=TEST_RISE_TIME,
        kernel=TEST_KERNEL
    )


@pytest.fixture
def low_quality_signal():
    """Generate low-quality test signal (reused across tests)."""
    np.random.seed(1000)
    return generate_pseudo_calcium_signal(
        duration=TEST_DURATION,
        sampling_rate=TEST_SAMPLING_RATE,
        event_rate=TEST_EVENT_RATE,
        amplitude_range=(0.05, 0.15),  # Weak events
        decay_time=TEST_DECAY_TIME,
        noise_std=0.3,  # High noise
        rise_time=TEST_RISE_TIME,
        kernel=TEST_KERNEL
    )


class TestReconstructionR2:
    """Test Neuron.get_reconstruction_r2() method."""

    def test_perfect_reconstruction(self, high_quality_signal):
        """Test R² for high-quality reconstruction with matching model."""
        neuron = Neuron("test_cell", high_quality_signal, None, fps=TEST_FPS)
        neuron.reconstruct_spikes(method="wavelet")  # Uses iterative=True by default

        # R² should be high for clean data with iterative detection
        r2 = neuron.get_reconstruction_r2()
        assert r2 > 0.7

    def test_noisy_reconstruction(self, moderate_quality_signal):
        """Test R² for noisy data (R² < 1.0)."""
        neuron = Neuron("test_cell", moderate_quality_signal, None, fps=TEST_FPS)
        neuron.reconstruct_spikes(method="wavelet")

        r2 = neuron.get_reconstruction_r2()

        # Should be good with iterative detection
        assert 0.5 < r2 < 0.99

    def test_r2_caching(self, moderate_quality_signal):
        """Test that R² is computed once and cached."""
        neuron = Neuron("test_cell", moderate_quality_signal, None, fps=TEST_FPS)
        neuron.reconstruct_spikes(method="wavelet")

        r2_first = neuron.get_reconstruction_r2()
        r2_second = neuron.get_reconstruction_r2()

        # Should return exact same value (cached)
        assert r2_first == r2_second
        assert neuron.reconstruction_r2 is not None

    def test_r2_requires_asp(self):
        """Test that R² raises error without amplitude spikes."""
        ca_signal = np.random.random(200)
        neuron = Neuron("test_cell", ca_signal, None, fps=TEST_FPS)
        # Don't call reconstruct_spikes - asp stays None

        with pytest.raises(ValueError, match="Amplitude spikes required"):
            neuron.get_reconstruction_r2()


class TestWaveletSNR:
    """Test Neuron.get_wavelet_snr() method."""

    def test_wavelet_snr_positive(self, moderate_quality_signal):
        """Test that wavelet SNR is positive."""
        neuron = Neuron("test_cell", moderate_quality_signal, None, fps=TEST_FPS)
        neuron.reconstruct_spikes(method="wavelet", create_event_regions=True)

        snr = neuron.get_wavelet_snr()
        assert snr > 0

    def test_wavelet_snr_high_quality(self, high_quality_signal):
        """Test wavelet SNR for high-quality signal."""
        neuron = Neuron("test_cell", high_quality_signal, None, fps=TEST_FPS)
        neuron.reconstruct_spikes(method="wavelet", create_event_regions=True)

        snr = neuron.get_wavelet_snr()
        assert snr > 5

    def test_wavelet_snr_low_quality(self, low_quality_signal):
        """Test wavelet SNR for low-quality signal."""
        neuron = Neuron("test_cell", low_quality_signal, None, fps=TEST_FPS)
        neuron.reconstruct_spikes(method="wavelet", create_event_regions=True)

        snr = neuron.get_wavelet_snr()
        assert snr < 30

    def test_wavelet_snr_caching(self, moderate_quality_signal):
        """Test that wavelet SNR is cached."""
        neuron = Neuron("test_cell", moderate_quality_signal, None, fps=TEST_FPS)
        neuron.reconstruct_spikes(method="wavelet", create_event_regions=True)

        snr_first = neuron.get_wavelet_snr()
        snr_second = neuron.get_wavelet_snr()

        assert snr_first == snr_second
        assert neuron.wavelet_snr is not None

    def test_wavelet_snr_requires_events(self):
        """Test that wavelet SNR requires event data."""
        ca_signal = np.random.random(200)
        neuron = Neuron("test_cell", ca_signal, None, fps=TEST_FPS)

        with pytest.raises(ValueError):
            neuron.get_wavelet_snr()


class TestQualityMetricsIntegration:
    """Integration tests for all quality metrics together."""

    def test_all_metrics_on_good_signal(self, high_quality_signal):
        """Test all quality metrics on high-quality synthetic signal."""
        neuron = Neuron("test_cell", high_quality_signal, None, fps=TEST_FPS)
        neuron.reconstruct_spikes(method="wavelet", create_event_regions=True)

        # All metrics should indicate good quality
        r2 = neuron.get_reconstruction_r2()
        snr = neuron.get_wavelet_snr()
        mae = neuron.get_mae()

        assert r2 > 0.7
        assert snr > 5
        assert mae < 0.2

    def test_all_metrics_on_poor_signal(self, low_quality_signal):
        """Test all quality metrics on low-quality synthetic signal."""
        neuron = Neuron("test_cell", low_quality_signal, None, fps=TEST_FPS)
        neuron.reconstruct_spikes(method="wavelet", create_event_regions=True)

        try:
            r2 = neuron.get_reconstruction_r2()
            snr = neuron.get_wavelet_snr()

            assert r2 < 0.8
            assert snr < 30
        except ValueError:
            pass

    def test_metrics_consistency(self, moderate_quality_signal):
        """Test that R² and wavelet SNR are consistent."""
        neuron = Neuron("test_cell", moderate_quality_signal, None, fps=TEST_FPS)
        neuron.reconstruct_spikes(method="wavelet", create_event_regions=True)

        r2 = neuron.get_reconstruction_r2()
        snr = neuron.get_wavelet_snr()

        if r2 > 0.8:
            assert snr > 3


class TestMetricsWithWrongWaveforms:
    """Test metrics detection of kernel/waveform mismatch."""

    def test_wrong_decay_time_degrades_metrics(self):
        """Test that using wrong decay time in reconstruction degrades all metrics."""
        np.random.seed(1000)
        fps = 20
        
        # Generate signal with decay_time = 2.0s
        true_decay_time = 2.0
        signal = generate_pseudo_calcium_signal(
            duration=TEST_DURATION,
            sampling_rate=TEST_SAMPLING_RATE,
            event_rate=TEST_EVENT_RATE,
            amplitude_range=(1.0, 3.0),
            decay_time=true_decay_time,
            noise_std=0.01,
            rise_time=TEST_RISE_TIME,
            kernel=TEST_KERNEL
        )
        
        # Reconstruct with correct decay time
        neuron_correct = Neuron("test", signal, None, fps=fps)
        neuron_correct.reconstruct_spikes(method="wavelet", create_event_regions=True)
        r2_correct = neuron_correct.get_reconstruction_r2()
        mae_correct = neuron_correct.get_mae()
        rmse_correct = neuron_correct.get_noise_ampl()

        # Reconstruct with wrong decay time (4.0s instead of 2.0s)
        wrong_decay_time = 4.0
        neuron_wrong = Neuron("test", signal, None, fps=fps,
                             default_t_off=wrong_decay_time)
        neuron_wrong.reconstruct_spikes(method="wavelet", create_event_regions=True)
        r2_wrong = neuron_wrong.get_reconstruction_r2()
        mae_wrong = neuron_wrong.get_mae()
        rmse_wrong = neuron_wrong.get_noise_ampl()

        # Wrong waveform should degrade reconstruction metrics
        assert r2_wrong < r2_correct, f"R² should decrease: {r2_wrong} vs {r2_correct}"
        assert mae_wrong > mae_correct, f"MAE should increase: {mae_wrong} vs {mae_correct}"
        assert rmse_wrong > rmse_correct, f"RMSE should increase: {rmse_wrong} vs {rmse_correct}"

        assert r2_correct > 0.7, "Correct decay should give R² > 0.7"
        # Note: Wrong decay can produce negative R² (worse than predicting mean)
        # This extreme sensitivity is desirable for quality control

    def test_faster_decay_than_true(self):
        """Test metrics detect difference between faster and true decay."""
        np.random.seed(123)
        fps = 20

        # Generate signal with slow decay (3.0s)
        signal = generate_pseudo_calcium_signal(
            duration=TEST_DURATION,
            sampling_rate=TEST_SAMPLING_RATE,
            event_rate=TEST_EVENT_RATE,
            amplitude_range=(1.0, 3.0),
            decay_time=3.0,
            noise_std=0.01,
            rise_time=TEST_RISE_TIME,
            kernel=TEST_KERNEL
        )

        # Correct reconstruction (3.0s)
        neuron_correct = Neuron("test", signal, None, fps=fps, default_t_off=3.0)
        neuron_correct.reconstruct_spikes(method="wavelet")
        r2_correct = neuron_correct.get_reconstruction_r2()
        mae_correct = neuron_correct.get_mae()

        # Fast decay (1.0s instead of 3.0s)
        neuron_fast = Neuron("test", signal, None, fps=fps, default_t_off=1.0)
        neuron_fast.reconstruct_spikes(method="wavelet")
        r2_fast = neuron_fast.get_reconstruction_r2()
        mae_fast = neuron_fast.get_mae()

        # Correct decay should give better metrics
        assert r2_correct > r2_fast, f"Correct decay should maximize R²: {r2_correct} vs {r2_fast}"
        assert mae_correct < mae_fast, f"Correct decay should minimize MAE: {mae_correct} vs {mae_fast}"

    def test_slower_decay_than_true(self):
        """Test metrics when reconstruction decay is slower than true decay."""
        np.random.seed(456)
        fps = 20
        
        # Generate signal with fast decay (1.0s)
        signal = generate_pseudo_calcium_signal(
            duration=TEST_DURATION,
            sampling_rate=TEST_SAMPLING_RATE,
            event_rate=TEST_EVENT_RATE,
            amplitude_range=(1.0, 3.0),
            decay_time=1.0,
            noise_std=0.01,
            rise_time=TEST_RISE_TIME,
            kernel=TEST_KERNEL
        )
        
        # Correct reconstruction
        neuron_correct = Neuron("test", signal, None, fps=fps)
        neuron_correct.reconstruct_spikes(method="wavelet")
        r2_correct = neuron_correct.get_reconstruction_r2()
        mae_correct = neuron_correct.get_mae()
        
        # Too-slow decay (4.0s instead of 1.0s)
        neuron_slow = Neuron("test", signal, None, fps=fps, default_t_off=4.0)  # in seconds
        neuron_slow.reconstruct_spikes(method="wavelet")
        r2_slow = neuron_slow.get_reconstruction_r2()
        mae_slow = neuron_slow.get_mae()
        
        # Slow decay should overfit the fast signal
        assert r2_slow < r2_correct
        assert mae_slow > mae_correct

    def test_metrics_rank_waveform_quality(self):
        """Test that metrics correctly rank different decay time mismatches."""
        np.random.seed(789)
        fps = 20

        # Generate signal with decay = 2.0s
        signal = generate_pseudo_calcium_signal(
            duration=TEST_DURATION,
            sampling_rate=TEST_SAMPLING_RATE,
            event_rate=TEST_EVENT_RATE,
            amplitude_range=(1.0, 3.0),
            decay_time=2.0,
            noise_std=0.01,
            rise_time=TEST_RISE_TIME,
            kernel=TEST_KERNEL
        )

        # Test different decay times (in seconds)
        decay_times = [1.5, 2.0, 2.5, 3.0, 4.0]  # 2.0 is correct
        r2_values = []
        mae_values = []

        for decay in decay_times:
            # default_t_off is in SECONDS, not frames
            neuron = Neuron("test", signal, None, fps=fps, default_t_off=decay)
            neuron.reconstruct_spikes(method="wavelet")
            r2_values.append(neuron.get_reconstruction_r2())
            mae_values.append(neuron.get_mae())

        # Find index of correct decay (2.0s = index 1)
        correct_idx = 1

        # Verify correct decay gives good R² and low MAE
        assert r2_values[correct_idx] > 0.7, "Correct decay should give R² > 0.7"
        assert mae_values[correct_idx] < 0.15, "Correct decay should give low MAE"

        # Verify metrics detect differences between decay times
        # Extreme decays should be worse
        assert r2_values[0] < r2_values[correct_idx] or r2_values[-1] < r2_values[correct_idx], \
            "Extreme decay times should give worse R²"
        assert mae_values[0] > mae_values[correct_idx] or mae_values[-1] > mae_values[correct_idx], \
            "Extreme decay times should give higher MAE"

    def test_exponential_kernel_mismatch(self):
        """Test that metrics detect when signal uses wrong kernel type (exponential vs double_exponential)."""
        np.random.seed(999)
        fps = 20

        # Generate signal with EXPONENTIAL kernel (instantaneous rise)
        signal_exp = generate_pseudo_calcium_signal(
            duration=TEST_DURATION,
            sampling_rate=TEST_SAMPLING_RATE,
            event_rate=TEST_EVENT_RATE,
            amplitude_range=(1.0, 3.0),
            decay_time=2.0,
            noise_std=0.01,
            kernel='exponential'  # Wrong kernel type
        )

        # Generate signal with DOUBLE_EXPONENTIAL (correct)
        signal_double = generate_pseudo_calcium_signal(
            duration=TEST_DURATION,
            sampling_rate=TEST_SAMPLING_RATE,
            event_rate=TEST_EVENT_RATE,
            amplitude_range=(1.0, 3.0),
            decay_time=2.0,
            noise_std=0.01,
            rise_time=TEST_RISE_TIME,
            kernel='double_exponential'  # Correct kernel type
        )

        # Reconstruct both with Neuron (which expects double_exponential)
        neuron_exp = Neuron("test", signal_exp, None, fps=fps)
        neuron_exp.reconstruct_spikes(method="wavelet")

        neuron_double = Neuron("test", signal_double, None, fps=fps)
        neuron_double.reconstruct_spikes(method="wavelet")

        # Double exponential should have better metrics
        r2_exp = neuron_exp.get_reconstruction_r2()
        r2_double = neuron_double.get_reconstruction_r2()

        mae_exp = neuron_exp.get_mae()
        mae_double = neuron_double.get_mae()

        # Matching kernel should give better metrics
        assert r2_double > r2_exp, "Matching kernel should have higher R²"
        assert mae_double < mae_exp, "Matching kernel should have lower MAE"

    def test_step_kernel_mismatch(self):
        """Test that metrics detect non-physiological step kernel."""
        np.random.seed(1000)
        fps = 20

        # Generate signal with STEP kernel (non-physiological)
        signal_step = generate_pseudo_calcium_signal(
            duration=TEST_DURATION,
            sampling_rate=TEST_SAMPLING_RATE,
            event_rate=TEST_EVENT_RATE,
            amplitude_range=(1.0, 3.0),
            decay_time=2.0,
            noise_std=0.01,
            kernel='step'  # Non-physiological
        )

        # Generate signal with DOUBLE_EXPONENTIAL (correct)
        signal_double = generate_pseudo_calcium_signal(
            duration=TEST_DURATION,
            sampling_rate=TEST_SAMPLING_RATE,
            event_rate=TEST_EVENT_RATE,
            amplitude_range=(1.0, 3.0),
            decay_time=2.0,
            noise_std=0.01,
            rise_time=TEST_RISE_TIME,
            kernel='double_exponential'
        )

        # Reconstruct both with Neuron
        neuron_step = Neuron("test", signal_step, None, fps=fps)
        neuron_step.reconstruct_spikes(method="wavelet")

        neuron_double = Neuron("test", signal_double, None, fps=fps)
        neuron_double.reconstruct_spikes(method="wavelet")

        # Get all metrics for both
        r2_step = neuron_step.get_reconstruction_r2()
        r2_double = neuron_double.get_reconstruction_r2()
        mae_step = neuron_step.get_mae()
        mae_double = neuron_double.get_mae()

        # Matching kernel should give better metrics
        # Note: Step kernel can still be detected well, but reconstruction fit should be worse
        assert r2_double >= r2_step, "Physiological kernel should have equal or higher R²"
        assert mae_double <= mae_step, "Physiological kernel should have equal or lower MAE"
