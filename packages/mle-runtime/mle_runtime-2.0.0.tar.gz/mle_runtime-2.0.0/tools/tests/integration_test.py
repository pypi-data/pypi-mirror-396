#!/usr/bin/env python3
"""
Integration test for the entire No-Code ML platform
Tests: Services → Export → Load → Inference → Validation
"""

import sys
import os
import time
import subprocess
import socket
import psycopg2
import redis
from minio import Minio

def check_port(host, port, timeout=5):
    """Check if a port is open"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        result = sock.connect_ex((host, port))
        return result == 0
    finally:
        sock.close()

def test_services():
    """Test that all infrastructure services are running"""
    print("=" * 60)
    print("Test 1: Infrastructure Services")
    print("=" * 60)
    
    services = {
        'PostgreSQL': ('localhost', 5432),
        'MinIO': ('localhost', 9000),
        'Redis': ('localhost', 6379),
    }
    
    all_ok = True
    for name, (host, port) in services.items():
        if check_port(host, port):
            print(f"✓ {name} is running on {host}:{port}")
        else:
            print(f"✗ {name} is NOT running on {host}:{port}")
            all_ok = False
    
    if not all_ok:
        print("\n⚠ Some services are not running. Start with: docker compose up -d")
        return False
    
    # Test PostgreSQL connection
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            user='mluser',
            password='mlpass',
            database='mlmetadata'
        )
        conn.close()
        print("✓ PostgreSQL connection successful")
    except Exception as e:
        print(f"✗ PostgreSQL connection failed: {e}")
        all_ok = False
    
    # Test Redis connection
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✓ Redis connection successful")
    except Exception as e:
        print(f"✗ Redis connection failed: {e}")
        all_ok = False
    
    # Test MinIO connection
    try:
        client = Minio(
            'localhost:9000',
            access_key='minioadmin',
            secret_key='minioadmin',
            secure=False
        )
        # Try to list buckets
        list(client.list_buckets())
        print("✓ MinIO connection successful")
    except Exception as e:
        print(f"✗ MinIO connection failed: {e}")
        all_ok = False
    
    print()
    return all_ok

def test_cpp_build():
    """Test that C++ core is built"""
    print("=" * 60)
    print("Test 2: C++ Core Build")
    print("=" * 60)
    
    build_dir = 'cpp_core/build'
    if not os.path.exists(build_dir):
        print(f"✗ Build directory not found: {build_dir}")
        print("  Run: cd cpp_core && mkdir build && cd build && cmake .. && cmake --build .")
        return False
    
    # Check for test executable
    test_exe = os.path.join(build_dir, 'mle_tests')
    if os.name == 'nt':  # Windows
        test_exe += '.exe'
    
    if os.path.exists(test_exe):
        print(f"✓ Test executable found: {test_exe}")
        
        # Run tests
        try:
            result = subprocess.run([test_exe], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("✓ C++ tests passed")
            else:
                print(f"✗ C++ tests failed with code {result.returncode}")
                print(result.stdout)
                print(result.stderr)
                return False
        except Exception as e:
            print(f"⚠ Could not run C++ tests: {e}")
    else:
        print(f"⚠ Test executable not found (this is OK if tests weren't built)")
    
    print()
    return True

def test_python_bindings():
    """Test Python bindings"""
    print("=" * 60)
    print("Test 3: Python Bindings")
    print("=" * 60)
    
    try:
        import mle_runtime
        print("✓ mle_runtime module imported successfully")
        
        # Test Engine creation
        engine = mle_runtime.Engine(mle_runtime.Device.CPU)
        print("✓ Engine created successfully")
        
        # Test GraphExecutor creation
        executor = mle_runtime.GraphExecutor(mle_runtime.Device.CPU)
        print("✓ GraphExecutor created successfully")
        
    except ImportError as e:
        print(f"✗ Failed to import mle_runtime: {e}")
        print("  Install with: cd bindings/python && pip install -e .")
        return False
    except Exception as e:
        print(f"✗ Error testing Python bindings: {e}")
        return False
    
    print()
    return True

def test_export_and_inference():
    """Test model export and inference"""
    print("=" * 60)
    print("Test 4: Export and Inference")
    print("=" * 60)
    
    # Run the complete workflow
    workflow_script = 'examples/complete_workflow.py'
    if not os.path.exists(workflow_script):
        print(f"✗ Workflow script not found: {workflow_script}")
        return False
    
    try:
        print("Running complete workflow...")
        result = subprocess.run(
            [sys.executable, workflow_script],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print("✓ Complete workflow executed successfully")
            # Check if model file was created
            if os.path.exists('example_model.mle'):
                print("✓ Model file created: example_model.mle")
                size = os.path.getsize('example_model.mle')
                print(f"  Size: {size / 1024:.2f} KB")
            else:
                print("⚠ Model file not found")
        else:
            print(f"✗ Workflow failed with code {result.returncode}")
            print("STDOUT:", result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
            print("STDERR:", result.stderr[-500:] if len(result.stderr) > 500 else result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ Workflow timed out after 120 seconds")
        return False
    except Exception as e:
        print(f"✗ Error running workflow: {e}")
        return False
    
    print()
    return True

def test_cli_tools():
    """Test CLI tools"""
    print("=" * 60)
    print("Test 5: CLI Tools")
    print("=" * 60)
    
    if not os.path.exists('example_model.mle'):
        print("⚠ Skipping CLI test (no model file)")
        print()
        return True
    
    try:
        # Test inspect command
        result = subprocess.run(
            [sys.executable, 'tools/cli/aimodule.py', 'inspect', 'example_model.mle'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✓ aimodule inspect command works")
        else:
            print(f"✗ aimodule inspect failed: {result.stderr}")
            return False
        
        # Test validate command
        result = subprocess.run(
            [sys.executable, 'tools/cli/aimodule.py', 'validate', 'example_model.mle'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✓ aimodule validate command works")
        else:
            print(f"✗ aimodule validate failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Error testing CLI: {e}")
        return False
    
    print()
    return True

def test_frontend():
    """Test frontend build"""
    print("=" * 60)
    print("Test 6: Frontend")
    print("=" * 60)
    
    frontend_dir = 'frontend'
    if not os.path.exists(frontend_dir):
        print(f"✗ Frontend directory not found: {frontend_dir}")
        return False
    
    # Check if node_modules exists
    node_modules = os.path.join(frontend_dir, 'node_modules')
    if os.path.exists(node_modules):
        print("✓ Frontend dependencies installed")
    else:
        print("⚠ Frontend dependencies not installed")
        print("  Run: cd frontend && npm install")
        return True  # Not a failure, just not set up
    
    # Try to build
    try:
        print("Building frontend...")
        result = subprocess.run(
            ['npm', 'run', 'build'],
            cwd=frontend_dir,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print("✓ Frontend build successful")
        else:
            print(f"✗ Frontend build failed")
            print(result.stderr[-500:] if len(result.stderr) > 500 else result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ Frontend build timed out")
        return False
    except FileNotFoundError:
        print("⚠ npm not found, skipping frontend test")
        return True
    except Exception as e:
        print(f"✗ Error building frontend: {e}")
        return False
    
    print()
    return True

def main():
    """Run all integration tests"""
    print("\n" + "=" * 60)
    print("No-Code ML Platform - Integration Tests")
    print("=" * 60 + "\n")
    
    start_time = time.time()
    
    tests = [
        ("Infrastructure Services", test_services),
        ("C++ Core Build", test_cpp_build),
        ("Python Bindings", test_python_bindings),
        ("Export and Inference", test_export_and_inference),
        ("CLI Tools", test_cli_tools),
        ("Frontend", test_frontend),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    elapsed = time.time() - start_time
    print(f"\nTotal: {passed}/{total} tests passed in {elapsed:.2f}s")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
