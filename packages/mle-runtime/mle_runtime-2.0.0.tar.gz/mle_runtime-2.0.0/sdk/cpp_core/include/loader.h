#pragma once

#include "mle_format.h"
#include "tensor_view.h"
#include <string>
#include <vector>
#include <memory>
#include <unordered_map>

namespace mle {

class ModelLoader {
public:
    explicit ModelLoader(const std::string& path);
    ~ModelLoader();
    
    // Disable copy
    ModelLoader(const ModelLoader&) = delete;
    ModelLoader& operator=(const ModelLoader&) = delete;
    
    // Getters
    const MLEHeader& header() const { return header_; }
    const GraphIR& graph() const { return *graph_; }
    
    // Get tensor by ID
    TensorView get_tensor(uint32_t tensor_id) const;
    
    // Get weight data (memory-mapped)
    const void* weights_data() const { return weights_ptr_; }
    
    // Metadata
    std::string get_metadata() const;
    
    // Verify signature
    bool verify_signature(const uint8_t* public_key) const;

private:
    void load_file(const std::string& path);
    void parse_header();
    void parse_graph();
    
    std::string path_;
    void* mapped_data_ = nullptr;
    size_t file_size_ = 0;
    
    MLEHeader header_;
    const GraphIR* graph_ = nullptr;
    const TensorDesc* tensors_ = nullptr;
    const void* weights_ptr_ = nullptr;
    
#ifdef _WIN32
    void* file_handle_ = nullptr;
    void* mapping_handle_ = nullptr;
#else
    int fd_ = -1;
#endif
};

} // namespace mle
