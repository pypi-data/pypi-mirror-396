#!/usr/bin/env python
"""
Test improved spatial tuning with:
1. Increased trajectory autocorrelation (slower, more dwelling movement)
2. Higher peak firing rate (2Hz instead of 1Hz)
"""

import sys
sys.path.insert(0, '/Users/nikita/PycharmProjects/driada2/src')
sys.path.insert(0, '/Users/nikita/PycharmProjects/driada2/examples/loo_simplified')

import numpy as np
from driada.experiment.synthetic import generate_mixed_population_exp
from loo_analysis_simplified import loo_analysis_simplified

print("="*60)
print("Testing Improved Spatial Tuning Parameters")
print("="*60)

# Test different configurations
# Default manifold parameters
default_params = {
    'field_sigma': 0.1,
    'baseline_rate': 0.1,
    'peak_rate': 1.0,
    'noise_std': 0.05,
    'decay_time': 2.0,
    'calcium_noise_std': 0.1,
    'step_size': 0.02,
    'momentum': 0.8
}

configs = [
    {
        'name': 'Baseline (Default)',
        'manifold_params': default_params.copy()
    },
    {
        'name': 'Higher Firing Rate Only',
        'manifold_params': {**default_params, 'peak_rate': 2.0}  # 2Hz instead of 1Hz
    },
    {
        'name': 'Slower Trajectory Only',
        'manifold_params': {
            **default_params,
            'step_size': 0.01,  # Reduced from 0.02 for slower movement
            'momentum': 0.95    # Increased from 0.8 for more autocorrelation
        }
    },
    {
        'name': 'Both Improvements',
        'manifold_params': {
            **default_params,
            'peak_rate': 2.0,   # 2Hz firing
            'step_size': 0.01,  # Slower movement
            'momentum': 0.95    # Higher autocorrelation
        }
    }
]

results_summary = []

for config in configs:
    print(f"\n{'-'*60}")
    print(f"Configuration: {config['name']}")
    print(f"{'-'*60}")

    # Generate experiment with specified parameters
    exp, info = generate_mixed_population_exp(
        n_neurons=60,
        manifold_fraction=0.6,  # 36 manifold, 24 feature neurons
        manifold_type='2d_spatial',
        n_discrete_features=2,
        n_continuous_features=2,
        correlation_mode='independent',
        duration=300,  # 5 minutes for faster testing
        fps=20.0,
        seed=42,
        verbose=False,
        return_info=True,
        manifold_params=config['manifold_params']
    )

    n_manifold = info['population_composition']['n_manifold']
    print(f"Generated: {n_manifold} manifold neurons, {exp.n_cells-n_manifold} feature neurons")

    # Analyze place field visit statistics
    x_pos = exp.dynamic_features['x_position'].data
    y_pos = exp.dynamic_features['y_position'].data
    neural_data = exp.calcium.scdata

    # Calculate trajectory speed to verify autocorrelation effect
    velocity = np.sqrt(np.diff(x_pos)**2 + np.diff(y_pos)**2) * exp.fps
    mean_speed = np.mean(velocity)
    speed_autocorr = np.corrcoef(velocity[:-1], velocity[1:])[0, 1]

    print(f"\nTrajectory statistics:")
    print(f"  Mean speed: {mean_speed:.3f} units/s")
    print(f"  Speed autocorrelation: {speed_autocorr:.3f}")

    # Analyze firing statistics for manifold neurons
    firing_rates = []
    spike_counts = []
    active_fractions = []

    for neuron_id in range(n_manifold):
        signal = neural_data[neuron_id]

        # Basic firing statistics
        mean_activity = np.mean(signal)
        threshold = mean_activity + np.std(signal)
        is_active = signal > threshold

        # Count spikes (peaks in signal)
        from scipy.signal import find_peaks
        peaks, _ = find_peaks(signal, height=threshold, distance=10)
        n_spikes = len(peaks)

        # Calculate statistics
        firing_rate = n_spikes / (exp.n_frames / exp.fps)
        active_fraction = np.sum(is_active) / len(signal)

        firing_rates.append(firing_rate)
        spike_counts.append(n_spikes)
        active_fractions.append(active_fraction)

    print(f"\nManifold neuron firing statistics:")
    print(f"  Mean firing rate: {np.mean(firing_rates):.2f} Hz")
    print(f"  Mean spike count: {np.mean(spike_counts):.1f} spikes")
    print(f"  Mean active fraction: {np.mean(active_fractions)*100:.1f}%")

    # Run simplified LOO analysis on subset for speed
    test_neurons = list(range(0, n_manifold, 6)) + list(range(n_manifold, exp.n_cells, 6))
    print(f"\nRunning LOO on {len(test_neurons)} neurons...")

    loo_results = loo_analysis_simplified(
        exp,
        method='pca',  # Use PCA for speed
        method_params={'dim': 2},
        neurons_to_test=test_neurons,
        downsampling=10,
        verbose=False
    )

    # Analyze results
    baseline = loo_results.loc['all']
    neuron_results = loo_results[loo_results.index != 'all'].copy()

    # Calculate importance
    neuron_results['error_increase'] = neuron_results['reconstruction_error'] - baseline['reconstruction_error']
    neuron_results['corr_decrease'] = baseline['alignment_corr'] - neuron_results['alignment_corr']
    neuron_results['importance'] = (neuron_results['error_increase'] + neuron_results['corr_decrease']) / 2

    # Classify neurons
    neuron_results['is_manifold'] = [idx < n_manifold for idx in neuron_results.index]

    # Compare importance
    manifold_neurons = neuron_results[neuron_results['is_manifold']]
    feature_neurons = neuron_results[~neuron_results['is_manifold']]

    manifold_importance = manifold_neurons['importance'].mean()
    feature_importance = feature_neurons['importance'].mean()

    print(f"\nLOO Results:")
    print(f"  Baseline alignment: {baseline['alignment_corr']:.4f}")
    print(f"  Manifold importance: {manifold_importance:.4f}")
    print(f"  Feature importance: {feature_importance:.4f}")
    if feature_importance > 0:
        ratio = manifold_importance / feature_importance
        print(f"  Ratio: {ratio:.2f}x")
    else:
        ratio = float('inf')
        print(f"  Ratio: ∞ (feature importance = 0)")

    # Statistical test
    from scipy.stats import mannwhitneyu
    if len(manifold_neurons) > 0 and len(feature_neurons) > 0:
        stat, pval = mannwhitneyu(
            manifold_neurons['importance'].values,
            feature_neurons['importance'].values,
            alternative='greater'
        )
        print(f"  P-value: {pval:.4e}")
        if pval < 0.05:
            print(f"  ✓ Significant difference!")
        else:
            print(f"  ✗ No significant difference")

    results_summary.append({
        'config': config['name'],
        'mean_speed': mean_speed,
        'speed_autocorr': speed_autocorr,
        'firing_rate': np.mean(firing_rates),
        'active_fraction': np.mean(active_fractions),
        'baseline_alignment': baseline['alignment_corr'],
        'manifold_importance': manifold_importance,
        'feature_importance': feature_importance,
        'ratio': ratio,
        'pval': pval if 'pval' in locals() else 1.0
    })

