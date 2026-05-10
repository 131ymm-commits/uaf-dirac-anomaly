#!/usr/bin/env python3
"""
Emulation Results Report - Detailed Metrics
"""

import numpy as np
import json
from datetime import datetime
from uaf_dirac_agent import UAFDiracAgent


class ResultsReporter:
    def __init__(self):
        self.timestamp = datetime.now().isoformat()
        self.results = {}
    
    def calculate_metrics(self, y_true, y_pred, threshold=0.5):
        """Calculate precision, recall, F1"""
        y_pred_binary = (y_pred > threshold).astype(int)
        
        tp = np.sum((y_pred_binary == 1) & (y_true == 1))
        fp = np.sum((y_pred_binary == 1) & (y_true == 0))
        fn = np.sum((y_pred_binary == 0) & (y_true == 1))
        tn = np.sum((y_pred_binary == 0) & (y_true == 0))
        
        precision = tp / (tp + fp + 1e-9)
        recall = tp / (tp + fn + 1e-9)
        f1 = 2 * (precision * recall) / (precision + recall + 1e-9)
        
        return {
            'tp': int(tp),
            'fp': int(fp),
            'fn': int(fn),
            'tn': int(tn),
            'precision': float(precision),
            'recall': float(recall),
            'f1': float(f1),
            'accuracy': float((tp + tn) / (tp + tn + fp + fn + 1e-9))
        }
    
    def report_scenario_1(self, signal, labels, events, agent):
        """Report Scenario 1 results"""
        print("\n" + "="*80)
        print("[SCENARIO 1 RESULTS] Synthetic Anomalies")
        print("="*80)
        
        # Create score array
        scores = np.zeros(len(signal))
        for event in events:
            idx = event['index']
            if 0 <= idx < len(scores):
                scores[idx] = event['score']
        
        # Calculate metrics
        metrics = self.calculate_metrics(labels, scores)
        
        print(f"\n📊 Data Summary:")
        print(f"   Total points: {len(signal)}")
        print(f"   Ground truth anomalies: {np.sum(labels)}")
        print(f"   Detected events: {len(events)}")
        print(f"   Signal range: [{signal.min():.2f}, {signal.max():.2f}]")
        print(f"   Signal mean: {signal.mean():.2f}, std: {signal.std():.2f}")
        
        print(f"\n🎯 Performance Metrics:")
        print(f"   Precision: {metrics['precision']:.4f}")
        print(f"   Recall:    {metrics['recall']:.4f}")
        print(f"   F1-Score:  {metrics['f1']:.4f}")
        print(f"   Accuracy:  {metrics['accuracy']:.4f}")
        print(f"   TP: {metrics['tp']}, FP: {metrics['fp']}, FN: {metrics['fn']}, TN: {metrics['tn']}")
        
        if events:
            scores_arr = np.array([e['score'] for e in events])
            z_scores = np.array([e['z'] for e in events])
            print(f"\n📈 Event Statistics:")
            print(f"   Score range: [{scores_arr.min():.4f}, {scores_arr.max():.4f}]")
            print(f"   Mean score: {scores_arr.mean():.4f}")
            print(f"   Z-score range: [{z_scores.min():.2f}, {z_scores.max():.2f}]")
        
        self.results['scenario_1'] = {
            'type': 'synthetic_anomalies',
            'data_points': len(signal),
            'ground_truth': int(np.sum(labels)),
            'events_detected': len(events),
            'metrics': metrics
        }
        
        return metrics
    
    def report_scenario_2(self, signal, events, agent):
        """Report Scenario 2 results"""
        print("\n" + "="*80)
        print("[SCENARIO 2 RESULTS] NAB-like Data (Daily Pattern)")
        print("="*80)
        
        print(f"\n📊 Data Summary:")
        print(f"   Total points: {len(signal)}")
        print(f"   Detected events: {len(events)}")
        print(f"   Signal range: [{signal.min():.2f}, {signal.max():.2f}]")
        print(f"   Signal mean: {signal.mean():.2f}, std: {signal.std():.2f}")
        print(f"   Signal min index: {np.argmin(signal)}, max index: {np.argmax(signal)}")
        
        if events:
            event_indices = [e['index'] for e in events]
            scores = [e['score'] for e in events]
            z_scores = [e['z'] for e in events]
            
            print(f"\n📍 Detected Event Indices (first 20):")
            print(f"   {event_indices[:20]}")
            
            print(f"\n📈 Event Statistics:")
            print(f"   Score range: [{min(scores):.4f}, {max(scores):.4f}]")
            print(f"   Mean score: {np.mean(scores):.4f}")
            print(f"   Z-score range: [{min(z_scores):.2f}, {max(z_scores):.2f}]")
            
            print(f"\n🔍 Top 5 Events (by score):")
            top_events = sorted(events, key=lambda x: x['score'], reverse=True)[:5]
            for i, e in enumerate(top_events, 1):
                print(f"   {i}. Index {e['index']}: score={e['score']:.4f}, z={e['z']:.2f}, "
                      f"gap={e['gap_breach']:.4f}, inv={e['inversion']:.4f}")
        
        self.results['scenario_2'] = {
            'type': 'nab_like_daily',
            'data_points': len(signal),
            'events_detected': len(events),
            'event_indices': [e['index'] for e in events[:20]]
        }
    
    def report_summary(self):
        """Print final summary"""
        print("\n" + "="*80)
        print("[FINAL SUMMARY]")
        print("="*80)
        
        print(f"\n✅ Validation Timestamp: {self.timestamp}")
        print(f"\n📋 Scenario Summaries:")
        
        if 'scenario_1' in self.results:
            s1 = self.results['scenario_1']
            print(f"\n   Scenario 1 (Synthetic):")
            print(f"      Points: {s1['data_points']}, Ground truth: {s1['ground_truth']}")
            print(f"      Detected: {s1['events_detected']}, F1: {s1['metrics']['f1']:.4f}")
        
        if 'scenario_2' in self.results:
            s2 = self.results['scenario_2']
            print(f"\n   Scenario 2 (NAB-like):")
            print(f"      Points: {s2['data_points']}, Detected: {s2['events_detected']}")
        
        print("\n" + "="*80)
        
        return self.results


def main():
    from test_simulation import scenario_1_synthetic_anomalies, scenario_2_nab_like
    
    reporter = ResultsReporter()
    
    # Run scenarios
    signal1, labels1, events1, agent1 = scenario_1_synthetic_anomalies()
    reporter.report_scenario_1(signal1, labels1, events1, agent1)
    
    signal2, events2, agent2 = scenario_2_nab_like()
    reporter.report_scenario_2(signal2, events2, agent2)
    
    # Final summary
    results = reporter.report_summary()
    
    # Save to JSON
    with open('results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Results saved to results.json")


if __name__ == "__main__":
    main()
