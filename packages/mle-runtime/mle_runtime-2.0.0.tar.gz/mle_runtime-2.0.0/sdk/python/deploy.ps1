# Python SDK Deployment Script (Windows)
# Builds and publishes to PyPI

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Python SDK - Build & Deploy" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check if twine is installed
if (!(Get-Command twine -ErrorAction SilentlyContinue)) {
    Write-Host "Installing twine..." -ForegroundColor Yellow
    pip install twine
}

# Clean previous builds
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path build) { Remove-Item -Recurse -Force build }
if (Test-Path dist) { Remove-Item -Recurse -Force dist }
Get-ChildItem -Filter "*.egg-info" -Recurse | Remove-Item -Recurse -Force

# Build source distribution and wheel
Write-Host "Building distribution packages..." -ForegroundColor Yellow
python setup.py sdist bdist_wheel

# Check packages
Write-Host ""
Write-Host "Checking packages..." -ForegroundColor Yellow
twine check dist/*

# Show what will be uploaded
Write-Host ""
Write-Host "Packages ready for upload:" -ForegroundColor Green
Get-ChildItem dist\ | Format-Table Name, Length

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Ready to deploy!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To upload to PyPI:" -ForegroundColor White
Write-Host "  Test PyPI:  twine upload --repository testpypi dist/*" -ForegroundColor Yellow
Write-Host "  Production: twine upload dist/*" -ForegroundColor Yellow
Write-Host ""
Write-Host "To test locally:" -ForegroundColor White
Write-Host "  pip install dist\mle_runtime-*.whl" -ForegroundColor Yellow
Write-Host ""
