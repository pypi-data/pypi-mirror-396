/**
 * MLE Runtime - C/C++ Client Library
 * Fast ML inference runtime with memory-mapped loading
 */

#pragma once

#include <string>
#include <vector>
#include <memory>
#include <cstdint>

namespace mle {

enum class Device {
    CPU,
    CUDA
};

enum class DType {
    FP32 = 0,
    FP16 = 1,
    INT8 = 2,
    INT32 = 3
};

struct TensorShape {
    std::vector<uint32_t> dimensions;
    DType dtype;
};

struct ModelMetadata {
    std::string model_name;
    std::string framework;
    struct {
        int major;
        int minor;
        int patch;
    } version;
    std::vector<TensorShape> input_shapes;
    std::vector<TensorShape> output_shapes;
    uint64_t export_timestamp;
};

class Tensor {
public:
    Tensor(const std::vector<uint32_t>& shape, DType dtype);
    ~Tensor();
    
    void* data();
    const void* data() const;
    size_t size() const;
    const std::vector<uint32_t>& shape() const;
    DType dtype() const;
    
private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};


class MLEEngine {
public:
    explicit MLEEngine(Device device = Device::CPU);
    ~MLEEngine();
    
    // Disable copy
    MLEEngine(const MLEEngine&) = delete;
    MLEEngine& operator=(const MLEEngine&) = delete;
    
    // Enable move
    MLEEngine(MLEEngine&&) noexcept;
    MLEEngine& operator=(MLEEngine&&) noexcept;
    
    /**
     * Load a model from .mle file
     * @param path Path to .mle model file
     * @throws std::runtime_error if loading fails
     */
    void load_model(const std::string& path);
    
    /**
     * Run inference on input tensors
     * @param inputs Vector of input tensors
     * @return Vector of output tensors
     * @throws std::runtime_error if inference fails
     */
    std::vector<std::shared_ptr<Tensor>> run(
        const std::vector<std::shared_ptr<Tensor>>& inputs);
    
    /**
     * Get model metadata
     * @return Model metadata or nullptr if no model loaded
     */
    const ModelMetadata* metadata() const;
    
    /**
     * Get peak memory usage in bytes
     * @return Peak memory usage
     */
    size_t peak_memory_usage() const;
    
    /**
     * Get current device
     * @return Device (CPU or CUDA)
     */
    Device device() const;
    
private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

/**
 * Utility functions
 */
class MLEUtils {
public:
    /**
     * Inspect .mle file and return metadata
     * @param path Path to .mle file
     * @return Model metadata
     * @throws std::runtime_error if inspection fails
     */
    static ModelMetadata inspect_model(const std::string& path);
    
    /**
     * Verify model signature
     * @param path Path to .mle file
     * @param public_key ED25519 public key (hex string)
     * @return true if signature is valid
     */
    static bool verify_model(const std::string& path, const std::string& public_key);
};

} // namespace mle
