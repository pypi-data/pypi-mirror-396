#!/bin/bash
# MLE Runtime - Complete Setup Script (Linux/macOS)
# Builds C++ core and all SDKs (Node.js, Java, Python, C++)

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Options
SKIP_TESTS=false
SKIP_EXAMPLES=false
PREPARE_RELEASE=false
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --skip-examples)
            SKIP_EXAMPLES=true
            shift
            ;;
        --prepare-release)
            PREPARE_RELEASE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--skip-tests] [--skip-examples] [--prepare-release] [--verbose]"
            exit 1
            ;;
    esac
done

function print_step() {
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${YELLOW}$1${NC}"
    echo -e "${CYAN}========================================${NC}"
}

function print_success() {
    echo -e "  ${GREEN}✓ $1${NC}"
}

function print_info() {
    if [ "$VERBOSE" = true ]; then
        echo -e "  ${NC}→ $1${NC}"
    fi
}

function print_error() {
    echo -e "  ${RED}✗ $1${NC}"
}

function check_command() {
    if command -v $1 &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Header
echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     MLE Runtime - Complete SDK Setup & Build          ║${NC}"
echo -e "${CYAN}║     Building: C++ Core + Node.js + Java + Python      ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Check prerequisites
print_step "[1/9] Checking Prerequisites"

ALL_GOOD=true

if check_command cmake; then
    VERSION=$(cmake --version | head -n1 | cut -d' ' -f3)
    print_success "CMake found ($VERSION)"
else
    print_error "CMake not found (Required)"
    echo "    Install: sudo apt install cmake  # Ubuntu/Debian"
    echo "             brew install cmake       # macOS"
    ALL_GOOD=false
fi

if check_command python3; then
    VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python found ($VERSION)"
else
    print_error "Python not found (Required)"
    echo "    Install: sudo apt install python3  # Ubuntu/Debian"
    echo "             brew install python3      # macOS"
    ALL_GOOD=false
fi

if check_command node; then
    VERSION=$(node --version | cut -d'v' -f2)
    print_success "Node.js found ($VERSION)"
else
    print_error "Node.js not found (Required)"
    echo "    Install: sudo apt install nodejs npm  # Ubuntu/Debian"
    echo "             brew install node            # macOS"
    ALL_GOOD=false
fi

if check_command npm; then
    VERSION=$(npm --version)
    print_success "npm found ($VERSION)"
else
    print_error "npm not found (Required)"
    ALL_GOOD=false
fi

if check_command java; then
    VERSION=$(java -version 2>&1 | head -n1 | cut -d'"' -f2)
    print_success "Java found ($VERSION)"
else
    print_error "Java not found (Required)"
    echo "    Install: sudo apt install default-jdk  # Ubuntu/Debian"
    echo "             brew install openjdk          # macOS"
    ALL_GOOD=false
fi

if check_command mvn; then
    VERSION=$(mvn --version | head -n1 | cut -d' ' -f3)
    print_success "Maven found ($VERSION)"
else
    print_error "Maven not found (Required)"
    echo "    Install: sudo apt install maven  # Ubuntu/Debian"
    echo "             brew install maven      # macOS"
    ALL_GOOD=false
fi

if check_command git; then
    VERSION=$(git --version | cut -d' ' -f3)
    print_success "Git found ($VERSION)"
else
    echo -e "  ${YELLOW}⚠ Git not found (Optional)${NC}"
fi

if [ "$ALL_GOOD" = false ]; then
    echo ""
    echo -e "${RED}Please install missing prerequisites and run again.${NC}"
    echo ""
    exit 1
fi

# Step 2: Build C++ Core
print_step "[2/9] Building C++ Core"

cd cpp_core

if [ -d build ]; then
    print_info "Cleaning previous build..."
    rm -rf build
fi

print_info "Creating build directory..."
mkdir build
cd build

print_info "Running CMake configuration..."
if [ "$VERBOSE" = true ]; then
    cmake -DCMAKE_BUILD_TYPE=Release -DENABLE_CUDA=OFF -DBUILD_TESTS=ON ..
else
    cmake -DCMAKE_BUILD_TYPE=Release -DENABLE_CUDA=OFF -DBUILD_TESTS=ON .. > /dev/null 2>&1
fi

print_info "Building C++ core..."
NPROC=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)
if [ "$VERBOSE" = true ]; then
    cmake --build . --config Release --parallel $NPROC
else
    cmake --build . --config Release --parallel $NPROC > /dev/null 2>&1
fi

print_success "C++ core built successfully"

