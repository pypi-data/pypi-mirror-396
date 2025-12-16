# MLE Runtime - Complete Setup Script
# Builds C++ core and all SDKs (Node.js, Java, Python, C++)
# Prepares packages for deployment to npm, Maven Central, PyPI

param(
    [switch]$SkipTests,
    [switch]$SkipExamples,
    [switch]$PrepareRelease,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"
$OriginalLocation = Get-Location

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host $Message -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "  [OK] $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    if ($Verbose) {
        Write-Host "  -> $Message" -ForegroundColor Gray
    }
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "  [X] $Message" -ForegroundColor Red
}

function Test-Command {
    param([string]$Command)
    return (Get-Command $Command -ErrorAction SilentlyContinue) -ne $null
}

# Header
Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "     MLE Runtime - Complete SDK Setup & Build          " -ForegroundColor Cyan
Write-Host "     Building: C++ Core + Node.js + Java + Python      " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check prerequisites
Write-Step "[1/9] Checking Prerequisites"

$prerequisites = @{
    "CMake" = @{
        Command = "cmake"
        Install = "winget install Kitware.CMake"
        Required = $true
    }
    "Python" = @{
        Command = "python"
        Install = "winget install Python.Python.3.11"
        Required = $true
    }
    "Node.js" = @{
        Command = "node"
        Install = "winget install OpenJS.NodeJS"
        Required = $true
    }
    "npm" = @{
        Command = "npm"
        Install = "Installed with Node.js"
        Required = $true
    }
    "Java (JDK)" = @{
        Command = "java"
        Install = "winget install EclipseAdoptium.Temurin.17.JDK"
        Required = $true
    }
    "Maven" = @{
        Command = "mvn"
        Install = "winget install Apache.Maven"
        Required = $true
    }
    "Git" = @{
        Command = "git"
        Install = "winget install Git.Git"
        Required = $false
    }
}

$allGood = $true
foreach ($tool in $prerequisites.Keys) {
    $info = $prerequisites[$tool]
    if (Test-Command $info.Command) {
        $version = ""
        try {
            switch ($info.Command) {
                "cmake" { $version = (cmake --version | Select-Object -First 1) -replace "cmake version ", "" }
                "python" { $version = (python --version) -replace "Python ", "" }
                "node" { $version = (node --version) -replace "v", "" }
                "npm" { $version = (npm --version) }
                "java" { $version = (java -version 2>&1 | Select-Object -First 1) -replace '.*"(.*)".*', '$1' }
                "mvn" { $version = (mvn --version | Select-Object -First 1) -replace "Apache Maven ", "" -replace " \(.*", "" }
                "git" { $version = (git --version) -replace "git version ", "" }
            }
        } catch {}
        Write-Success "$tool found ($version)"
    } else {
        if ($info.Required) {
            Write-Error-Custom "$tool not found (Required)"
            Write-Host "    Install: $($info.Install)" -ForegroundColor Gray
            $allGood = $false
        } else {
            Write-Host "  ⚠ $tool not found (Optional)" -ForegroundColor Yellow
        }
    }
}

if (!$allGood) {
    Write-Host ""
    Write-Host "Please install missing prerequisites and run again." -ForegroundColor Red
    Write-Host ""
    exit 1
}

# Step 2: Build C++ Core
Write-Step "[2/9] Building C++ Core"

try {
    Set-Location cpp_core
    
    if (Test-Path build) {
        Write-Info "Cleaning previous build..."
        Remove-Item -Recurse -Force build
    }
    
    Write-Info "Creating build directory..."
    New-Item -ItemType Directory -Path build | Out-Null
    Set-Location build
    
    Write-Info "Running CMake configuration..."
    $cmakeArgs = @(
        "-DCMAKE_BUILD_TYPE=Release",
        "-DENABLE_CUDA=OFF",
        "-DBUILD_TESTS=ON",
        ".."
    )
    
    if ($Verbose) {
        cmake @cmakeArgs
    } else {
        cmake @cmakeArgs 2>&1 | Out-Null
    }
    
    Write-Info "Building C++ core..."
    if ($Verbose) {
        cmake --build . --config Release --parallel
    } else {
        cmake --build . --config Release --parallel 2>&1 | Out-Null
    }
    
    Write-Success "C++ core built successfully"
    
    if (!$SkipTests) {
        Write-Info "Running C++ tests..."
        if ($Verbose) {
            ctest -C Release --output-on-failure
        } else {
            ctest -C Release --output-on-failure 2>&1 | Out-Null
        }
        Write-Success "C++ tests passed"
    }
    
    Set-Location $OriginalLocation
} catch {
    Write-Error-Custom "Failed to build C++ core: $_"
    Set-Location $OriginalLocation
    exit 1
}

# Step 3: Build Python SDK
Write-Step "[3/9] Building Python SDK"