# Summary comparison
print("\n" + "="*60)
print("SUMMARY COMPARISON")
print("="*60)

print("\nTrajectory & Firing:")
print(f"{'Config':<25} {'Speed':<8} {'Autocorr':<8} {'Firing Hz':<10} {'Active %':<10}")
print("-" * 70)
for r in results_summary:
    print(f"{r['config']:<25} {r['mean_speed']:<8.3f} {r['speed_autocorr']:<8.3f} "
          f"{r['firing_rate']:<10.2f} {r['active_fraction']*100:<10.1f}")

print("\nLOO Performance:")
print(f"{'Config':<25} {'Alignment':<10} {'Manifold':<10} {'Feature':<10} {'Ratio':<8} {'P-value':<12}")
print("-" * 85)
for r in results_summary:
    ratio_str = f"{r['ratio']:.2f}x" if r['ratio'] != float('inf') else "∞"
    sig_marker = "***" if r['pval'] < 0.001 else ("**" if r['pval'] < 0.01 else ("*" if r['pval'] < 0.05 else ""))
    print(f"{r['config']:<25} {r['baseline_alignment']:<10.4f} {r['manifold_importance']:<10.4f} "
          f"{r['feature_importance']:<10.4f} {ratio_str:<8} {r['pval']:<12.4e} {sig_marker}")

# Find best configuration
best_config = max(results_summary, key=lambda x: x['ratio'] if x['ratio'] != float('inf') else 1000)
print(f"\n✅ BEST CONFIGURATION: {best_config['config']}")
print(f"   Achieves {best_config['ratio']:.2f}x better distinction between manifold and feature neurons")

if best_config['config'] == 'Both Improvements':
    print("\n" + "="*60)
    print("SUCCESS: Combined improvements work best!")
    print("="*60)
    print("Recommendations:")
    print("1. Set peak_rate=2.0 for manifold neurons")
    print("2. Set trajectory autocorr_time=2.0 for slower movement")
    print("These changes make place cells significantly more distinguishable from feature neurons.")