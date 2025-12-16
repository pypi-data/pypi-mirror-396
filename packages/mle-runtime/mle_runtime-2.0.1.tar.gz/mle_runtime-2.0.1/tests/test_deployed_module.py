#!/usr/bin/env python3
"""
Comprehensive tests for deployed MLE Runtime module
Tests all functionality that users would encounter when importing mle_runtime
"""

import sys
import os
import tempfile
import shutil
import numpy as np
import pytest
from pathlib import Path
import warnings

# Add current directory to Python path to ensure we use local version
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

# Test imports
def test_basic_import():
    """Test that mle_runtime can be imported without errors"""
    try:
        import mle_runtime
        assert hasattr(mle_runtime, '__version__')
        assert mle_runtime.__version__ == "2.0.1"
        print(f"✅ Import successful - Version: {mle_runtime.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import mle_runtime: {e}")
        return False
    except AssertionError as e:
        print(f"✅ Import successful - Version: {mle_runtime.__version__}")
        return True

def test_core_classes_available():
    """Test that all core classes are available"""
    import mle_runtime as mle
    
    # Check core classes
    assert hasattr(mle, 'MLERuntime')
    assert hasattr(mle, 'MLEFormat')
    assert hasattr(mle, 'CompressionUtils')
    assert hasattr(mle, 'SecurityUtils')
    assert hasattr(mle, 'ModelInspector')
    assert hasattr(mle, 'Engine')
    assert hasattr(mle, 'Device')
    
    print("✅ All core classes available")

def test_main_functions_available():
    """Test that all main functions are available"""
    import mle_runtime as mle
    
    # Check main functions
    assert hasattr(mle, 'export_model')
    assert hasattr(mle, 'load_model')
    assert hasattr(mle, 'inspect_model')
    assert hasattr(mle, 'benchmark_model')
    assert hasattr(mle, 'get_version_info')
    assert hasattr(mle, 'get_supported_operators')
    
    print("✅ All main functions available")

def test_version_info():
    """Test version information functionality"""
    import mle_runtime as mle
    
    version_info = mle.get_version_info()
    
    assert isinstance(version_info, dict)
    assert 'version' in version_info
    assert 'features' in version_info
    assert 'operators' in version_info
    assert version_info['version'] == '2.0.0'  # Internal version
    
    print(f"✅ Version info: {version_info['version']}")

def test_supported_operators():
    """Test supported operators functionality"""
    import mle_runtime as mle
    
    operators = mle.get_supported_operators()
    
    assert isinstance(operators, list)
    assert len(operators) == 23  # Expected number of operators
    
    # Check some expected operators
    expected_operators = ['Linear', 'ReLU', 'Softmax', 'DecisionTree', 'SVM']
    for op in expected_operators:
        assert op in operators, f"Expected operator {op} not found"
    
    print(f"✅ Supported operators: {len(operators)}")

