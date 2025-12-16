#!/usr/bin/env pwsh
# Build and install Python SDK with C++ bindings

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Building MLE Runtime Python SDK with C++ Extensions" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}
Write-Host "✓ $pythonVersion" -ForegroundColor Green
Write-Host ""

# Check pybind11
Write-Host "Checking pybind11..." -ForegroundColor Yellow
$pybind11Check = python -c "import pybind11; print(pybind11.__version__)" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing pybind11..." -ForegroundColor Yellow
    pip install pybind11
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to install pybind11" -ForegroundColor Red
        exit 1
    }
}
Write-Host "✓ pybind11 installed" -ForegroundColor Green
Write-Host ""

# Build C++ bindings
Write-Host "Building C++ bindings..." -ForegroundColor Yellow
Push-Location bindings/python

# Uninstall old version
Write-Host "Removing old installation..." -ForegroundColor Yellow
pip uninstall -y mle-runtime 2>$null

# Build and install
Write-Host "Building extension..." -ForegroundColor Yellow
python setup.py build_ext --inplace
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to build C++ extension" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host "Installing package..." -ForegroundColor Yellow
pip install -e .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to install package" -ForegroundColor Red
    Pop-Location
    exit 1
}

Pop-Location

Write-Host "✓ C++ bindings built and installed" -ForegroundColor Green
Write-Host ""

# Verify installation
Write-Host "Verifying installation..." -ForegroundColor Yellow
python -c "import mle_runtime; print('✓ mle_runtime imported successfully')" 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to import mle_runtime" -ForegroundColor Red
    exit 1
}

Write-Host "✓ mle_runtime imported successfully" -ForegroundColor Green
Write-Host ""

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Build Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now run examples:" -ForegroundColor White
Write-Host "  python examples/complete_workflow.py" -ForegroundColor Cyan
Write-Host "  python examples/test_mle_runtime.py example_model.mle --test all" -ForegroundColor Cyan
Write-Host ""