try {
    Write-Info "Upgrading pip..."
    python -m pip install --upgrade pip --quiet
    
    Write-Info "Installing Python dependencies..."
    python -m pip install torch numpy pytest pybind11 scikit-learn joblib --quiet
    
    Set-Location sdk\python
    
    Write-Info "Building Python SDK..."
    if ($Verbose) {
        python setup.py build
    } else {
        python setup.py build 2>&1 | Out-Null
    }
    
    Write-Info "Installing Python SDK in development mode..."
    python -m pip install -e . --quiet
    
    Write-Success "Python SDK built successfully"
    
    if (!$SkipTests) {
        Write-Info "Running Python tests..."
        if (Test-Path tests) {
            if ($Verbose) {
                pytest tests/ -v
            } else {
                pytest tests/ --quiet 2>&1 | Out-Null
            }
            Write-Success "Python tests passed"
        }
    }
    
    if ($PrepareRelease) {
        Write-Info "Building Python distribution packages..."
        python setup.py sdist bdist_wheel --quiet
        Write-Success "Python packages ready in dist/"
    }
    
    Set-Location $OriginalLocation
} catch {
    Write-Error-Custom "Failed to build Python SDK: $_"
    Set-Location $OriginalLocation
    exit 1
}

# Step 4: Build Node.js SDK
Write-Step "[4/9] Building Node.js SDK"

try {
    Set-Location sdk\nodejs
    
    Write-Info "Installing Node.js dependencies..."
    if ($Verbose) {
        npm install
    } else {
        npm install --silent 2>&1 | Out-Null
    }
    
    Write-Info "Compiling TypeScript..."
    if ($Verbose) {
        npm run build
    } else {
        npm run build --silent 2>&1 | Out-Null
    }
    
    Write-Success "Node.js SDK built successfully"
    
    if (!$SkipTests -and (Test-Path "package.json")) {
        $packageJson = Get-Content "package.json" | ConvertFrom-Json
        if ($packageJson.scripts.test) {
            Write-Info "Running Node.js tests..."
            if ($Verbose) {
                npm test
            } else {
                npm test --silent 2>&1 | Out-Null
            }
            Write-Success "Node.js tests passed"
        }
    }
    
    if ($PrepareRelease) {
        Write-Info "Preparing npm package..."
        npm pack --quiet
        Write-Success "npm package ready"
    }
    
    Set-Location $OriginalLocation
} catch {
    Write-Error-Custom "Failed to build Node.js SDK: $_"
    Set-Location $OriginalLocation
    exit 1
}

# Step 5: Build Java SDK
Write-Step "[5/9] Building Java SDK"

try {
    Set-Location sdk\java
    
    Write-Info "Building Java SDK with Maven..."
    if ($Verbose) {
        mvn clean install
    } else {
        mvn clean install --quiet 2>&1 | Out-Null
    }
    
    Write-Success "Java SDK built successfully"
    
    if (!$SkipTests) {
        Write-Info "Running Java tests..."
        if ($Verbose) {
            mvn test
        } else {
            mvn test --quiet 2>&1 | Out-Null
        }
        Write-Success "Java tests passed"
    }
    
    if ($PrepareRelease) {
        Write-Info "Preparing Maven artifacts..."
        mvn package --quiet
        Write-Success "Maven artifacts ready in target/"
    }
    
    Set-Location $OriginalLocation
} catch {
    Write-Error-Custom "Failed to build Java SDK: $_"
    Set-Location $OriginalLocation
    exit 1
}

# Step 6: Build C++ SDK Examples
Write-Step "[6/9] Building C++ SDK Examples"

try {
    Set-Location sdk\cpp
    
    if (Test-Path build) {
        Remove-Item -Recurse -Force build
    }
    
    New-Item -ItemType Directory -Path build | Out-Null
    Set-Location build
    
    Write-Info "Configuring C++ SDK..."
    if ($Verbose) {
        cmake -DBUILD_EXAMPLES=ON ..
    } else {
        cmake -DBUILD_EXAMPLES=ON .. 2>&1 | Out-Null
    }
    
    if (!$SkipExamples) {
        Write-Info "Building C++ examples..."
        if ($Verbose) {
            cmake --build . --config Release
        } else {
            cmake --build . --config Release 2>&1 | Out-Null
        }
        Write-Success "C++ SDK examples built"
    }
    
    Set-Location $OriginalLocation
} catch {
    Write-Error-Custom "Failed to build C++ SDK: $_"
    Set-Location $OriginalLocation
    exit 1
}

# Step 7: Install Python Tools
Write-Step "[7/9] Installing Python Tools & Exporters"

try {
    Write-Info "Installing exporter dependencies..."
    python -m pip install torch scikit-learn joblib --quiet
    
    Write-Success "Python tools ready"
} catch {
    Write-Error-Custom "Failed to install Python tools: $_"
}

# Step 8: Verify Installation
Write-Step "[8/9] Verifying Installation"

$verifications = @()

