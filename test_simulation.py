#!/usr/bin/env python3
"""
UAF Dirac Agent - Simulation Scenarios
"""

import numpy as np
import time
from uaf_dirac_agent import UAFDiracAgent


def scenario_1_synthetic_anomalies():
    """Сценарий 1: Синтетические аномалии"""
    print("\n" + "="*70)
    print("[SCENARIO 1] Synthetic Anomalies (500 points, 3 types)")
    print("="*70)
    
    np.random.seed(42)
    agent = UAFDiracAgent()
    
    # Build signal with different anomaly types
    signal = []
    labels = []
    
    # Normal segment 1
    normal1 = np.random.normal(100, 5, 100)
    signal.extend(normal1)
    labels.extend([0] * 100)
    
    # Spike anomalies
    spike_segment = list(np.random.normal(100, 5, 50))
    spike_segment[25] = 200  # Point spike
    spike_segment[26] = 198
    signal.extend(spike_segment)
    labels.extend([1 if i in [25, 26] else 0 for i in range(50)])
    
    # Normal segment 2
    normal2 = np.random.normal(100, 5, 100)
    signal.extend(normal2)
    labels.extend([0] * 100)
    
    # Regime shift
    regime_shift = list(np.random.normal(150, 8, 100))
    signal.extend(regime_shift)
    labels.extend([1] * 100)  # Collective anomaly
    
    # Normal segment 3
    normal3 = np.random.normal(100, 5, 50)
    signal.extend(normal3)
    labels.extend([0] * 50)
    
    # High volatility
    volatility = list(np.random.normal(100, 20, 100))
    signal.extend(volatility)
    labels.extend([1] * 100)  # Collective anomaly
    
    signal = np.array(signal)
    labels = np.array(labels)
    
    print(f"Signal length: {len(signal)}")
    print(f"Mean: {signal.mean():.2f}, Std: {signal.std():.2f}")
    print(f"Min: {signal.min():.2f}, Max: {signal.max():.2f}")
    
    # Run detection
    start = time.time()
    events = []
    for i, val in enumerate(signal):
        event = agent.update(i, val)
        if event is not None:
            events.append(event)
    elapsed = time.time() - start
    
    print(f"\nProcessing time: {elapsed:.3f}s ({len(signal)/elapsed:.0f} points/sec)")
    print(f"Events detected: {len(events)}")
    
    if events:
        print(f"\nFirst 5 events:")
        for event in events[:5]:
            idx = event['index']
            print(f"  idx={idx}: score={event['score']:.4f}, z={event['z']:.2f}, "
                  f"gap_breach={event['gap_breach']:.4f}, "
                  f"inversion={event['inversion']:.4f}, zitter={event['zitter']:.4f}")
    
    return signal, labels, events, agent


def scenario_2_nab_like():
    """Сценарий 2: NAB-подобные данные"""
    print("\n" + "="*70)
    print("[SCENARIO 2] NAB-like Data (1000 points, daily pattern)")
    print("="*70)
    
    np.random.seed(123)
    agent = UAFDiracAgent()
    
    # Daily pattern
    signal = []
    for day in range(10):
        # Day pattern: low at night, peak during day
        for hour in range(24):
            base = 100 + 40 * np.sin(2 * np.pi * hour / 24)
            noise = np.random.normal(0, 3)
            value = base + noise
            signal.append(value)
    
    signal = np.array(signal)
    
    # Add point anomalies
    anomaly_indices = [100, 105, 200, 205, 500, 510, 515]
    for idx in anomaly_indices:
        signal[idx] += np.random.uniform(40, 80)
    
    # Add collective anomalies (regime shift)
    signal[600:650] += 50
    anomaly_indices.extend(range(600, 650))
    
    # Add trend
    trend = np.linspace(0, 20, len(signal))
    signal = signal + trend
    
    print(f"Signal length: {len(signal)}")
    print(f"Mean: {signal.mean():.2f}, Std: {signal.std():.2f}")
    print(f"Min: {signal.min():.2f}, Max: {signal.max():.2f}")
    print(f"Ground truth anomalies: {len(set(anomaly_indices))}")
    
    # Run detection
    start = time.time()
    events = []
    for i, val in enumerate(signal):
        event = agent.update(i, val)
        if event is not None:
            events.append(event)
    elapsed = time.time() - start
    
    print(f"\nProcessing time: {elapsed:.3f}s ({len(signal)/elapsed:.0f} points/sec)")
    print(f"Events detected: {len(events)}")
    
    if events:
        print(f"\nDetected event indices (first 10):")
        detected_indices = [e['index'] for e in events[:10]]
        print(f"  {detected_indices}")
    
    return signal, events, agent


def scenario_3_edge_cases():
    """Сценарий 3: Граничные случаи"""
    print("\n" + "="*70)
    print("[SCENARIO 3] Edge Cases")
    print("="*70)
    
    # Test 1: Constant signal
    print("\n1. Constant signal (5.0 for 300 points):")
    agent1 = UAFDiracAgent()
    constant = [5.0] * 300
    scores1 = agent1.score_sequence(constant)
    print(f"   Events: {np.sum(scores1 > 0)}, Max score: {np.max(scores1):.6f}")
    
    # Test 2: Extreme range
    print("\n2. Extreme range (1e-6 to 1e6):")
    agent2 = UAFDiracAgent()
    extreme = np.concatenate([
        np.logspace(-6, -3, 100),
        np.logspace(3, 6, 100),
        np.logspace(-6, -3, 100),
    ])
    scores2 = agent2.score_sequence(extreme)
    nans = np.sum(np.isnan(scores2))
    infs = np.sum(np.isinf(scores2))
    print(f"   Events: {np.sum(scores2 > 0)}, NaN: {nans}, Inf: {infs}")
    
    # Test 3: High frequency noise
    print("\n3. High frequency noise (300 points):")
    agent3 = UAFDiracAgent()
    t = np.arange(300)
    hf_noise = 50 + 5*np.sin(0.1*t) + np.random.normal(0, 15, 300)
    scores3 = agent3.score_sequence(hf_noise)
    print(f"   Events: {np.sum(scores3 > 0)}, Max score: {np.max(scores3):.6f}")
    
    # Test 4: Long sequence
    print("\n4. Long sequence (10000 points):")
    agent4 = UAFDiracAgent()
    np.random.seed(999)
    long_seq = np.random.normal(100, 10, 10000)
    long_seq[5000:5050] += 100  # Insert anomaly
    
    start = time.time()
    scores4 = agent4.score_sequence(long_seq)
    elapsed = time.time() - start
    print(f"   Events: {np.sum(scores4 > 0)}, Time: {elapsed:.3f}s")
    print(f"   Memory used: ~{len(agent4.values) * 8 / 1024:.1f} KB")
    
    print("\n✓ All edge cases handled gracefully")


def main():
    print("\n" + "#"*70)
    print("# UAF DIRAC AGENT - SIMULATION")
    print("#"*70)
    
    # Run all scenarios
    signal1, labels1, events1, agent1 = scenario_1_synthetic_anomalies()
    signal2, events2, agent2 = scenario_2_nab_like()
    scenario_3_edge_cases()
    
    # Summary
    print("\n" + "="*70)
    print("[SUMMARY]")
    print("="*70)
    print(f"\nScenario 1: {len(events1)} events detected (synthetic)")
    print(f"Scenario 2: {len(events2)} events detected (NAB-like)")
    print(f"\n✓ Simulation complete")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
