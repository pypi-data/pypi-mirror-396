#!/usr/bin/env python
"""
Test LOO analysis on mixed population with 2D spatial manifold.

This test creates a population where:
- Some neurons encode 2D spatial position (place cells)
- Other neurons are unrelated (random/noise)

The LOO analysis should identify that removing manifold-encoding neurons
degrades reconstruction more than removing unrelated neurons.
"""

import sys
sys.path.insert(0, '/Users/nikita/PycharmProjects/driada2/src')
sys.path.insert(0, '/Users/nikita/PycharmProjects/driada2/examples/loo_simplified')

import numpy as np
import matplotlib.pyplot as plt
from driada.experiment.synthetic import generate_mixed_population_exp
from loo_analysis_simplified import loo_analysis_simplified

def main(feature_type='continuous', n_neurons=60, use_shuffled=False, seed=42):
    """Test LOO on mixed population with 2D spatial manifold.

    Args:
        feature_type: 'continuous', 'discrete', or 'mixed'
        n_neurons: Number of neurons to simulate
        use_shuffled: If True, shuffle neural data to test null hypothesis
        seed: Random seed for reproducibility (affects data generation and shuffling)
    """

    print("="*70)
    print("LOO Analysis on Mixed Population with 2D Spatial Manifold")
    print("="*70)

    # Generate mixed population
    print(f"\n1. Generating mixed population experiment ({n_neurons} neurons)...")
    print("   - 60% neurons encode 2D spatial position (place cells)")

    if feature_type == 'discrete':
        print("   - 40% neurons encode DISCRETE features (not spatial)")
        n_discrete = 4
        n_continuous = 0
    elif feature_type == 'continuous':
        print("   - 40% neurons encode CONTINUOUS features (not spatial)")
        n_discrete = 0
        n_continuous = 4
    elif feature_type == 'mixed':
        print("   - 40% neurons encode MIXED features (2 discrete + 2 continuous)")
        n_discrete = 2
        n_continuous = 2
    else:
        raise ValueError(f"Unknown feature type: {feature_type}")

    # Use "weaker" parameters that actually work better for LOO discrimination
    optimized_manifold_params = {
        'field_sigma': 0.12,      # Wider fields for more diversity
        'baseline_rate': 0.1,     # Higher baseline for better separation
        'peak_rate': 1.5,         # Lower peak maintains diversity
        'noise_std': 0.05,        # More noise for realistic signals
        'decay_time': 2.0,        # Will be used as t_off_sec in neuron creation
        'calcium_noise_std': 0.08,
        'step_size': 0.02,        # Faster movement for varied sampling
        'momentum': 0.8           # Lower autocorrelation for more variability
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

    exp, info = generate_mixed_population_exp(
        n_neurons=n_neurons,  # Total neurons
        manifold_fraction=0.6,  # 60% are place cells
        manifold_type='2d_spatial',
        n_discrete_features=n_discrete,
        n_continuous_features=n_continuous,
        correlation_mode='independent',  # No correlation between spatial and features
        duration=800,  # Longer duration for better statistics
        fps=20.0,
        seed=seed,  # Use provided seed
        verbose=False,
        return_info=True,
        manifold_params=optimized_manifold_params,
        feature_params=optimized_feature_params
    )

    print(f"\nExperiment created:")
    print(f"  Total neurons: {exp.n_cells}")
    print(f"  Manifold neurons: {info['population_composition']['n_manifold']}")
    print(f"  Feature neurons: {info['population_composition']['n_feature_selective']}")
    print(f"  Duration: {exp.n_frames / exp.fps:.1f} seconds")

    # Check available ground truth
    print("\nGround truth features available:")
    for feat_name, feat_data in exp.dynamic_features.items():
        if hasattr(feat_data, 'data'):
            print(f"  - {feat_name}: shape {feat_data.data.shape}")
        else:
            print(f"  - {feat_name}: type {type(feat_data).__name__}")

    # Run LOO analysis with simplified version
    print("\n2. Running Leave-One-Out analysis (simplified version)...")
    print("   Testing how each neuron affects 2D spatial manifold reconstruction")

    if use_shuffled:
        print("\n⚠️  SHUFFLING NEURAL DATA TO TEST NULL HYPOTHESIS")
        print("   Neural data will be randomly shuffled across time using circular shifts")

    loo_results = loo_analysis_simplified(
        exp,
        method='isomap',  # Use Isomap for non-linear manifold
        method_params={'dim': 2, 'nn': 20},  # More neighbors for better connectivity
        downsampling=10,  # Use aggressive downsampling like deep analysis
        neurons_to_test=None,  # Test all neurons
        verbose=False,
        shuffled=use_shuffled,  # Pass the shuffled flag
        shuffle_seed=seed  # Use same seed for shuffling
    )

    print(f"\n   LOO completed for all {exp.n_cells} neurons")
    print(f"   Metrics computed: {list(loo_results.columns)}")

    # Analyze results
    print("\n3. Analyzing Results:")
    print("-"*60)

    # Get baseline performance
    baseline = loo_results.loc['all']
    print(f"Baseline (all neurons):")
    print(f"  Reconstruction error: {baseline['reconstruction_error']:.4f}")
    print(f"  Alignment correlation: {baseline['alignment_corr']:.4f}")
    print(f"  Decoding R²: {baseline['decoding_r2']:.4f}")

    # Calculate degradation for each neuron
    # Exclude 'all' row which is at index 'all', not at the end
    neuron_results = loo_results[loo_results.index != 'all'].copy()

    # Degradation = how much worse it gets when neuron is removed
    neuron_results['error_increase'] = neuron_results['reconstruction_error'] - baseline['reconstruction_error']
    neuron_results['corr_decrease'] = baseline['alignment_corr'] - neuron_results['alignment_corr']
    neuron_results['r2_decrease'] = baseline['decoding_r2'] - neuron_results['decoding_r2']

    # Identify which neurons are manifold vs feature-selective
    n_manifold = info['population_composition']['n_manifold']
    # Convert index to numeric for comparison (exclude 'all' row)
    neuron_results['is_manifold'] = [idx < n_manifold for idx in neuron_results.index]

    # Compare metrics for manifold vs feature neurons
    print("\n4. Metric Analysis for Neuron Type Discrimination:")
    print("-"*60)

    # Import ROC-AUC for ranking quality
    from sklearn.metrics import roc_auc_score

    # Create binary labels: 1 for manifold, 0 for feature
    y_true = neuron_results['is_manifold'].astype(int).values

    # Compute ROC-AUC for each metric
    print("ROC-AUC scores (perfect ranking = 1.0, random = 0.5):")
    print()

    # Error increase
    roc_error = roc_auc_score(y_true, neuron_results['error_increase'].values)
    print(f"  Reconstruction Error Increase: {roc_error:.4f}")

    # Correlation decrease
    roc_corr = roc_auc_score(y_true, neuron_results['corr_decrease'].values)
    print(f"  Alignment Correlation Decrease: {roc_corr:.4f}")

    # R2 decrease
    roc_r2 = roc_auc_score(y_true, neuron_results['r2_decrease'].values)
    print(f"  Decoding R² Decrease: {roc_r2:.4f}")

    # Find best metric
    best_roc = max([(roc_error, 'Error'), (roc_corr, 'Alignment'), (roc_r2, 'R²')])
    print(f"\n  Best metric: {best_roc[1]} (ROC-AUC = {best_roc[0]:.4f})")

    # Interpret ROC-AUC scores
    print("\nInterpretation:")
    for metric, score in [('Error', roc_error), ('Alignment', roc_corr), ('R²', roc_r2)]:
        if score > 0.7:
            quality = "Good"
        elif score > 0.6:
            quality = "Fair"
        elif score > 0.5:
            quality = "Poor"
        else:
            quality = "No better than random"
        print(f"  {metric}: {quality} discrimination")

    # Statistical tests for each metric
    from scipy.stats import mannwhitneyu
    print("\n5. Statistical Significance (Mann-Whitney U test):")
    print("-"*60)

    # Test error increase
    manifold_error = neuron_results[neuron_results['is_manifold']]['error_increase']
    feature_error = neuron_results[~neuron_results['is_manifold']]['error_increase']
    stat_err, pval_err = mannwhitneyu(manifold_error, feature_error, alternative='greater')
    print(f"  Error increase: p={pval_err:.4e} {'***' if pval_err < 0.001 else ('**' if pval_err < 0.01 else ('*' if pval_err < 0.05 else ''))}")

    # Test correlation decrease
    manifold_corr = neuron_results[neuron_results['is_manifold']]['corr_decrease']
    feature_corr = neuron_results[~neuron_results['is_manifold']]['corr_decrease']
    stat_corr, pval_corr = mannwhitneyu(manifold_corr, feature_corr, alternative='greater')
    print(f"  Corr decrease:  p={pval_corr:.4e} {'***' if pval_corr < 0.001 else ('**' if pval_corr < 0.01 else ('*' if pval_corr < 0.05 else ''))}")

    # Test R2 decrease
    manifold_r2 = neuron_results[neuron_results['is_manifold']]['r2_decrease']
    feature_r2 = neuron_results[~neuron_results['is_manifold']]['r2_decrease']
    stat_r2, pval_r2 = mannwhitneyu(manifold_r2, feature_r2, alternative='greater')
    print(f"  R² decrease:    p={pval_r2:.4e} {'***' if pval_r2 < 0.001 else ('**' if pval_r2 < 0.01 else ('*' if pval_r2 < 0.05 else ''))}")

    # Show which metric is most discriminative
    best_metric = min([(pval_err, 'Error increase'),
                      (pval_corr, 'Alignment correlation'),
                      (pval_r2, 'Decoding R²')])
    print(f"\n  Most significant: {best_metric[1]} (p={best_metric[0]:.4e})")

    # Show top neurons by best metric
    print("\n6. Top 10 Neurons by Best Metric (Alignment Correlation):")
    print("-"*60)

    top_neurons = neuron_results.nlargest(10, 'corr_decrease')
    for idx, row in top_neurons.iterrows():
        neuron_type = "manifold" if row['is_manifold'] else "feature"
        print(f"  Neuron {idx:2d} ({neuron_type:8s}): "
              f"corr_decrease={row['corr_decrease']:.4f}, "
              f"error_increase={row['error_increase']:.4f}, "
              f"r2_decrease={row['r2_decrease']:.4f}")

    # Count how many of top neurons are manifold
    n_top_manifold = top_neurons['is_manifold'].sum()
    print(f"\n  {n_top_manifold}/10 of top neurons are manifold neurons")

    # Visualize results
    print("\n7. Creating visualization...")

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Plot 1: Correlation decrease distribution
    ax = axes[0]
    positions = [1, 2]
    data = [manifold_corr.values, feature_corr.values]
    bp = ax.boxplot(data, positions=positions, widths=0.6, patch_artist=True)
    bp['boxes'][0].set_facecolor('blue')
    bp['boxes'][1].set_facecolor('red')
    ax.set_xticks(positions)
    ax.set_xticklabels(['Manifold', 'Feature'])
    ax.set_ylabel('Alignment Corr Decrease')
    ax.set_title(f'Best Metric (ROC-AUC={roc_corr:.3f})')
    ax.grid(True, alpha=0.3)

    # Plot 2: Correlation decrease by neuron index
    ax = axes[1]
    colors = ['blue' if is_m else 'red' for is_m in neuron_results['is_manifold']]
    bars = ax.bar(range(len(neuron_results)), neuron_results['corr_decrease'], color=colors, alpha=0.7)
    ax.axvline(x=n_manifold-0.5, color='black', linestyle='--', alpha=0.5, label='Manifold/Feature boundary')
    ax.set_xlabel('Neuron Index')
    ax.set_ylabel('Alignment Corr Decrease')
    ax.set_title('Correlation Impact by Neuron')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Plot 3: Error increase vs correlation decrease
    ax = axes[2]
    for is_m in [True, False]:
        mask = neuron_results['is_manifold'] == is_m
        label = 'Manifold' if is_m else 'Feature'
        color = 'blue' if is_m else 'red'
        ax.scatter(neuron_results[mask]['error_increase'],
                  neuron_results[mask]['corr_decrease'],
                  label=label, alpha=0.6, s=50, c=color)
    ax.set_xlabel('Reconstruction Error Increase')
    ax.set_ylabel('Alignment Correlation Decrease')
    ax.set_title('Impact on Different Metrics')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('loo_mixed_2d_manifold_results.png', dpi=150, bbox_inches='tight')
    print("   Saved visualization to: loo_mixed_2d_manifold_results.png")

    # Summary
    print("\n" + "="*70)
    print("SUMMARY:")
    print("="*70)

    print(f"\nROC-AUC Scores (1.0 = perfect ranking, 0.5 = random):")
    print(f"  Alignment Correlation: {roc_corr:.3f} - {best_roc[1] if best_roc[1] == 'Alignment' else ''}")
    print(f"  Reconstruction Error:  {roc_error:.3f}")
    print(f"  Decoding R²:          {roc_r2:.3f}")

    print(f"\nStatistical Significance:")
    print(f"  Best metric (Alignment): p = {pval_corr:.4e}")

    if roc_corr > 0.7 and pval_corr < 0.001:
        print("\n✅ EXCELLENT: LOO analysis with alignment correlation strongly")
        print("  distinguishes manifold neurons from feature neurons.")
        print(f"  ROC-AUC = {roc_corr:.3f} indicates good ranking ability.")
    elif roc_corr > 0.6 and pval_corr < 0.05:
        print("\n✓ GOOD: LOO analysis can distinguish manifold from feature neurons")
        print(f"  ROC-AUC = {roc_corr:.3f} indicates fair discrimination.")
    else:
        print("\n✗ POOR: LOO analysis struggles to distinguish neuron types.")
        print("  Consider different parameters or methods.")

    return loo_results, neuron_results, info

if __name__ == "__main__":
    import sys

    # Parse command line arguments
    feature_type = 'continuous'  # default
    n_neurons = 60  # default
    use_shuffled = False  # default
    seed = 42  # default

    if '--discrete' in sys.argv or '-d' in sys.argv:
        feature_type = 'discrete'
    elif '--mixed' in sys.argv or '-m' in sys.argv:
        feature_type = 'mixed'
    elif '--continuous' in sys.argv or '-c' in sys.argv:
        feature_type = 'continuous'

    if '--random' in sys.argv or '--shuffled' in sys.argv:
        use_shuffled = True

    # Check for neuron count and seed
    for arg in sys.argv[1:]:
        if arg.startswith('--seed='):
            seed = int(arg.split('=')[1])
        elif arg.startswith('--neurons='):
            n_neurons = int(arg.split('=')[1])

    print(f"\n🔄 Configuration:")
    print(f"   - Feature type: {feature_type.upper()}")
    print(f"   - Number of neurons: {n_neurons}")
    print(f"   - Shuffled data: {'YES' if use_shuffled else 'NO'}")
    print(f"   - Random seed: {seed}")

    loo_results, neuron_analysis, exp_info = main(feature_type=feature_type, n_neurons=n_neurons, use_shuffled=use_shuffled, seed=seed)