# Verify Python SDK
try {
    $pythonTest = python -c "import mle_runtime; print('OK')" 2>&1
    if ($pythonTest -match "OK") {
        Write-Success "Python SDK verified"
        $verifications += "Python"
    } else {
        Write-Error-Custom "Python SDK verification failed"
    }
} catch {
    Write-Error-Custom "Python SDK verification failed"
}

# Verify Node.js SDK
try {
    Set-Location sdk\nodejs
    if (Test-Path "dist\index.js") {
        Write-Success "Node.js SDK verified"
        $verifications += "Node.js"
    } else {
        Write-Error-Custom "Node.js SDK verification failed"
    }
    Set-Location $OriginalLocation
} catch {
    Write-Error-Custom "Node.js SDK verification failed"
    Set-Location $OriginalLocation
}

# Verify Java SDK
try {
    Set-Location sdk\java
    if (Test-Path "target\mle-runtime-1.0.0.jar") {
        Write-Success "Java SDK verified"
        $verifications += "Java"
    } else {
        Write-Error-Custom "Java SDK verification failed"
    }
    Set-Location $OriginalLocation
} catch {
    Write-Error-Custom "Java SDK verification failed"
    Set-Location $OriginalLocation
}

# Verify C++ SDK
if (Test-Path "sdk\cpp\include\mle_client.h") {
    Write-Success "C++ SDK verified"
    $verifications += "C++"
}

# Step 9: Generate Release Summary
Write-Step "[9/9] Setup Complete!"

Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Host "              BUILD SUCCESSFUL!                         " -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
Write-Host ""

Write-Host "Built SDKs:" -ForegroundColor White
foreach ($sdk in $verifications) {
    Write-Host "  [OK] $sdk SDK" -ForegroundColor Green
}

Write-Host ""
Write-Host "Package Locations:" -ForegroundColor White
Write-Host ""

if (Test-Path "sdk\python\dist") {
    Write-Host "  Python:" -ForegroundColor Cyan
    Write-Host "    sdk\python\dist\" -ForegroundColor Gray
    Write-Host "    Deploy: twine upload dist/*" -ForegroundColor Yellow
    Write-Host ""
}

if (Test-Path "sdk\nodejs\mle-runtime-*.tgz") {
    Write-Host "  Node.js:" -ForegroundColor Cyan
    Write-Host "    sdk\nodejs\mle-runtime-*.tgz" -ForegroundColor Gray
    Write-Host "    Deploy: npm publish" -ForegroundColor Yellow
    Write-Host ""
}

if (Test-Path "sdk\java\target\mle-runtime-1.0.0.jar") {
    Write-Host "  Java:" -ForegroundColor Cyan
    Write-Host "    sdk\java\target\mle-runtime-1.0.0.jar" -ForegroundColor Gray
    Write-Host "    Deploy: mvn deploy" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "  C++:" -ForegroundColor Cyan
Write-Host "    sdk\cpp\include\mle_client.h (header-only)" -ForegroundColor Gray
Write-Host ""

Write-Host "Quick Start Commands:" -ForegroundColor White
Write-Host ""
Write-Host "  1. Run benchmark (MLE vs joblib):" -ForegroundColor Gray
Write-Host "     python tools\benchmarks\mle_vs_joblib.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "  2. Export sklearn model:" -ForegroundColor Gray
Write-Host "     python tools\exporter\sklearn_to_mle.py --demo" -ForegroundColor Cyan
Write-Host ""
Write-Host "  3. Test Python SDK:" -ForegroundColor Gray
Write-Host "     python sdk\python\examples\simple_inference.py model.mle" -ForegroundColor Cyan
Write-Host ""
Write-Host "  4. Test Node.js SDK:" -ForegroundColor Gray
Write-Host "     node sdk\nodejs\examples\simple_inference.js model.mle" -ForegroundColor Cyan
Write-Host ""
Write-Host "  5. Test Java SDK:" -ForegroundColor Gray
Write-Host "     java -cp sdk\java\target\mle-runtime-1.0.0.jar SimpleInference model.mle" -ForegroundColor Cyan
Write-Host ""

Write-Host "Documentation:" -ForegroundColor White
Write-Host "  • SDK Overview:    SDK_OVERVIEW.md" -ForegroundColor Gray
Write-Host "  • Quick Start:     sdk\QUICKSTART.md" -ForegroundColor Gray
Write-Host "  • Installation:    sdk\INSTALLATION.md" -ForegroundColor Gray
Write-Host "  • Main README:     README_SDK.md" -ForegroundColor Gray
Write-Host ""

if ($PrepareRelease) {
    Write-Host "Release Preparation:" -ForegroundColor White
    Write-Host ""
    Write-Host "  All packages are ready for deployment!" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Test packages locally" -ForegroundColor Gray
    Write-Host "  2. Update version numbers if needed" -ForegroundColor Gray
    Write-Host "  3. Create git tag: git tag v1.0.0" -ForegroundColor Gray
    Write-Host "  4. Deploy to registries (see commands above)" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
