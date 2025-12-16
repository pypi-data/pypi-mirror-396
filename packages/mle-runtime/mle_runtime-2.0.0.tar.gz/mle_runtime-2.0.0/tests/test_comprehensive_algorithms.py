#!/usr/bin/env python3
"""
Comprehensive Algorithm Testing Suite
Tests every ML and DL algorithm from linear regression to CNN
"""

import sys
import os
import time
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Tuple
import warnings
warnings.filterwarnings('ignore')

# Add mle_runtime to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import mle_runtime
    from mle_runtime import (
        load_model, export_model, benchmark_model,
        get_supported_operators, get_version_info
    )
    HAS_MLE_RUNTIME = True
except ImportError as e:
    print(f"❌ MLE Runtime not available: {e}")
    HAS_MLE_RUNTIME = False

# Import ML/DL libraries
ML_LIBRARIES = {}

try:
    import sklearn
    from sklearn.datasets import make_classification, make_regression, make_blobs
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import (
        LogisticRegression, LinearRegression, Ridge, Lasso, ElasticNet,
        SGDClassifier, SGDRegressor, Perceptron
    )
    from sklearn.ensemble import (
        RandomForestClassifier, RandomForestRegressor,
        GradientBoostingClassifier, GradientBoostingRegressor,
        AdaBoostClassifier, AdaBoostRegressor,
        ExtraTreesClassifier, ExtraTreesRegressor,
        BaggingClassifier, BaggingRegressor
    )
    from sklearn.svm import SVC, SVR, NuSVC, NuSVR, LinearSVC, LinearSVR
    from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB
    from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
    from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
    from sklearn.decomposition import PCA, TruncatedSVD
    from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
    from sklearn.neural_network import MLPClassifier, MLPRegressor
    ML_LIBRARIES['sklearn'] = True
except ImportError:
    ML_LIBRARIES['sklearn'] = False

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    ML_LIBRARIES['pytorch'] = True
except ImportError:
    ML_LIBRARIES['pytorch'] = False

try:
    import tensorflow as tf
    from tensorflow import keras
    ML_LIBRARIES['tensorflow'] = True
except ImportError:
    ML_LIBRARIES['tensorflow'] = False

try:
    import xgboost as xgb
    ML_LIBRARIES['xgboost'] = True
except ImportError:
    ML_LIBRARIES['xgboost'] = False

try:
    import lightgbm as lgb
    ML_LIBRARIES['lightgbm'] = True
except ImportError:
    ML_LIBRARIES['lightgbm'] = False

try:
    import catboost as cb
    ML_LIBRARIES['catboost'] = True
except ImportError:
    ML_LIBRARIES['catboost'] = False

