# Build Deployable SDK Packages
# Creates distribution packages ready for npm, PyPI, and Maven Central

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Building Deployable SDK Packages" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

$startTime = Get-Date

# Step 1: Build C++ Core (required for all SDKs)
Write-Host "[1/5] Building C++ Core..." -ForegroundColor Yellow

Set-Location cpp_core

if (Test-Path build) {
    Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
}

New-Item -ItemType Directory -Path build | Out-Null
Set-Location build

cmake -DCMAKE_BUILD_TYPE=Release -DENABLE_CUDA=OFF -DBUILD_TESTS=OFF .. | Out-Null
cmake --build . --config Release --parallel 4 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] C++ core built" -ForegroundColor Green
} else {
    Write-Host "  [X] C++ core build failed" -ForegroundColor Red
    Set-Location ..\..
    exit 1
}

Set-Location ..\..

# Step 2: Build Node.js SDK
Write-Host ""
Write-Host "[2/5] Building Node.js SDK..." -ForegroundColor Yellow

Set-Location sdk\nodejs

Write-Host "  Installing dependencies..." -ForegroundColor Gray
npm install --silent 2>&1 | Out-Null

Write-Host "  Compiling TypeScript..." -ForegroundColor Gray
npm run build --silent 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "  Creating npm package..." -ForegroundColor Gray
    npm pack --silent 2>&1 | Out-Null
    
    $package = Get-ChildItem *.tgz | Select-Object -First 1
    if ($package) {
        Write-Host "  [OK] Package created: $($package.Name)" -ForegroundColor Green
        Write-Host "      Size: $([math]::Round($package.Length/1KB, 2)) KB" -ForegroundColor Gray
    }
} else {
    Write-Host "  [X] Node.js build failed" -ForegroundColor Red
}

Set-Location ..\..

# Step 3: Build Python SDK
Write-Host ""
Write-Host "[3/5] Building Python SDK..." -ForegroundColor Yellow

Set-Location sdk\python

# Clean previous builds
if (Test-Path build) { Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue }
if (Test-Path dist) { Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue }
Get-ChildItem -Filter "*.egg-info" -Recurse | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "  Building distribution packages..." -ForegroundColor Gray
python setup.py sdist bdist_wheel --quiet 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0 -and (Test-Path dist)) {
    $packages = Get-ChildItem dist\*
    Write-Host "  [OK] Packages created:" -ForegroundColor Green
    foreach ($pkg in $packages) {
        Write-Host "      $($pkg.Name) - $([math]::Round($pkg.Length/1KB, 2)) KB" -ForegroundColor Gray
    }
} else {
    Write-Host "  [X] Python build failed" -ForegroundColor Red
}

Set-Location ..\..

# Step 4: Build Java SDK
Write-Host ""
Write-Host "[4/5] Building Java SDK..." -ForegroundColor Yellow

Set-Location sdk\java

Write-Host "  Running Maven build..." -ForegroundColor Gray
mvn clean package -DskipTests --quiet 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0 -and (Test-Path target)) {
    $jars = Get-ChildItem target\*.jar
    Write-Host "  [OK] Artifacts created:" -ForegroundColor Green
    foreach ($jar in $jars) {
        Write-Host "      $($jar.Name) - $([math]::Round($jar.Length/1KB, 2)) KB" -ForegroundColor Gray
    }
} else {
    Write-Host "  [X] Java build failed" -ForegroundColor Red
}

Set-Location ..\..

# Step 5: Package C++ SDK
Write-Host ""
Write-Host "[5/5] Packaging C++ SDK..." -ForegroundColor Yellow

Set-Location sdk\cpp

if (Test-Path dist) { Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue }
New-Item -ItemType Directory -Path dist | Out-Null

Write-Host "  Creating header package..." -ForegroundColor Gray

# Copy headers
Copy-Item include\mle_client.h dist\
Copy-Item README.md dist\
Copy-Item CMakeLists.txt dist\

# Create archive
$version = "1.0.0"
$archiveName = "mle-cpp-sdk-$version.zip"

if (Test-Path $archiveName) { Remove-Item $archiveName }

Compress-Archive -Path dist\* -DestinationPath $archiveName

if (Test-Path $archiveName) {
    $archive = Get-Item $archiveName
    Write-Host "  [OK] Package created: $archiveName" -ForegroundColor Green
    Write-Host "      Size: $([math]::Round($archive.Length/1KB, 2)) KB" -ForegroundColor Gray
}

Set-Location ..\..

# Summary
$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Host "Build Complete!" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Build time: $($duration.TotalSeconds) seconds" -ForegroundColor Gray
Write-Host ""

Write-Host "Deployable Packages:" -ForegroundColor White
Write-Host ""

# Node.js
if (Test-Path sdk\nodejs\*.tgz) {
    $pkg = Get-ChildItem sdk\nodejs\*.tgz | Select-Object -First 1
    Write-Host "  Node.js:" -ForegroundColor Cyan
    Write-Host "    Location: sdk\nodejs\$($pkg.Name)" -ForegroundColor Gray
    Write-Host "    Deploy: cd sdk\nodejs && npm publish" -ForegroundColor Yellow
    Write-Host ""
}

# Python
if (Test-Path sdk\python\dist) {
    Write-Host "  Python:" -ForegroundColor Cyan
    Write-Host "    Location: sdk\python\dist\" -ForegroundColor Gray
    Write-Host "    Deploy: cd sdk\python && twine upload dist/*" -ForegroundColor Yellow
    Write-Host ""
}

# Java
if (Test-Path sdk\java\target\*.jar) {
    Write-Host "  Java:" -ForegroundColor Cyan
    Write-Host "    Location: sdk\java\target\" -ForegroundColor Gray
    Write-Host "    Deploy: cd sdk\java && mvn deploy" -ForegroundColor Yellow
    Write-Host ""
}

# C++
if (Test-Path sdk\cpp\mle-cpp-sdk-*.zip) {
    $pkg = Get-ChildItem sdk\cpp\mle-cpp-sdk-*.zip | Select-Object -First 1
    Write-Host "  C++:" -ForegroundColor Cyan
    Write-Host "    Location: sdk\cpp\$($pkg.Name)" -ForegroundColor Gray
    Write-Host "    Deploy: Upload to GitHub releases" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Next Steps:" -ForegroundColor White
Write-Host "  1. Test packages locally" -ForegroundColor Gray
Write-Host "  2. Review DEPLOYMENT.md for detailed instructions" -ForegroundColor Gray
Write-Host "  3. Deploy to package registries" -ForegroundColor Gray
Write-Host ""

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
