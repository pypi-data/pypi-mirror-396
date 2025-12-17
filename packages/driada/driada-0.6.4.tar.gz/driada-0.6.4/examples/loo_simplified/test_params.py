#!/usr/bin/env python
"""Test the data_type and use_scaled parameters."""

from driada.experiment.synthetic import generate_2d_manifold_exp
from loo_analysis_simplified import loo_analysis_simplified

# Generate test data
print("Generating test experiment...")
exp = generate_2d_manifold_exp(
    n_neurons=10,
    duration=50,
    fps=20,
    seed=42
)

print("\n" + "="*60)
print("Test 1: Calcium data, scaled")
print("="*60)
results1 = loo_analysis_simplified(
    exp,
    method='pca',
    data_type='calcium',
    use_scaled=True,
    neurons_to_test=[0, 1, 2],
    verbose=True
)

print("\n" + "="*60)
print("Test 2: Calcium data, unscaled")
print("="*60)
results2 = loo_analysis_simplified(
    exp,
    method='pca',
    data_type='calcium',
    use_scaled=False,
    neurons_to_test=[0, 1, 2],
    verbose=True
)

print("\n" + "="*60)
print("Comparing results:")
print("="*60)
print("\nScaled data baseline:")
print(results1.loc['all'])
print("\nUnscaled data baseline:")
print(results2.loc['all'])

# Check if there's a difference
diff = abs(results1.loc['all']['reconstruction_error'] - results2.loc['all']['reconstruction_error'])
print(f"\nDifference in reconstruction error: {diff:.6f}")
print(f"Using {'different' if diff > 0.001 else 'same'} data")