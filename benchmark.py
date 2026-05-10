#!/usr/bin/env python3
"""
Quick benchmark of all components
"""

import time
import numpy as np
from uaf_dirac_agent import UAFDiracAgent

print("\n" + "="*80)
print("[QUICK BENCHMARK] UAF Dirac Agent Performance")
print("="*80)

# Test 1: Small sequence
print("\n1️⃣  Small sequence (500 points):")
agent = UAFDiracAgent()
data = np.random.normal(100, 10, 500)
start = time.time()
for i, val in enumerate(data):
    agent.update(i, val)
elapsed = time.time() - start
print(f"   Time: {elapsed*1000:.2f}ms ({len(data)/elapsed:.0f} points/sec)")

# Test 2: Medium sequence
print("\n2️⃣  Medium sequence (5,000 points):")
agent = UAFDiracAgent()
data = np.random.normal(100, 10, 5000)
start = time.time()
for i, val in enumerate(data):
    agent.update(i, val)
elapsed = time.time() - start
print(f"   Time: {elapsed*1000:.2f}ms ({len(data)/elapsed:.0f} points/sec)")

# Test 3: Large sequence
print("\n3️⃣  Large sequence (50,000 points):")
agent = UAFDiracAgent()
data = np.random.normal(100, 10, 50000)
start = time.time()
scores = agent.score_sequence(data)
elapsed = time.time() - start
print(f"   Time: {elapsed*1000:.2f}ms ({len(data)/elapsed:.0f} points/sec)")

# Test 4: Memory usage
print("\n4️⃣  Memory efficiency:")
data_size = len(agent.values) * 8  # bytes
print(f"   Raw values buffer: {data_size/1024:.2f} KB")
scores_size = len(agent.raw_scores) * 8
print(f"   Scores buffer: {scores_size/1024:.2f} KB")
print(f"   Total: {(data_size + scores_size)/1024:.2f} KB for {len(agent.values)} points")

print("\n" + "="*80 + "\n")
