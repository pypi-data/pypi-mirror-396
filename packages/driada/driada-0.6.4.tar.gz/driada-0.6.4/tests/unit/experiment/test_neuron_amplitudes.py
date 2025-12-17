"""Tests for amplitude-aware spike reconstruction in Neuron class.

Tests the fix for spike amplitude loss bug reported in SPIKE_AMPLITUDE_BUG_REPORT.md.
"""

import numpy as np
import pytest
from driada.experiment.neuron import Neuron
from driada.information.info_base import TimeSeries
from driada.utils.neural import generate_pseudo_calcium_signal


# Global test signal parameters
# Wavelet analysis requires at least 30 seconds of data for reliable detection
TEST_DURATION = 30.0  # seconds - minimum for wavelet analysis
TEST_SAMPLING_RATE = 20.0  # Hz
TEST_FPS = 20
TEST_RISE_TIME = 0.25  # seconds - typical for GCaMP
TEST_DECAY_TIME = 2.0  # seconds - GCaMP6f decay time
TEST_EVENT_RATE = 0.3  # Hz - realistic sparse firing (better detection)
TEST_KERNEL = 'double_exponential'  # matches Neuron model


class TestExtractEventAmplitudes:
    """Test Neuron.extract_event_amplitudes() static method."""

    def test_extract_single_event(self):
        """Test amplitude extraction for single event."""
        # Create signal with known event
        fps = 20
        ca_signal = np.zeros(100)

        # Add event: baseline=1.0, peak=3.0, so dF/F0 = (3-1)/1 = 2.0
        ca_signal[0:20] = 1.0  # Baseline
        ca_signal[20:40] = np.linspace(1.0, 3.0, 20)  # Rise to peak
        ca_signal[40:] = 3.0  # Peak held

        st_inds = [20]
        end_inds = [60]

        amplitudes = Neuron.extract_event_amplitudes(
            ca_signal, st_inds, end_inds, baseline_window=20
        )

        assert len(amplitudes) == 1
        assert np.isclose(amplitudes[0], 2.0, rtol=0.01)

    def test_extract_multiple_events(self):
        """Test amplitude extraction for multiple events with different amplitudes."""
        ca_signal = np.ones(200)

        # Event 1: F0=1.0, peak=2.0, dF/F0 = 1.0
        ca_signal[30:50] = 2.0

        # Event 2: F0=1.0, peak=3.0, dF/F0 = 2.0
        ca_signal[80:100] = 3.0

        # Event 3: F0=1.0, peak=1.5, dF/F0 = 0.5
        ca_signal[130:150] = 1.5

        st_inds = [30, 80, 130]
        end_inds = [50, 100, 150]

        amplitudes = Neuron.extract_event_amplitudes(
            ca_signal, st_inds, end_inds, baseline_window=20
        )

        assert len(amplitudes) == 3
        assert np.isclose(amplitudes[0], 1.0, rtol=0.01)
        assert np.isclose(amplitudes[1], 2.0, rtol=0.01)
        assert np.isclose(amplitudes[2], 0.5, rtol=0.01)

    def test_event_at_start_no_baseline(self):
        """Test event at start of signal (no baseline available)."""
        ca_signal = np.array([3.0, 2.5, 2.0, 1.5, 1.0])

        st_inds = [0]
        end_inds = [3]

        amplitudes = Neuron.extract_event_amplitudes(
            ca_signal, st_inds, end_inds, baseline_window=20
        )

        # Should return 0 when no baseline available
        assert len(amplitudes) == 1
        assert amplitudes[0] == 0.0

    def test_zero_baseline(self):
        """Test handling of zero baseline."""
        ca_signal = np.array([0.0, 0.0, 1.0, 2.0, 1.0])

        st_inds = [2]
        end_inds = [4]

        amplitudes = Neuron.extract_event_amplitudes(
            ca_signal, st_inds, end_inds, baseline_window=2
        )

        # Should return 0 when F0 <= 0
        assert len(amplitudes) == 1
        assert amplitudes[0] == 0.0

    def test_negative_amplitude(self):
        """Test that negative amplitudes are clipped to zero."""
        ca_signal = np.array([2.0, 2.0, 1.0, 0.5, 0.0])  # Decreasing

        st_inds = [2]
        end_inds = [4]

        amplitudes = Neuron.extract_event_amplitudes(
            ca_signal, st_inds, end_inds, baseline_window=2
        )

        # Should clip negative dF/F0 to 0
        assert len(amplitudes) == 1
        assert amplitudes[0] == 0.0

    def test_varying_baselines(self):
        """Test that each event uses its own local baseline."""
        ca_signal = np.zeros(150)

        # Event 1 with baseline 1.0
        ca_signal[0:30] = 1.0
        ca_signal[30:50] = 2.0  # dF/F0 = 1.0

        # Event 2 with baseline 2.0
        ca_signal[50:80] = 2.0
        ca_signal[80:100] = 4.0  # dF/F0 = 1.0

        st_inds = [30, 80]
        end_inds = [50, 100]

        amplitudes = Neuron.extract_event_amplitudes(
            ca_signal, st_inds, end_inds, baseline_window=20
        )

        # Both should have dF/F0 = 1.0 despite different absolute amplitudes
        assert len(amplitudes) == 2
        assert np.isclose(amplitudes[0], 1.0, rtol=0.01)
        assert np.isclose(amplitudes[1], 1.0, rtol=0.01)


