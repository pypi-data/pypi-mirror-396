"""
Additional tests for manifold analysis functions to increase coverage.
Focuses on edge cases and untested paths.
"""

import pytest
import numpy as np
import logging
from unittest.mock import Mock, patch

from driada.integration import get_functional_organization, compare_embeddings
from driada.intense.intense_base import IntenseResults
from driada.experiment.exp_build import load_exp_from_aligned_data


class TestManifoldAnalysisCoverage:
    """Test cases to increase coverage of manifold analysis functions."""

    @pytest.fixture
    def mock_experiment(self):
        """Create a mock experiment with minimal required attributes."""
        exp = Mock()
        exp.n_cells = 20
        exp.n_frames = 1000
        exp.embeddings = {"calcium": {}, "spikes": {}}
        exp.stats_tables = {"calcium": {}}
        exp.significance_tables = {"calcium": {}}
        
        # Mock get_embedding to return proper structure
        exp.get_embedding = Mock(
            return_value={
                "data": np.random.randn(100, 2),  # 100 timepoints, 2 components
                "metadata": {"neuron_indices": list(range(20))},
            }
        )
        
        return exp

    def test_functional_organization_with_full_selectivity(self, mock_experiment):
        """Test get_functional_organization with complete selectivity data."""
        exp = mock_experiment
        
        # Create IntenseResults object with significance data
        intense_results = IntenseResults()
        intense_results.significance = {
            "pca_comp0": {
                0: {"stage2": True},
                1: {"stage2": True},
                5: {"stage2": False},
            },
            "pca_comp1": {
                1: {"stage2": True},
                2: {"stage2": True},
                5: {"stage2": True},
            },
        }
        
        # Test with intense_results
        org = get_functional_organization(exp, "pca", "calcium", intense_results=intense_results)
        
        assert "neuron_participation" in org
        assert len(org["neuron_participation"]) == 4  # neurons 0, 1, 2, 5 participate
        assert "functional_clusters" in org
        assert "n_participating_neurons" in org
        assert org["n_participating_neurons"] == 4
        
        # Check neuron 1 participates in both components
        assert 1 in org["neuron_participation"]
        assert org["neuron_participation"][1] == [0, 1]
        
        # Check component specialization
        assert org["component_specialization"][0]["n_selective_neurons"] == 2
        assert org["component_specialization"][1]["n_selective_neurons"] == 3

    def test_functional_organization_no_significance_tables(self, mock_experiment):
        """Test when significance data is None."""
        exp = mock_experiment
        exp.significance_tables = None
        exp.stats_tables = {"calcium": {"pca_comp0": {}}}
        
        # Create IntenseResults with None significance
        intense_results = IntenseResults()
        intense_results.significance = None
        
        org = get_functional_organization(exp, "pca", "calcium", intense_results=intense_results)
        
        # Should still work but without detailed selectivity info
        assert "component_importance" in org
        assert "neuron_participation" not in org

    def test_functional_organization_missing_metadata(self, mock_experiment):
        """Test with missing neuron_indices in metadata."""
        exp = mock_experiment
        exp.get_embedding = Mock(
            return_value={
                "data": np.random.randn(100, 2),
                "metadata": {},  # No neuron_indices
            }
        )
        
        org = get_functional_organization(exp, "pca", "calcium")
        
        # Should use all neurons as default
        assert org["n_neurons_used"] == exp.n_cells
        assert org["neuron_indices"] == list(range(exp.n_cells))

    def test_compare_embeddings_with_missing_neuron_participation(self, mock_experiment):
        """Test compare_embeddings when some methods lack neuron_participation."""
        exp = mock_experiment
        
        # Mock two different organizations
        with patch('driada.integration.manifold_analysis.get_functional_organization') as mock_get_org:
            # First call returns org with participation, second without
            mock_get_org.side_effect = [
                {
                    "n_components": 2,
                    "neuron_participation": {0: [0], 1: [1]},
                    "n_participating_neurons": 2,
                    "mean_components_per_neuron": 1.0,
                    "functional_clusters": [],
                },
                {
                    "n_components": 3,
                    "n_participating_neurons": 0,
                    "mean_components_per_neuron": 0,
                    "functional_clusters": [],
                    # No neuron_participation
                },
            ]
            
            comparison = compare_embeddings(exp, ["pca", "umap"])
            
            # Should still work but without overlap calculation
            assert "participation_overlap" not in comparison
            assert comparison["n_components"]["pca"] == 2
            assert comparison["n_components"]["umap"] == 3

    def test_compare_embeddings_empty_neuron_sets(self, mock_experiment):
        """Test overlap calculation with empty neuron sets."""
        exp = mock_experiment
        
        with patch('driada.integration.manifold_analysis.get_functional_organization') as mock_get_org:
            # Both methods have empty neuron participation
            mock_get_org.return_value = {
                "n_components": 2,
                "neuron_participation": {},  # Empty
                "n_participating_neurons": 0,
                "mean_components_per_neuron": 0,
                "functional_clusters": [],
            }
            
            comparison = compare_embeddings(exp, ["pca", "umap"])
            
            # Overlap should be 0 for empty sets
            assert comparison["participation_overlap"]["pca_vs_umap"] == 0

    def test_compare_embeddings_single_method_warning(self, mock_experiment):
        """Test warning when only one valid embedding exists."""
        exp = mock_experiment
        
        with patch('driada.integration.manifold_analysis.get_functional_organization') as mock_get_org:
            # First succeeds, second fails
            mock_get_org.side_effect = [
                {"n_components": 2, "n_participating_neurons": 5},
                KeyError("Not found"),
            ]
            
            with patch('driada.integration.manifold_analysis.logging.getLogger') as mock_logger:
                logger_instance = Mock()
                mock_logger.return_value = logger_instance
                
                comparison = compare_embeddings(exp, ["pca", "nonexistent"])
                
                # Should log warning about missing embedding
                logger_instance.warning.assert_called_once()
                assert "No embedding found" in logger_instance.warning.call_args[0][0]
                
                # Should still return valid results for single method
                assert len(comparison["methods"]) == 1
                assert "pca" in comparison["methods"]

    def test_functional_organization_with_clusters(self, mock_experiment):
        """Test functional cluster detection."""
        exp = mock_experiment
        exp.stats_tables = {"calcium": {"pca_comp0": {}, "pca_comp1": {}}}
        
        # Create IntenseResults with significance data
        intense_results = IntenseResults()
        intense_results.significance = {
            "pca_comp0": {
                0: {"stage2": True},
                1: {"stage2": True},
                2: {"stage2": True},
            },
            "pca_comp1": {
                0: {"stage2": True},
                1: {"stage2": True},
                3: {"stage2": True},
            },
        }
        
        org = get_functional_organization(exp, "pca", "calcium", intense_results=intense_results)
        
        # Should find cluster of neurons 0,1 (selective to both components)
        assert len(org["functional_clusters"]) > 0
        
        # Find the cluster with neurons 0 and 1
        cluster_01 = None
        for cluster in org["functional_clusters"]:
            if set(cluster["neurons"]) == {0, 1}:
                cluster_01 = cluster
                break
                
        assert cluster_01 is not None
        assert cluster_01["components"] == [0, 1]
        assert cluster_01["size"] == 2

    def test_create_embedding_edge_cases(self):
        """Test create_embedding method edge cases."""
        from driada.experiment.exp_base import Experiment
        from driada.information.info_base import TimeSeries, MultiTimeSeries
        from driada.experiment.neuron import Neuron
        
        # Create a minimal experiment with longer time series to ensure valid shuffle masks
        n_neurons = 10
        n_frames = 1000  # Longer to ensure shuffle mask has valid positions
        
        # Generate synthetic calcium data
        np.random.seed(42)
        calcium_data = np.random.randn(n_neurons, n_frames) + 2.0  # Positive baseline
        
        # Create experiment using the Experiment constructor directly
        # Use small t_off to minimize shuffle mask restrictions
        exp = Experiment(
            exp_identificators={'exp_name': 'test_edge_cases'},
            signature='test_signature',
            calcium=calcium_data,
            spikes=None,
            static_features={'fps': 30.0, 't_off_sec': 0.5},  # Small t_off
            dynamic_features={},
            reconstruct_spikes=None,  # Don't reconstruct spikes
            verbose=False  # Suppress progress bar
        )
        
        # Test ValueError for invalid data_type
        with pytest.raises(ValueError, match="must be 'calcium' or 'spikes'"):
            exp.create_embedding("pca", data_type="invalid")

    def test_functional_organization_spike_data(self):
        """Test functional organization with spike data."""
        # Create a synthetic experiment with calcium data
        n_neurons = 5
        n_frames = 1000
        
        # Generate synthetic calcium traces with some activity
        np.random.seed(42)
        calcium_data = np.zeros((n_neurons, n_frames))
        
        # Add some spike-like events to calcium traces
        for i in range(n_neurons):
            spike_times = np.random.choice(n_frames, size=20, replace=False)
            for t in spike_times:
                # Add calcium transient
                duration = min(50, n_frames - t)
                calcium_data[i, t:t+duration] += np.exp(-np.arange(duration) / 10.0)
        
        # Add noise
        calcium_data += np.random.normal(0, 0.1, calcium_data.shape)
        
        # Create experiment
        exp = load_exp_from_aligned_data(
            data_source="IABS",
            exp_params={
                "track": "STFP",
                "animal_id": "test",
                "session": "spike_org"
            },
            data={"calcium": calcium_data},
            reconstruct_spikes="wavelet",  # This will use wavelet to extract spikes
            verbose=False  # Suppress output for testing
        )
        
        # Create PCA embedding for spikes
        exp.create_embedding("pca", data_type="spikes")
        
        # Get functional organization for spike data
        org = get_functional_organization(exp, "pca", "spikes")
        
        # Verify basic structure
        assert "component_importance" in org
        assert "n_components" in org
        assert "n_neurons_used" in org
        assert org["n_neurons_used"] == n_neurons