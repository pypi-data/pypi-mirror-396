# Simple build script for MLE Runtime
# Builds C++ core and verifies SDK structure

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MLE Runtime - Build Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Build C++ Core
Write-Host "[1/2] Building C++ Core..." -ForegroundColor Yellow

Set-Location cpp_core

if (Test-Path build) {
    Remove-Item -Recurse -Force build
}

New-Item -ItemType Directory -Path build | Out-Null
Set-Location build

Write-Host "  Running CMake..." -ForegroundColor Gray
cmake -DCMAKE_BUILD_TYPE=Release -DENABLE_CUDA=OFF -DBUILD_TESTS=OFF .. | Out-Null

Write-Host "  Building..." -ForegroundColor Gray
cmake --build . --config Release --parallel 4

if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] C++ core built successfully" -ForegroundColor Green
} else {
    Write-Host "  [X] C++ core build failed" -ForegroundColor Red
    Set-Location ..\..
    exit 1
}

Set-Location ..\..

# Step 2: Verify SDK Structure
Write-Host ""
Write-Host "[2/2] Verifying SDK Structure..." -ForegroundColor Yellow

.\verify-sdks.ps1

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Build Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor White
Write-Host "  1. Build Node.js SDK: cd sdk\nodejs && npm install && npm run build" -ForegroundColor Cyan
Write-Host "  2. Build Java SDK: cd sdk\java && mvn clean install" -ForegroundColor Cyan
Write-Host "  3. Build Python SDK: cd sdk\python && pip install -e ." -ForegroundColor Cyan
Write-Host ""