class ComprehensiveAlgorithmTester:
    """Test every ML and DL algorithm from linear regression to CNN"""
    
    def __init__(self):
        self.results = []
        self.test_data = {}
        self.models = {}
        self.export_results = {}
        
    def generate_datasets(self):
        """Generate comprehensive test datasets"""
        print("📊 Generating comprehensive test datasets...")
        
        # Classification datasets
        X_cls_small, y_cls_small = make_classification(
            n_samples=1000, n_features=20, n_classes=3, 
            n_informative=15, random_state=42
        ) if ML_LIBRARIES['sklearn'] else (np.random.randn(1000, 20), np.random.randint(0, 3, 1000))
        
        X_cls_large, y_cls_large = make_classification(
            n_samples=10000, n_features=100, n_classes=10,
            n_informative=80, random_state=42
        ) if ML_LIBRARIES['sklearn'] else (np.random.randn(10000, 100), np.random.randint(0, 10, 10000))
        
        # Regression datasets
        X_reg_small, y_reg_small = make_regression(
            n_samples=1000, n_features=20, noise=0.1, random_state=42
        ) if ML_LIBRARIES['sklearn'] else (np.random.randn(1000, 20), np.random.randn(1000))
        
        X_reg_large, y_reg_large = make_regression(
            n_samples=10000, n_features=100, noise=0.1, random_state=42
        ) if ML_LIBRARIES['sklearn'] else (np.random.randn(10000, 100), np.random.randn(10000))
        
        # Clustering datasets
        X_cluster, _ = make_blobs(
            n_samples=2000, centers=5, n_features=10, random_state=42
        ) if ML_LIBRARIES['sklearn'] else (np.random.randn(2000, 10), None)
        
        # Image-like data for CNN
        X_image = np.random.randn(1000, 32, 32, 3).astype(np.float32)
        y_image = np.random.randint(0, 10, 1000)
        
        # Sequence data for RNN/LSTM
        X_sequence = np.random.randn(1000, 50, 100).astype(np.float32)
        y_sequence = np.random.randint(0, 5, 1000)
        
        # Text-like data
        X_text = np.random.randint(0, 10000, (1000, 200))  # Token IDs
        y_text = np.random.randint(0, 2, 1000)  # Binary classification
        
        self.test_data = {
            'classification_small': (X_cls_small.astype(np.float32), y_cls_small),
            'classification_large': (X_cls_large.astype(np.float32), y_cls_large),
            'regression_small': (X_reg_small.astype(np.float32), y_reg_small.astype(np.float32)),
            'regression_large': (X_reg_large.astype(np.float32), y_reg_large.astype(np.float32)),
            'clustering': (X_cluster.astype(np.float32), None),
            'image': (X_image, y_image),
            'sequence': (X_sequence, y_sequence),
            'text': (X_text, y_text)
        }
        
        print(f"✅ Generated {len(self.test_data)} comprehensive datasets")
    
    def test_sklearn_algorithms(self):
        """Test all scikit-learn algorithms"""
        if not ML_LIBRARIES['sklearn']:
            print("⚠️  Scikit-learn not available, skipping sklearn tests")
            return {}
        
        print("🔬 Testing Scikit-learn Algorithms...")
        
        X_cls, y_cls = self.test_data['classification_small']
        X_reg, y_reg = self.test_data['regression_small']
        X_cluster, _ = self.test_data['clustering']
        
        # Split data
        X_cls_train, X_cls_test, y_cls_train, y_cls_test = train_test_split(
            X_cls, y_cls, test_size=0.2, random_state=42
        )
        X_reg_train, X_reg_test, y_reg_train, y_reg_test = train_test_split(
            X_reg, y_reg, test_size=0.2, random_state=42
        )
        
        sklearn_results = {}
        
        # Linear Models
        linear_models = [
            ('LogisticRegression', LogisticRegression(random_state=42, max_iter=1000)),
            ('LinearRegression', LinearRegression()),
            ('Ridge', Ridge(random_state=42)),
            ('Lasso', Lasso(random_state=42)),
            ('ElasticNet', ElasticNet(random_state=42)),
            ('SGDClassifier', SGDClassifier(random_state=42, max_iter=1000)),
            ('SGDRegressor', SGDRegressor(random_state=42, max_iter=1000)),
            ('Perceptron', Perceptron(random_state=42, max_iter=1000))
        ]
        
        # Tree Models
        tree_models = [
            ('DecisionTreeClassifier', DecisionTreeClassifier(random_state=42)),
            ('DecisionTreeRegressor', DecisionTreeRegressor(random_state=42)),
            ('RandomForestClassifier', RandomForestClassifier(n_estimators=10, random_state=42)),
            ('RandomForestRegressor', RandomForestRegressor(n_estimators=10, random_state=42)),
            ('GradientBoostingClassifier', GradientBoostingClassifier(n_estimators=10, random_state=42)),
            ('GradientBoostingRegressor', GradientBoostingRegressor(n_estimators=10, random_state=42)),
            ('AdaBoostClassifier', AdaBoostClassifier(n_estimators=10, random_state=42)),
            ('AdaBoostRegressor', AdaBoostRegressor(n_estimators=10, random_state=42)),
            ('ExtraTreesClassifier', ExtraTreesClassifier(n_estimators=10, random_state=42)),
            ('ExtraTreesRegressor', ExtraTreesRegressor(n_estimators=10, random_state=42))
        ]
        
        # SVM Models
        svm_models = [
            ('SVC', SVC(random_state=42, probability=True)),
            ('SVR', SVR()),
            ('LinearSVC', LinearSVC(random_state=42, max_iter=1000)),
            ('LinearSVR', LinearSVR(random_state=42, max_iter=1000))
        ]
        
        # Other Models
        other_models = [
            ('GaussianNB', GaussianNB()),
            ('KNeighborsClassifier', KNeighborsClassifier(n_neighbors=5)),
            ('KNeighborsRegressor', KNeighborsRegressor(n_neighbors=5)),
            ('MLPClassifier', MLPClassifier(hidden_layer_sizes=(50,), max_iter=500, random_state=42)),
            ('MLPRegressor', MLPRegressor(hidden_layer_sizes=(50,), max_iter=500, random_state=42))
        ]
        
        # Clustering Models
        clustering_models = [
            ('KMeans', KMeans(n_clusters=5, random_state=42, n_init=10)),
            ('DBSCAN', DBSCAN(eps=0.5, min_samples=5)),
            ('AgglomerativeClustering', AgglomerativeClustering(n_clusters=5))
        ]
        
        # Decomposition Models
        decomposition_models = [
            ('PCA', PCA(n_components=10, random_state=42)),
            ('TruncatedSVD', TruncatedSVD(n_components=10, random_state=42))
        ]
        
        all_models = linear_models + tree_models + svm_models + other_models
        
        # Test classification and regression models
        for name, model in all_models:
            try:
                start_time = time.time()
                
                # Determine if it's a classifier or regressor
                if 'Classifier' in name or name in ['LogisticRegression', 'SVC', 'LinearSVC', 'GaussianNB', 'Perceptron']:
                    model.fit(X_cls_train, y_cls_train)
                    predictions = model.predict(X_cls_test)
                    test_data = X_cls_test
                    task_type = 'classification'
                elif 'Regressor' in name or name in ['LinearRegression', 'Ridge', 'Lasso', 'ElasticNet', 'SVR', 'LinearSVR']:
                    model.fit(X_reg_train, y_reg_train)
                    predictions = model.predict(X_reg_test)
                    test_data = X_reg_test
                    task_type = 'regression'
                else:
                    continue
                
                train_time = time.time() - start_time
                
                # Test export
                export_start = time.time()
                export_path = f"temp_{name.lower()}.mle"
                
                if HAS_MLE_RUNTIME:
                    try:
                        export_info = export_model(model, export_path, input_shape=test_data.shape)
                        export_success = True
                        export_time = time.time() - export_start
                    except Exception as e:
                        export_success = False
                        export_time = 0
                        export_info = {'error': str(e)}
                else:
                    export_success = False
                    export_time = 0
                    export_info = {'error': 'MLE Runtime not available'}
                
                sklearn_results[name] = {
                    'algorithm_type': 'sklearn',
                    'task_type': task_type,
                    'train_time_ms': train_time * 1000,
                    'export_success': export_success,
                    'export_time_ms': export_time * 1000,
                    'export_info': export_info,
                    'model_params': len(str(model.get_params())),
                    'test_samples': len(test_data),
                    'features': test_data.shape[1] if len(test_data.shape) > 1 else 1
                }
                
                print(f"  ✅ {name}: Train={train_time*1000:.1f}ms, Export={'✅' if export_success else '❌'}")
                
            except Exception as e:
                sklearn_results[name] = {
                    'algorithm_type': 'sklearn',
                    'task_type': 'unknown',
                    'train_time_ms': 0,
                    'export_success': False,
                    'export_time_ms': 0,
                    'export_info': {'error': str(e)},
                    'error': str(e)
                }
                print(f"  ❌ {name}: {str(e)}")
        
        # Test clustering models
        for name, model in clustering_models:
            try:
                start_time = time.time()
                
                if hasattr(model, 'fit_predict'):
                    labels = model.fit_predict(X_cluster)
                else:
                    model.fit(X_cluster)
                    labels = model.labels_ if hasattr(model, 'labels_') else None
                
                train_time = time.time() - start_time
                
                sklearn_results[name] = {
                    'algorithm_type': 'sklearn',
                    'task_type': 'clustering',
                    'train_time_ms': train_time * 1000,
                    'export_success': False,  # Clustering models not yet supported for export
                    'export_time_ms': 0,
                    'export_info': {'note': 'Clustering export not implemented'},
                    'n_clusters': getattr(model, 'n_clusters', 'auto'),
                    'test_samples': len(X_cluster)
                }
                
                print(f"  ✅ {name}: Train={train_time*1000:.1f}ms")
                
            except Exception as e:
                sklearn_results[name] = {
                    'algorithm_type': 'sklearn',
                    'task_type': 'clustering',
                    'error': str(e)
                }
                print(f"  ❌ {name}: {str(e)}")
        
        # Test decomposition models
        for name, model in decomposition_models:
            try:
                start_time = time.time()
                model.fit(X_cls)
                transformed = model.transform(X_cls)
                train_time = time.time() - start_time
                
                sklearn_results[name] = {
                    'algorithm_type': 'sklearn',
                    'task_type': 'decomposition',
                    'train_time_ms': train_time * 1000,
                    'export_success': False,  # Decomposition models not yet supported
                    'export_time_ms': 0,
                    'export_info': {'note': 'Decomposition export not implemented'},
                    'n_components': model.n_components,
                    'test_samples': len(X_cls)
                }
                
                print(f"  ✅ {name}: Train={train_time*1000:.1f}ms")
                
            except Exception as e:
                sklearn_results[name] = {
                    'algorithm_type': 'sklearn',
                    'task_type': 'decomposition',
                    'error': str(e)
                }
                print(f"  ❌ {name}: {str(e)}")
        
        print(f"✅ Tested {len(sklearn_results)} scikit-learn algorithms")
        return sklearn_results
    
    def test_pytorch_algorithms(self):
        """Test PyTorch neural network algorithms"""
        if not ML_LIBRARIES['pytorch']:
            print("⚠️  PyTorch not available, skipping PyTorch tests")
            return {}
        
        print("🔥 Testing PyTorch Algorithms...")
        
        pytorch_results = {}
        
        # Simple MLP
        class SimpleMLP(nn.Module):
            def __init__(self, input_size, hidden_size, num_classes):
                super(SimpleMLP, self).__init__()
                self.fc1 = nn.Linear(input_size, hidden_size)
                self.relu = nn.ReLU()
                self.fc2 = nn.Linear(hidden_size, num_classes)
                
            def forward(self, x):
                x = self.fc1(x)
                x = self.relu(x)
                x = self.fc2(x)
                return x
        
        # CNN for image classification
        class SimpleCNN(nn.Module):
            def __init__(self, num_classes=10):
                super(SimpleCNN, self).__init__()
                self.conv1 = nn.Conv2d(3, 32, 3, padding=1)
                self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
                self.pool = nn.MaxPool2d(2, 2)
                self.fc1 = nn.Linear(64 * 8 * 8, 128)
                self.fc2 = nn.Linear(128, num_classes)
                self.relu = nn.ReLU()
                
            def forward(self, x):
                x = self.pool(self.relu(self.conv1(x)))
                x = self.pool(self.relu(self.conv2(x)))
                x = x.view(-1, 64 * 8 * 8)
                x = self.relu(self.fc1(x))
                x = self.fc2(x)
                return x
        
        # LSTM for sequence data
        class SimpleLSTM(nn.Module):
            def __init__(self, input_size, hidden_size, num_layers, num_classes):
                super(SimpleLSTM, self).__init__()
                self.hidden_size = hidden_size
                self.num_layers = num_layers
                self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
                self.fc = nn.Linear(hidden_size, num_classes)
                
            def forward(self, x):
                h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
                c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
                out, _ = self.lstm(x, (h0, c0))
                out = self.fc(out[:, -1, :])
                return out
        
        # Transformer-like attention
        class SimpleAttention(nn.Module):
            def __init__(self, embed_dim, num_heads):
                super(SimpleAttention, self).__init__()
                # Ensure embed_dim is divisible by num_heads
                self.embed_dim = embed_dim
                self.num_heads = min(num_heads, embed_dim)  # Ensure divisibility
                if self.embed_dim % self.num_heads != 0:
                    self.num_heads = 1  # Fallback to single head
                self.attention = nn.MultiheadAttention(self.embed_dim, self.num_heads, batch_first=True)
                self.norm = nn.LayerNorm(self.embed_dim)
                self.fc = nn.Linear(self.embed_dim, 10)
                
            def forward(self, x):
                attn_out, _ = self.attention(x, x, x)
                x = self.norm(x + attn_out)
                x = x.mean(dim=1)  # Global average pooling
                x = self.fc(x)
                return x
        
        pytorch_models = [
            ('SimpleMLP', SimpleMLP(20, 64, 3), 'classification_small'),
            ('SimpleCNN', SimpleCNN(10), 'image'),
            ('SimpleLSTM', SimpleLSTM(100, 64, 2, 5), 'sequence'),
            ('SimpleAttention', SimpleAttention(100, 4), 'sequence')  # 100 is divisible by 4
        ]
        
        for name, model, data_key in pytorch_models:
            try:
                start_time = time.time()
                
                # Get appropriate data
                X, y = self.test_data[data_key]
                
                # Convert to tensors
                if data_key == 'image':
                    X_tensor = torch.FloatTensor(X).permute(0, 3, 1, 2)  # NHWC to NCHW
                else:
                    X_tensor = torch.FloatTensor(X)
                
                # Simple forward pass (no training for speed)
                model.eval()
                with torch.no_grad():
                    output = model(X_tensor[:32])  # Use small batch for speed
                
                inference_time = time.time() - start_time
                
                # Test export
                export_start = time.time()
                export_path = f"temp_{name.lower()}.mle"
                
                if HAS_MLE_RUNTIME:
                    try:
                        export_info = export_model(model, export_path, input_shape=X_tensor[:1].shape)
                        export_success = True
                        export_time = time.time() - export_start
                    except Exception as e:
                        export_success = False
                        export_time = 0
                        export_info = {'error': str(e)}
                else:
                    export_success = False
                    export_time = 0
                    export_info = {'error': 'MLE Runtime not available'}
                
                pytorch_results[name] = {
                    'algorithm_type': 'pytorch',
                    'task_type': 'neural_network',
                    'inference_time_ms': inference_time * 1000,
                    'export_success': export_success,
                    'export_time_ms': export_time * 1000,
                    'export_info': export_info,
                    'model_params': sum(p.numel() for p in model.parameters()),
                    'test_samples': 32,
                    'data_type': data_key
                }
                
                print(f"  ✅ {name}: Inference={inference_time*1000:.1f}ms, Export={'✅' if export_success else '❌'}")
                
            except Exception as e:
                pytorch_results[name] = {
                    'algorithm_type': 'pytorch',
                    'task_type': 'neural_network',
                    'error': str(e)
                }
                print(f"  ❌ {name}: {str(e)}")
        
        print(f"✅ Tested {len(pytorch_results)} PyTorch algorithms")
        return pytorch_results
    
    def test_tensorflow_algorithms(self):
        """Test TensorFlow/Keras algorithms"""
        if not ML_LIBRARIES['tensorflow']:
            print("⚠️  TensorFlow not available, skipping TensorFlow tests")
            return {}
        
        print("🧠 Testing TensorFlow/Keras Algorithms...")
        
        tensorflow_results = {}
        
        # Simple Dense Network
        def create_dense_model():
            model = keras.Sequential([
                keras.layers.Dense(64, activation='relu', input_shape=(20,)),
                keras.layers.Dense(32, activation='relu'),
                keras.layers.Dense(3, activation='softmax')
            ])
            return model
        
        # CNN Model
        def create_cnn_model():
            model = keras.Sequential([
                keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(32, 32, 3)),
                keras.layers.MaxPooling2D((2, 2)),
                keras.layers.Conv2D(64, (3, 3), activation='relu'),
                keras.layers.MaxPooling2D((2, 2)),
                keras.layers.Flatten(),
                keras.layers.Dense(128, activation='relu'),
                keras.layers.Dense(10, activation='softmax')
            ])
            return model
        
        # LSTM Model
        def create_lstm_model():
            model = keras.Sequential([
                keras.layers.LSTM(64, input_shape=(50, 100)),
                keras.layers.Dense(32, activation='relu'),
                keras.layers.Dense(5, activation='softmax')
            ])
            return model
        
        tensorflow_models = [
            ('DenseNetwork', create_dense_model, 'classification_small'),
            ('CNN', create_cnn_model, 'image'),
            ('LSTM', create_lstm_model, 'sequence')
        ]
        
        for name, model_fn, data_key in tensorflow_models:
            try:
                start_time = time.time()
                
                model = model_fn()
                model.compile(optimizer='adam', loss='sparse_categorical_crossentropy')
                
                # Get appropriate data
                X, y = self.test_data[data_key]
                
                # Simple prediction (no training for speed)
                predictions = model.predict(X[:32], verbose=0)
                
                inference_time = time.time() - start_time
                
                # Test export
                export_start = time.time()
                export_path = f"temp_{name.lower()}.mle"
                
                if HAS_MLE_RUNTIME:
                    try:
                        export_info = export_model(model, export_path, input_shape=X[:1].shape)
                        export_success = True
                        export_time = time.time() - export_start
                    except Exception as e:
                        export_success = False
                        export_time = 0
                        export_info = {'error': str(e)}
                else:
                    export_success = False
                    export_time = 0
                    export_info = {'error': 'MLE Runtime not available'}
                
                tensorflow_results[name] = {
                    'algorithm_type': 'tensorflow',
                    'task_type': 'neural_network',
                    'inference_time_ms': inference_time * 1000,
                    'export_success': export_success,
                    'export_time_ms': export_time * 1000,
                    'export_info': export_info,
                    'model_params': model.count_params(),
                    'test_samples': 32,
                    'data_type': data_key
                }
                
                print(f"  ✅ {name}: Inference={inference_time*1000:.1f}ms, Export={'✅' if export_success else '❌'}")
                
            except Exception as e:
                tensorflow_results[name] = {
                    'algorithm_type': 'tensorflow',
                    'task_type': 'neural_network',
                    'error': str(e)
                }
                print(f"  ❌ {name}: {str(e)}")
        
        print(f"✅ Tested {len(tensorflow_results)} TensorFlow algorithms")
        return tensorflow_results
    
    def test_gradient_boosting_algorithms(self):
        """Test gradient boosting frameworks (XGBoost, LightGBM, CatBoost)"""
        print("🌳 Testing Gradient Boosting Algorithms...")
        
        gb_results = {}
        X_cls, y_cls = self.test_data['classification_small']
        X_reg, y_reg = self.test_data['regression_small']
        
        # XGBoost
        if ML_LIBRARIES['xgboost']:
            xgb_models = [
                ('XGBClassifier', xgb.XGBClassifier(n_estimators=10, random_state=42), X_cls, y_cls, 'classification'),
                ('XGBRegressor', xgb.XGBRegressor(n_estimators=10, random_state=42), X_reg, y_reg, 'regression')
            ]
            
            for name, model, X, y, task in xgb_models:
                try:
                    start_time = time.time()
                    model.fit(X, y)
                    predictions = model.predict(X[:100])
                    train_time = time.time() - start_time
                    
                    # Test export
                    export_start = time.time()
                    export_path = f"temp_{name.lower()}.mle"
                    
                    if HAS_MLE_RUNTIME:
                        try:
                            export_info = export_model(model, export_path, input_shape=X[:1].shape)
                            export_success = True
                            export_time = time.time() - export_start
                        except Exception as e:
                            export_success = False
                            export_time = 0
                            export_info = {'error': str(e)}
                    else:
                        export_success = False
                        export_time = 0
                        export_info = {'error': 'MLE Runtime not available'}
                    
                    gb_results[name] = {
                        'algorithm_type': 'xgboost',
                        'task_type': task,
                        'train_time_ms': train_time * 1000,
                        'export_success': export_success,
                        'export_time_ms': export_time * 1000,
                        'export_info': export_info,
                        'n_estimators': model.n_estimators,
                        'test_samples': 100
                    }
                    
                    print(f"  ✅ {name}: Train={train_time*1000:.1f}ms, Export={'✅' if export_success else '❌'}")
                    
                except Exception as e:
                    gb_results[name] = {
                        'algorithm_type': 'xgboost',
                        'task_type': task,
                        'error': str(e)
                    }
                    print(f"  ❌ {name}: {str(e)}")
        
        # LightGBM
        if ML_LIBRARIES['lightgbm']:
            lgb_models = [
                ('LGBMClassifier', lgb.LGBMClassifier(n_estimators=10, random_state=42, verbose=-1), X_cls, y_cls, 'classification'),
                ('LGBMRegressor', lgb.LGBMRegressor(n_estimators=10, random_state=42, verbose=-1), X_reg, y_reg, 'regression')
            ]
            
            for name, model, X, y, task in lgb_models:
                try:
                    start_time = time.time()
                    model.fit(X, y)
                    predictions = model.predict(X[:100])
                    train_time = time.time() - start_time
                    
                    # Test export
                    export_start = time.time()
                    export_path = f"temp_{name.lower()}.mle"
                    
                    if HAS_MLE_RUNTIME:
                        try:
                            export_info = export_model(model, export_path, input_shape=X[:1].shape)
                            export_success = True
                            export_time = time.time() - export_start
                        except Exception as e:
                            export_success = False
                            export_time = 0
                            export_info = {'error': str(e)}
                    else:
                        export_success = False
                        export_time = 0
                        export_info = {'error': 'MLE Runtime not available'}
                    
                    gb_results[name] = {
                        'algorithm_type': 'lightgbm',
                        'task_type': task,
                        'train_time_ms': train_time * 1000,
                        'export_success': export_success,
                        'export_time_ms': export_time * 1000,
                        'export_info': export_info,
                        'n_estimators': model.n_estimators,
                        'test_samples': 100
                    }
                    
                    print(f"  ✅ {name}: Train={train_time*1000:.1f}ms, Export={'✅' if export_success else '❌'}")
                    
                except Exception as e:
                    gb_results[name] = {
                        'algorithm_type': 'lightgbm',
                        'task_type': task,
                        'error': str(e)
                    }
                    print(f"  ❌ {name}: {str(e)}")
        
        # CatBoost
        if ML_LIBRARIES['catboost']:
            cb_models = [
                ('CatBoostClassifier', cb.CatBoostClassifier(iterations=10, random_state=42, verbose=False), X_cls, y_cls, 'classification'),
                ('CatBoostRegressor', cb.CatBoostRegressor(iterations=10, random_state=42, verbose=False), X_reg, y_reg, 'regression')
            ]
            
            for name, model, X, y, task in cb_models:
                try:
                    start_time = time.time()
                    model.fit(X, y)
                    predictions = model.predict(X[:100])
                    train_time = time.time() - start_time
                    
                    # Test export
                    export_start = time.time()
                    export_path = f"temp_{name.lower()}.mle"
                    
                    if HAS_MLE_RUNTIME:
                        try:
                            export_info = export_model(model, export_path, input_shape=X[:1].shape)
                            export_success = True
                            export_time = time.time() - export_start
                        except Exception as e:
                            export_success = False
                            export_time = 0
                            export_info = {'error': str(e)}
                    else:
                        export_success = False
                        export_time = 0
                        export_info = {'error': 'MLE Runtime not available'}
                    
                    gb_results[name] = {
                        'algorithm_type': 'catboost',
                        'task_type': task,
                        'train_time_ms': train_time * 1000,
                        'export_success': export_success,
                        'export_time_ms': export_time * 1000,
                        'export_info': export_info,
                        'iterations': model.get_param('iterations'),
                        'test_samples': 100
                    }
                    
                    print(f"  ✅ {name}: Train={train_time*1000:.1f}ms, Export={'✅' if export_success else '❌'}")
                    
                except Exception as e:
                    gb_results[name] = {
                        'algorithm_type': 'catboost',
                        'task_type': task,
                        'error': str(e)
                    }
                    print(f"  ❌ {name}: {str(e)}")
        
        print(f"✅ Tested {len(gb_results)} gradient boosting algorithms")
        return gb_results
    
    def run_comprehensive_test(self):
        """Run comprehensive test of all algorithms"""
        print("🚀 Starting Comprehensive Algorithm Testing Suite")
        print("=" * 60)
        
        # Check available libraries
        print("📋 Available ML/DL Libraries:")
        for lib, available in ML_LIBRARIES.items():
            status = "✅" if available else "❌"
            print(f"  {status} {lib}")
        print()
        
        # Generate datasets
        self.generate_datasets()
        print()
        
        # Test all frameworks
        all_results = {}
        
        # Scikit-learn
        sklearn_results = self.test_sklearn_algorithms()
        all_results.update(sklearn_results)
        print()
        
        # PyTorch
        pytorch_results = self.test_pytorch_algorithms()
        all_results.update(pytorch_results)
        print()
        
        # TensorFlow
        tensorflow_results = self.test_tensorflow_algorithms()
        all_results.update(tensorflow_results)
        print()
        
        # Gradient Boosting
        gb_results = self.test_gradient_boosting_algorithms()
        all_results.update(gb_results)
        print()
        
        # Generate summary
        self.generate_comprehensive_report(all_results)
        
        return all_results
    
    def generate_comprehensive_report(self, results):
        """Generate comprehensive test report"""
        print("📊 Generating Comprehensive Test Report...")
        
        # Summary statistics
        total_algorithms = len(results)
        successful_tests = sum(1 for r in results.values() if 'error' not in r)
        successful_exports = sum(1 for r in results.values() if r.get('export_success', False))
        
        # Framework breakdown
        framework_stats = {}
        for name, result in results.items():
            framework = result.get('algorithm_type', 'unknown')
            if framework not in framework_stats:
                framework_stats[framework] = {'total': 0, 'successful': 0, 'exported': 0}
            
            framework_stats[framework]['total'] += 1
            if 'error' not in result:
                framework_stats[framework]['successful'] += 1
            if result.get('export_success', False):
                framework_stats[framework]['exported'] += 1
        
        # Task type breakdown
        task_stats = {}
        for name, result in results.items():
            task = result.get('task_type', 'unknown')
            if task not in task_stats:
                task_stats[task] = {'total': 0, 'successful': 0}
            
            task_stats[task]['total'] += 1
            if 'error' not in result:
                task_stats[task]['successful'] += 1
        
        # Performance statistics
        train_times = [r.get('train_time_ms', 0) for r in results.values() if 'train_time_ms' in r and r['train_time_ms'] > 0]
        export_times = [r.get('export_time_ms', 0) for r in results.values() if 'export_time_ms' in r and r['export_time_ms'] > 0]
        
        # Create comprehensive report
        report = {
            'test_summary': {
                'total_algorithms_tested': total_algorithms,
                'successful_tests': successful_tests,
                'successful_exports': successful_exports,
                'success_rate': successful_tests / total_algorithms if total_algorithms > 0 else 0,
                'export_rate': successful_exports / total_algorithms if total_algorithms > 0 else 0,
                'test_timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            },
            'framework_breakdown': framework_stats,
            'task_breakdown': task_stats,
            'performance_stats': {
                'avg_train_time_ms': np.mean(train_times) if train_times else 0,
                'avg_export_time_ms': np.mean(export_times) if export_times else 0,
                'fastest_train_ms': np.min(train_times) if train_times else 0,
                'slowest_train_ms': np.max(train_times) if train_times else 0
            },
            'library_availability': ML_LIBRARIES,
            'mle_runtime_available': HAS_MLE_RUNTIME,
            'detailed_results': results
        }
        
        # Save report
        report_path = 'comprehensive_algorithm_test_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Print summary
        print("=" * 60)
        print("🎯 COMPREHENSIVE ALGORITHM TEST SUMMARY")
        print("=" * 60)
        print(f"📊 Total Algorithms Tested: {total_algorithms}")
        print(f"✅ Successful Tests: {successful_tests} ({successful_tests/total_algorithms*100:.1f}%)")
        print(f"📦 Successful Exports: {successful_exports} ({successful_exports/total_algorithms*100:.1f}%)")
        print()
        
        print("📋 Framework Breakdown:")
        for framework, stats in framework_stats.items():
            print(f"  {framework}: {stats['successful']}/{stats['total']} tests, {stats['exported']} exports")
        print()
        
        print("🎯 Task Type Breakdown:")
        for task, stats in task_stats.items():
            print(f"  {task}: {stats['successful']}/{stats['total']} successful")
        print()
        
        if train_times:
            print(f"⚡ Performance:")
            print(f"  Average train time: {np.mean(train_times):.1f}ms")
            print(f"  Fastest algorithm: {np.min(train_times):.1f}ms")
            print(f"  Slowest algorithm: {np.max(train_times):.1f}ms")
        
        print(f"\n📄 Detailed report saved to: {report_path}")
        print("=" * 60)

def main():
    """Main test execution"""
    tester = ComprehensiveAlgorithmTester()
    results = tester.run_comprehensive_test()
    return results

if __name__ == "__main__":
    main()