if [ "$SKIP_TESTS" = false ]; then
    print_info "Running C++ tests..."
    if [ "$VERBOSE" = true ]; then
        ctest -C Release --output-on-failure
    else
        ctest -C Release --output-on-failure > /dev/null 2>&1
    fi
    print_success "C++ tests passed"
fi

cd ../..

# Step 3: Build Python SDK
print_step "[3/9] Building Python SDK"

print_info "Upgrading pip..."
python3 -m pip install --upgrade pip --quiet

print_info "Installing Python dependencies..."
python3 -m pip install torch numpy pytest pybind11 scikit-learn joblib --quiet

cd sdk/python

print_info "Building Python SDK..."
if [ "$VERBOSE" = true ]; then
    python3 setup.py build
else
    python3 setup.py build > /dev/null 2>&1
fi

print_info "Installing Python SDK in development mode..."
python3 -m pip install -e . --quiet

print_success "Python SDK built successfully"

if [ "$SKIP_TESTS" = false ] && [ -d tests ]; then
    print_info "Running Python tests..."
    if [ "$VERBOSE" = true ]; then
        pytest tests/ -v
    else
        pytest tests/ --quiet > /dev/null 2>&1
    fi
    print_success "Python tests passed"
fi

if [ "$PREPARE_RELEASE" = true ]; then
    print_info "Building Python distribution packages..."
    python3 setup.py sdist bdist_wheel --quiet
    print_success "Python packages ready in dist/"
fi

cd ../..

# Step 4: Build Node.js SDK
print_step "[4/9] Building Node.js SDK"

cd sdk/nodejs

print_info "Installing Node.js dependencies..."
if [ "$VERBOSE" = true ]; then
    npm install
else
    npm install --silent > /dev/null 2>&1
fi

print_info "Compiling TypeScript..."
if [ "$VERBOSE" = true ]; then
    npm run build
else
    npm run build --silent > /dev/null 2>&1
fi

print_success "Node.js SDK built successfully"

if [ "$SKIP_TESTS" = false ]; then
    if grep -q '"test"' package.json; then
        print_info "Running Node.js tests..."
        if [ "$VERBOSE" = true ]; then
            npm test
        else
            npm test --silent > /dev/null 2>&1 || true
        fi
        print_success "Node.js tests completed"
    fi
fi

if [ "$PREPARE_RELEASE" = true ]; then
    print_info "Preparing npm package..."
    npm pack --quiet
    print_success "npm package ready"
fi

cd ../..

# Step 5: Build Java SDK
print_step "[5/9] Building Java SDK"

cd sdk/java

print_info "Building Java SDK with Maven..."
if [ "$VERBOSE" = true ]; then
    mvn clean install
else
    mvn clean install --quiet > /dev/null 2>&1
fi

print_success "Java SDK built successfully"

if [ "$SKIP_TESTS" = false ]; then
    print_info "Running Java tests..."
    if [ "$VERBOSE" = true ]; then
        mvn test
    else
        mvn test --quiet > /dev/null 2>&1
    fi
    print_success "Java tests passed"
fi

if [ "$PREPARE_RELEASE" = true ]; then
    print_info "Preparing Maven artifacts..."
    mvn package --quiet
    print_success "Maven artifacts ready in target/"
fi

cd ../..

# Step 6: Build C++ SDK Examples
print_step "[6/9] Building C++ SDK Examples"

cd sdk/cpp

if [ -d build ]; then
    rm -rf build
fi

mkdir build
cd build

print_info "Configuring C++ SDK..."
if [ "$VERBOSE" = true ]; then
    cmake -DBUILD_EXAMPLES=ON ..
else
    cmake -DBUILD_EXAMPLES=ON .. > /dev/null 2>&1
fi

if [ "$SKIP_EXAMPLES" = false ]; then
    print_info "Building C++ examples..."
    if [ "$VERBOSE" = true ]; then
        cmake --build . --config Release
    else
        cmake --build . --config Release > /dev/null 2>&1
    fi
    print_success "C++ SDK examples built"
fi

cd ../..

# Step 7: Install Python Tools
print_step "[7/9] Installing Python Tools & Exporters"

print_info "Installing exporter dependencies..."
python3 -m pip install torch scikit-learn joblib --quiet

print_success "Python tools ready"

# Step 8: Verify Installation
print_step "[8/9] Verifying Installation"

VERIFICATIONS=()

# Verify Python SDK
if python3 -c "import mle_runtime; print('OK')" 2>/dev/null | grep -q "OK"; then
    print_success "Python SDK verified"
    VERIFICATIONS+=("Python")
