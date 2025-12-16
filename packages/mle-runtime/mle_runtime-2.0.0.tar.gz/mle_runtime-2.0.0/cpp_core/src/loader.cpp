#include "loader.h"
#include "compression.h"
#include "security.h"
#include <fstream>
#include <stdexcept>
#include <cstring>
#include <iostream>

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
    
    // First, check if this is a legacy format (version 1)
    uint32_t magic, version;
    std::memcpy(&magic, mapped_data_, sizeof(uint32_t));
    std::memcpy(&version, static_cast<const uint8_t*>(mapped_data_) + 4, sizeof(uint32_t));
    
    if (magic != MLE_MAGIC) {
        throw std::runtime_error("Invalid magic number");
    }
    
    // Handle backward compatibility
    if (version == 1) {
        parse_legacy_header_v1();
        return;
    } else if (version < MIN_SUPPORTED_VERSION || version > MAX_SUPPORTED_VERSION) {
        throw std::runtime_error("Unsupported version: " + std::to_string(version) + 
                                ". Supported range: " + std::to_string(MIN_SUPPORTED_VERSION) + 
                                "-" + std::to_string(MAX_SUPPORTED_VERSION));
    }
    
    // Parse current format (version 2+)
    std::memcpy(&header_, mapped_data_, sizeof(MLEHeader));
    
    // Verify header integrity if checksums are present
    if (header_.feature_flags & static_cast<uint32_t>(FeatureFlags::SIGNING)) {
        if (!verify_header_integrity()) {
            throw std::runtime_error("Header integrity check failed");
        }
    }
    
    // Handle compression
    if (header_.feature_flags & static_cast<uint32_t>(FeatureFlags::COMPRESSION)) {
        decompress_sections();
    } else {
        // Set weights pointer directly
        weights_ptr_ = static_cast<const uint8_t*>(mapped_data_) + header_.weights_offset;
    }
    
    std::cout << "Loaded MLE model version " << header_.version 
              << " with features: 0x" << std::hex << header_.feature_flags << std::dec << std::endl;
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

void ModelLoader::parse_legacy_header_v1() {
    // Legacy header structure (64 bytes)
    struct LegacyMLEHeader {
        uint32_t magic;
        uint32_t version;
        uint64_t metadata_offset;
        uint64_t metadata_size;
        uint64_t graph_offset;
        uint64_t graph_size;
        uint64_t weights_offset;
        uint64_t weights_size;
        uint64_t signature_offset;
        uint8_t reserved[8];
    };
    
    if (file_size_ < sizeof(LegacyMLEHeader)) {
        throw std::runtime_error("File too small for legacy header");
    }
    
    LegacyMLEHeader legacy_header;
    std::memcpy(&legacy_header, mapped_data_, sizeof(LegacyMLEHeader));
    
    // Convert to new format
    header_ = {};
    header_.magic = legacy_header.magic;
    header_.version = legacy_header.version;
    header_.feature_flags = static_cast<uint32_t>(FeatureFlags::NONE);
    header_.header_size = sizeof(LegacyMLEHeader);
    header_.metadata_offset = legacy_header.metadata_offset;
    header_.metadata_size = legacy_header.metadata_size;
    header_.graph_offset = legacy_header.graph_offset;
    header_.graph_size = legacy_header.graph_size;
    header_.weights_offset = legacy_header.weights_offset;
    header_.weights_size = legacy_header.weights_size;
    header_.signature_offset = legacy_header.signature_offset;
    header_.signature_size = (legacy_header.signature_offset > 0) ? 64 : 0;  // Legacy signature size
    header_.min_reader_version = 1;
    header_.writer_version = 1;
    
    // Set weights pointer
    weights_ptr_ = static_cast<const uint8_t*>(mapped_data_) + header_.weights_offset;
    
    std::cout << "Loaded legacy MLE model (version 1) with backward compatibility" << std::endl;
}

