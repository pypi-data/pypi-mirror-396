#!/usr/bin/env python
"""
Test LOO analysis with truly spatially-independent feature neurons.
Uses high-frequency oscillations to ensure zero correlation with spatial trajectory.
"""

import sys
sys.path.insert(0, '/Users/nikita/PycharmProjects/driada2/src')
sys.path.insert(0, '/Users/nikita/PycharmProjects/driada2/examples/loo_simplified')

import numpy as np
from scipy.stats import pearsonr
from driada.experiment import Experiment
from driada.experiment.synthetic import generate_2d_manifold_exp
from loo_analysis_simplified import loo_analysis_simplified

def add_independent_neurons(exp, n_neurons=20, seed=42):
    """
    Add truly spatially-independent neurons using high-frequency oscillations.
    """
    np.random.seed(seed)

    # Get experiment parameters
    duration = exp.n_frames / exp.fps
    n_frames = exp.n_frames

    # Get spatial positions for correlation check
    x_pos = exp.dynamic_features['x'].data
    y_pos = exp.dynamic_features['y'].data

    # Generate high-frequency oscillating neurons (5-20 Hz)
    # Much higher than movement frequency (~0.1 Hz)
    time = np.linspace(0, duration, n_frames)
    new_neurons = []
    correlations = []

    for i in range(n_neurons):
        # Random frequency between 5-20 Hz
        freq = np.random.uniform(5.0, 20.0)
        phase = np.random.uniform(0, 2 * np.pi)
        amplitude = np.random.uniform(0.5, 2.0)

        # Generate oscillation
        signal = amplitude * np.sin(2 * np.pi * freq * time + phase)

        # Add noise
        signal += np.random.randn(n_frames) * 0.3

        # Make positive (neural activity)
        signal = np.maximum(signal + 2, 0)

        # Check correlation with position
        corr_x = abs(pearsonr(signal, x_pos)[0])
        corr_y = abs(pearsonr(signal, y_pos)[0])
        correlations.append((corr_x, corr_y))

        new_neurons.append(signal)

    # Combine with existing neurons
    original_data = exp.calcium.scdata
    combined_data = np.vstack([original_data, np.array(new_neurons)])

    # Update experiment
    exp.calcium.scdata = combined_data
    exp.calcium.data = combined_data  # Update non-scaled too
    exp.n_cells = combined_data.shape[0]

    # Report correlations
    mean_corr = np.mean([max(cx, cy) for cx, cy in correlations])
    print(f"Added {n_neurons} independent neurons")
    print(f"Mean correlation with position: {mean_corr:.4f}")

    return exp, len(original_data)  # Return boundary index


# Generate base experiment with only spatial neurons
print("="*60)
print("Creating experiment with place cells + independent neurons")
print("="*60)

# Start with pure spatial manifold
exp = generate_2d_manifold_exp(
    n_neurons=30,  # All place cells
    duration=300,
    fps=20,
    seed=42
)

print(f"\nOriginal: {exp.n_cells} place cells")

# Add truly independent neurons
exp, n_manifold = add_independent_neurons(exp, n_neurons=20, seed=123)
print(f"Final: {n_manifold} place cells + {exp.n_cells - n_manifold} independent neurons")

# Test subset for speed
test_neurons = list(range(0, n_manifold, 5)) + list(range(n_manifold, exp.n_cells, 5))
print(f"\nTesting {len(test_neurons)} neurons: {test_neurons}")

# Run LOO analysis
print("\n" + "="*60)
print("Running LOO Analysis")
print("="*60)

results = loo_analysis_simplified(
    exp,
    method='pca',  # Use PCA for clear linear separation
    method_params={'dim': 2},
    neurons_to_test=test_neurons,
    downsampling=10,
    verbose=False
)

# Analyze results
baseline = results.loc['all']
neuron_results = results[results.index != 'all'].copy()

# Calculate importance
neuron_results['error_increase'] = neuron_results['reconstruction_error'] - baseline['reconstruction_error']
neuron_results['corr_decrease'] = baseline['alignment_corr'] - neuron_results['alignment_corr']
neuron_results['importance'] = (neuron_results['error_increase'] + neuron_results['corr_decrease']) / 2

# Classify neurons
neuron_results['is_manifold'] = [idx < n_manifold for idx in neuron_results.index]

# Compare importance
manifold_neurons = neuron_results[neuron_results['is_manifold']]
independent_neurons = neuron_results[~neuron_results['is_manifold']]

print(f"\nResults:")
print(f"Baseline reconstruction error: {baseline['reconstruction_error']:.4f}")
print(f"Baseline alignment correlation: {baseline['alignment_corr']:.4f}")

print(f"\nManifold neurons (n={len(manifold_neurons)}):")
print(f"  Mean importance: {manifold_neurons['importance'].mean():.4f}")
print(f"  Std: {manifold_neurons['importance'].std():.4f}")

print(f"\nIndependent neurons (n={len(independent_neurons)}):")
print(f"  Mean importance: {independent_neurons['importance'].mean():.4f}")
print(f"  Std: {independent_neurons['importance'].std():.4f}")

# Statistical test
if len(manifold_neurons) > 0 and len(independent_neurons) > 0:
    ratio = manifold_neurons['importance'].mean() / (abs(independent_neurons['importance'].mean()) + 1e-10)
    print(f"\nManifold neurons are {ratio:.1f}x more important")

    if ratio > 5:
        print("✅ SUCCESS: LOO clearly distinguishes truly independent neurons!")
    elif ratio > 2:
        print("✅ GOOD: LOO shows significant distinction")
    else:
        print("❌ FAIL: Even with true independence, LOO doesn't distinguish")

# Show top neurons
print(f"\nTop 5 most important neurons:")
top5 = neuron_results.nlargest(5, 'importance')
for idx, row in top5.iterrows():
    neuron_type = "manifold" if row['is_manifold'] else "independent"
    print(f"  Neuron {idx:2d} ({neuron_type:11s}): importance={row['importance']:.4f}")