#!/usr/bin/env python3
"""
Test Suite Runner - All Tests
"""

import subprocess
import sys


def run_command(cmd, description):
    """Run command and report results"""
    print(f"\n{'='*80}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*80}\n")
    
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def main():
    print("\n" + "#"*80)
    print("# UAF DIRAC AGENT - COMPLETE TEST SUITE")
    print("#"*80)
    
    tests = [
        ([sys.executable, 'test_validation.py'], 
         'Validation Checks (Tolerances, Stability, Evolution)'),
        
        ([sys.executable, 'test_simulation.py'],
         'Simulation Scenarios (Synthetic, NAB-like, Edge Cases)'),
        
        ([sys.executable, 'results_reporter.py'],
         'Results Reporter (Detailed Metrics)'),
        
        ([sys.executable, 'nab_evaluator.py'],
         'NAB Dataset Evaluation (Real Anomaly Data)'),
    ]
    
    results = {}
    for cmd, desc in tests:
        success = run_command(cmd, desc)
        results[desc] = 'PASS' if success else 'FAIL'
    
    # Summary
    print("\n" + "#"*80)
    print("# TEST SUITE SUMMARY")
    print("#"*80)
    
    for test_name, status in results.items():
        symbol = "✓" if status == "PASS" else "✗"
        print(f"{symbol} {test_name}: {status}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v == "PASS")
    print(f"\nTotal: {passed}/{total} tests passed")
    print("#"*80 + "\n")


if __name__ == "__main__":
    main()
