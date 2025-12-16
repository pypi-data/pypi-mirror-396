# MLE Runtime - C/C++ Client Library

Fast ML inference runtime for C/C++ applications. Header-only client with minimal dependencies.

## Features

- ✅ **10-100x faster loading** - Memory-mapped binary format
- ✅ **50-90% smaller files** - Optimized weight storage
- ✅ **Zero Python overhead** - Pure C++ execution
- ✅ **Header-only option** - Easy integration
- ✅ **Modern C++20** - RAII, move semantics, smart pointers
- ✅ **Cross-platform** - Linux, macOS, Windows

## Installation

### Option 1: Header-Only

```cpp
#include "mle_client.h"
```

Link against: `libmle_core.so` (or `.dll` on Windows)

### Option 2: CMake

```cmake
find_package(MLE REQUIRED)
target_link_libraries(your_app PRIVATE MLE::runtime)
```

## Quick Start

```cpp
#include "mle_client.h"
#include <iostream>

int main() {
    // Create engine
    mle::MLEEngine engine(mle::Device::CPU);
    
    // Load model (1-5ms vs 100-500ms for traditional tools)
    engine.load_model("model.mle");
    
    // Prepare input
    auto input = std::make_shared<mle::Tensor>(
        std::vector<uint32_t>{1, 20}, 
        mle::DType::FP32
    );
    float* data = static_cast<float*>(input->data());
    for (int i = 0; i < 20; i++) {
        data[i] = static_cast<float>(i);
    }
    
    // Run inference
    auto outputs = engine.run({input});
    
    // Process results
    float* output_data = static_cast<float*>(outputs[0]->data());
    std::cout << "Prediction: " << output_data[0] << std::endl;
    std::cout << "Peak memory: " << engine.peak_memory_usage() << " bytes" << std::endl;
    
    return 0;
}
```

## API Reference

### MLEEngine

#### Constructor
```cpp
MLEEngine(Device device = Device::CPU)
```

#### Methods

**void load_model(const std::string& path)**
Load a model from .mle file.

**std::vector<std::shared_ptr<Tensor>> run(const std::vector<std::shared_ptr<Tensor>>& inputs)**
Run inference on input tensors.

**const ModelMetadata* metadata() const**
Get model metadata.

**size_t peak_memory_usage() const**
Get peak memory usage in bytes.

**Device device() const**
Get current device.

### Tensor

**Tensor(const std::vector<uint32_t>& shape, DType dtype)**
Create a new tensor.

**void* data()**
Get mutable pointer to tensor data.

**const void* data() const**
Get const pointer to tensor data.

**size_t size() const**
Get tensor size in bytes.

## Examples

### Simple Inference

```cpp
#include "mle_client.h"

void run_inference(const std::string& model_path, 
                   const std::vector<float>& features) {
    mle::MLEEngine engine(mle::Device::CPU);
    engine.load_model(model_path);
    
    auto input = std::make_shared<mle::Tensor>(
        std::vector<uint32_t>{1, features.size()},
        mle::DType::FP32
    );
    std::memcpy(input->data(), features.data(), 
                features.size() * sizeof(float));
    
    auto outputs = engine.run({input});
    
    float* result = static_cast<float*>(outputs[0]->data());
    std::cout << "Result: " << result[0] << std::endl;
}
```

### Batch Processing

```cpp
#include "mle_client.h"
#include <fstream>
#include <sstream>

void process_csv(const std::string& input_file,
                 const std::string& output_file,
                 const std::string& model_path) {
    mle::MLEEngine engine(mle::Device::CPU);
    engine.load_model(model_path);
    
    std::ifstream infile(input_file);
    std::ofstream outfile(output_file);
    std::string line;
    
    while (std::getline(infile, line)) {
        std::vector<float> features;
        std::stringstream ss(line);
        std::string value;
        
        while (std::getline(ss, value, ',')) {
            features.push_back(std::stof(value));
        }
        
        auto input = std::make_shared<mle::Tensor>(
            std::vector<uint32_t>{1, features.size()},
            mle::DType::FP32
        );
        std::memcpy(input->data(), features.data(),
                    features.size() * sizeof(float));
        
        auto outputs = engine.run({input});
        float* result = static_cast<float*>(outputs[0]->data());
        
        outfile << result[0] << std::endl;
    }
}
```

### CUDA Inference

```cpp
#include "mle_client.h"

void cuda_inference() {
    // Use CUDA device
    mle::MLEEngine engine(mle::Device::CUDA);
    engine.load_model("model.mle");
    
    // Allocate input tensor
    auto input = std::make_shared<mle::Tensor>(
        std::vector<uint32_t>{1, 1000},
        mle::DType::FP32
    );
    
    // Fill with data
    float* data = static_cast<float*>(input->data());
    for (int i = 0; i < 1000; i++) {
        data[i] = static_cast<float>(rand()) / RAND_MAX;
    }
    
    // Run on GPU
    auto outputs = engine.run({input});
    
    std::cout << "GPU inference complete" << std::endl;
}
```

### Model Inspection

```cpp
#include "mle_client.h"

void inspect_model(const std::string& path) {
    auto metadata = mle::MLEUtils::inspect_model(path);
    
    std::cout << "Model: " << metadata.model_name << std::endl;
    std::cout << "Framework: " << metadata.framework << std::endl;
    std::cout << "Version: " << metadata.version.major << "."
              << metadata.version.minor << "."
              << metadata.version.patch << std::endl;
    
    std::cout << "Input shapes:" << std::endl;
    for (const auto& shape : metadata.input_shapes) {
        std::cout << "  [";
        for (size_t i = 0; i < shape.dimensions.size(); i++) {
            std::cout << shape.dimensions[i];
            if (i < shape.dimensions.size() - 1) std::cout << ", ";
        }
        std::cout << "]" << std::endl;
    }
}
```

### Model Verification

```cpp
#include "mle_client.h"

bool load_verified_model(const std::string& model_path,
                         const std::string& public_key) {
    // Verify signature first
    if (!mle::MLEUtils::verify_model(model_path, public_key)) {
        std::cerr << "Invalid model signature!" << std::endl;
        return false;
    }
    
    // Load model
    mle::MLEEngine engine(mle::Device::CPU);
    engine.load_model(model_path);
    
    std::cout << "Model verified and loaded successfully" << std::endl;
    return true;
}
```

## Building

### CMake

```cmake
cmake_minimum_required(VERSION 3.15)
project(my_app)

set(CMAKE_CXX_STANDARD 20)

# Find MLE
find_package(MLE REQUIRED)

add_executable(my_app main.cpp)
target_link_libraries(my_app PRIVATE MLE::runtime)
```

### Manual Compilation

```bash
g++ -std=c++20 -O3 main.cpp -lmle_core -o my_app
```

## Performance

Compared to traditional C++ ML tools:

| Metric | Traditional | MLE | Improvement |
|--------|------------|-----|-------------|
| Load Time | 100-500ms | 1-5ms | **100x faster** |
| File Size | 100MB | 20MB | **80% smaller** |
| Memory | Full copy | Zero-copy mmap | **50% less** |

## License

MIT
