#pragma once

#include "mle_format.h"
#include <vector>
#include <memory>
#include <stdexcept>

namespace mle {

class TensorView {
public:
    TensorView() : data_(nullptr), size_(0), dtype_(DType::FP32), ndim_(0) {}
    
    TensorView(void* data, const std::vector<uint32_t>& shape, DType dtype)
        : data_(data), shape_(shape), dtype_(dtype), ndim_(shape.size()) {
        size_ = element_size(dtype);
        for (auto dim : shape) size_ *= dim;
    }
    
    void* data() { return data_; }
    const void* data() const { return data_; }
    
    size_t size() const { return size_; }
    size_t ndim() const { return ndim_; }
    const std::vector<uint32_t>& shape() const { return shape_; }
    DType dtype() const { return dtype_; }
    
    size_t numel() const {
        size_t n = 1;
        for (auto dim : shape_) n *= dim;
        return n;
    }
    
    static size_t element_size(DType dtype) {
        switch (dtype) {
            case DType::FP32: return 4;
            case DType::FP16: return 2;
            case DType::INT8: return 1;
            case DType::INT32: return 4;
            default: throw std::runtime_error("Unknown dtype");
        }
    }
    
    // Create owned tensor
    static std::shared_ptr<TensorView> create(const std::vector<uint32_t>& shape, DType dtype) {
        size_t size = element_size(dtype);
        for (auto dim : shape) size *= dim;
        
        // Platform-specific aligned allocation
        void* data = nullptr;
        #ifdef _MSC_VER
            data = _aligned_malloc(size, 64);
        #else
            data = aligned_alloc(64, size);
        #endif
        
        if (!data) throw std::bad_alloc();
        auto tensor = std::make_shared<TensorView>(data, shape, dtype);
        tensor->owned_ = true;
        return tensor;
    }
    
    ~TensorView() {
        if (owned_ && data_) {
            #ifdef _MSC_VER
                _aligned_free(data_);
            #else
                free(data_);
            #endif
        }
    }

private:
    void* data_;
    std::vector<uint32_t> shape_;
    size_t size_;
    DType dtype_;
    size_t ndim_;
    bool owned_ = false;
};

} // namespace mle
