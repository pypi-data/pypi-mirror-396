#pragma once

#include "loader.h"
#include "tensor_view.h"
#include <vector>
#include <memory>

namespace mle {

enum class Device {
    CPU,
    CUDA
};

class Engine {
public:
    explicit Engine(Device device = Device::CPU);
    ~Engine();
    
    // Load model
    void load_model(const std::string& path);
    
    // Run inference
    std::vector<std::shared_ptr<TensorView>> run(
        const std::vector<std::shared_ptr<TensorView>>& inputs);
    
    // Get device
    Device device() const { return device_; }
    
    // Memory stats
    size_t peak_memory_usage() const { return peak_memory_; }

private:
    void execute_node(const GraphNode& node);
    std::shared_ptr<TensorView> allocate_tensor(const TensorDesc& desc);
    std::shared_ptr<TensorView> get_or_load_tensor(uint32_t tensor_id);
    
    Device device_;
    std::unique_ptr<ModelLoader> loader_;
    
    // Execution state
    std::unordered_map<uint32_t, std::shared_ptr<TensorView>> tensor_cache_;
    size_t peak_memory_ = 0;
    
    // Device-specific context
    void* cuda_context_ = nullptr;
};

} // namespace mle