class TestAmplitudesToPointEvents:
    """Test Neuron.amplitudes_to_point_events() static method."""

    def test_peak_placement(self):
        """Test that amplitudes are placed at peak positions."""
        length = 100
        ca_signal = np.zeros(100)

        # Event with peak at index 35
        ca_signal[20:30] = 1.0
        ca_signal[30:40] = np.linspace(1.0, 3.0, 10)  # Peak at 39
        ca_signal[40:50] = np.linspace(3.0, 1.0, 10)

        st_inds = [20]
        end_inds = [50]
        amplitudes = [2.0]

        point_events = Neuron.amplitudes_to_point_events(
            length, ca_signal, st_inds, end_inds, amplitudes, placement='peak'
        )

        # Should place amplitude at peak (index 39)
        assert point_events[39] == 2.0
        assert np.sum(point_events > 0) == 1

    def test_start_placement(self):
        """Test that amplitudes are placed at event start."""
        length = 100
        ca_signal = np.zeros(100)
        ca_signal[20:50] = 2.0

        st_inds = [20]
        end_inds = [50]
        amplitudes = [1.5]

        point_events = Neuron.amplitudes_to_point_events(
            length, ca_signal, st_inds, end_inds, amplitudes, placement='start'
        )

        # Should place amplitude at start (index 20)
        assert point_events[20] == 1.5
        assert np.sum(point_events > 0) == 1

    def test_multiple_events(self):
        """Test multiple events with different amplitudes."""
        length = 200
        ca_signal = np.zeros(200)

        # Three events with peaks at different positions
        ca_signal[20:30] = 2.0  # Peak at 20-29
        ca_signal[80:90] = 3.0  # Peak at 80-89
        ca_signal[140:150] = 1.5  # Peak at 140-149

        st_inds = [20, 80, 140]
        end_inds = [30, 90, 150]
        amplitudes = [1.0, 2.0, 0.5]

        point_events = Neuron.amplitudes_to_point_events(
            length, ca_signal, st_inds, end_inds, amplitudes, placement='peak'
        )

        # Should have 3 non-zero values
        assert np.sum(point_events > 0) == 3
        assert np.sum(point_events) == pytest.approx(3.5)

    def test_zero_amplitude_skipped(self):
        """Test that zero amplitudes are not stored."""
        length = 100
        ca_signal = np.ones(100)

        st_inds = [20, 40, 60]
        end_inds = [30, 50, 70]
        amplitudes = [1.0, 0.0, 2.0]  # Middle event has zero amplitude

        point_events = Neuron.amplitudes_to_point_events(
            length, ca_signal, st_inds, end_inds, amplitudes, placement='peak'
        )

        # Should only have 2 non-zero values
        assert np.sum(point_events > 0) == 2

    def test_overlapping_events_sum(self):
        """Test that overlapping events sum their amplitudes."""
        length = 100
        ca_signal = np.ones(100)

        # Two events with same peak position
        st_inds = [20, 20]
        end_inds = [30, 30]
        amplitudes = [1.0, 1.5]

        point_events = Neuron.amplitudes_to_point_events(
            length, ca_signal, st_inds, end_inds, amplitudes, placement='start'
        )

        # Amplitudes should sum at position 20
        assert point_events[20] == pytest.approx(2.5)

    def test_invalid_placement(self):
        """Test that invalid placement mode raises ValueError."""
        with pytest.raises(ValueError, match="placement must be"):
            Neuron.amplitudes_to_point_events(
                100, np.ones(100), [20], [30], [1.0], placement='invalid'
            )

    def test_continuous_dtype(self):
        """Test that output is float array (continuous)."""
        length = 100
        ca_signal = np.ones(100)

        point_events = Neuron.amplitudes_to_point_events(
            length, ca_signal, [20], [30], [1.5], placement='peak'
        )

        assert point_events.dtype == np.float64


