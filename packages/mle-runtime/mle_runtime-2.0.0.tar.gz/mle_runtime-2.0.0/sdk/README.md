# MLE Runtime - Client SDKs

Official client libraries for the MLE (Machine Learning Engine) runtime across multiple languages and platforms.

## Overview

MLE provides fast ML inference with memory-mapped loading, delivering **10-100x faster** performance than traditional serialization tools like joblib/pickle.

## Available SDKs

### 🟦 Node.js / TypeScript
**Location:** `sdk/nodejs/`

```bash
npm install @mle/runtime
```

```typescript
import { MLEEngine, Device } from '@mle/runtime';

const engine = new MLEEngine(Device.CPU);
await engine.loadModel('model.mle');
const outputs = await engine.run([input]);
```

**Features:**
- Full TypeScript support
- Async/await API
- Native C++ performance via N-API
- Works with Express, Fastify, etc.

[Full Documentation](nodejs/README.md)

---

### ☕ Java
**Location:** `sdk/java/`

```xml
<dependency>
    <groupId>com.mle</groupId>
    <artifactId>mle-runtime</artifactId>
    <version>1.0.0</version>
</dependency>
```

```java
try (MLEEngine engine = new MLEEngine(Device.CPU)) {
    engine.loadModel("model.mle");
    List<float[]> outputs = engine.run(inputs);
}
```

**Features:**
- AutoCloseable for resource management
- Zero-copy direct buffer support
- JNI bindings to native C++
- Works with Spring Boot, Micronaut, etc.

[Full Documentation](java/README.md)

---

### 🐍 Python
**Location:** `sdk/python/`

```bash
pip install mle-runtime
```

```python
import mle_runtime

engine = mle_runtime.MLEEngine(mle_runtime.Device.CPU)
engine.load_model("model.mle")
outputs = engine.run([input_array])
```

**Features:**
- NumPy integration
- Context manager support
- Type hints included
- 10-100x faster than joblib
- Works with Flask, FastAPI, etc.

[Full Documentation](python/README.md)

---

### ⚡ C/C++
**Location:** `sdk/cpp/`

```cpp
#include "mle_client.h"

mle::MLEEngine engine(mle::Device::CPU);
engine.load_model("model.mle");
auto outputs = engine.run({input});
```

**Features:**
- Modern C++20
- Header-only option
- RAII and move semantics
- Zero overhead abstraction
- CMake integration

[Full Documentation](cpp/README.md)

---

## Performance Comparison

All SDKs provide similar performance characteristics:

| Metric | Traditional Tools | MLE | Improvement |
|--------|------------------|-----|-------------|
| **Load Time** | 100-500ms | 1-5ms | **100x faster** |
| **File Size** | 100MB | 20MB | **80% smaller** |
| **Inference** | Python/JVM | Native C++ | **2-5x faster** |
| **Memory** | Full copy | Zero-copy mmap | **50% less** |

## Common Features

All SDKs support:

✅ Memory-mapped model loading  
✅ CPU and CUDA execution  
✅ Model metadata inspection  
✅ Cryptographic signature verification  
✅ Zero-copy inference (where applicable)  
✅ Cross-platform support (Linux, macOS, Windows)  

## Quick Start by Language

### Node.js
```bash
cd sdk/nodejs
npm install
npm run build
```

### Java
```bash
cd sdk/java
mvn clean install
```

### Python
```bash
cd sdk/python
pip install -e .
```

### C++
```bash
cd sdk/cpp
mkdir build && cd build
cmake ..
make
```

## Example Use Cases

### Web API Server
- **Node.js**: Express, Fastify
- **Java**: Spring Boot, Micronaut
- **Python**: Flask, FastAPI
- **C++**: Crow, Drogon

### Batch Processing
- **Node.js**: Stream processing
- **Java**: Apache Spark, Flink
- **Python**: Pandas, Dask
- **C++**: High-performance pipelines

### Edge Deployment
- **Node.js**: Electron apps
- **Java**: Android apps
- **Python**: Raspberry Pi
- **C++**: Embedded systems

### Microservices
- **Node.js**: Serverless functions
- **Java**: Kubernetes pods
- **Python**: Docker containers
- **C++**: Minimal footprint services

## Building from Source

### Prerequisites
- CMake 3.15+
- C++20 compiler (GCC 10+, Clang 12+, MSVC 2019+)
- Language-specific tools (Node.js, JDK, Python)

### Build All SDKs
```bash
# Build C++ core first
cd cpp_core
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
cmake --build . --config Release

# Then build language bindings
cd ../../sdk

# Node.js
cd nodejs && npm install && npm run build && cd ..

# Java
cd java && mvn clean install && cd ..

# Python
cd python && pip install -e . && cd ..
```

## Architecture

```
┌─────────────────────────────────────────┐
│         Application Layer               │
│  (Node.js, Java, Python, C++ apps)      │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│         SDK Layer (This Directory)      │
│  ┌──────────┬──────────┬──────────┐     │
│  │ Node.js  │  Java    │  Python  │     │
│  │ Bindings │  JNI     │  PyBind  │     │
│  └──────────┴──────────┴──────────┘     │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│         C++ Core Engine                 │
│  (cpp_core/ - Native inference)         │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│         Hardware Layer                  │
│  (CPU, CUDA, Memory-mapped files)       │
└─────────────────────────────────────────┘
```

## Contributing

Contributions welcome! Each SDK has its own conventions:

- **Node.js**: Follow TypeScript best practices
- **Java**: Follow Google Java Style Guide
- **Python**: Follow PEP 8
- **C++**: Follow C++ Core Guidelines

## License

MIT License - see LICENSE file for details

## Support

- 📖 Documentation: See individual SDK READMEs
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions
- 📧 Email: support@mle.dev

---

**Choose your language and start building fast ML applications!** 🚀
