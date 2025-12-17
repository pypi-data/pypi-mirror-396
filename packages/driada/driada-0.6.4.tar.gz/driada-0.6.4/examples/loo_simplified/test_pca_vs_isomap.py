#!/usr/bin/env python
"""
Test if PCA (linear method) better distinguishes manifold vs feature neurons.
If feature neurons have spurious spatial correlations, PCA should also fail to distinguish.
"""

import sys
sys.path.insert(0, '/Users/nikita/PycharmProjects/driada2/src')
sys.path.insert(0, '/Users/nikita/PycharmProjects/driada2/examples/loo_simplified')

import numpy as np
from driada.experiment.synthetic import generate_mixed_population_exp
from loo_analysis_simplified import loo_analysis_simplified

# Generate experiment
print("Generating mixed population...")
exp, info = generate_mixed_population_exp(
    n_neurons=40,  # Fewer for speed
    manifold_fraction=0.5,  # 20 manifold, 20 feature
    manifold_type='2d_spatial',
    n_discrete_features=2,
    n_continuous_features=2,
    correlation_mode='independent',
    duration=200,
    fps=20.0,
    seed=42,
    verbose=False,
    return_info=True
)

n_manifold = info['population_composition']['n_manifold']
print(f"Created: {n_manifold} manifold neurons, {40-n_manifold} feature neurons")

# Test subset of neurons for speed
test_neurons = list(range(0, n_manifold, 4)) + list(range(n_manifold, 40, 4))  # Sample both types
print(f"Testing {len(test_neurons)} neurons: {test_neurons}")

print("\n" + "="*60)
print("Testing with PCA (linear method)")
print("="*60)

results_pca = loo_analysis_simplified(
    exp,
    method='pca',
    method_params={'dim': 2},
    neurons_to_test=test_neurons,
    downsampling=5,
    verbose=False
)

# Analyze
baseline = results_pca.loc['all']
neuron_results = results_pca[results_pca.index != 'all'].copy()

# Calculate importance
neuron_results['error_increase'] = neuron_results['reconstruction_error'] - baseline['reconstruction_error']
neuron_results['corr_decrease'] = baseline['alignment_corr'] - neuron_results['alignment_corr']

# Average importance
neuron_results['importance'] = (
    neuron_results['error_increase'] / (neuron_results['error_increase'].max() + 1e-10) +
    neuron_results['corr_decrease'] / (neuron_results['corr_decrease'].max() + 1e-10)
) / 2

# Classify neurons
neuron_results['is_manifold'] = [idx < n_manifold for idx in neuron_results.index]

# Compare
manifold_importance = neuron_results[neuron_results['is_manifold']]['importance'].mean()
feature_importance = neuron_results[~neuron_results['is_manifold']]['importance'].mean()

print(f"\nPCA Results:")
print(f"Baseline reconstruction error: {baseline['reconstruction_error']:.4f}")
print(f"Baseline alignment correlation: {baseline['alignment_corr']:.4f}")
print(f"\nManifold neurons mean importance: {manifold_importance:.4f}")
print(f"Feature neurons mean importance: {feature_importance:.4f}")
print(f"Ratio: {manifold_importance/(feature_importance+1e-10):.2f}x")

print("\n" + "="*60)
print("Testing with Isomap (nonlinear method)")
print("="*60)

results_iso = loo_analysis_simplified(
    exp,
    method='isomap',
    method_params={'dim': 2, 'nn': 20},
    neurons_to_test=test_neurons,
    downsampling=5,
    verbose=False
)

# Analyze Isomap
baseline_iso = results_iso.loc['all']
neuron_results_iso = results_iso[results_iso.index != 'all'].copy()

neuron_results_iso['error_increase'] = neuron_results_iso['reconstruction_error'] - baseline_iso['reconstruction_error']
neuron_results_iso['corr_decrease'] = baseline_iso['alignment_corr'] - neuron_results_iso['alignment_corr']
neuron_results_iso['importance'] = (
    neuron_results_iso['error_increase'] / (neuron_results_iso['error_increase'].max() + 1e-10) +
    neuron_results_iso['corr_decrease'] / (neuron_results_iso['corr_decrease'].max() + 1e-10)
) / 2

neuron_results_iso['is_manifold'] = [idx < n_manifold for idx in neuron_results_iso.index]

manifold_importance_iso = neuron_results_iso[neuron_results_iso['is_manifold']]['importance'].mean()
feature_importance_iso = neuron_results_iso[~neuron_results_iso['is_manifold']]['importance'].mean()

print(f"\nIsomap Results:")
print(f"Baseline reconstruction error: {baseline_iso['reconstruction_error']:.4f}")
print(f"Baseline alignment correlation: {baseline_iso['alignment_corr']:.4f}")
print(f"\nManifold neurons mean importance: {manifold_importance_iso:.4f}")
print(f"Feature neurons mean importance: {feature_importance_iso:.4f}")
print(f"Ratio: {manifold_importance_iso/(feature_importance_iso+1e-10):.2f}x")

print("\n" + "="*60)
print("CONCLUSION:")
print("="*60)
if manifold_importance / (feature_importance+1e-10) < 1.5 and manifold_importance_iso / (feature_importance_iso+1e-10) < 1.5:
    print("Both PCA and Isomap fail to distinguish manifold from feature neurons.")
    print("This suggests feature neurons have spurious spatial correlations.")
else:
    print("Methods show different abilities to distinguish neuron types.")
    print("This reveals differences in how linear vs nonlinear methods work.")