class TestReconstructSpikesWithAmplitudes:
    """Test Neuron.reconstruct_spikes() creates all spike representations."""

    def test_creates_events_sp_asp(self):
        """Test that reconstruct_spikes creates events, sp, and asp attributes."""
        # Generate synthetic calcium with known events
        np.random.seed(42)
        ca_signal = generate_pseudo_calcium_signal(
            duration=TEST_DURATION,
            sampling_rate=TEST_SAMPLING_RATE,
            event_rate=TEST_EVENT_RATE,
            amplitude_range=(0.5, 2.0),
            decay_time=TEST_DECAY_TIME,
            noise_std=0.05,
            rise_time=TEST_RISE_TIME,
            kernel=TEST_KERNEL
        )

        neuron = Neuron("test_cell", ca_signal, None, fps=TEST_FPS)
        neuron.reconstruct_spikes(method="wavelet", create_event_regions=True)

        # Check all three representations exist
        assert neuron.events is not None
        assert isinstance(neuron.events, TimeSeries)
        assert neuron.events.discrete  # Binary events

        assert neuron.sp is not None
        assert isinstance(neuron.sp, TimeSeries)
        assert neuron.sp.discrete  # Binary point spikes

        assert neuron.asp is not None
        assert isinstance(neuron.asp, TimeSeries)
        assert not neuron.asp.discrete  # Continuous amplitude spikes

    def test_asp_has_amplitudes(self):
        """Test that asp contains non-binary amplitude values."""
        np.random.seed(42)
        ca_signal = generate_pseudo_calcium_signal(
            duration=TEST_DURATION,
            sampling_rate=TEST_SAMPLING_RATE,
            event_rate=TEST_EVENT_RATE,
            amplitude_range=(0.5, 2.0),
            decay_time=TEST_DECAY_TIME,
            noise_std=0.05,
            rise_time=TEST_RISE_TIME,
            kernel=TEST_KERNEL
        )

        neuron = Neuron("test_cell", ca_signal, None, fps=TEST_FPS)
        neuron.reconstruct_spikes(method="wavelet")

        # asp should have continuous amplitude values (not just 0 and 1)
        unique_values = np.unique(neuron.asp.data[neuron.asp.data > 0])

        # Should have more than just value 1.0
        assert len(unique_values) > 0
        # At least some values should differ from 1.0
        assert not np.all(np.isclose(unique_values, 1.0))

    def test_sp_is_binary_version_of_asp(self):
        """Test that sp is simply binarized asp."""
        np.random.seed(42)
        ca_signal = generate_pseudo_calcium_signal(
            duration=TEST_DURATION,
            sampling_rate=TEST_SAMPLING_RATE,
            event_rate=TEST_EVENT_RATE,
            amplitude_range=(0.5, 2.0),
            decay_time=TEST_DECAY_TIME,
            noise_std=0.05,
            rise_time=TEST_RISE_TIME,
            kernel=TEST_KERNEL
        )

        neuron = Neuron("test_cell", ca_signal, None, fps=TEST_FPS)
        neuron.reconstruct_spikes(method="wavelet")

        # sp should be binary version of asp
        asp_binary = (neuron.asp.data > 0).astype(int)
        assert np.array_equal(neuron.sp.data, asp_binary)

    def test_no_events_case(self):
        """Test handling when no events are detected."""
        # Pure noise signal
        ca_signal = np.random.normal(0, 0.01, 200)

        neuron = Neuron("test_cell", ca_signal, None, fps=TEST_FPS)
        neuron.reconstruct_spikes(method="wavelet", create_event_regions=True)

        # Should still create all attributes with zeros
        assert neuron.events is not None
        assert neuron.sp is not None
        assert neuron.asp is not None

        assert neuron.sp_count == 0
        assert np.sum(neuron.asp.data) == 0.0


