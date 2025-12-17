"""Test that plot_neuron_feature_density works with continuous TimeSeries features."""

import numpy as np
import pytest
from unittest.mock import MagicMock, patch, Mock
from types import SimpleNamespace

from driada.information import TimeSeries
from driada.intense.visual import plot_neuron_feature_density


class TestPlotNeuronFeatureDensityWithRealTimeSeries:
    """Test plot_neuron_feature_density with real TimeSeries objects."""

    def test_continuous_feature_no_attribute_error(self):
        """Test that continuous TimeSeries features don't cause AttributeError."""
        # Create minimal mock experiment
        exp = Mock()
        exp.n_frames = 100
        
        # Create mock neuron with calcium data
        neuron = Mock()
        calcium_ts = Mock()
        calcium_ts.scdata = np.random.randn(100) + 1.0
        neuron.ca = calcium_ts
        exp.neurons = [neuron]
        
        # Add continuous feature as real TimeSeries
        speed_data = np.abs(np.random.randn(100)) * 0.5
        speed_ts = TimeSeries(speed_data, discrete=False)
        
        # Verify is_binary exists and is False
        assert hasattr(speed_ts, 'is_binary')
        assert speed_ts.is_binary is False
        
        # Set the TimeSeries as an attribute
        exp.speed = speed_ts
        
        # Mock matplotlib
        with patch('matplotlib.pyplot.subplots') as mock_subplots, \
             patch('driada.intense.visual.gaussian_kde') as mock_kde:
            
            # Setup mocks
            fig = MagicMock()
            ax = MagicMock()
            mock_subplots.return_value = (fig, ax)
            
            # Mock KDE
            kde_instance = MagicMock()
            kde_instance.return_value = np.ones(10000)  # 100x100 grid
            mock_kde.return_value = kde_instance
            
            # This should not raise AttributeError
            result = plot_neuron_feature_density(
                exp, "calcium", 0, "speed", ind1=0, ind2=50
            )
            
            # Verify it worked
            assert result is ax
            assert mock_kde.called
            assert ax.pcolormesh.called

    def test_binary_feature_works(self):
        """Test that binary TimeSeries features work correctly."""
        # Create minimal mock experiment
        exp = Mock()
        exp.n_frames = 100
        
        # Create mock neuron with calcium data
        neuron = Mock()
        calcium_ts = Mock()
        calcium_ts.scdata = np.random.randn(100) + 1.0
        neuron.ca = calcium_ts
        exp.neurons = [neuron]
        
        # Add binary feature as real TimeSeries
        licking_data = np.random.choice([0, 1], size=100)
        licking_ts = TimeSeries(licking_data, discrete=True)
        
        # Verify is_binary exists and is True
        assert hasattr(licking_ts, 'is_binary')
        assert licking_ts.is_binary is True
        
        # Set the TimeSeries as an attribute
        exp.licking = licking_ts
        
        # Mock matplotlib and seaborn
        with patch('matplotlib.pyplot.subplots') as mock_subplots, \
             patch('driada.intense.visual.sns.kdeplot') as mock_kdeplot:
            
            # Setup mocks
            fig = MagicMock()
            ax = MagicMock()
            mock_subplots.return_value = (fig, ax)
            mock_kdeplot.return_value = None
            
            # This should work correctly
            result = plot_neuron_feature_density(
                exp, "calcium", 0, "licking", ind1=0, ind2=50
            )
            
            # Verify it worked
            assert result is ax
            assert mock_kdeplot.called
            # Should be called twice for binary feature (vals0 and vals1)
            assert mock_kdeplot.call_count == 2

    def test_autodetected_continuous_feature(self):
        """Test with auto-detected continuous feature."""
        # Create minimal mock experiment
        exp = Mock()
        exp.n_frames = 200
        
        # Create mock neuron with calcium data
        neuron = Mock()
        calcium_ts = Mock()
        calcium_ts.scdata = np.random.randn(200) + 1.0
        neuron.ca = calcium_ts
        exp.neurons = [neuron]
        
        # Add continuous feature without specifying discrete parameter
        # This will trigger auto-detection
        position_data = np.cumsum(np.random.randn(200) * 0.1)
        position_ts = TimeSeries(position_data)  # Auto-detection
        
        # Verify is_binary exists and is False
        assert hasattr(position_ts, 'is_binary')
        assert position_ts.is_binary is False
        
        # Set the TimeSeries as an attribute
        exp.position = position_ts
        
        # Mock matplotlib
        with patch('matplotlib.pyplot.subplots') as mock_subplots, \
             patch('driada.intense.visual.gaussian_kde') as mock_kde:
            
            # Setup mocks
            fig = MagicMock()
            ax = MagicMock()
            mock_subplots.return_value = (fig, ax)
            
            # Mock KDE
            kde_instance = MagicMock()
            kde_instance.return_value = np.ones(10000)
            mock_kde.return_value = kde_instance
            
            # This should not raise AttributeError
            result = plot_neuron_feature_density(
                exp, "calcium", 0, "position", ind1=0, ind2=100
            )
            
            # Verify it worked
            assert result is ax
            assert mock_kde.called