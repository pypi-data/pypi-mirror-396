# SDK Installation Guide

Complete installation instructions for all MLE Runtime SDKs.

## Prerequisites

### All Platforms

**C++ Core (Required for all SDKs)**
- CMake 3.15 or higher
- C++20 compatible compiler:
  - GCC 10+ (Linux)
  - Clang 12+ (macOS)
  - MSVC 2019+ (Windows)

### Language-Specific

**Node.js SDK**
- Node.js 16.0 or higher
- npm or yarn

**Java SDK**
- JDK 11 or higher
- Maven 3.6+ or Gradle 7+

**Python SDK**
- Python 3.8 or higher
- pip

**C++ SDK**
- No additional requirements (uses core)

---

## Quick Install (Pre-built Packages)

### Node.js
```bash
npm install @mle/runtime
```

### Java (Maven)
```xml
<dependency>
    <groupId>com.mle</groupId>
    <artifactId>mle-runtime</artifactId>
    <version>1.0.0</version>
</dependency>
```

### Java (Gradle)
```gradle
implementation 'com.mle:mle-runtime:1.0.0'
```

### Python
```bash
pip install mle-runtime
```

### C++
```bash
# Header-only - just copy the header
cp sdk/cpp/include/mle_client.h /usr/local/include/
```

---

## Build from Source

### Step 1: Build C++ Core

All SDKs depend on the C++ core library.

#### Linux / macOS
```bash
cd cpp_core
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
cmake --build . --config Release
sudo cmake --install .
```

#### Windows (PowerShell)
```powershell
cd cpp_core
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
cmake --build . --config Release
cmake --install .
```

### Step 2: Build Language SDKs

#### Node.js SDK

```bash
cd sdk/nodejs

# Install dependencies
npm install

# Build TypeScript
npm run build

# Build native addon
npm run build:native

# Run tests
npm test

# Install globally (optional)
npm link
```

**Verify installation:**
```bash
node -e "const mle = require('@mle/runtime'); console.log('MLE loaded successfully');"
```

#### Java SDK

```bash
cd sdk/java

# Build with Maven
mvn clean install

# Or with Gradle
gradle build

# Run tests
mvn test

# Install to local Maven repository
mvn install
```

**Verify installation:**
```bash
java -cp target/mle-runtime-1.0.0.jar com.mle.runtime.MLEEngine
```

#### Python SDK

```bash
cd sdk/python

# Install in development mode
pip install -e .

# Or build wheel
python setup.py bdist_wheel
pip install dist/mle_runtime-1.0.1-*.whl

# Run tests
pytest tests/

# Install for production
pip install .
```

**Verify installation:**
```bash
python -c "import mle_runtime; print('MLE loaded successfully')"
```

#### C++ SDK

```bash
cd sdk/cpp
mkdir build && cd build

# Configure
cmake ..

# Build examples (optional)
cmake -DBUILD_EXAMPLES=ON ..
make

# Install headers
sudo make install
```

**Verify installation:**
```bash
g++ -std=c++20 -o test test.cpp -lmle_core
./test
```

---

## Platform-Specific Instructions

### Ubuntu / Debian

```bash
# Install prerequisites
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    cmake \
    git \
    python3-dev \
    nodejs \
    npm \
    default-jdk \
    maven

# Build C++ core
cd cpp_core
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j$(nproc)
sudo make install

# Build all SDKs
cd ../../sdk

# Node.js
cd nodejs && npm install && npm run build && cd ..

# Java
cd java && mvn clean install && cd ..

# Python
cd python && pip install -e . && cd ..
```

### macOS

```bash
# Install prerequisites with Homebrew
brew install cmake node python@3.11 openjdk maven

# Build C++ core
cd cpp_core
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j$(sysctl -n hw.ncpu)
sudo make install

# Build all SDKs (same as Ubuntu)
```

### Windows

