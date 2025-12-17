#!/usr/bin/env python
"""
Test demonstrating the nn parameter bug in Isomap.
"""

import sys
sys.path.insert(0, '/Users/nikita/PycharmProjects/driada2/src')

import numpy as np
from driada.dim_reduction import MVData

# Create test data
np.random.seed(42)
data = np.random.randn(20, 1000)  # 20 features, 1000 samples
mvdata = MVData(data)

print("Testing Isomap nn parameter bug")
print("="*50)

# Test 1: Using nn parameter (BROKEN)
print("\n1. Using nn=50 (should use 50 neighbors):")
emb1 = mvdata.get_embedding(method='isomap', nn=50, dim=2)

# Check what parameters were actually used
if hasattr(emb1, 'e_params'):
    print(f"  Embedding params: {emb1.e_params}")
if hasattr(emb1, 'g') and emb1.g is not None:
    print(f"  Graph object exists: {emb1.g}")
    if hasattr(emb1.g, 'nn'):
        print(f"  Graph nn value: {emb1.g.nn}")
    else:
        print("  Graph has no nn attribute")

# Test 2: Using n_neighbors (should work)
print("\n2. Using n_neighbors=50 (workaround):")
emb2 = mvdata.get_embedding(method='isomap', n_neighbors=50, dim=2)
if hasattr(emb2, 'e_params'):
    print(f"  Embedding params: {emb2.e_params}")
if hasattr(emb2, 'g') and emb2.g is not None:
    print(f"  Graph object exists: {emb2.g}")
    if hasattr(emb2.g, 'nn'):
        print(f"  Graph nn value: {emb2.g.nn}")
    else:
        print("  Graph has no nn attribute")

# Test 3: Check default value
print("\n3. Default (should be 15 neighbors):")
emb3 = mvdata.get_embedding(method='isomap', dim=2)
if hasattr(emb3, 'e_params'):
    print(f"  Embedding params: {emb3.e_params}")
if hasattr(emb3, 'g') and emb3.g is not None:
    print(f"  Graph object exists: {emb3.g}")
    if hasattr(emb3.g, 'nn'):
        print(f"  Graph nn value: {emb3.g.nn}")
    else:
        print("  Graph has no nn attribute")

# Additional test: inspect graph construction
print("\n4. Detailed inspection of graph params:")
from driada.dim_reduction.dr_base import merge_params_with_defaults

# Test nn mapping
params_with_nn = merge_params_with_defaults('isomap', {'nn': 50, 'dim': 2})
print(f"  With nn=50: g_params = {params_with_nn['g_params']}")

# Test n_neighbors mapping
params_with_n_neighbors = merge_params_with_defaults('isomap', {'n_neighbors': 50, 'dim': 2})
print(f"  With n_neighbors=50: g_params = {params_with_n_neighbors['g_params']}")

print("\n" + "="*50)
print("CONCLUSION:")
if params_with_nn['g_params']['nn'] == 15:  # Still default
    print("BUG CONFIRMED: nn parameter is NOT properly mapped!")
    print("The nn=50 is being ignored, using default nn=15 instead.")
else:
    print("nn parameter appears to be working.")

if params_with_n_neighbors['g_params']['nn'] == 50:
    print("WORKAROUND: Use 'n_neighbors' instead of 'nn'.")
else:
    print("Even n_neighbors is not working properly!")