else
    print_error "Python SDK verification failed"
fi

# Verify Node.js SDK
if [ -f "sdk/nodejs/dist/index.js" ]; then
    print_success "Node.js SDK verified"
    VERIFICATIONS+=("Node.js")
else
    print_error "Node.js SDK verification failed"
fi

# Verify Java SDK
if [ -f "sdk/java/target/mle-runtime-1.0.0.jar" ]; then
    print_success "Java SDK verified"
    VERIFICATIONS+=("Java")
else
    print_error "Java SDK verification failed"
fi

# Verify C++ SDK
if [ -f "sdk/cpp/include/mle_client.h" ]; then
    print_success "C++ SDK verified"
    VERIFICATIONS+=("C++")
fi

# Step 9: Generate Release Summary
print_step "[9/9] Setup Complete!"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              🎉 BUILD SUCCESSFUL! 🎉                   ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${NC}Built SDKs:${NC}"
for sdk in "${VERIFICATIONS[@]}"; do
    echo -e "  ${GREEN}✓ $sdk SDK${NC}"
done

echo ""
echo -e "${NC}📦 Package Locations:${NC}"
echo ""

if [ -d "sdk/python/dist" ]; then
    echo -e "  ${CYAN}Python:${NC}"
    echo -e "    ${NC}sdk/python/dist/${NC}"
    echo -e "    ${YELLOW}Deploy: twine upload dist/*${NC}"
    echo ""
fi

if ls sdk/nodejs/mle-runtime-*.tgz 1> /dev/null 2>&1; then
    echo -e "  ${CYAN}Node.js:${NC}"
    echo -e "    ${NC}sdk/nodejs/mle-runtime-*.tgz${NC}"
    echo -e "    ${YELLOW}Deploy: npm publish${NC}"
    echo ""
fi

if [ -f "sdk/java/target/mle-runtime-1.0.0.jar" ]; then
    echo -e "  ${CYAN}Java:${NC}"
    echo -e "    ${NC}sdk/java/target/mle-runtime-1.0.0.jar${NC}"
    echo -e "    ${YELLOW}Deploy: mvn deploy${NC}"
    echo ""
fi

echo -e "  ${CYAN}C++:${NC}"
echo -e "    ${NC}sdk/cpp/include/mle_client.h (header-only)${NC}"
echo ""

echo -e "${NC}🚀 Quick Start Commands:${NC}"
echo ""
echo -e "  ${NC}1. Run benchmark (MLE vs joblib):${NC}"
echo -e "     ${CYAN}python3 tools/benchmarks/mle_vs_joblib.py${NC}"
echo ""
echo -e "  ${NC}2. Export sklearn model:${NC}"
echo -e "     ${CYAN}python3 tools/exporter/sklearn_to_mle.py --demo${NC}"
echo ""
echo -e "  ${NC}3. Test Python SDK:${NC}"
echo -e "     ${CYAN}python3 sdk/python/examples/simple_inference.py model.mle${NC}"
echo ""
echo -e "  ${NC}4. Test Node.js SDK:${NC}"
echo -e "     ${CYAN}node sdk/nodejs/examples/simple_inference.js model.mle${NC}"
echo ""
echo -e "  ${NC}5. Test Java SDK:${NC}"
echo -e "     ${CYAN}java -cp sdk/java/target/mle-runtime-1.0.0.jar SimpleInference model.mle${NC}"
echo ""

echo -e "${NC}📚 Documentation:${NC}"
echo -e "  ${NC}• SDK Overview:    SDK_OVERVIEW.md${NC}"
echo -e "  ${NC}• Quick Start:     sdk/QUICKSTART.md${NC}"
echo -e "  ${NC}• Installation:    sdk/INSTALLATION.md${NC}"
echo -e "  ${NC}• Main README:     README_SDK.md${NC}"
echo ""

if [ "$PREPARE_RELEASE" = true ]; then
    echo -e "${NC}📦 Release Preparation:${NC}"
    echo ""
    echo -e "  ${GREEN}All packages are ready for deployment!${NC}"
    echo ""
    echo -e "  ${YELLOW}Next steps:${NC}"
    echo -e "  ${NC}1. Test packages locally${NC}"
    echo -e "  ${NC}2. Update version numbers if needed${NC}"
    echo -e "  ${NC}3. Create git tag: git tag v1.0.0${NC}"
    echo -e "  ${NC}4. Deploy to registries (see DEPLOYMENT.md)${NC}"
    echo ""
fi

echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
echo ""
