#include "loader.h"
#include <fstream>
#include <stdexcept>
#include <cstring>

#ifdef _WIN32
#include <windows.h>
#else
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#endif

namespace mle {

ModelLoader::ModelLoader(const std::string& path) : path_(path) {
    load_file(path);
    parse_header();
    parse_graph();
}

ModelLoader::~ModelLoader() {
#ifdef _WIN32
    if (mapped_data_) UnmapViewOfFile(mapped_data_);
    if (mapping_handle_) CloseHandle(mapping_handle_);
    if (file_handle_) CloseHandle(file_handle_);
#else
    if (mapped_data_) munmap(mapped_data_, file_size_);
    if (fd_ >= 0) close(fd_);
#endif
}

void ModelLoader::load_file(const std::string& path) {
#ifdef _WIN32
    file_handle_ = CreateFileA(path.c_str(), GENERIC_READ, FILE_SHARE_READ,
                               nullptr, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr);
    if (file_handle_ == INVALID_HANDLE_VALUE) {
        throw std::runtime_error("Failed to open file: " + path);
    }
    
    LARGE_INTEGER size;
    if (!GetFileSizeEx(file_handle_, &size)) {
        throw std::runtime_error("Failed to get file size");
    }
    file_size_ = size.QuadPart;
    
    mapping_handle_ = CreateFileMappingA(file_handle_, nullptr, PAGE_READONLY,
                                         0, 0, nullptr);
    if (!mapping_handle_) {
        throw std::runtime_error("Failed to create file mapping");
    }
    
    mapped_data_ = MapViewOfFile(mapping_handle_, FILE_MAP_READ, 0, 0, 0);
    if (!mapped_data_) {
        throw std::runtime_error("Failed to map file");
    }
#else
    fd_ = open(path.c_str(), O_RDONLY);
    if (fd_ < 0) {
        throw std::runtime_error("Failed to open file: " + path);
    }
    
    struct stat st;
    if (fstat(fd_, &st) < 0) {
        throw std::runtime_error("Failed to stat file");
    }
    file_size_ = st.st_size;
    
    mapped_data_ = mmap(nullptr, file_size_, PROT_READ, MAP_PRIVATE, fd_, 0);
    if (mapped_data_ == MAP_FAILED) {
        throw std::runtime_error("Failed to mmap file");
    }
#endif
}

void ModelLoader::parse_header() {
    if (file_size_ < sizeof(MLEHeader)) {
        throw std::runtime_error("File too small for header");
    }
    
    std::memcpy(&header_, mapped_data_, sizeof(MLEHeader));
    
    if (header_.magic != MLE_MAGIC) {
        throw std::runtime_error("Invalid magic number");
    }
    
    if (header_.version != MLE_VERSION) {
        throw std::runtime_error("Unsupported version");
    }
    
    // Set weights pointer
    weights_ptr_ = static_cast<const uint8_t*>(mapped_data_) + header_.weights_offset;
}

void ModelLoader::parse_graph() {
    if (header_.graph_offset + header_.graph_size > file_size_) {
        throw std::runtime_error("Invalid graph offset/size");
    }
    
    graph_ = reinterpret_cast<const GraphIR*>(
        static_cast<const uint8_t*>(mapped_data_) + header_.graph_offset);
    
    // Tensors follow GraphIR header
    tensors_ = reinterpret_cast<const TensorDesc*>(graph_ + 1);
}

TensorView ModelLoader::get_tensor(uint32_t tensor_id) const {
    if (tensor_id >= graph_->num_tensors) {
        throw std::out_of_range("Invalid tensor ID");
    }
    
    const TensorDesc& desc = tensors_[tensor_id];
    
    // Check if this is a placeholder tensor (no data)
    if (desc.size == 0) {
        throw std::runtime_error("Cannot load placeholder tensor - it has no data");
    }
    
    void* data = const_cast<void*>(
        static_cast<const void*>(
            static_cast<const uint8_t*>(weights_ptr_) + desc.offset));
    
    std::vector<uint32_t> shape(desc.shape, desc.shape + desc.ndim);
    return TensorView(data, shape, desc.dtype);
}

std::string ModelLoader::get_metadata() const {
    if (header_.metadata_size == 0) return "{}";
    
    const char* metadata = static_cast<const char*>(mapped_data_) + header_.metadata_offset;
    return std::string(metadata, header_.metadata_size);
}

bool ModelLoader::verify_signature(const uint8_t* public_key) const {
    // TODO: Implement ED25519 signature verification
    // For now, return true if signature exists
    return header_.signature_offset > 0;
}

} // namespace mle
