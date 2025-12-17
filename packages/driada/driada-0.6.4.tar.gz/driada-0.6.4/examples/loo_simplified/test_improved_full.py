#!/usr/bin/env python
"""
Full test of improved spatial tuning with proper parameters.
"""

import sys
sys.path.insert(0, '/Users/nikita/PycharmProjects/driada2/src')
sys.path.insert(0, '/Users/nikita/PycharmProjects/driada2/examples/loo_simplified')

import numpy as np
from driada.experiment.synthetic import generate_mixed_population_exp
from loo_analysis_simplified import loo_analysis_simplified

print("="*70)
print("FULL TEST: Improved Spatial Tuning for Better LOO Discrimination")
print("="*70)

# Optimal parameters based on analysis
optimal_manifold_params = {
    'field_sigma': 0.08,      # Sharper fields (was 0.1)
    'baseline_rate': 0.07,    # Lower baseline (was 0.1)
    'peak_rate': 2.0,         # Higher firing rate (was 1.0)
    'noise_std': 0.04,        # Less noise (was 0.05)
    'decay_time': 2.0,        # Keep default
    'calcium_noise_std': 0.1, # Keep default
    'step_size': 0.01,        # Slower movement (was 0.02)
    'momentum': 0.95          # Higher autocorrelation (was 0.8)
}

# Also adjust feature parameters to reduce skip probability
optimal_feature_params = {
    'skip_prob': 0.05,        # Reduced from 0.1
    'rate_0': 0.1,
    'rate_1': 1.0,
    'hurst': 0.3,
    'ampl_range': (0.5, 2.0),
    'decay_time': 2.0,
    'noise_std': 0.1
}

print("\nOptimized parameters:")
print("  - Peak firing rate: 2.0 Hz (doubled)")
print("  - Trajectory autocorrelation: increased via momentum=0.95")
print("  - Place field sharpness: sigma=0.08 (20% sharper)")
print("  - Skip probability: 0.05 (50% reduction)")
print("  - Movement speed: step_size=0.01 (50% slower)")

print("\nGenerating optimized experiment...")
exp_opt, info_opt = generate_mixed_population_exp(
    n_neurons=60,
    manifold_fraction=0.6,
    manifold_type='2d_spatial',
    n_discrete_features=2,
    n_continuous_features=2,
    correlation_mode='independent',
    duration=600,  # Full 10 minutes
    fps=20.0,
    seed=42,
    verbose=False,
    return_info=True,
    manifold_params=optimal_manifold_params,
    feature_params=optimal_feature_params
)

print("\nGenerating baseline for comparison...")
exp_base, info_base = generate_mixed_population_exp(
    n_neurons=60,
    manifold_fraction=0.6,
    manifold_type='2d_spatial',
    n_discrete_features=2,
    n_continuous_features=2,
    correlation_mode='independent',
    duration=600,
    fps=20.0,
    seed=42,
    verbose=False,
    return_info=True
)

n_manifold = info_opt['population_composition']['n_manifold']
print(f"\nExperiment structure: {n_manifold} manifold + {60-n_manifold} feature neurons")

# Analyze improvements in firing patterns
def analyze_firing(exp, n_manifold, label):
    neural_data = exp.calcium.scdata
    x_pos = exp.dynamic_features['x_position'].data
    y_pos = exp.dynamic_features['y_position'].data

    # Trajectory statistics
    velocity = np.sqrt(np.diff(x_pos)**2 + np.diff(y_pos)**2) * exp.fps
    mean_speed = np.mean(velocity)

    # Place cell firing statistics
    manifold_stats = []
    for i in range(n_manifold):
        signal = neural_data[i]
        mean_val = np.mean(signal)
        std_val = np.std(signal)
        threshold = mean_val + std_val

        # Count firing events
        is_firing = signal > threshold
        firing_changes = np.diff(np.concatenate([[0], is_firing.astype(int), [0]]))
        n_events = len(np.where(firing_changes == 1)[0])

        # Activity percentage
        percent_active = 100 * np.sum(is_firing) / len(signal)

        manifold_stats.append({
            'n_events': n_events,
            'percent_active': percent_active
        })

    # Feature neuron statistics
    feature_stats = []
    for i in range(n_manifold, exp.n_cells):
        signal = neural_data[i]
        mean_val = np.mean(signal)
        std_val = np.std(signal)
        threshold = mean_val + std_val
        is_firing = signal > threshold
        percent_active = 100 * np.sum(is_firing) / len(signal)
        feature_stats.append(percent_active)

    print(f"\n{label} Statistics:")
    print(f"  Trajectory speed: {mean_speed:.3f} units/s")
    print(f"  Manifold neurons:")
    print(f"    Firing events: {np.mean([s['n_events'] for s in manifold_stats]):.1f} ± {np.std([s['n_events'] for s in manifold_stats]):.1f}")
    print(f"    Active time: {np.mean([s['percent_active'] for s in manifold_stats]):.1f}% ± {np.std([s['percent_active'] for s in manifold_stats]):.1f}%")
    print(f"  Feature neurons:")
    print(f"    Active time: {np.mean(feature_stats):.1f}% ± {np.std(feature_stats):.1f}%")

    return manifold_stats

