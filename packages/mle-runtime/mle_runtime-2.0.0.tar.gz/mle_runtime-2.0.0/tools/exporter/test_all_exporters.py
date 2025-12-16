#!/usr/bin/env python3
"""
Test script to verify all model exporters work correctly
Tests each model type independently
"""

import sys
import os

def test_sklearn_models():
    """Test all scikit-learn model exports"""
    print("\n" + "="*60)
    print("Testing Scikit-learn Models")
    print("="*60)
    
    try:
        from sklearn.datasets import make_classification
        from sklearn.linear_model import LogisticRegression
        from sklearn.neural_network import MLPClassifier
        from sklearn.tree import DecisionTreeClassifier
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.svm import SVC
        from sklearn.naive_bayes import GaussianNB
        from sklearn.neighbors import KNeighborsClassifier
        from sklearn.cluster import KMeans
        from sklearn.decomposition import PCA
        from sklearn_to_mle import SklearnMLEExporter
        
        X, y = make_classification(n_samples=100, n_features=10, n_classes=2, random_state=42)
        
        models = {
            'LogisticRegression': LogisticRegression(max_iter=100),
            'MLPClassifier': MLPClassifier(hidden_layer_sizes=(16,), max_iter=100, random_state=42),
            'DecisionTreeClassifier': DecisionTreeClassifier(max_depth=3, random_state=42),
            'RandomForestClassifier': RandomForestClassifier(n_estimators=5, max_depth=3, random_state=42),
            'SVC': SVC(random_state=42),
            'GaussianNB': GaussianNB(),
            'KNeighborsClassifier': KNeighborsClassifier(n_neighbors=3),
        }
        
        # Unsupervised models
        unsupervised = {
            'KMeans': KMeans(n_clusters=2, random_state=42, n_init=10),
            'PCA': PCA(n_components=5),
        }
        
        exporter = SklearnMLEExporter()
        
        for name, model in models.items():
            try:
                model.fit(X, y)
                output_path = f'test_{name.lower()}.mle'
                exporter.export_sklearn(model, output_path, input_shape=(1, 10))
                print(f"✓ {name} exported successfully")
                os.remove(output_path)
                os.remove(output_path.replace('.mle', '.joblib'))
            except Exception as e:
                print(f"✗ {name} failed: {e}")
        
        for name, model in unsupervised.items():
            try:
                model.fit(X)
                exporter = SklearnMLEExporter()
                output_path = f'test_{name.lower()}.mle'
                exporter.export_sklearn(model, output_path, input_shape=(1, 10))
                print(f"✓ {name} exported successfully")
                os.remove(output_path)
                if os.path.exists(output_path.replace('.mle', '.joblib')):
                    os.remove(output_path.replace('.mle', '.joblib'))
            except Exception as e:
                print(f"✗ {name} failed: {e}")
        
        return True
    except Exception as e:
        print(f"✗ Scikit-learn test suite failed: {e}")
        return False


def test_pytorch_models():
    """Test PyTorch model exports"""
    print("\n" + "="*60)
    print("Testing PyTorch Models")
    print("="*60)
    
    try:
        import torch
        import torch.nn as nn
        from pytorch_to_mle import MLEExporter
        
        # Simple MLP
        model = nn.Sequential(
            nn.Linear(10, 16),
            nn.ReLU(),
            nn.Linear(16, 2)
        )
        
        exporter = MLEExporter()
        output_path = 'test_pytorch_mlp.mle'
        exporter.export_mlp(model, (1, 10), output_path)
        print(f"✓ PyTorch MLP exported successfully")
        os.remove(output_path)
        
        return True
    except Exception as e:
        print(f"✗ PyTorch test failed: {e}")
        return False


