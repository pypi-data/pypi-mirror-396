#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Build MLE Runtime Python package for deployment
.DESCRIPTION
    Creates wheel and source distributions ready for PyPI or private deployment
#>

param(
    [switch]$Clean,
    [switch]$Test,
    [switch]$Upload,
    [string]$Repository = "pypi"
)

$ErrorActionPreference = "Stop"

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "MLE Runtime - Build Deployable Package" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $ScriptDir

try {
    # Clean previous builds
    if ($Clean) {
        Write-Host "`n[1/6] Cleaning previous builds..." -ForegroundColor Yellow
        
        if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
        if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
        if (Test-Path "mle_runtime.egg-info") { Remove-Item -Recurse -Force "mle_runtime.egg-info" }
        
        # Clean Python cache
        Get-ChildItem -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force
        Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force
        Get-ChildItem -Recurse -Filter "*.pyo" | Remove-Item -Force
        
        Write-Host "✓ Cleaned" -ForegroundColor Green
    }
    
    # Check dependencies
    Write-Host "`n[2/6] Checking build dependencies..." -ForegroundColor Yellow
    
    $required = @("setuptools", "wheel", "build", "twine")
    foreach ($pkg in $required) {
        $installed = python -m pip show $pkg 2>$null
        if (-not $installed) {
            Write-Host "Installing $pkg..." -ForegroundColor Gray
            python -m pip install $pkg --quiet
        }
    }
    
    Write-Host "✓ Dependencies ready" -ForegroundColor Green
    
    # Build source distribution
    Write-Host "`n[3/6] Building source distribution..." -ForegroundColor Yellow
    python -m build --sdist
    
    if ($LASTEXITCODE -ne 0) {
        throw "Source distribution build failed"
    }
    
    Write-Host "✓ Source distribution built" -ForegroundColor Green
    
    # Build wheel distribution
    Write-Host "`n[4/6] Building wheel distribution..." -ForegroundColor Yellow
    python -m build --wheel
    
    if ($LASTEXITCODE -ne 0) {
        throw "Wheel distribution build failed"
    }
    
    Write-Host "✓ Wheel distribution built" -ForegroundColor Green
    
    # List built packages
    Write-Host "`n[5/6] Built packages:" -ForegroundColor Yellow
    Get-ChildItem dist | ForEach-Object {
        $size = [math]::Round($_.Length / 1KB, 2)
        Write-Host "  - $($_.Name) ($size KB)" -ForegroundColor Gray
    }
    
    # Run tests
    if ($Test) {
        Write-Host "`n[6/6] Running tests..." -ForegroundColor Yellow
        
        # Install package in development mode
        python -m pip install -e ".[dev]" --quiet
        
        # Run pytest
        python -m pytest tests/ -v
        
        if ($LASTEXITCODE -ne 0) {
            throw "Tests failed"
        }
        
        Write-Host "✓ All tests passed" -ForegroundColor Green
    } else {
        Write-Host "`n[6/6] Skipping tests (use -Test to run)" -ForegroundColor Gray
    }
    
    # Check package with twine
    Write-Host "`nChecking package integrity..." -ForegroundColor Yellow
    python -m twine check dist/*
    
    if ($LASTEXITCODE -ne 0) {
        throw "Package check failed"
    }
    
    Write-Host "✓ Package integrity verified" -ForegroundColor Green
    
    # Upload to PyPI
    if ($Upload) {
        Write-Host "`nUploading to $Repository..." -ForegroundColor Yellow
        
        if ($Repository -eq "pypi") {
            python -m twine upload dist/*
        } elseif ($Repository -eq "testpypi") {
            python -m twine upload --repository testpypi dist/*
        } else {
            python -m twine upload --repository $Repository dist/*
        }
        
        if ($LASTEXITCODE -ne 0) {
            throw "Upload failed"
        }
        
        Write-Host "✓ Uploaded successfully" -ForegroundColor Green
    } else {
        Write-Host "`nSkipping upload (use -Upload to publish)" -ForegroundColor Gray
    }
    
    # Summary
    Write-Host "`n" + "=" * 80 -ForegroundColor Cyan
    Write-Host "BUILD COMPLETE!" -ForegroundColor Green
    Write-Host "=" * 80 -ForegroundColor Cyan
    
    Write-Host "`nPackages ready in: $ScriptDir\dist" -ForegroundColor White
    Write-Host "`nInstallation commands:" -ForegroundColor Yellow
    Write-Host "  Local:  pip install dist/mle_runtime-*.whl" -ForegroundColor Gray
    Write-Host "  PyPI:   pip install mle-runtime" -ForegroundColor Gray
    Write-Host "`nWith extras:" -ForegroundColor Yellow
    Write-Host "  pip install mle-runtime[sklearn]      # Scikit-learn support" -ForegroundColor Gray
    Write-Host "  pip install mle-runtime[pytorch]      # PyTorch support" -ForegroundColor Gray
    Write-Host "  pip install mle-runtime[tensorflow]   # TensorFlow support" -ForegroundColor Gray
    Write-Host "  pip install mle-runtime[all]          # Everything" -ForegroundColor Gray
    
} catch {
    Write-Host "`n✗ Build failed: $_" -ForegroundColor Red
    exit 1
} finally {
    Pop-Location
}