baseline_stats = analyze_firing(exp_base, n_manifold, "BASELINE")
optimized_stats = analyze_firing(exp_opt, n_manifold, "OPTIMIZED")

# Calculate improvement
baseline_events = np.mean([s['n_events'] for s in baseline_stats])
optimized_events = np.mean([s['n_events'] for s in optimized_stats])
improvement = 100 * (optimized_events - baseline_events) / baseline_events

print(f"\n📈 Firing event improvement: {improvement:+.1f}%")

# Run LOO analysis on both
print("\n" + "="*70)
print("Running LOO Analysis Comparison")
print("="*70)

# Test all neurons for comprehensive analysis
print("\n1. Testing BASELINE configuration...")
loo_base = loo_analysis_simplified(
    exp_base,
    method='isomap',
    method_params={'dim': 2, 'nn': 30},
    neurons_to_test=None,  # Test all
    downsampling=10,
    verbose=False
)

print("2. Testing OPTIMIZED configuration...")
loo_opt = loo_analysis_simplified(
    exp_opt,
    method='isomap',
    method_params={'dim': 2, 'nn': 30},
    neurons_to_test=None,  # Test all
    downsampling=10,
    verbose=False
)

# Analyze results
def analyze_loo(results, n_manifold, label):
    baseline = results.loc['all']
    neuron_results = results[results.index != 'all'].copy()

    neuron_results['error_increase'] = neuron_results['reconstruction_error'] - baseline['reconstruction_error']
    neuron_results['corr_decrease'] = baseline['alignment_corr'] - neuron_results['alignment_corr']
    neuron_results['importance'] = (neuron_results['error_increase'] + neuron_results['corr_decrease']) / 2

    neuron_results['is_manifold'] = [idx < n_manifold for idx in neuron_results.index]

    manifold_neurons = neuron_results[neuron_results['is_manifold']]
    feature_neurons = neuron_results[~neuron_results['is_manifold']]

    print(f"\n{label} LOO Results:")
    print(f"  Baseline alignment: {baseline['alignment_corr']:.4f}")
    print(f"  Manifold importance: {manifold_neurons['importance'].mean():.4f} ± {manifold_neurons['importance'].std():.4f}")
    print(f"  Feature importance: {feature_neurons['importance'].mean():.4f} ± {feature_neurons['importance'].std():.4f}")

    if feature_neurons['importance'].mean() != 0:
        ratio = manifold_neurons['importance'].mean() / abs(feature_neurons['importance'].mean())
    else:
        ratio = float('inf')

    # Statistical test
    from scipy.stats import mannwhitneyu
    stat, pval = mannwhitneyu(
        manifold_neurons['importance'].values,
        feature_neurons['importance'].values,
        alternative='greater'
    )

    print(f"  Importance ratio: {ratio:.2f}x")
    print(f"  P-value: {pval:.4e}")

    # Count how many of top-10 are manifold neurons
    top10 = neuron_results.nlargest(10, 'importance')
    n_manifold_in_top10 = sum(top10['is_manifold'])
    print(f"  Top-10 neurons: {n_manifold_in_top10}/10 are manifold neurons")

    return {
        'alignment': baseline['alignment_corr'],
        'manifold_imp': manifold_neurons['importance'].mean(),
        'feature_imp': feature_neurons['importance'].mean(),
        'ratio': ratio,
        'pval': pval,
        'top10_manifold': n_manifold_in_top10
    }

base_results = analyze_loo(loo_base, n_manifold, "BASELINE")
opt_results = analyze_loo(loo_opt, n_manifold, "OPTIMIZED")

# Summary
print("\n" + "="*70)
print("FINAL COMPARISON")
print("="*70)

print(f"\nAlignment quality:")
print(f"  Baseline:  {base_results['alignment']:.4f}")
print(f"  Optimized: {opt_results['alignment']:.4f}")
print(f"  Change: {100*(opt_results['alignment']-base_results['alignment'])/base_results['alignment']:+.1f}%")

print(f"\nManifold/Feature discrimination:")
print(f"  Baseline ratio:  {base_results['ratio']:.2f}x")
print(f"  Optimized ratio: {opt_results['ratio']:.2f}x")

print(f"\nStatistical significance:")
print(f"  Baseline p-value:  {base_results['pval']:.4e}")
print(f"  Optimized p-value: {opt_results['pval']:.4e}")

print(f"\nTop-10 accuracy:")
print(f"  Baseline:  {base_results['top10_manifold']}/10 manifold neurons")
print(f"  Optimized: {opt_results['top10_manifold']}/10 manifold neurons")

# Final verdict
print("\n" + "="*70)
if opt_results['pval'] < 0.05 and opt_results['ratio'] > base_results['ratio']:
    print("✅ SUCCESS: Optimized parameters significantly improve LOO discrimination!")
    print(f"   - {improvement:.0f}% more firing events")
    print(f"   - {opt_results['ratio']/base_results['ratio']:.1f}x better manifold/feature separation")
    print(f"   - Statistical significance achieved (p={opt_results['pval']:.3e})")
else:
    print("⚠️ PARTIAL SUCCESS: Some improvement but not fully significant")
print("="*70)