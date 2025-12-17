#!/usr/bin/env python
"""
Test script to verify the R² calculation fix works correctly.
"""

import numpy as np
import sys
import os
from sklearn.decomposition import PCA

# Add the src directory to the path so we can import driada
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from driada.dim_reduction.manifold_metrics import compute_decoding_accuracy
from driada.experiment.synthetic import generate_2d_manifold_exp


def test_fixed_r2_calculation():
    """Test that the fixed R² calculation gives reasonable results."""
    print("Testing R² calculation fix...")

    # Generate a larger test experiment with stronger signal
    exp = generate_2d_manifold_exp(
        n_neurons=50,
        duration=300,
        fps=20,
        seed=42
    )

    # Get neural data and ground truth
    neural_data = exp.calcium.scdata.T  # (n_samples, n_neurons)
    positions = exp.dynamic_features['position_2d'].data.T  # (n_samples, 2)

    print(f"Neural data shape: {neural_data.shape}")
    print(f"Positions shape: {positions.shape}")

    # Apply PCA for dimensionality reduction (more realistic scenario)
    pca = PCA(n_components=10)
    neural_data_pca = pca.fit_transform(neural_data)
    print(f"PCA data shape: {neural_data_pca.shape}")
    print(f"PCA explained variance ratio: {pca.explained_variance_ratio_[:3]}")

    # Test 1: Real data (should have decent R²)
    print("\n=== Test 1: Real Data ===")
    result_real = compute_decoding_accuracy(
        neural_data_pca, positions,
        manifold_type='spatial',
        train_fraction=0.8
    )
    print(f"Real data R²: {result_real['test_r2']:.4f}")
    print(f"Real data test error: {result_real['test_error']:.4f}")

    # Test 2: Shuffled neural data (should have poor R²)
    print("\n=== Test 2: Shuffled Neural Data ===")
    np.random.seed(123)
    shuffled_neural = neural_data.copy()
    for i in range(shuffled_neural.shape[1]):  # Shuffle each neuron independently
        np.random.shuffle(shuffled_neural[:, i])

    # Apply same PCA transformation to shuffled data
    shuffled_neural_pca = pca.transform(shuffled_neural)

    result_shuffled = compute_decoding_accuracy(
        shuffled_neural_pca, positions,
        manifold_type='spatial',
        train_fraction=0.8
    )
    print(f"Shuffled data R²: {result_shuffled['test_r2']:.4f}")
    print(f"Shuffled data test error: {result_shuffled['test_error']:.4f}")

    # Test 3: Random data (should have poor R²)
    print("\n=== Test 3: Random Data ===")
    np.random.seed(456)
    random_neural_pca = np.random.randn(*neural_data_pca.shape)

    result_random = compute_decoding_accuracy(
        random_neural_pca, positions,
        manifold_type='spatial',
        train_fraction=0.8
    )
    print(f"Random data R²: {result_random['test_r2']:.4f}")
    print(f"Random data test error: {result_random['test_error']:.4f}")

    # Validation checks
    print("\n=== Validation ===")

    # R² for real data should be positive and reasonably high
    if result_real['test_r2'] > 0.1:
        print("✅ Real data has positive R² as expected")
    else:
        print(f"❌ Real data R² is too low: {result_real['test_r2']:.4f}")

    # R² for shuffled/random data should be low or negative
    if result_shuffled['test_r2'] < 0.1:
        print("✅ Shuffled data has low R² as expected")
    else:
        print(f"❌ Shuffled data R² is too high: {result_shuffled['test_r2']:.4f}")

    if result_random['test_r2'] < 0.1:
        print("✅ Random data has low R² as expected")
    else:
        print(f"❌ Random data R² is too high: {result_random['test_r2']:.4f}")


if __name__ == "__main__":
    test_fixed_r2_calculation()