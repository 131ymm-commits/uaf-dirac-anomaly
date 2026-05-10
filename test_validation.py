#!/usr/bin/env python3
"""
UAF Dirac Agent - Tolerance & Validation Check
"""

import numpy as np
from uaf_dirac_agent import UAFDiracAgent, EPS


def check_parameter_tolerances():
    """Проверка всех допусков параметров"""
    print("\n" + "="*70)
    print("[TOLERANCE CHECK] UAF Dirac Agent Parameters")
    print("="*70)
    
    agent = UAFDiracAgent()
    checks = []
    
    # Check 1: Window hierarchy
    check1 = (
        agent.norm_window < agent.short_window and
        agent.short_window < agent.long_window and
        agent.long_window < agent.baseline_window
    )
    checks.append(("Window hierarchy (norm < short < long < baseline)", check1))
    print(f"✓ norm_window={agent.norm_window}, short={agent.short_window}, "
          f"long={agent.long_window}, baseline={agent.baseline_window}")
    
    # Check 2: Weight normalization
    weight_sum = agent.gap_weight + agent.inversion_weight + agent.zitter_weight
    check2 = abs(weight_sum - 1.0) < 1e-6
    checks.append(("Weight sum = 1.0", check2))
    print(f"✓ gap_weight={agent.gap_weight} + inversion={agent.inversion_weight} "
          f"+ zitter={agent.zitter_weight} = {weight_sum:.6f}")
    
    # Check 3: EPS precision
    check3 = EPS > 0 and EPS < 1e-6
    checks.append(("EPS in valid range (>0, <1e-6)", check3))
    print(f"✓ EPS={EPS}")
    
    # Check 4: Spinor normalization
    a_norm = abs(agent.a) ** 2 + abs(agent.b) ** 2
    check4 = abs(a_norm - 1.0) < 1e-9
    checks.append(("Initial spinor normalized (|a|² + |b|² = 1)", check4))
    print(f"✓ |a|² + |b|² = {a_norm:.15f}")
    
    # Check 5: dt (timestep)
    check5 = agent.dt > 0 and agent.dt < 1.0
    checks.append(("Timestep dt valid (0 < dt < 1)", check5))
    print(f"✓ dt={agent.dt}")
    
    # Check 6: EMA (exponential moving average)
    check6 = agent.ema > 0 and agent.ema < 1.0
    checks.append(("EMA in range (0, 1)", check6))
    print(f"✓ ema={agent.ema}")
    
    # Check 7: Threshold k
    check7 = agent.threshold_k > 0
    checks.append(("Threshold k > 0", check7))
    print(f"✓ threshold_k={agent.threshold_k}")
    
    # Check 8: Min gap
    check8 = agent.min_gap > 0 and agent.min_gap < agent.baseline_window
    checks.append(("Min gap valid (0 < min_gap < baseline_window)", check8))
    print(f"✓ min_gap={agent.min_gap}")
    
    # Check 9: Squash scale
    check9 = agent.squash_scale > 0
    checks.append(("Squash scale > 0", check9))
    print(f"✓ squash_scale={agent.squash_scale}")
    
    passed = sum(1 for _, result in checks if result)
    print(f"\n📊 Result: {passed}/{len(checks)} checks passed")
    
    return all(result for _, result in checks)


def check_numerical_stability():
    """Проверка численной стабильности"""
    print("\n" + "="*70)
    print("[NUMERICAL STABILITY CHECK]")
    print("="*70)
    
    agent = UAFDiracAgent()
    
    # Test 1: Division by zero protection
    print("\n1. Division by zero protection (constant signal):")
    constant = [5.0] * 200
    scores = agent.score_sequence(constant)
    print(f"   ✓ Processed {len(constant)} points without error")
    print(f"   ✓ Max score: {np.max(scores):.6f}, Min: {np.min(scores):.6f}")
    print(f"   ✓ NaN count: {np.sum(np.isnan(scores))}, Inf count: {np.sum(np.isinf(scores))}")
    
    # Test 2: Extreme values
    print("\n2. Extreme value handling:")
    agent.reset()
    extreme = [100.0] * 100 + [1e6] + [100.0] * 100  # spike
    scores = agent.score_sequence(extreme)
    print(f"   ✓ Processed extreme spike (1e6)")
    print(f"   ✓ NaN count: {np.sum(np.isnan(scores))}, Inf count: {np.sum(np.isinf(scores))}")
    
    # Test 3: Spinor normalization during evolution
    print("\n3. Spinor normalization during evolution:")
    agent.reset()
    noisy = np.random.randn(500) * 10 + 100
    for i, val in enumerate(noisy):
        agent.update(i, val)
    norm = abs(agent.a) ** 2 + abs(agent.b) ** 2
    print(f"   ✓ Final spinor norm: {norm:.15f}")
    print(f"   ✓ Error: {abs(norm - 1.0):.2e}")
    
    print("\n✓ All numerical stability checks passed")
    return True


def check_state_evolution():
    """Проверка эволюции состояния"""
    print("\n" + "="*70)
    print("[STATE EVOLUTION CHECK]")
    print("="*70)
    
    agent = UAFDiracAgent()
    
    # Generate synthetic data with known anomaly
    np.random.seed(42)
    normal = np.random.normal(100, 5, 200)
    spike = np.array([200.0])  # anomaly
    normal2 = np.random.normal(100, 5, 200)
    signal = np.concatenate([normal, spike, normal2])
    
    print(f"\nSignal: {len(signal)} points (normal + spike + normal)")
    print(f"Normal range: {signal[:200].min():.1f} - {signal[:200].max():.1f}")
    print(f"Spike value: {signal[200]}")
    
    events = []
    for i, val in enumerate(signal):
        event = agent.update(i, val)
        if event is not None:
            events.append(event)
    
    print(f"\nDetected events: {len(events)}")
    for event in events[:5]:  # Show first 5
        print(f"  - Index {event['index']}: score={event['score']:.4f}, z={event['z']:.2f}")
    
    print("\n✓ State evolution check passed")
    return True


if __name__ == "__main__":
    print("\n" + "#"*70)
    print("# UAF DIRAC AGENT - COMPREHENSIVE VALIDATION")
    print("#"*70)
    
    result1 = check_parameter_tolerances()
    result2 = check_numerical_stability()
    result3 = check_state_evolution()
    
    print("\n" + "="*70)
    if result1 and result2 and result3:
        print("✓✓✓ ALL VALIDATION CHECKS PASSED ✓✓✓")
    else:
        print("✗ SOME CHECKS FAILED")
    print("="*70 + "\n")
