# UAF Dirac Agent - Online Anomaly Detector

Sophisticated quantum-inspired anomaly detection system based on 2-component Dirac dynamics.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Example

```python
from uaf_dirac_agent import UAFDiracAgent
import numpy as np

# Initialize detector
agent = UAFDiracAgent()

# Process streaming data
for timestamp, value in enumerate(data):
    event = agent.update(timestamp, value)
    if event is not None:
        print(f"Anomaly detected at {timestamp}: score={event['score']:.4f}")
```

### Batch Scoring

```python
# Process entire sequence
scores = agent.score_sequence(data)
```

## Parameters

- `norm_window` (50): Normalization window size
- `short_window` (20): Short-term analysis window
- `long_window` (60): Long-term analysis window  
- `baseline_window` (120): Baseline for z-score calculation
- `dt` (0.060): Spinor evolution timestep
- `ema` (0.10): Exponential moving average coefficient
- `threshold_k` (3.0): Z-score threshold for anomaly
- `min_gap` (30): Minimum points between events
- `gap_weight` (0.25): Weight for mass-gap breach score
- `inversion_weight` (0.35): Weight for spinor inversion score
- `zitter_weight` (0.40): Weight for energy zitter score
- `squash_scale` (3.0): Exponential squashing scale

## Validation

Run validation tests:

```bash
python test_validation.py
```

This checks:
- Parameter tolerances
- Numerical stability
- State evolution

## Simulation

Run full simulation with 3 scenarios:

```bash
python test_simulation.py
```

Scenarios:
1. Synthetic anomalies (spike, regime shift, volatility)
2. NAB-like data (daily pattern, point/collective anomalies)
3. Edge cases (constant, extreme range, high frequency, long sequences)

## Physics Background

The detector implements UAF (Unified Anomaly Framework) translation of 2-component Dirac dynamics:

**Hamiltonian**: H = p·σₓ + κ·σᵧ + m·σᵤ

Where:
- **mass (m)**: Structural inertia from regime history
- **momentum (p)**: Present flow pressure
- **curvature (κ)**: Local reorientation signal
- **spinor polarization**: Structure vs motion dominance
- **anomaly score**: Combination of gap breach, inversion, and energy zitter

## Event Output

When an anomaly is detected, `update()` returns:

```python
{
    'timestamp': <int>,
    'index': <int>,
    'score': <float>,  # Final anomaly score [0,1]
    'raw_score': <float>,  # Pre-normalized score
    'z': <float>,  # Z-score vs baseline
    'gap_breach': <float>,  # Mass-gap deviation
    'inversion': <float>,  # Spinor inversion
    'zitter': <float>,  # Energy jump
    'polarization': <float>,  # |a|² - |b|²
    'momentum': <float>,  # Pressure term
    'curvature': <float>,  # Local reorientation
    'mass': <float>,  # Regime mass term
    'gamma_short': <float>,  # Short-term entropy
    'gamma_long': <float>,  # Long-term entropy
    'energy': <float>,  # Total energy
}
```

## Performance

Typical performance on 10,000 point sequences:
- **Speed**: ~5,000-10,000 points/sec
- **Memory**: <1 MB per 10k points
- **False positive rate**: Tunable via threshold_k

## References

- Quantum anomaly detection inspired by Dirac equation
- Spinor normalization ensures numerical stability
- EMA smoothing adapts to regime changes
- Z-score thresholding provides statistical calibration
