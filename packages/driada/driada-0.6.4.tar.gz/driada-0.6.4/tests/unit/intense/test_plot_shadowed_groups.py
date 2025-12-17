"""Test plot_shadowed_groups function."""

import numpy as np
import pytest
import matplotlib.pyplot as plt
from unittest.mock import MagicMock, patch, Mock

from driada.intense.visual import plot_shadowed_groups


class TestPlotShadowedGroups:
    """Test the plot_shadowed_groups function."""

    def test_single_group(self):
        """Test shading a single group of 1s."""
        fig, ax = plt.subplots()
        xvals = np.arange(10)
        binary_series = np.array([0, 0, 1, 1, 1, 0, 0, 0, 0, 0])

        result = plot_shadowed_groups(ax, xvals, binary_series, color='red', alpha=0.5)

        # Check that axis is returned
        assert result is ax

        # Check that one patch was added (axvspan creates a patch)
        patches = [p for p in ax.patches if hasattr(p, 'get_xy')]
        assert len(patches) > 0

        plt.close(fig)

    def test_multiple_groups(self):
        """Test shading multiple groups of 1s."""
        fig, ax = plt.subplots()
        xvals = np.arange(15)
        binary_series = np.array([1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0])

        result = plot_shadowed_groups(ax, xvals, binary_series, color='blue', alpha=0.3)

        # Check that axis is returned
        assert result is ax

        # Check that multiple patches were added (4 groups)
        patches = [p for p in ax.patches if hasattr(p, 'get_xy')]
        assert len(patches) == 4

        plt.close(fig)

    def test_no_ones(self):
        """Test with binary series containing no 1s."""
        fig, ax = plt.subplots()
        xvals = np.arange(10)
        binary_series = np.zeros(10)

        result = plot_shadowed_groups(ax, xvals, binary_series)

        # Check that axis is returned
        assert result is ax

        # No patches should be added
        patches = [p for p in ax.patches if hasattr(p, 'get_xy')]
        assert len(patches) == 0

        plt.close(fig)

    def test_all_ones(self):
        """Test with binary series containing all 1s."""
        fig, ax = plt.subplots()
        xvals = np.arange(10)
        binary_series = np.ones(10)

        result = plot_shadowed_groups(ax, xvals, binary_series, color='green')

        # Check that axis is returned
        assert result is ax

        # One continuous patch should be added
        patches = [p for p in ax.patches if hasattr(p, 'get_xy')]
        assert len(patches) == 1

        plt.close(fig)

    def test_custom_label(self):
        """Test that custom label is applied only once."""
        fig, ax = plt.subplots()
        xvals = np.arange(10)
        binary_series = np.array([1, 1, 0, 1, 1, 0, 1, 1, 0, 0])

        result = plot_shadowed_groups(ax, xvals, binary_series, label='test_label')

        # Check that axis is returned
        assert result is ax

        # Get legend handles and labels
        handles, labels = ax.get_legend_handles_labels()

        # Should have exactly one label even with multiple groups
        assert labels.count('test_label') == 1

        plt.close(fig)

    def test_scaled_xvals(self):
        """Test with scaled x values (e.g., time in seconds)."""
        fig, ax = plt.subplots()
        xvals = np.arange(10) / 20.0  # Convert to seconds
        binary_series = np.array([0, 1, 1, 0, 0, 1, 1, 1, 0, 0])

        result = plot_shadowed_groups(ax, xvals, binary_series)

        # Check that axis is returned
        assert result is ax

        # Check that patches were added
        patches = [p for p in ax.patches if hasattr(p, 'get_xy')]
        assert len(patches) == 2  # Two groups of 1s

        plt.close(fig)

    def test_empty_series(self):
        """Test with empty binary series."""
        fig, ax = plt.subplots()
        xvals = np.array([])
        binary_series = np.array([])

        result = plot_shadowed_groups(ax, xvals, binary_series)

        # Check that axis is returned
        assert result is ax

        # No patches should be added
        patches = [p for p in ax.patches if hasattr(p, 'get_xy')]
        assert len(patches) == 0

        plt.close(fig)

    def test_single_element(self):
        """Test with single element series."""
        fig, ax = plt.subplots()

        # Test with single 1
        xvals = np.array([5.0])
        binary_series = np.array([1])

        result = plot_shadowed_groups(ax, xvals, binary_series)
        assert result is ax

        # Should create one patch
        patches = [p for p in ax.patches if hasattr(p, 'get_xy')]
        assert len(patches) == 1

        plt.close(fig)

        # Test with single 0
        fig, ax = plt.subplots()
        binary_series = np.array([0])

        result = plot_shadowed_groups(ax, xvals, binary_series)
        assert result is ax

        # Should create no patches
        patches = [p for p in ax.patches if hasattr(p, 'get_xy')]
        assert len(patches) == 0

        plt.close(fig)

    def test_default_parameters(self):
        """Test that default parameters work correctly."""
        fig, ax = plt.subplots()
        xvals = np.arange(5)
        binary_series = np.array([0, 1, 1, 0, 1])

        # Call with minimal parameters
        result = plot_shadowed_groups(ax, xvals, binary_series)

        assert result is ax

        # Check patches exist (2 groups)
        patches = [p for p in ax.patches if hasattr(p, 'get_xy')]
        assert len(patches) == 2

        plt.close(fig)