```powershell
# Install prerequisites
# - Visual Studio 2019+ with C++ tools
# - CMake (from cmake.org)
# - Node.js (from nodejs.org)
# - Python (from python.org)
# - JDK (from adoptium.net)

# Build C++ core
cd cpp_core
mkdir build
cd build
cmake -G "Visual Studio 16 2019" -A x64 ..
cmake --build . --config Release
cmake --install .

# Build Node.js SDK
cd ..\..\sdk\nodejs
npm install
npm run build

# Build Java SDK
cd ..\java
mvn clean install

# Build Python SDK
cd ..\python
pip install -e .
```

---

## Docker Installation

### Pre-built Docker Images

```bash
# Node.js
docker pull mle/runtime-nodejs:latest

# Java
docker pull mle/runtime-java:latest

# Python
docker pull mle/runtime-python:latest
```

### Build Your Own

```dockerfile
# Node.js
FROM node:18
RUN npm install -g @mle/runtime
COPY model.mle /app/
WORKDIR /app
CMD ["node", "server.js"]

# Java
FROM openjdk:17
COPY target/app.jar /app/
COPY model.mle /app/
CMD ["java", "-jar", "/app/app.jar"]

# Python
FROM python:3.11
RUN pip install mle-runtime
COPY model.mle /app/
WORKDIR /app
CMD ["python", "server.py"]
```

---

## Troubleshooting

### Common Issues

#### "Cannot find libmle_core.so"

**Solution:**
```bash
# Linux
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

# macOS
export DYLD_LIBRARY_PATH=/usr/local/lib:$DYLD_LIBRARY_PATH

# Or add to system library path
sudo ldconfig  # Linux
```

#### "CMake version too old"

**Solution:**
```bash
# Ubuntu
sudo apt-get install cmake

# Or install from source
wget https://github.com/Kitware/CMake/releases/download/v3.27.0/cmake-3.27.0.tar.gz
tar -xzf cmake-3.27.0.tar.gz
cd cmake-3.27.0
./bootstrap && make && sudo make install
```

#### "C++20 not supported"

**Solution:**
```bash
# Ubuntu - install newer GCC
sudo apt-get install gcc-11 g++-11
export CC=gcc-11
export CXX=g++-11

# macOS - update Xcode
xcode-select --install
```

#### Node.js: "Cannot find module 'mle_node'"

**Solution:**
```bash
cd sdk/nodejs
npm rebuild
```

#### Java: "UnsatisfiedLinkError: no mle_jni"

**Solution:**
```bash
# Ensure native library is in java.library.path
java -Djava.library.path=/usr/local/lib -jar app.jar
```

#### Python: "ImportError: No module named '_mle_core'"

**Solution:**
```bash
cd sdk/python
pip install --force-reinstall -e .
```

---

## Verification

### Test All SDKs

```bash
# Node.js
node sdk/nodejs/examples/simple_inference.js model.mle

# Java
java -cp sdk/java/target/mle-runtime-1.0.0.jar SimpleInference model.mle

# Python
python sdk/python/examples/simple_inference.py model.mle

# C++
./sdk/cpp/build/simple_inference model.mle
```

### Run Benchmarks

```bash
# Compare with joblib
python tools/benchmarks/mle_vs_joblib.py
```

---

## Environment Variables

### Optional Configuration

```bash
# Model cache directory
export MLE_CACHE_DIR=/tmp/mle_cache

# Log level (DEBUG, INFO, WARN, ERROR)
export MLE_LOG_LEVEL=INFO

# Default device (CPU, CUDA)
export MLE_DEVICE=CPU

# Thread count for CPU inference
export MLE_NUM_THREADS=4
```

---

## Next Steps

1. ✅ Installation complete
2. 📖 Read [QUICKSTART.md](QUICKSTART.md) for usage examples
3. 🚀 Deploy your first model
4. 📊 Run benchmarks to see performance gains

## Support

- 📖 Documentation: See individual SDK READMEs
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions
- 📧 Email: support@mle.dev

---

**Installation complete! Start building fast ML applications.** 🚀
