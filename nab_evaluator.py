#!/usr/bin/env python3
"""
NAB (Numenta Anomaly Benchmark) Integration
Download and evaluate on real NAB data
"""

import os
import csv
import json
import numpy as np
from datetime import datetime
from urllib.request import urlopen
import urllib.error
from uaf_dirac_agent import UAFDiracAgent


class NABEvaluator:
    """Evaluate UAF Dirac Agent on NAB datasets"""
    
    # NAB data URLs (GitHub raw content)
    NAB_BASE = "https://raw.githubusercontent.com/numenta/NAB/master/data"
    
    DATASETS = {
        'realKnownCause': [
            'machine_temperature_system_failure.csv',
            'nyc_taxi.csv',
            'rogue_agent_market_close.csv',
        ],
        'realAWSCloudwatch': [
            'ec2_cpu_utilization_24ae8d.csv',
            'ec2_cpu_utilization_53ea38.csv',
        ],
        'realTraffic': [
            'occupancy_t4013.csv',
            'speed_7578.csv',
        ],
    }
    
    def __init__(self, cache_dir='nab_data'):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def download_csv(self, category, filename):
        """Download single CSV file from NAB"""
        url = f"{self.NAB_BASE}/{category}/{filename}"
        local_path = os.path.join(self.cache_dir, f"{category}_{filename}")
        
        if os.path.exists(local_path):
            print(f"   ✓ Using cached: {local_path}")
            return local_path
        
        try:
            print(f"   ⬇ Downloading: {url}")
            with urlopen(url, timeout=10) as response:
                with open(local_path, 'wb') as f:
                    f.write(response.read())
            print(f"   ✓ Saved: {local_path}")
            return local_path
        except urllib.error.URLError as e:
            print(f"   ✗ Failed: {e}")
            return None
    
    def load_nab_csv(self, filepath):
        """Load NAB CSV with timestamp, value, and anomaly label"""
        timestamps = []
        values = []
        labels = []  # 1 = anomaly, 0 = normal
        
        try:
            with open(filepath, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    timestamps.append(row.get('timestamp', ''))
                    try:
                        values.append(float(row.get('value', 0)))
                        # NAB uses 1 for anomaly windows, 0 for normal
                        anomaly_val = row.get('anomaly', 0)
                        labels.append(int(anomaly_val) if anomaly_val else 0)
                    except ValueError:
                        continue
        except Exception as e:
            print(f"   Error reading {filepath}: {e}")
            return None, None, None
        
        return np.array(timestamps), np.array(values), np.array(labels)
    
    def calculate_metrics(self, y_true, scores, threshold=0.5):
        """Calculate anomaly detection metrics"""
        y_pred = (scores > threshold).astype(int)
        
        tp = np.sum((y_pred == 1) & (y_true == 1))
        fp = np.sum((y_pred == 1) & (y_true == 0))
        fn = np.sum((y_pred == 0) & (y_true == 1))
        tn = np.sum((y_pred == 0) & (y_true == 0))
        
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
    
    def evaluate_file(self, filepath, filename):
        """Evaluate on single file"""
        print(f"\n📊 Evaluating: {filename}")
        
        timestamps, values, labels = self.load_nab_csv(filepath)
        if values is None or len(values) == 0:
            print(f"   ✗ No data loaded")
            return None
        
        print(f"   Data: {len(values)} points, {np.sum(labels)} anomalies")
        print(f"   Range: [{values.min():.2f}, {values.max():.2f}]")
        
        # Run detector
        agent = UAFDiracAgent()
        scores = np.zeros(len(values))
        events = []
        
        for i, val in enumerate(values):
            event = agent.update(i, val)
            if event is not None:
                scores[i] = event['score']
                events.append(event)
        
        # Calculate metrics
        metrics = self.calculate_metrics(labels, scores)
        
        print(f"   ✓ F1={metrics['f1']:.4f}, Precision={metrics['precision']:.4f}, "
              f"Recall={metrics['recall']:.4f}")
        print(f"   Events detected: {len(events)}, Ground truth: {np.sum(labels)}")
        
        return {
            'filename': filename,
            'points': len(values),
            'anomalies': int(np.sum(labels)),
            'events_detected': len(events),
            'metrics': metrics,
            'data_range': (float(values.min()), float(values.max())),
            'data_mean': float(values.mean()),
            'data_std': float(values.std()),
        }
    
    def run_evaluation(self, limit_per_category=2):
        """Run full evaluation on available NAB datasets"""
        print("\n" + "="*80)
        print("[NAB EVALUATION] UAF Dirac Agent on Real Anomaly Data")
        print("="*80)
        
        results = {}
        
        for category, files in self.DATASETS.items():
            print(f"\n📁 Category: {category}")
            results[category] = []
            
            for filename in files[:limit_per_category]:
                filepath = self.download_csv(category, filename)
                if filepath and os.path.exists(filepath):
                    result = self.evaluate_file(filepath, filename)
                    if result:
                        results[category].append(result)
        
        return self.report_results(results)
    
    def report_results(self, results):
        """Generate summary report"""
        print("\n" + "="*80)
        print("[NAB EVALUATION SUMMARY]")
        print("="*80)
        
        all_f1 = []
        all_precision = []
        all_recall = []
        
        for category, dataset_results in results.items():
            if not dataset_results:
                continue
            
            print(f"\n📊 {category}:")
            category_f1 = []
            
            for result in dataset_results:
                f1 = result['metrics']['f1']
                precision = result['metrics']['precision']
                recall = result['metrics']['recall']
                
                print(f"   {result['filename']:40s} F1={f1:.4f} P={precision:.4f} R={recall:.4f}")
                
                category_f1.append(f1)
                all_f1.append(f1)
                all_precision.append(precision)
                all_recall.append(recall)
            
            if category_f1:
                print(f"   {'Category Average':40s} F1={np.mean(category_f1):.4f}")
        
        if all_f1:
            print(f"\n🎯 Overall Metrics:")
            print(f"   Mean F1-Score:  {np.mean(all_f1):.4f}")
            print(f"   Mean Precision: {np.mean(all_precision):.4f}")
            print(f"   Mean Recall:    {np.mean(all_recall):.4f}")
            print(f"   Datasets evaluated: {len(all_f1)}")
        
        print("\n" + "="*80)
        
        return results


def main():
    evaluator = NABEvaluator()
    results = evaluator.run_evaluation(limit_per_category=2)
    
    # Save results
    with open('nab_results.json', 'w') as f:
        # Convert numpy types for JSON serialization
        json_results = json.dumps(results, default=str, indent=2)
        f.write(json_results)
    print(f"\n💾 NAB results saved to nab_results.json")


if __name__ == "__main__":
    main()
