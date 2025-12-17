"""Test that is_binary attribute is always set for TimeSeries objects."""

import numpy as np
import pytest

from driada.information import TimeSeries


class TestIsBinaryAttribute:
    """Test is_binary attribute is always present."""

    def test_continuous_timeseries_has_is_binary(self):
        """Test that continuous TimeSeries has is_binary = False."""
        # Create continuous TimeSeries
        data = np.random.randn(100)
        ts = TimeSeries(data, discrete=False)
        
        # Check is_binary exists and is False
        assert hasattr(ts, 'is_binary')
        assert ts.is_binary is False

    def test_discrete_binary_timeseries_has_is_binary(self):
        """Test that discrete binary TimeSeries has is_binary = True."""
        # Create binary discrete TimeSeries
        data = np.array([0, 1, 0, 1, 1, 0, 0, 1])
        ts = TimeSeries(data, discrete=True)
        
        # Check is_binary exists and is True
        assert hasattr(ts, 'is_binary')
        assert ts.is_binary is True

    def test_discrete_nonbinary_timeseries_has_is_binary(self):
        """Test that discrete non-binary TimeSeries has is_binary = False."""
        # Create non-binary discrete TimeSeries
        data = np.array([0, 1, 2, 1, 3, 2, 0, 1])
        ts = TimeSeries(data, discrete=True)
        
        # Check is_binary exists and is False
        assert hasattr(ts, 'is_binary')
        assert ts.is_binary is False

    def test_autodetected_continuous_has_is_binary(self):
        """Test that auto-detected continuous TimeSeries has is_binary = False."""
        # Create data that will be auto-detected as continuous
        data = np.linspace(0, 10, 100) + np.random.randn(100) * 0.1
        ts = TimeSeries(data)  # No discrete parameter
        
        # Check is_binary exists and is False
        assert hasattr(ts, 'is_binary')
        assert ts.is_binary is False

    def test_autodetected_discrete_has_is_binary(self):
        """Test that auto-detected discrete TimeSeries has proper is_binary."""
        # Create data that will be auto-detected as discrete
        data = np.array([1, 1, 2, 1, 2, 1, 1, 2, 1, 2] * 10)
        ts = TimeSeries(data)  # No discrete parameter
        
        # Check is_binary exists and has correct value
        assert hasattr(ts, 'is_binary')
        # Should be True since only 2 unique values
        assert ts.is_binary is True

    def test_type_specified_continuous_has_is_binary(self):
        """Test that type-specified continuous TimeSeries has is_binary = False."""
        # Create TimeSeries with explicit type
        data = np.random.randn(100)
        ts = TimeSeries(data, ts_type='linear')
        
        # Check is_binary exists and is False
        assert hasattr(ts, 'is_binary')
        assert ts.is_binary is False

    def test_type_specified_binary_has_is_binary(self):
        """Test that type-specified binary TimeSeries has is_binary = True."""
        # Create TimeSeries with explicit binary type
        data = np.array([0, 1, 0, 1, 1, 0])
        ts = TimeSeries(data, ts_type='binary')
        
        # Check is_binary exists and is True
        assert hasattr(ts, 'is_binary')
        assert ts.is_binary is True