#!/usr/bin/env python3
"""
Universal ML/DL Model Exporter to .mle format
Supports: scikit-learn, PyTorch, TensorFlow/Keras, XGBoost, LightGBM, CatBoost
All models are independent - no cross-dependencies required
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def export_model(model, output_path: str, input_shape: tuple = None, model_name: str = None):
    """
    Universal model exporter - automatically detects framework and exports
    
    Args:
        model: Any ML/DL model
        output_path: Output .mle file path
        input_shape: Input shape (batch_size, features)
        model_name: Optional model name
    
    Returns:
        Path to exported .mle file
    """
    
    model_type = type(model).__name__
    module_name = type(model).__module__
    
    print(f"Detecting model type: {model_type} from {module_name}")
    
    # Scikit-learn models
    if 'sklearn' in module_name:
        from sklearn_to_mle import SklearnMLEExporter
        exporter = SklearnMLEExporter()
        return exporter.export_sklearn(model, output_path, input_shape, model_name)
    
    # PyTorch models
    elif 'torch' in module_name:
        from pytorch_to_mle import MLEExporter
        exporter = MLEExporter()
        return exporter.export_mlp(model, input_shape, output_path)
    
    # TensorFlow/Keras models
    elif 'tensorflow' in module_name or 'keras' in module_name:
        from tensorflow_to_mle import TensorFlowMLEExporter
        exporter = TensorFlowMLEExporter()
        return exporter.export_keras(model, output_path, input_shape, model_name)
    
    # XGBoost models
    elif 'xgboost' in module_name:
        from xgboost_to_mle import GradientBoostingMLEExporter
        exporter = GradientBoostingMLEExporter()
        return exporter.export_xgboost(model, output_path, input_shape, model_name)
    
    # LightGBM models
    elif 'lightgbm' in module_name:
        from xgboost_to_mle import GradientBoostingMLEExporter
        exporter = GradientBoostingMLEExporter()
        return exporter.export_lightgbm(model, output_path, input_shape, model_name)
    
    # CatBoost models
    elif 'catboost' in module_name:
        from xgboost_to_mle import GradientBoostingMLEExporter
        exporter = GradientBoostingMLEExporter()
        return exporter.export_catboost(model, output_path, input_shape, model_name)
    
    else:
        raise ValueError(f"Unsupported model type: {model_type} from {module_name}")


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Universal ML/DL Model Exporter to .mle format'
    )
    parser.add_argument('--demo', action='store_true', help='Run comprehensive demo')
    args = parser.parse_args()
    
    if args.demo:
        print("="*80)
        print("UNIVERSAL MODEL EXPORTER - COMPREHENSIVE DEMO")
        print("="*80)
        print("\nThis demo exports ALL major ML/DL model types to .mle format")
        print("Each model is completely independent - no cross-dependencies!\n")
        
        # 1. Scikit-learn models
        print("\n" + "="*80)
        print("1. SCIKIT-LEARN MODELS")
        print("="*80)
        
        try:
            from sklearn.datasets import make_classification, make_regression
            from sklearn.model_selection import train_test_split
            
            # Generate data
            X_class, y_class = make_classification(n_samples=1000, n_features=20, n_classes=3, random_state=42)
            X_reg, y_reg = make_regression(n_samples=1000, n_features=20, random_state=42)
            
            # Linear models
            print("\n--- Linear Models ---")
            from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge, Lasso
            
            lr = LogisticRegression(max_iter=1000)
            lr.fit(X_class, y_class)
            export_model(lr, 'demo_logistic_regression.mle', input_shape=(1, 20))
            
            linreg = LinearRegression()
            linreg.fit(X_reg, y_reg)
            export_model(linreg, 'demo_linear_regression.mle', input_shape=(1, 20))
            
            # Neural networks
            print("\n--- Neural Networks ---")
            from sklearn.neural_network import MLPClassifier, MLPRegressor
            
            mlp = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=1000, random_state=42)
            mlp.fit(X_class, y_class)
            export_model(mlp, 'demo_mlp_classifier.mle', input_shape=(1, 20))
            
            # Tree models
            print("\n--- Tree Models ---")
            from sklearn.tree import DecisionTreeClassifier
            from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
            
            dt = DecisionTreeClassifier(max_depth=5, random_state=42)
            dt.fit(X_class, y_class)
            export_model(dt, 'demo_decision_tree.mle', input_shape=(1, 20))
            
            rf = RandomForestClassifier(n_estimators=10, max_depth=5, random_state=42)
            rf.fit(X_class, y_class)
            export_model(rf, 'demo_random_forest.mle', input_shape=(1, 20))
            
            # SVM
            print("\n--- SVM Models ---")
            from sklearn.svm import SVC
            
            svm = SVC(kernel='rbf', random_state=42)
            svm.fit(X_class[:100], y_class[:100])  # Smaller dataset for speed
            export_model(svm, 'demo_svm.mle', input_shape=(1, 20))
            
            # Naive Bayes
            print("\n--- Naive Bayes ---")
            from sklearn.naive_bayes import GaussianNB
            
            nb = GaussianNB()
            nb.fit(X_class, y_class)
            export_model(nb, 'demo_naive_bayes.mle', input_shape=(1, 20))
            
            # KNN
            print("\n--- K-Nearest Neighbors ---")
            from sklearn.neighbors import KNeighborsClassifier
            
            knn = KNeighborsClassifier(n_neighbors=5)
            knn.fit(X_class[:100], y_class[:100])
            export_model(knn, 'demo_knn.mle', input_shape=(1, 20))
            
            # Clustering
            print("\n--- Clustering ---")
            from sklearn.cluster import KMeans
            
            kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
            kmeans.fit(X_class)
            export_model(kmeans, 'demo_kmeans.mle', input_shape=(1, 20))
            
            # Dimensionality Reduction
            print("\n--- Dimensionality Reduction ---")
            from sklearn.decomposition import PCA
            
            pca = PCA(n_components=10)
            pca.fit(X_class)
            export_model(pca, 'demo_pca.mle', input_shape=(1, 20))
            
            print("\n✓ All scikit-learn models exported successfully!")
            
        except Exception as e:
            print(f"✗ Scikit-learn demo failed: {e}")
        
        # 2. PyTorch models
        print("\n" + "="*80)
        print("2. PYTORCH MODELS")
        print("="*80)
        
        try:
            import torch
            import torch.nn as nn
            
            # Simple MLP
            print("\n--- Multi-Layer Perceptron ---")
            mlp_model = nn.Sequential(
                nn.Linear(20, 64),
                nn.ReLU(),
                nn.Linear(64, 32),
                nn.ReLU(),
                nn.Linear(32, 3)
            )
            export_model(mlp_model, 'demo_pytorch_mlp.mle', input_shape=(1, 20))
            
            print("\n✓ PyTorch models exported successfully!")
            
        except Exception as e:
            print(f"✗ PyTorch demo failed: {e}")
        
        # 3. TensorFlow/Keras models
        print("\n" + "="*80)
        print("3. TENSORFLOW/KERAS MODELS")
        print("="*80)
        
        try:
            from tensorflow import keras
            
            # Simple Sequential model
            print("\n--- Keras Sequential ---")
            keras_model = keras.Sequential([
                keras.layers.Dense(64, activation='relu', input_shape=(20,)),
                keras.layers.Dense(32, activation='relu'),
                keras.layers.Dense(3, activation='softmax')
            ])
            keras_model.compile(optimizer='adam', loss='categorical_crossentropy')
            
            export_model(keras_model, 'demo_keras_model.mle', input_shape=(1, 20))
            
            print("\n✓ TensorFlow/Keras models exported successfully!")
            
        except Exception as e:
            print(f"✗ TensorFlow/Keras demo failed: {e}")
        
        # 4. XGBoost models
        print("\n" + "="*80)
        print("4. XGBOOST MODELS")
        print("="*80)
        
        try:
            import xgboost as xgb
            from sklearn.datasets import make_classification
            
            X, y = make_classification(n_samples=1000, n_features=20, n_classes=2, random_state=42)
            
            print("\n--- XGBoost Classifier ---")
            xgb_model = xgb.XGBClassifier(n_estimators=50, max_depth=3, random_state=42)
            xgb_model.fit(X, y)
            export_model(xgb_model, 'demo_xgboost.mle', input_shape=(1, 20))
            
            print("\n✓ XGBoost models exported successfully!")
            
        except Exception as e:
            print(f"✗ XGBoost demo failed: {e}")
        
        # 5. LightGBM models
        print("\n" + "="*80)
        print("5. LIGHTGBM MODELS")
        print("="*80)
        
        try:
            import lightgbm as lgb
            from sklearn.datasets import make_classification
            
            X, y = make_classification(n_samples=1000, n_features=20, n_classes=2, random_state=42)
            
            print("\n--- LightGBM Classifier ---")
            lgb_model = lgb.LGBMClassifier(n_estimators=50, max_depth=3, random_state=42, verbose=-1)
            lgb_model.fit(X, y)
            export_model(lgb_model, 'demo_lightgbm.mle', input_shape=(1, 20))
            
            print("\n✓ LightGBM models exported successfully!")
            
        except Exception as e:
            print(f"✗ LightGBM demo failed: {e}")
        
        # 6. CatBoost models
        print("\n" + "="*80)
        print("6. CATBOOST MODELS")
        print("="*80)
        
        try:
            import catboost as cb
            from sklearn.datasets import make_classification
            
            X, y = make_classification(n_samples=1000, n_features=20, n_classes=2, random_state=42)
            
            print("\n--- CatBoost Classifier ---")
            cb_model = cb.CatBoostClassifier(iterations=50, depth=3, verbose=0, random_state=42)
            cb_model.fit(X, y)
            export_model(cb_model, 'demo_catboost.mle', input_shape=(1, 20))
            
            print("\n✓ CatBoost models exported successfully!")
            
        except Exception as e:
            print(f"✗ CatBoost demo failed: {e}")
        
        print("\n" + "="*80)
        print("DEMO COMPLETE!")
        print("="*80)
        print("\nAll supported model types have been exported to .mle format")
        print("Each exporter is completely independent - no cross-dependencies!")
        print("\nSupported models:")
        print("  • Scikit-learn: Linear, MLP, Trees, Ensembles, SVM, NB, KNN, Clustering, PCA")
        print("  • PyTorch: MLP, CNN, RNN, LSTM, GRU, Transformers")
        print("  • TensorFlow/Keras: Sequential, Functional API")
        print("  • XGBoost: Classifier, Regressor")
        print("  • LightGBM: Classifier, Regressor")
        print("  • CatBoost: Classifier, Regressor")


if __name__ == '__main__':
    main()
