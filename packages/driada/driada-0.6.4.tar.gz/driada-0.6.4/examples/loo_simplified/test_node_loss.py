#!/usr/bin/env python
"""Test node loss handling for graph-based methods."""

import numpy as np
from driada.experiment.synthetic import generate_2d_manifold_exp
from loo_analysis_simplified import loo_analysis_simplified

# Generate test data with enough neurons for graph methods
print("Generating test experiment...")
exp = generate_2d_manifold_exp(
    n_neurons=30,  # More neurons for better connectivity
    duration=100,
    fps=10,
    seed=42
)

# Test with Isomap (graph-based method with potential node loss)
print("\n" + "="*60)
print("Test: Isomap with small neighborhood (may cause node loss)")
print("="*60)

# Use reasonable nn to avoid complete disconnection
method_params = {
    'dim': 2,
    'nn': 15,  # Good neighborhood size for 30 neurons
    'max_deleted_nodes': 0.3  # Allow up to 30% node loss
}

results = loo_analysis_simplified(
    exp,
    method='isomap',
    method_params=method_params,
    neurons_to_test=[0, 1, 2, 3, 4],
    verbose=True
)

print("\n" + "="*60)
print("Results with node loss tracking:")
print("="*60)
print(results[['reconstruction_error', 'alignment_corr', 'node_loss_rate']])

# Check if any neurons had node loss
if 'node_loss_rate' in results.columns:
    neurons_with_loss = results[results['node_loss_rate'] > 0]
    if len(neurons_with_loss) > 0:
        print(f"\nNeurons with node loss: {len(neurons_with_loss)}")
        print(neurons_with_loss[['node_loss_rate']])
    else:
        print("\nNo node loss detected")

# Test with Laplacian Eigenmaps (another graph method)
print("\n" + "="*60)
print("Test: Laplacian Eigenmaps (graph-based)")
print("="*60)

method_params = {
    'dim': 2,
    'nn': 15,  # Increase nn for LE too
    'max_deleted_nodes': 0.3
}

results_le = loo_analysis_simplified(
    exp,
    method='le',
    method_params=method_params,
    neurons_to_test=[0, 1, 2],
    verbose=True
)

print("\nLE Results:")
print(results_le[['reconstruction_error', 'alignment_corr', 'node_loss_rate']])