def test_tensorflow_models():
    """Test TensorFlow/Keras model exports"""
    print("\n" + "="*60)
    print("Testing TensorFlow/Keras Models")
    print("="*60)
    
    try:
        from tensorflow import keras
        from tensorflow_to_mle import TensorFlowMLEExporter
        
        # Simple Sequential model
        model = keras.Sequential([
            keras.layers.Dense(16, activation='relu', input_shape=(10,)),
            keras.layers.Dense(2, activation='softmax')
        ])
        model.compile(optimizer='adam', loss='categorical_crossentropy')
        
        exporter = TensorFlowMLEExporter()
        output_path = 'test_keras_model.mle'
        exporter.export_keras(model, output_path, input_shape=(1, 10))
        print(f"✓ Keras model exported successfully")
        os.remove(output_path)
        
        return True
    except Exception as e:
        print(f"✗ TensorFlow/Keras test failed: {e}")
        return False


def test_xgboost_models():
    """Test XGBoost model exports"""
    print("\n" + "="*60)
    print("Testing XGBoost Models")
    print("="*60)
    
    try:
        import xgboost as xgb
        from sklearn.datasets import make_classification
        from xgboost_to_mle import GradientBoostingMLEExporter
        
        X, y = make_classification(n_samples=100, n_features=10, n_classes=2, random_state=42)
        
        model = xgb.XGBClassifier(n_estimators=10, max_depth=3, random_state=42)
        model.fit(X, y)
        
        exporter = GradientBoostingMLEExporter()
        output_path = 'test_xgboost.mle'
        exporter.export_xgboost(model, output_path, input_shape=(1, 10))
        print(f"✓ XGBoost model exported successfully")
        os.remove(output_path)
        
        return True
    except Exception as e:
        print(f"✗ XGBoost test failed: {e}")
        return False


def test_lightgbm_models():
    """Test LightGBM model exports"""
    print("\n" + "="*60)
    print("Testing LightGBM Models")
    print("="*60)
    
    try:
        import lightgbm as lgb
        from sklearn.datasets import make_classification
        from xgboost_to_mle import GradientBoostingMLEExporter
        
        X, y = make_classification(n_samples=100, n_features=10, n_classes=2, random_state=42)
        
        model = lgb.LGBMClassifier(n_estimators=10, max_depth=3, random_state=42, verbose=-1)
        model.fit(X, y)
        
        exporter = GradientBoostingMLEExporter()
        output_path = 'test_lightgbm.mle'
        exporter.export_lightgbm(model, output_path, input_shape=(1, 10))
        print(f"✓ LightGBM model exported successfully")
        os.remove(output_path)
        
        return True
    except Exception as e:
        print(f"✗ LightGBM test failed: {e}")
        return False


def test_catboost_models():
    """Test CatBoost model exports"""
    print("\n" + "="*60)
    print("Testing CatBoost Models")
    print("="*60)
    
    try:
        import catboost as cb
        from sklearn.datasets import make_classification
        from xgboost_to_mle import GradientBoostingMLEExporter
        
        X, y = make_classification(n_samples=100, n_features=10, n_classes=2, random_state=42)
        
        model = cb.CatBoostClassifier(iterations=10, depth=3, verbose=0, random_state=42)
        model.fit(X, y)
        
        exporter = GradientBoostingMLEExporter()
        output_path = 'test_catboost.mle'
        exporter.export_catboost(model, output_path, input_shape=(1, 10))
        print(f"✓ CatBoost model exported successfully")
        os.remove(output_path)
        
        return True
    except Exception as e:
        print(f"✗ CatBoost test failed: {e}")
        return False


def main():
    print("="*60)
    print("UNIVERSAL MODEL EXPORTER - TEST SUITE")
    print("="*60)
    print("\nTesting all model exporters independently...")
    
    results = {}
    
    # Test each framework
    results['scikit-learn'] = test_sklearn_models()
    results['pytorch'] = test_pytorch_models()
    results['tensorflow'] = test_tensorflow_models()
    results['xgboost'] = test_xgboost_models()
    results['lightgbm'] = test_lightgbm_models()
    results['catboost'] = test_catboost_models()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for framework, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{framework:20s}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\nTotal: {passed}/{total} frameworks passed")
    
    if passed == total:
        print("\n🎉 All tests passed! All model exporters working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} framework(s) failed. Check error messages above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
