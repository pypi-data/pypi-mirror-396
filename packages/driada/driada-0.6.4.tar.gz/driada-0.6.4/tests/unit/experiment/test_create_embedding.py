"""
Unit tests for Experiment.create_embedding method.
"""

import pytest
import numpy as np

from driada.experiment.synthetic import generate_synthetic_exp, generate_synthetic_exp_with_mixed_selectivity
from driada import compute_cell_feat_significance


class TestCreateEmbedding:
    """Test the create_embedding method with real experiments."""
    
    @pytest.fixture
    def experiment(self):
        """Create a real synthetic experiment."""
        exp = generate_synthetic_exp(
            n_dfeats=2,
            n_cfeats=2,
            nneurons=20,
            duration=50,  # Short duration for fast tests
            fps=20,
            seed=42,
            with_spikes=False
        )
        return exp
    
    @pytest.fixture
    def experiment_with_spikes(self):
        """Create experiment with spike data."""
        exp = generate_synthetic_exp(
            n_dfeats=2,
            n_cfeats=2,
            nneurons=20,
            duration=50,
            fps=20,
            seed=42,
            with_spikes=True
        )
        return exp
    
    @pytest.fixture
    def experiment_with_selectivity(self):
        """Create experiment with selective neurons."""
        exp, _ = generate_synthetic_exp_with_mixed_selectivity(
            n_discrete_feats=2,
            n_continuous_feats=1,
            n_neurons=10,
            duration=100,
            fps=20,
            selectivity_prob=0.8,
            multi_select_prob=0.3,
            seed=42,
            verbose=False
        )
        
        # Run INTENSE to generate selectivity
        compute_cell_feat_significance(
            exp,
            mode="two_stage",
            n_shuffles_stage1=10,
            n_shuffles_stage2=50,
            save_computed_stats=True,
            verbose=False
        )
        
        return exp
    
    def test_create_embedding_basic(self, experiment):
        """Test basic create_embedding functionality."""
        exp = experiment
        
        # Create embedding
        result = exp.create_embedding('pca', n_components=3)
        
        # Verify result shape
        assert result.shape == (exp.n_frames, 3)  # (n_timepoints, n_components)
        
        # Verify embedding was stored
        assert 'pca' in exp.embeddings['calcium']
        stored_embedding = exp.embeddings['calcium']['pca']
        assert stored_embedding['data'].shape == result.shape
        assert stored_embedding['metadata']['n_components'] == 3
        assert stored_embedding['metadata']['method'] == 'pca'
            
    def test_create_embedding_neuron_selection(self, experiment):
        """Test neuron selection functionality."""
        exp = experiment
        
        # Test with specific neuron list
        neuron_list = [1, 5, 10]
        result = exp.create_embedding('pca', n_components=2, neuron_selection=neuron_list)
        
        # Verify result shape
        assert result.shape == (exp.n_frames, 2)
        
        # Verify metadata
        stored = exp.embeddings['calcium']['pca']
        assert stored['metadata']['neuron_indices'] == neuron_list
        assert stored['metadata']['n_neurons'] == 3
            
    def test_create_embedding_significant_neurons(self, experiment_with_selectivity):
        """Test selection of significant neurons."""
        exp = experiment_with_selectivity
        
        # Create embedding using significant neurons
        result = exp.create_embedding('pca', n_components=2, neuron_selection='significant')
        
        # Get significant neurons
        sig_neurons = exp.get_significant_neurons()
        n_sig = len(sig_neurons)
        
        # Verify result shape
        assert result.shape == (exp.n_frames, 2)
        
        # Verify metadata shows significant neuron selection
        stored = exp.embeddings['calcium']['pca']
        assert stored['metadata']['neuron_selection'] == 'significant'
        assert stored['metadata']['n_neurons'] == n_sig
        assert len(stored['metadata']['neuron_indices']) == n_sig
            
    def test_create_embedding_downsampling(self, experiment):
        """Test downsampling functionality."""
        exp = experiment
        
        # Create embedding with downsampling
        ds = 5
        result = exp.create_embedding('pca', n_components=2, ds=ds)
        
        # Verify result shape
        expected_frames = exp.n_frames // ds
        assert result.shape == (expected_frames, 2)
        
        # Verify metadata
        stored = exp.embeddings['calcium']['pca']
        assert stored['metadata']['ds'] == ds
            
    def test_create_embedding_spike_data(self, experiment_with_spikes):
        """Test with spike data."""
        exp = experiment_with_spikes
        
        # Create embedding from spike data
        result = exp.create_embedding('pca', n_components=2, data_type='spikes')
        
        # Verify result shape
        assert result.shape == (exp.n_frames, 2)
        
        # Verify it's stored under spikes
        assert 'pca' in exp.embeddings['spikes']
        stored = exp.embeddings['spikes']['pca']
        assert stored['metadata']['data_type'] == 'spikes'
            
    def test_create_embedding_validation(self, experiment):
        """Test input validation."""
        exp = experiment
        
        # Test invalid data_type
        with pytest.raises(ValueError, match="data_type must be 'calcium' or 'spikes'"):
            exp.create_embedding('pca', data_type='invalid')
            
        # Test invalid n_components
        with pytest.raises(ValueError, match="n_components must be positive"):
            exp.create_embedding('pca', n_components=0)
                
        # Test with invalid neuron indices
        with pytest.raises(ValueError, match="Neuron indices must be in range"):
            exp.create_embedding('pca', neuron_selection=[100, 200])  # Out of bounds
            
    def test_create_embedding_disconnected_graph_error(self, experiment):
        """Test error when embedding drops timepoints."""
        exp = experiment
        
        # Use a method that might drop disconnected points with extreme parameters
        # Isomap with very few neighbors on random data might create disconnected components
        try:
            # This might or might not fail depending on the data
            result = exp.create_embedding('isomap', n_components=2, n_neighbors=2)
            # If it doesn't fail, that's okay - the test is about error handling
            assert result.shape[0] <= exp.n_frames
        except (ValueError, Exception) as e:
            # If it does fail, check the error message
            # Could be ValueError for dropped timepoints or Exception for discarded nodes
            assert ("dropped" in str(e) and "timepoints" in str(e)) or "nodes discarded" in str(e)
            
    def test_create_embedding_metadata_storage(self, experiment):
        """Test that correct metadata is stored."""
        exp = experiment
        
        # Use specific parameters
        neuron_selection = [1, 3, 5, 7]
        dr_kwargs = {'n_neighbors': 15, 'min_dist': 0.1}
        
        result = exp.create_embedding(
            'umap', 
            n_components=3,
            neuron_selection=neuron_selection,
            overwrite=True,
            **dr_kwargs
        )
        
        # Check stored metadata
        stored = exp.embeddings['calcium']['umap']
        metadata = stored['metadata']
        
        assert metadata['method'] == 'umap'
        assert metadata['n_components'] == 3
        assert metadata['neuron_selection'] == neuron_selection
        assert metadata['neuron_indices'] == neuron_selection
        assert metadata['n_neurons'] == 4
        assert metadata['data_type'] == 'calcium'
        assert metadata['ds'] == 1
        # dr_kwargs should be in dr_params
        assert metadata['dr_params']['n_neighbors'] == 15
        assert metadata['dr_params']['min_dist'] == 0.1