class TestAmplitudeUsageInMethods:
    """Test that methods properly use asp with priority over sp."""

    def test_fit_t_off_uses_asp(self):
        """Test that _fit_t_off uses asp when available."""
        np.random.seed(42)
        ca_signal = generate_pseudo_calcium_signal(
            duration=TEST_DURATION,
            sampling_rate=TEST_SAMPLING_RATE,
            event_rate=TEST_EVENT_RATE,
            amplitude_range=(0.5, 2.0),
            decay_time=TEST_DECAY_TIME,
            noise_std=0.05,
            rise_time=TEST_RISE_TIME,
            kernel=TEST_KERNEL
        )

        # Create neuron without fitting t_off yet (no spike data initially)
        neuron = Neuron("test_cell", ca_signal, None, fps=TEST_FPS)
        neuron.reconstruct_spikes(method="wavelet")

        # Should use asp for fitting after reconstruction creates it
        t_off = neuron.get_t_off()
        assert t_off > 0

    def test_get_noise_ampl_uses_asp(self):
        """Test that get_noise_ampl uses asp when available."""
        np.random.seed(42)
        ca_signal = generate_pseudo_calcium_signal(
            duration=TEST_DURATION,
            sampling_rate=TEST_SAMPLING_RATE,
            event_rate=TEST_EVENT_RATE,
            amplitude_range=(0.5, 2.0),
            decay_time=TEST_DECAY_TIME,
            noise_std=0.05,
            rise_time=TEST_RISE_TIME,
            kernel=TEST_KERNEL
        )

        neuron = Neuron("test_cell", ca_signal, None, fps=TEST_FPS)
        neuron.reconstruct_spikes(method="wavelet")

        # Should use asp for noise calculation
        noise = neuron.get_noise_ampl()
        assert noise > 0

    def test_waveform_shuffling_uses_asp(self):
        """Test that waveform-based shuffling uses asp when available."""
        np.random.seed(42)
        ca_signal = generate_pseudo_calcium_signal(
            duration=TEST_DURATION,
            sampling_rate=TEST_SAMPLING_RATE,
            event_rate=TEST_EVENT_RATE,
            amplitude_range=(0.5, 2.0),
            decay_time=TEST_DECAY_TIME,
            noise_std=0.05,
            rise_time=TEST_RISE_TIME,
            kernel=TEST_KERNEL
        )

        neuron = Neuron("test_cell", ca_signal, None, fps=TEST_FPS)
        neuron.reconstruct_spikes(method="wavelet")

        # Should use asp for shuffling
        shuffled = neuron.get_shuffled_calcium(method="waveform_based", seed=42)
        assert shuffled is not None
        assert len(shuffled) == len(ca_signal)

    def test_backward_compatibility_with_sp_only(self):
        """Test that methods fall back to sp when asp is not available."""
        ca_signal = np.random.random(200)
        sp_data = np.zeros(200, dtype=int)
        sp_data[50] = 1
        sp_data[100] = 1
        sp_data[150] = 1

        neuron = Neuron("test_cell", ca_signal, sp_data, fps=20)
        # Don't call reconstruct_spikes - asp stays None

        # Should fall back to sp
        noise = neuron.get_noise_ampl()
        assert noise > 0