bool ModelLoader::verify_header_integrity() const {
    // Create a copy of header with checksum field zeroed
    MLEHeader temp_header = header_;
    temp_header.header_checksum = 0;
    
    uint32_t computed_checksum = Compressor::checksum(&temp_header, sizeof(temp_header));
    return computed_checksum == header_.header_checksum;
}

void ModelLoader::decompress_sections() {
    if (header_.compression_size == 0) {
        throw std::runtime_error("Compression flag set but no compression metadata found");
    }
    
    // Read compression metadata
    const CompressionHeader* comp_header = reinterpret_cast<const CompressionHeader*>(
        static_cast<const uint8_t*>(mapped_data_) + header_.compression_offset);
    
    // Decompress weights section
    const uint8_t* compressed_weights = static_cast<const uint8_t*>(mapped_data_) + header_.weights_offset;
    
    try {
        decompressed_weights_ = Compressor::decompress(
            compressed_weights,
            header_.weights_size,
            comp_header->uncompressed_size,
            comp_header->type
        );
        
        // Verify checksum
        uint32_t computed_checksum = Compressor::checksum(decompressed_weights_.data(), decompressed_weights_.size());
        if (computed_checksum != comp_header->checksum) {
            throw std::runtime_error("Decompressed weights checksum mismatch");
        }
        
        weights_ptr_ = decompressed_weights_.data();
        
        std::cout << "Decompressed weights: " << header_.weights_size << " -> " 
                  << decompressed_weights_.size() << " bytes (ratio: " 
                  << (float)header_.weights_size / decompressed_weights_.size() << ")" << std::endl;
        
    } catch (const std::exception& e) {
        throw std::runtime_error("Failed to decompress weights: " + std::string(e.what()));
    }
}

bool ModelLoader::verify_signature(const uint8_t* public_key) const {
    if (!(header_.feature_flags & static_cast<uint32_t>(FeatureFlags::SIGNING))) {
        return false;  // Model is not signed
    }
    
    if (header_.signature_offset == 0 || header_.signature_size == 0) {
        return false;  // No signature data
    }
    
    try {
        return ModelSigner::verify_model(path_, public_key);
    } catch (const std::exception& e) {
        std::cerr << "Signature verification failed: " << e.what() << std::endl;
        return false;
    }
}

bool ModelLoader::verify_integrity() const {
    try {
        return ModelSigner::verify_integrity(path_);
    } catch (const std::exception& e) {
        std::cerr << "Integrity verification failed: " << e.what() << std::endl;
        return false;
    }
}

std::string ModelLoader::get_compression_info() const {
    if (!(header_.feature_flags & static_cast<uint32_t>(FeatureFlags::COMPRESSION))) {
        return "No compression";
    }
    
    if (header_.compression_size == 0) {
        return "Compression flag set but no metadata";
    }
    
    const CompressionHeader* comp_header = reinterpret_cast<const CompressionHeader*>(
        static_cast<const uint8_t*>(mapped_data_) + header_.compression_offset);
    
    std::string type_name;
    switch (comp_header->type) {
        case CompressionType::NONE: type_name = "None"; break;
        case CompressionType::LZ4: type_name = "LZ4"; break;
        case CompressionType::ZSTD: type_name = "ZSTD"; break;
        case CompressionType::BROTLI: type_name = "Brotli"; break;
        case CompressionType::QUANTIZE_INT8: type_name = "INT8 Quantization"; break;
        case CompressionType::QUANTIZE_FP16: type_name = "FP16 Quantization"; break;
        default: type_name = "Unknown"; break;
    }
    
    float ratio = (float)header_.weights_size / comp_header->uncompressed_size;
    return type_name + " (level " + std::to_string(comp_header->level) + 
           ", ratio: " + std::to_string(ratio) + ")";
}

uint32_t ModelLoader::get_feature_flags() const {
    return header_.feature_flags;
}

bool ModelLoader::has_feature(FeatureFlags feature) const {
    return header_.feature_flags & static_cast<uint32_t>(feature);
}

} // namespace mle
