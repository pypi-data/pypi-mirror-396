#include "engine.h"
#include <cuda_runtime.h>
#include <stdexcept>

namespace mle {

class CUDADeviceContext {
public:
    CUDADeviceContext() {
        int device_count = 0;
        cudaError_t err = cudaGetDeviceCount(&device_count);
        
        if (err != cudaSuccess || device_count == 0) {
            throw std::runtime_error("No CUDA devices available");
        }
        
        // Use device 0 by default
        cudaSetDevice(0);
        
        // Get device properties
        cudaDeviceProp prop;
        cudaGetDeviceProperties(&prop, 0);
        
        device_name_ = prop.name;
        compute_capability_ = prop.major * 10 + prop.minor;
        total_memory_ = prop.totalGlobalMem;
    }
    
    ~CUDADeviceContext() {
        cudaDeviceReset();
    }
    
    const std::string& device_name() const { return device_name_; }
    int compute_capability() const { return compute_capability_; }
    size_t total_memory() const { return total_memory_; }

private:
    std::string device_name_;
    int compute_capability_;
    size_t total_memory_;
};

void* create_cuda_context() {
    return new CUDADeviceContext();
}

void destroy_cuda_context(void* ctx) {
    delete static_cast<CUDADeviceContext*>(ctx);
}

} // namespace mle