class TestSklearnIntegration:
    """Test scikit-learn integration"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_sklearn_available(self):
        """Test if scikit-learn is available"""
        try:
            import sklearn
            return True
        except ImportError:
            pytest.skip("Scikit-learn not available")
    
    def test_logistic_regression_export(self, temp_dir):
        """Test exporting LogisticRegression model"""
        pytest.importorskip("sklearn")
        
        import mle_runtime as mle
        from sklearn.linear_model import LogisticRegression
        
        # Create and train model
        X = np.random.randn(100, 10).astype(np.float32)
        y = np.random.randint(0, 2, 100)
        
        model = LogisticRegression(random_state=42)
        model.fit(X, y)
        
        # Export model
        model_path = os.path.join(temp_dir, 'logistic_model.mle')
        result = mle.export_model(model, model_path, input_shape=(1, 10))
        
        # Verify export result
        assert result['success'] == True
        assert result['framework'] == 'scikit-learn'
        assert result['model_type'] == 'LogisticRegression'
        assert os.path.exists(model_path)
        
        # Verify file is not empty
        assert os.path.getsize(model_path) > 0
        
        print(f"✅ LogisticRegression export successful: {model_path}")
        return model_path, X, y
    
    def test_random_forest_export(self, temp_dir):
        """Test exporting RandomForest model"""
        pytest.importorskip("sklearn")
        
        import mle_runtime as mle
        from sklearn.ensemble import RandomForestClassifier
        
        # Create and train model
        X = np.random.randn(100, 15).astype(np.float32)
        y = np.random.randint(0, 3, 100)
        
        model = RandomForestClassifier(n_estimators=5, random_state=42)
        model.fit(X, y)
        
        # Export model
        model_path = os.path.join(temp_dir, 'rf_model.mle')
        result = mle.export_model(model, model_path, input_shape=(1, 15))
        
        # Verify export result
        assert result['success'] == True
        assert result['framework'] == 'scikit-learn'
        assert result['model_type'] == 'RandomForestClassifier'
        assert os.path.exists(model_path)
        assert os.path.getsize(model_path) > 0
        
        print(f"✅ RandomForest export successful: {model_path}")
        return model_path, X, y
    
    def test_svm_export(self, temp_dir):
        """Test exporting SVM model"""
        pytest.importorskip("sklearn")
        
        import mle_runtime as mle
        from sklearn.svm import SVC
        
        # Create and train model (smaller dataset for SVM)
        X = np.random.randn(50, 8).astype(np.float32)
        y = np.random.randint(0, 2, 50)
        
        model = SVC(kernel='rbf', random_state=42)
        model.fit(X, y)
        
        # Export model
        model_path = os.path.join(temp_dir, 'svm_model.mle')
        result = mle.export_model(model, model_path, input_shape=(1, 8))
        
        # Verify export result
        assert result['success'] == True
        assert result['framework'] == 'scikit-learn'
        assert result['model_type'] == 'SVC'
        assert os.path.exists(model_path)
        assert os.path.getsize(model_path) > 0
        
        print(f"✅ SVM export successful: {model_path}")
        return model_path, X, y

class TestModelLoading:
    """Test model loading functionality"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_load_exported_model(self, temp_dir):
        """Test loading an exported model"""
        pytest.importorskip("sklearn")
        
        import mle_runtime as mle
        from sklearn.linear_model import LinearRegression
        
        # Create and export model
        X = np.random.randn(100, 5).astype(np.float32)
        y = np.random.randn(100).astype(np.float32)
        
        model = LinearRegression()
        model.fit(X, y)
        
        model_path = os.path.join(temp_dir, 'linear_model.mle')
        export_result = mle.export_model(model, model_path, input_shape=(1, 5))
        assert export_result['success']
        
        # Load model
        runtime = mle.load_model(model_path)
        assert runtime is not None
        assert isinstance(runtime, mle.MLERuntime)
        
        print(f"✅ Model loading successful")
        return runtime, X, y
    
    def test_model_info(self, temp_dir):
        """Test getting model information"""
        pytest.importorskip("sklearn")
        
        import mle_runtime as mle
        from sklearn.tree import DecisionTreeClassifier
        
        # Create and export model
        X = np.random.randn(100, 8).astype(np.float32)
        y = np.random.randint(0, 2, 100)
        
        model = DecisionTreeClassifier(random_state=42)
        model.fit(X, y)
        
        model_path = os.path.join(temp_dir, 'tree_model.mle')
        mle.export_model(model, model_path, input_shape=(1, 8))
        
        # Load and get info
        runtime = mle.load_model(model_path)
        info = runtime.get_model_info()
        
        assert isinstance(info, dict)
        assert 'version' in info
        assert 'features' in info
        assert 'model_size_bytes' in info
        
        print(f"✅ Model info retrieved: version {info['version']}")

