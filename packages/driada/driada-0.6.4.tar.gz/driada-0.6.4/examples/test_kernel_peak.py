"""Test to find the exact kernel peak offset empirically."""

import numpy as np
from driada.experiment.neuron import Neuron

# Test parameters matching our usage
t_rise_frames = 5.0  # 0.25s * 20 Hz
t_off_frames = 40.0  # 2.0s * 20 Hz

# Generate the actual kernel
t = np.linspace(0, 1000, num=1000)
kernel = Neuron.spike_form(t, t_rise_frames, t_off_frames)

# Find peak
peak_idx = np.argmax(kernel)
peak_value = kernel[peak_idx]

print("=" * 80)
print("KERNEL PEAK ANALYSIS")
print("=" * 80)
print(f"\nParameters:")
print(f"  t_rise: {t_rise_frames} frames (0.25s @ 20Hz)")
print(f"  t_off: {t_off_frames} frames (2.0s @ 20Hz)")

print(f"\nEmpirical kernel peak:")
print(f"  Peak at index: {peak_idx} frames")
print(f"  Peak time: {peak_idx / 20.0:.4f} s")
print(f"  Peak value: {peak_value:.6f}")

# Analytical formula
analytical_peak = (t_rise_frames * t_off_frames *
                  np.log(t_off_frames / t_rise_frames) /
                  (t_off_frames - t_rise_frames))
print(f"\nAnalytical formula:")
print(f"  Peak at: {analytical_peak:.4f} frames")
print(f"  Peak time: {analytical_peak / 20.0:.4f} s")

print(f"\nDifference:")
print(f"  Empirical - Analytical: {peak_idx - analytical_peak:.4f} frames")
print(f"  Current code uses: analytical - 1 = {analytical_peak - 1:.4f} frames")
print(f"  Should use: {peak_idx} frames (empirical)")

print(f"\nRecommendation:")
print(f"  Use offset of {peak_idx} frames for perfect alignment")
print("=" * 80)
