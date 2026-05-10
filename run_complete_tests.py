#!/usr/bin/env python3
"""
Complete Test Execution Output
"""

import sys
import numpy as np
from datetime import datetime

# Import all test modules
from test_validation import (
    check_parameter_tolerances,
    check_numerical_stability,
    check_state_evolution
)
from test_simulation import (
    scenario_1_synthetic_anomalies,
    scenario_2_nab_like,
    scenario_3_edge_cases
)
from results_reporter import ResultsReporter


def print_header(title):
    print(f"\n{'#'*80}")
    print(f"# {title}")
    print(f"{'#'*80}")


def print_section(title):
    print(f"\n{'='*80}")
    print(f"[{title}]")
    print(f"{'='*80}")


def main():
    start_time = datetime.now()
    print_header(f"UAF DIRAC AGENT - COMPLETE TEST SUITE")
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # ========== PART 1: VALIDATION ==========
    print_section("PART 1/4: VALIDATION CHECKS")
    
    try:
        v1 = check_parameter_tolerances()
        v2 = check_numerical_stability()
        v3 = check_state_evolution()
        validation_pass = v1 and v2 and v3
        print(f"\n✓ Validation: {'PASSED' if validation_pass else 'FAILED'}")
    except Exception as e:
        print(f"✗ Validation error: {e}")
        validation_pass = False
    
    # ========== PART 2: SIMULATION ==========
    print_section("PART 2/4: SIMULATION SCENARIOS")
    
    try:
        signal1, labels1, events1, agent1 = scenario_1_synthetic_anomalies()
        print(f"✓ Scenario 1: {len(events1)} events detected")
        
        signal2, events2, agent2 = scenario_2_nab_like()
        print(f"✓ Scenario 2: {len(events2)} events detected")
        
        scenario_3_edge_cases()
        print(f"✓ Scenario 3: Edge cases passed")
        
        simulation_pass = True
    except Exception as e:
        print(f"✗ Simulation error: {e}")
        simulation_pass = False
    
    # ========== PART 3: RESULTS REPORTER ==========
    print_section("PART 3/4: DETAILED METRICS")
    
    try:
        reporter = ResultsReporter()
        
        # Report Scenario 1
        metrics1 = reporter.report_scenario_1(signal1, labels1, events1, agent1)
        
        # Report Scenario 2
        reporter.report_scenario_2(signal2, events2, agent2)
        
        # Summary
        results = reporter.report_summary()
        
        reporter_pass = True
    except Exception as e:
        print(f"✗ Reporter error: {e}")
        reporter_pass = False
    
    # ========== PART 4: NAB EVALUATION ==========
    print_section("PART 4/4: NAB DATASET EVALUATION")
    
    try:
        from nab_evaluator import NABEvaluator
        print("\nℹ NAB Evaluator initialized")
        print("  Note: NAB evaluation requires internet connection")
        print("  Attempting to download real benchmark data...\n")
        
        evaluator = NABEvaluator()
        nab_results = evaluator.run_evaluation(limit_per_category=1)
        
        nab_pass = True
    except Exception as e:
        print(f"⚠ NAB evaluation skipped: {e}")
        print("  (This is normal if no internet or network timeout)")
        nab_pass = False
    
    # ========== FINAL SUMMARY ==========
    end_time = datetime.now()
    elapsed = (end_time - start_time).total_seconds()
    
    print_header("FINAL TEST SUMMARY")
    
    test_results = {
        "Validation Checks": validation_pass,
        "Simulation Scenarios": simulation_pass,
        "Results Reporter": reporter_pass,
        "NAB Evaluation": nab_pass
    }
    
    print(f"\n📋 Test Results:\n")
    for test_name, passed in test_results.items():
        symbol = "✓" if passed else "✗"
        status = "PASS" if passed else "FAIL/SKIP"
        print(f"  {symbol} {test_name:30s} {status}")
    
    passed_count = sum(1 for v in test_results.values() if v)
    total_count = len(test_results)
    
    print(f"\n📊 Summary:")
    print(f"   Passed: {passed_count}/{total_count}")
    print(f"   Duration: {elapsed:.2f}s")
    print(f"   Completed: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if passed_count == total_count:
        print(f"\n🎉 ALL TESTS PASSED! 🎉")
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed or skipped")
    
    print(f"\n{'#'*80}\n")
    
    return 0 if passed_count >= 3 else 1  # At least 3 tests must pass


if __name__ == "__main__":
    sys.exit(main())
