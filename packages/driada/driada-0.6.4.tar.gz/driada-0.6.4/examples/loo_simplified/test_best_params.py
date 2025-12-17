#!/usr/bin/env python
"""
Test best parameters: Higher firing rate without slowing trajectory too much.
"""

import sys
sys.path.insert(0, '/Users/nikita/PycharmProjects/driada2/src')
sys.path.insert(0, '/Users/nikita/PycharmProjects/driada2/examples/loo_simplified')

import numpy as np
from driada.experiment.synthetic import generate_mixed_population_exp
from loo_analysis_simplified import loo_analysis_simplified

print("="*70)
print("OPTIMAL CONFIGURATION: Balanced improvements")
print("="*70)

# Best balance: higher firing + moderate trajectory slowing
best_manifold_params = {
    'field_sigma': 0.08,      # Sharper fields
    'baseline_rate': 0.05,    # Much lower baseline (was 0.1)
    'peak_rate': 3.0,         # 3x higher firing rate
    'noise_std': 0.03,        # Less noise
    'decay_time': 2.0,
    'calcium_noise_std': 0.08,
    'step_size': 0.015,       # Moderate slowing (was 0.02)
    'momentum': 0.9           # Moderate autocorrelation (was 0.8)
}

best_feature_params = {
    'skip_prob': 0.02,        # Much lower skip (was 0.1)
    'rate_0': 0.05,           # Lower baseline
    'rate_1': 0.5,            # Lower peak for features
    'hurst': 0.3,
    'ampl_range': (0.3, 1.5), # Less variable
    'decay_time': 2.0,
    'noise_std': 0.15         # More noise for features
}

print("\nKey improvements:")
print("  ✓ 3x higher peak firing rate for place cells")
print("  ✓ 2x lower baseline rate (better SNR)")
print("  ✓ Only 25% slower movement (balance visits vs dwelling)")
print("  ✓ 80% reduction in skip probability")
print("  ✓ Lower feature neuron rates (increase contrast)")

print("\nGenerating optimized experiment...")
exp, info = generate_mixed_population_exp(
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
    return_info=True,
    manifold_params=best_manifold_params,
    feature_params=best_feature_params
)

n_manifold = info['population_composition']['n_manifold']
print(f"Generated: {n_manifold} manifold + {60-n_manifold} feature neurons")

# Quick statistics
neural_data = exp.calcium.scdata
x_pos = exp.dynamic_features['x_position'].data
y_pos = exp.dynamic_features['y_position'].data

# Trajectory speed
velocity = np.sqrt(np.diff(x_pos)**2 + np.diff(y_pos)**2) * exp.fps
print(f"\nTrajectory speed: {np.mean(velocity):.3f} units/s")

# Spatial correlations
from scipy.stats import pearsonr
manifold_corrs = []
feature_corrs = []

for i in range(exp.n_cells):
    corr_x = abs(pearsonr(neural_data[i], x_pos)[0])
    corr_y = abs(pearsonr(neural_data[i], y_pos)[0])
    max_corr = max(corr_x, corr_y)

    if i < n_manifold:
        manifold_corrs.append(max_corr)
    else:
        feature_corrs.append(max_corr)

print(f"\nSpatial correlations:")
print(f"  Manifold neurons: {np.mean(manifold_corrs):.3f} ± {np.std(manifold_corrs):.3f}")
print(f"  Feature neurons:  {np.mean(feature_corrs):.3f} ± {np.std(feature_corrs):.3f}")
print(f"  Ratio: {np.mean(manifold_corrs)/np.mean(feature_corrs):.2f}x")

# Run LOO on subset for speed
test_neurons = list(range(0, n_manifold, 3)) + list(range(n_manifold, 60, 3))
print(f"\nRunning LOO on {len(test_neurons)} neurons...")

loo_results = loo_analysis_simplified(
    exp,
    method='isomap',
    method_params={'dim': 2, 'nn': 20},
    neurons_to_test=test_neurons,
    downsampling=10,
    verbose=False
)

# Analyze results
baseline = loo_results.loc['all']
neuron_results = loo_results[loo_results.index != 'all'].copy()

neuron_results['error_increase'] = neuron_results['reconstruction_error'] - baseline['reconstruction_error']
neuron_results['corr_decrease'] = baseline['alignment_corr'] - neuron_results['alignment_corr']
neuron_results['importance'] = (neuron_results['error_increase'] + neuron_results['corr_decrease']) / 2
neuron_results['is_manifold'] = [idx < n_manifold for idx in neuron_results.index]

manifold_neurons = neuron_results[neuron_results['is_manifold']]
feature_neurons = neuron_results[~neuron_results['is_manifold']]

print(f"\nLOO Results:")
print(f"  Baseline alignment: {baseline['alignment_corr']:.4f}")
print(f"  Baseline error: {baseline['reconstruction_error']:.4f}")

print(f"\n  Manifold neurons (n={len(manifold_neurons)}):")
print(f"    Importance: {manifold_neurons['importance'].mean():.4f} ± {manifold_neurons['importance'].std():.4f}")
print(f"    Max importance: {manifold_neurons['importance'].max():.4f}")

print(f"\n  Feature neurons (n={len(feature_neurons)}):")
print(f"    Importance: {feature_neurons['importance'].mean():.4f} ± {feature_neurons['importance'].std():.4f}")
print(f"    Max importance: {feature_neurons['importance'].max():.4f}")

# Statistical test
from scipy.stats import mannwhitneyu
stat, pval = mannwhitneyu(
    manifold_neurons['importance'].values,
    feature_neurons['importance'].values,
    alternative='greater'
)

if abs(feature_neurons['importance'].mean()) > 1e-6:
    ratio = manifold_neurons['importance'].mean() / abs(feature_neurons['importance'].mean())
    print(f"\n  Importance ratio: {ratio:.2f}x")
else:
    print(f"\n  Importance ratio: ∞ (feature importance ≈ 0)")

print(f"  Statistical test: p={pval:.4e}")

# Show top neurons
print(f"\nTop 5 most important neurons:")
top5 = neuron_results.nlargest(5, 'importance')
for idx, row in top5.iterrows():
    neuron_type = "manifold" if row['is_manifold'] else "feature "
    print(f"  Neuron {idx:2d} ({neuron_type}): {row['importance']:.4f}")

print("\n" + "="*70)
if pval < 0.05 and manifold_neurons['importance'].mean() > feature_neurons['importance'].mean():
    print("✅ SUCCESS: Optimized parameters achieve significant discrimination!")
    print(f"   Manifold neurons are significantly more important (p={pval:.3e})")
    print(f"   Spatial correlation ratio: {np.mean(manifold_corrs)/np.mean(feature_corrs):.2f}x")
elif pval < 0.1:
    print("⚠️ MARGINAL: Trending toward significance (p<0.1)")
else:
    print("❌ Not significant at p<0.05 level")
print("="*70)