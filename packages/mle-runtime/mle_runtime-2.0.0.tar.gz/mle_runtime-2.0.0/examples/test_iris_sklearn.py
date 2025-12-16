#!/usr/bin/env python3
"""
Iris Dataset Test - Train, Export, and Test with MLE Runtime

This example demonstrates:
1. Training a scikit-learn MLPClassifier on Iris dataset
2. Exporting to .mle format
3. Loading and running inference with MLE Runtime
4. Comparing accuracy with original sklearn model
"""

import sys
import os
import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, classification_report
import time

# Add bindings to path for direct testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'bindings', 'python'))

def main():
    print("="*70)
    print("Iris Dataset Classification - MLE Runtime Test")
    print("="*70)
    
    # Step 1: Load Iris dataset
    print("\n[Step 1] Loading Iris dataset...")
    iris = load_iris()
    X, y = iris.data, iris.target
    
    # Split into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    
    print(f"  Training samples: {len(X_train)}")
    print(f"  Test samples: {len(X_test)}")
    print(f"  Features: {X.shape[1]}")
    print(f"  Classes: {len(np.unique(y))}")
    
    # Step 2: Train MLPClassifier
    print("\n[Step 2] Training MLPClassifier...")
    start_time = time.perf_counter()
    
    model = MLPClassifier(
        hidden_layer_sizes=(16, 8),
        activation='relu',
        max_iter=1000,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    train_time = (time.perf_counter() - start_time) * 1000
    print(f"  Training time: {train_time:.2f} ms")
    
    # Step 3: Test with sklearn
    print("\n[Step 3] Testing with sklearn...")
    start_time = time.perf_counter()
    sklearn_predictions = model.predict(X_test)
    sklearn_inference_time = (time.perf_counter() - start_time) * 1000
    
    sklearn_accuracy = accuracy_score(y_test, sklearn_predictions)
    print(f"  Sklearn accuracy: {sklearn_accuracy:.4f}")
    print(f"  Sklearn inference time: {sklearn_inference_time:.2f} ms")
    
    # Step 4: Export to MLE format
    print("\n[Step 4] Exporting to MLE format...")
    
    # Import exporter
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools', 'exporter'))
    from sklearn_to_mle import SklearnMLEExporter
    
    exporter = SklearnMLEExporter()
    mle_path = 'iris_model.mle'
    
    start_time = time.perf_counter()
    exporter.export_sklearn(model, mle_path, input_shape=(1, 4), model_name='IrisClassifier')
    export_time = (time.perf_counter() - start_time) * 1000
    
    print(f"  Export time: {export_time:.2f} ms")
    print(f"  Model saved to: {mle_path}")
    
    # Step 5: Load with MLE Runtime
    print("\n[Step 5] Loading with MLE Runtime...")
    import mle_runtime
    
    engine = mle_runtime.Engine(mle_runtime.Device.CPU)
    
    start_time = time.perf_counter()
    engine.load_model(mle_path)
    load_time = (time.perf_counter() - start_time) * 1000
    
    print(f"  Load time: {load_time:.2f} ms")
    
    # Step 6: Run inference with MLE Runtime
    print("\n[Step 6] Running inference with MLE Runtime...")
    
    # Run inference on each test sample
    mle_predictions = []
    start_time = time.perf_counter()
    
    for i in range(len(X_test)):
        # Prepare input
        input_data = X_test[i:i+1].astype(np.float32)
        
        # Run inference
        outputs = engine.run([input_data])
        
        # Get prediction (argmax of output)
        prediction = np.argmax(outputs[0])
        mle_predictions.append(prediction)
    
    mle_inference_time = (time.perf_counter() - start_time) * 1000
    mle_predictions = np.array(mle_predictions)
    
    # Step 7: Compare results
    print("\n[Step 7] Comparing results...")
    
    mle_accuracy = accuracy_score(y_test, mle_predictions)
    print(f"  MLE Runtime accuracy: {mle_accuracy:.4f}")
    print(f"  MLE Runtime inference time: {mle_inference_time:.2f} ms")
    print(f"  Average time per sample: {mle_inference_time/len(X_test):.2f} ms")
    
    # Check if predictions match
    matches = np.sum(sklearn_predictions == mle_predictions)
    match_rate = matches / len(y_test)
    print(f"\n  Prediction match rate: {match_rate:.4f} ({matches}/{len(y_test)})")
    
    # Detailed classification report
    print("\n[Step 8] Classification Report (MLE Runtime):")
    print(classification_report(y_test, mle_predictions, target_names=iris.target_names))
    
    # Performance comparison
    print("\n" + "="*70)
    print("Performance Summary")
    print("="*70)
    print(f"{'Metric':<30} {'Sklearn':<15} {'MLE Runtime':<15} {'Speedup':<10}")
    print("-"*70)
    print(f"{'Accuracy':<30} {sklearn_accuracy:<15.4f} {mle_accuracy:<15.4f} {'-':<10}")
    print(f"{'Inference Time (ms)':<30} {sklearn_inference_time:<15.2f} {mle_inference_time:<15.2f} {sklearn_inference_time/mle_inference_time:<10.2f}x")
    print(f"{'Load Time (ms)':<30} {'-':<15} {load_time:<15.2f} {'-':<10}")
    print(f"{'Export Time (ms)':<30} {'-':<15} {export_time:<15.2f} {'-':<10}")
    print("="*70)
    
    # Verify accuracy
    if mle_accuracy >= 0.90:
        print("\n✓ SUCCESS: Model achieves >90% accuracy!")
    else:
        print(f"\n⚠ WARNING: Model accuracy is {mle_accuracy:.2%}, expected >90%")
    
    if match_rate >= 0.95:
        print("✓ SUCCESS: MLE Runtime predictions match sklearn (>95%)")
    else:
        print(f"⚠ WARNING: Prediction mismatch rate: {(1-match_rate)*100:.1f}%")
    
    # Cleanup
    try:
        if os.path.exists(mle_path):
            # Close any file handles
            import gc
            gc.collect()
            os.remove(mle_path)
            print(f"\n✓ Cleaned up: {mle_path}")
    except Exception as e:
        print(f"\n⚠ Could not remove {mle_path}: {e}")
    
    return 0 if (mle_accuracy >= 0.90 and match_rate >= 0.95) else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