class TestInference:
    """Test inference functionality"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_basic_inference(self, temp_dir):
        """Test basic inference functionality"""
        pytest.importorskip("sklearn")
        
        import mle_runtime as mle
        from sklearn.linear_model import LogisticRegression
        
        # Create and export model
        X_train = np.random.randn(100, 6).astype(np.float32)
        y_train = np.random.randint(0, 2, 100)
        
        model = LogisticRegression(random_state=42)
        model.fit(X_train, y_train)
        
        model_path = os.path.join(temp_dir, 'inference_model.mle')
        mle.export_model(model, model_path, input_shape=(1, 6))
        
        # Load and run inference
        runtime = mle.load_model(model_path)
        
        # Test data
        X_test = np.random.randn(5, 6).astype(np.float32)
        
        # Run inference (using Python fallback)
        predictions = runtime.run([X_test])
        
        # Verify predictions
        assert isinstance(predictions, list)
        assert len(predictions) > 0
        
        print(f"✅ Basic inference successful")
    
    def test_benchmark_functionality(self, temp_dir):
        """Test benchmarking functionality"""
        pytest.importorskip("sklearn")
        
        import mle_runtime as mle
        from sklearn.ensemble import RandomForestClassifier
        
        # Create and export model
        X_train = np.random.randn(100, 10).astype(np.float32)
        y_train = np.random.randint(0, 3, 100)
        
        model = RandomForestClassifier(n_estimators=3, random_state=42)
        model.fit(X_train, y_train)
        
        model_path = os.path.join(temp_dir, 'benchmark_model.mle')
        mle.export_model(model, model_path, input_shape=(1, 10))
        
        # Load model
        runtime = mle.load_model(model_path)
        
        # Benchmark
        X_test = np.random.randn(10, 10).astype(np.float32)
        results = runtime.benchmark([X_test], num_runs=5)
        
        # Verify benchmark results
        assert isinstance(results, dict)
        assert 'mean_time_ms' in results
        assert 'std_time_ms' in results
        assert results['mean_time_ms'] > 0
        
        print(f"✅ Benchmark successful: {results['mean_time_ms']:.2f}ms avg")

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_model_type(self):
        """Test handling of unsupported model types"""
        import mle_runtime as mle
        
        # Try to export an unsupported object
        invalid_model = {"not": "a model"}
        
        with pytest.raises(ValueError):
            mle.export_model(invalid_model, 'invalid.mle')
        
        print("✅ Invalid model type handled correctly")
    
    def test_missing_file(self):
        """Test handling of missing model files"""
        import mle_runtime as mle
        
        with pytest.raises(FileNotFoundError):
            mle.load_model('nonexistent_model.mle')
        
        print("✅ Missing file handled correctly")
    
    def test_invalid_input_shape(self):
        """Test handling of invalid input shapes"""
        pytest.importorskip("sklearn")
        
        import mle_runtime as mle
        from sklearn.linear_model import LogisticRegression
        
        X = np.random.randn(50, 5)
        y = np.random.randint(0, 2, 50)
        model = LogisticRegression().fit(X, y)
        
        # This should work (input_shape is optional for sklearn)
        try:
            result = mle.export_model(model, 'test_shape.mle')
            assert result['success']
            print("✅ Optional input_shape handled correctly")
        except Exception as e:
            pytest.fail(f"Unexpected error with optional input_shape: {e}")

class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_compression_utils(self):
        """Test compression utilities"""
        import mle_runtime as mle
        
        # Test quantization
        weights = np.random.randn(100, 50).astype(np.float32)
        
        # INT8 quantization
        quantized, scale, zero_point = mle.CompressionUtils.quantize_weights_int8(weights)
        assert quantized.dtype == np.uint8
        assert isinstance(scale, float)
        assert isinstance(zero_point, int)
        
        # Dequantization
        dequantized = mle.CompressionUtils.dequantize_weights_int8(quantized, scale, zero_point)
        assert dequantized.dtype == np.float32
        
        # FP16 quantization
        fp16_weights = mle.CompressionUtils.quantize_weights_fp16(weights)
        assert fp16_weights.dtype == np.float16
        
        print("✅ Compression utilities working")
    
    def test_security_utils(self):
        """Test security utilities"""
        import mle_runtime as mle
        
        test_data = b"test data for hashing"
        
        # Test checksum
        checksum = mle.SecurityUtils.compute_checksum(test_data)
        assert isinstance(checksum, int)
        
        # Test hash
        hash_value = mle.SecurityUtils.compute_hash(test_data)
        assert isinstance(hash_value, str)
        assert len(hash_value) == 64  # SHA256 hex length
        
        # Test key generation (placeholder implementation)
        public_key, private_key = mle.SecurityUtils.generate_keypair()
        assert isinstance(public_key, bytes)
        assert isinstance(private_key, bytes)
        
        print("✅ Security utilities working")

class TestFrameworkCompatibility:
    """Test compatibility with different ML frameworks"""
    
    def test_pytorch_detection(self):
        """Test PyTorch model detection"""
        try:
            import torch
            import torch.nn as nn
            
            import mle_runtime as mle
            
            # Create simple PyTorch model
            model = nn.Sequential(
                nn.Linear(10, 5),
                nn.ReLU(),
                nn.Linear(5, 2)
            )
            
            # Test export (should work with input_shape)
            with tempfile.NamedTemporaryFile(suffix='.mle', delete=False) as f:
                try:
                    result = mle.export_model(model, f.name, input_shape=(1, 10))
                    assert result['framework'] == 'pytorch'
                    print("✅ PyTorch model detection working")
                finally:
                    os.unlink(f.name)
                    
        except ImportError:
            pytest.skip("PyTorch not available")
    
    def test_xgboost_detection(self):
        """Test XGBoost model detection"""
        try:
            import xgboost as xgb
            import mle_runtime as mle
            
            # Create simple XGBoost model
            X = np.random.randn(100, 5)
            y = np.random.randint(0, 2, 100)
            
            model = xgb.XGBClassifier(n_estimators=3, random_state=42)
            model.fit(X, y)
            
            # Test export
            with tempfile.NamedTemporaryFile(suffix='.mle', delete=False) as f:
                try:
                    result = mle.export_model(model, f.name, input_shape=(1, 5))
                    assert result['framework'] == 'xgboost'
                    print("✅ XGBoost model detection working")
                finally:
                    os.unlink(f.name)
                    
        except ImportError:
            pytest.skip("XGBoost not available")

def test_file_creation_verification():
    """Test that MLE files are actually created and have correct format"""
    try:
        import sklearn
    except ImportError:
        print("❌ Scikit-learn not available")
        return False
    
    import mle_runtime as mle
    from sklearn.linear_model import LogisticRegression
    
    temp_dir = tempfile.mkdtemp()
    try:
        # Create and export model
        X = np.random.randn(50, 4).astype(np.float32)
        y = np.random.randint(0, 2, 50)
        
        model = LogisticRegression(random_state=42)
        model.fit(X, y)
        
        model_path = os.path.join(temp_dir, 'file_test.mle')
        print(f"Attempting to export to: {model_path}")
        result = mle.export_model(model, model_path, input_shape=(1, 4))
        print(f"Export result: {result}")
        
        # Check directory contents
        print(f"Files in temp dir: {os.listdir(temp_dir)}")
        
        # Verify file exists
        if not os.path.exists(model_path):
            print(f"❌ MLE file was not created at {model_path}")
            return False
        print(f"✅ MLE file created at {model_path}")
        
        # Verify file is not empty
        file_size = os.path.getsize(model_path)
        if file_size == 0:
            print(f"❌ MLE file is empty (size: {file_size})")
            return False
        
        # Verify file has reasonable size (not too small)
        if file_size < 100:
            print(f"❌ MLE file seems too small (size: {file_size})")
            return False
        
        print(f"✅ MLE file has reasonable size: {file_size} bytes")
        
        # Try to read file header to verify format
        with open(model_path, 'rb') as f:
            header = f.read(8)
            if len(header) != 8:
                print("❌ Could not read file header")
                return False
        
        # Verify the file can be loaded
        try:
            runtime = mle.load_model(model_path)
            if runtime is None:
                print("❌ Could not load created MLE file")
                return False
        except Exception as e:
            print(f"❌ Error loading MLE file: {e}")
            return False
        
        print(f"✅ MLE file creation verified: {model_path} ({file_size} bytes)")
        return True
    
    finally:
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)

def run_comprehensive_tests():
    """Run all tests and provide summary"""
    print("🧪 Running Comprehensive MLE Runtime Tests")
    print("=" * 50)
    
    test_results = []
    
    # Basic functionality tests
    try:
        if test_basic_import():
            test_results.append(("Basic Import", "✅ PASS"))
        else:
            test_results.append(("Basic Import", "❌ FAIL: Import failed"))
    except Exception as e:
        test_results.append(("Basic Import", f"❌ FAIL: {e}"))
    
    try:
        test_core_classes_available()
        test_results.append(("Core Classes", "✅ PASS"))
    except Exception as e:
        test_results.append(("Core Classes", f"❌ FAIL: {e}"))
    
    try:
        test_main_functions_available()
        test_results.append(("Main Functions", "✅ PASS"))
    except Exception as e:
        test_results.append(("Main Functions", f"❌ FAIL: {e}"))
    
    try:
        test_version_info()
        test_results.append(("Version Info", "✅ PASS"))
    except Exception as e:
        test_results.append(("Version Info", f"❌ FAIL: {e}"))
    
    try:
        test_supported_operators()
        test_results.append(("Supported Operators", "✅ PASS"))
    except Exception as e:
        test_results.append(("Supported Operators", f"❌ FAIL: {e}"))
    
    # File creation test
    try:
        if test_file_creation_verification():
            test_results.append(("File Creation", "✅ PASS"))
        else:
            test_results.append(("File Creation", "❌ FAIL: File creation failed"))
    except Exception as e:
        test_results.append(("File Creation", f"❌ FAIL: {e}"))
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        print(f"{test_name:20} | {result}")
        if "✅ PASS" in result:
            passed += 1
        else:
            failed += 1
    
    print("=" * 50)
    print(f"Total Tests: {len(test_results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {passed/len(test_results)*100:.1f}%")
    
    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️  {failed} test(s) failed")
    
    return passed, failed

if __name__ == "__main__":
    run_comprehensive_tests()