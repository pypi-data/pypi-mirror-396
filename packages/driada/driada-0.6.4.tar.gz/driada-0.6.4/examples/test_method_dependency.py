#!/usr/bin/env python
"""
Test if the LOO paradoxes depend on the specific DR method used (Isomap vs PCA)
"""

import sys
sys.path.insert(0, '/Users/nikita/PycharmProjects/driada2/src')
sys.path.insert(0, '/Users/nikita/PycharmProjects/driada2/examples/loo_simplified')

import numpy as np
from sklearn.metrics import roc_auc_score
from scipy.stats import mannwhitneyu

from driada.experiment.synthetic import generate_mixed_population_exp
from loo_analysis_simplified import loo_analysis_simplified

print("TESTING: Method Dependency of LOO Paradoxes")
print("="*60)

# Use the exact parameters from test_loo_mixed_2d_manifold.py
weaker_manifold_params = {
    'field_sigma': 0.12,      # Wider fields for more diversity
    'baseline_rate': 0.1,     # Higher baseline for better separation
    'peak_rate': 1.5,         # Lower peak maintains diversity
    'noise_std': 0.05,        # More noise for realistic signals
    'decay_time': 2.0,        # Will be used as t_off_sec in neuron creation
    'calcium_noise_std': 0.08,
    'step_size': 0.02,        # Faster movement for varied sampling
    'momentum': 0.8           # Lower autocorrelation for more variability
}

optimized_manifold_params = {
    'field_sigma': 0.08,
    'baseline_rate': 0.05,
    'peak_rate': 2.0,
    'noise_std': 0.03,
    'decay_time': 2.0,
    'calcium_noise_std': 0.08,
    'step_size': 0.015,
    'momentum': 0.9
}

optimized_feature_params = {
    'skip_prob': 0.1,         # Higher skip for more distinction
    'rate_0': 0.1,            # Higher baseline for separation
    'rate_1': 1.0,            # Keep at 1.0 as requested
    'hurst': 0.3,
    'ampl_range': (0.5, 2.0),
    'decay_time': 2.0,        # Will be used as t_off_sec in neuron creation
    'noise_std': 0.1
}

# Test with both parameter sets and both methods
results = {}

for param_name, manifold_params in [("Weaker", weaker_manifold_params), ("Optimized", optimized_manifold_params)]:
    results[param_name] = {}

    print(f"\n--- {param_name} Parameters ---")

    # Generate experiment (smaller for speed)
    exp, info = generate_mixed_population_exp(
        n_neurons=30,  # Smaller
        manifold_fraction=0.6,
        manifold_type='2d_spatial',
        n_discrete_features=0,
        n_continuous_features=4,
        correlation_mode='independent',
        duration=300,  # Shorter
        fps=20.0,
        seed=42,
        verbose=False,
        return_info=True,
        manifold_params=manifold_params,
        feature_params=optimized_feature_params
    )

    n_manifold = info['population_composition']['n_manifold']
    test_neurons = list(range(0, n_manifold, 2)) + list(range(n_manifold, exp.n_cells, 2))

    print(f"Testing {len(test_neurons)} neurons from {exp.n_cells} total")

    # Test with both PCA and Isomap
    for method in ['pca', 'isomap']:
        print(f"\n  Testing {method.upper()}...")

        if method == 'isomap':
            method_params = {'dim': 2, 'nn': 20}
        else:
            method_params = {'dim': 2}

        try:
            loo_results = loo_analysis_simplified(
                exp,
                method=method,
                method_params=method_params,
                neurons_to_test=test_neurons,
                downsampling=5,
                verbose=False
            )

            # Analyze results
            baseline = loo_results.loc['all']
            neuron_results = loo_results[loo_results.index != 'all'].copy()

            neuron_results['corr_decrease'] = baseline['alignment_corr'] - neuron_results['alignment_corr']
            neuron_results['is_manifold'] = [idx < n_manifold for idx in neuron_results.index]

            # Check if we have both types
            manifold_mask = neuron_results['is_manifold'].values
            if np.sum(manifold_mask) > 0 and np.sum(~manifold_mask) > 0:
                y_true = manifold_mask.astype(int)
                scores = neuron_results['corr_decrease'].values

                roc_auc = roc_auc_score(y_true, scores)

                manifold_vals = scores[manifold_mask]
                feature_vals = scores[~manifold_mask]
                _, p_val = mannwhitneyu(manifold_vals, feature_vals, alternative='greater')

                results[param_name][method] = {
                    'roc_auc': roc_auc,
                    'p_value': p_val,
                    'baseline_alignment': baseline['alignment_corr'],
                    'baseline_r2': baseline['decoding_r2'],
                    'n_manifold_tested': np.sum(manifold_mask),
                    'n_feature_tested': np.sum(~manifold_mask)
                }

                print(f"    ROC-AUC: {roc_auc:.3f}")
                print(f"    P-value: {p_val:.3e}")
                print(f"    Baseline: alignment={baseline['alignment_corr']:.3f}, r2={baseline['decoding_r2']:.3f}")

            else:
                print(f"    Not enough neurons of each type")
                results[param_name][method] = None

        except Exception as e:
            print(f"    Failed: {e}")
            results[param_name][method] = None

# Summary comparison
print("\n" + "="*60)
print("SUMMARY COMPARISON")
print("="*60)

for method in ['pca', 'isomap']:
    print(f"\n{method.upper()} Results:")
    print("-" * 30)

    weaker_result = results.get("Weaker", {}).get(method)
    optimized_result = results.get("Optimized", {}).get(method)

    if weaker_result and optimized_result:
        weaker_roc = weaker_result['roc_auc']
        optimized_roc = optimized_result['roc_auc']
        weaker_p = weaker_result['p_value']
        optimized_p = optimized_result['p_value']

        print(f"  Weaker Params:    ROC-AUC = {weaker_roc:.3f}, p = {weaker_p:.3e}")
        print(f"  Optimized Params: ROC-AUC = {optimized_roc:.3f}, p = {optimized_p:.3e}")

        if weaker_roc > optimized_roc:
            print(f"  ✓ Weaker params work better (difference: {weaker_roc - optimized_roc:.3f})")
            if weaker_p < 0.01 and optimized_p > 0.1:
                print(f"  ✅ PARADOX REPRODUCED with {method.upper()}!")
            else:
                print(f"  ⚠️  Effect exists but significance levels don't match expected pattern")
        else:
            print(f"  ❌ Optimized params work better (difference: {optimized_roc - weaker_roc:.3f})")
    else:
        print(f"  Incomplete results for {method}")

print(f"\nConclusion:")
print(f"- Check if paradox is method-specific (Isomap vs PCA)")
print(f"- May need larger datasets or different parameter combinations")
print(f"- Statistical power might be low with small test datasets")