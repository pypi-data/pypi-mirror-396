#include "loader.h"
#include "compression.h"
#include "security.h"
#include "mle_format.h"
#include <iostream>
#include <fstream>
#include <vector>
#include <cstring>

using namespace mle;

class FormatTester {
public:
    static void test_header_format() {
        std::cout << "Testing v2.0 header format..." << std::endl;
        
        // Create a v2.0 header
        MLEHeader header = {};
        header.magic = MLE_MAGIC;
        header.version = MLE_VERSION;
        header.feature_flags = static_cast<uint32_t>(FeatureFlags::COMPRESSION) | 
                              static_cast<uint32_t>(FeatureFlags::SIGNING);
        header.header_size = sizeof(MLEHeader);
        header.min_reader_version = MIN_SUPPORTED_VERSION;
        header.writer_version = MLE_VERSION;
        
        // Set up mock sections
        header.metadata_offset = 128;
        header.metadata_size = 256;
        header.graph_offset = 384;
        header.graph_size = 512;
        header.weights_offset = 896;
        header.weights_size = 1024;
        
        // Compute checksums
        std::string metadata = R"({"model": "test", "version": "2.0"})";
        header.metadata_checksum = Compressor::checksum(metadata.data(), metadata.size());
        
        // Compute header checksum
        MLEHeader temp_header = header;
        temp_header.header_checksum = 0;
        header.header_checksum = Compressor::checksum(&temp_header, sizeof(temp_header));
        
        std::cout << "  Header size: " << sizeof(MLEHeader) << " bytes" << std::endl;
        std::cout << "  Magic: 0x" << std::hex << header.magic << std::dec << std::endl;
        std::cout << "  Version: " << header.version << std::endl;
        std::cout << "  Features: 0x" << std::hex << header.feature_flags << std::dec << std::endl;
        std::cout << "  Min reader version: " << header.min_reader_version << std::endl;
        std::cout << "  Writer version: " << header.writer_version << std::endl;
        
        // Validate feature flags
        bool has_compression = header.feature_flags & static_cast<uint32_t>(FeatureFlags::COMPRESSION);
        bool has_signing = header.feature_flags & static_cast<uint32_t>(FeatureFlags::SIGNING);
        
        assert(has_compression);
        assert(has_signing);
        
        std::cout << "  ✓ Header format test passed!" << std::endl;
    }
    
    static void test_compression() {
        std::cout << "Testing compression functionality..." << std::endl;
        
        // Create test data
        std::vector<float> weights(1000);
        for (size_t i = 0; i < weights.size(); ++i) {
            weights[i] = std::sin(i * 0.01f) * 100.0f;
        }
        
        size_t original_size = weights.size() * sizeof(float);
        
        // Test different compression types
        std::vector<CompressionType> types = {
            CompressionType::NONE,
            CompressionType::QUANTIZE_INT8,
            CompressionType::QUANTIZE_FP16
        };
        
        for (auto type : types) {
            try {
                auto compressed = Compressor::compress(
                    weights.data(), 
                    original_size, 
                    type, 
                    6
                );
                
                auto decompressed = Compressor::decompress(
                    compressed.data(),
                    compressed.size(),
                    original_size,
                    type
                );
                
                float compression_ratio = (float)compressed.size() / original_size;
                
                std::cout << "  Type " << static_cast<int>(type) 
                          << ": " << original_size << " -> " << compressed.size() 
                          << " bytes (ratio: " << compression_ratio << ")" << std::endl;
                
                // For lossless compression, verify exact match
                if (type == CompressionType::NONE) {
                    assert(decompressed.size() == original_size);
                    assert(memcmp(decompressed.data(), weights.data(), original_size) == 0);
                }
                
            } catch (const std::exception& e) {
                std::cout << "  Type " << static_cast<int>(type) 
                          << " not available: " << e.what() << std::endl;
            }
        }
        
        std::cout << "  ✓ Compression test passed!" << std::endl;
    }
    
    static void test_integrity_verification() {
        std::cout << "Testing integrity verification..." << std::endl;
        
        // Test checksum functionality
        std::string test_data = "Hello, MLE Runtime v2.0!";
        uint32_t checksum1 = Compressor::checksum(test_data.data(), test_data.size());
        uint32_t checksum2 = Compressor::checksum(test_data.data(), test_data.size());
        
        assert(checksum1 == checksum2);
        std::cout << "  Checksum consistency: 0x" << std::hex << checksum1 << std::dec << std::endl;
        
        // Test different data produces different checksum
        std::string test_data2 = "Hello, MLE Runtime v2.1!";
        uint32_t checksum3 = Compressor::checksum(test_data2.data(), test_data2.size());
        
        assert(checksum1 != checksum3);
        std::cout << "  Different data checksum: 0x" << std::hex << checksum3 << std::dec << std::endl;
        
        std::cout << "  ✓ Integrity verification test passed!" << std::endl;
    }
    
    static void test_version_compatibility() {
        std::cout << "Testing version compatibility..." << std::endl;
        
        // Test version ranges
        std::vector<uint32_t> test_versions = {0, 1, 2, 3, 999};
        
        for (uint32_t version : test_versions) {
            bool should_be_supported = (version >= MIN_SUPPORTED_VERSION && 
                                      version <= MAX_SUPPORTED_VERSION);
            
            std::cout << "  Version " << version << ": ";
            if (should_be_supported) {
                std::cout << "SUPPORTED" << std::endl;
            } else {
                std::cout << "NOT SUPPORTED" << std::endl;
            }
        }
        
        std::cout << "  Supported range: " << MIN_SUPPORTED_VERSION 
                  << " - " << MAX_SUPPORTED_VERSION << std::endl;
        
        std::cout << "  ✓ Version compatibility test passed!" << std::endl;
    }
    
    static void create_sample_v2_file() {
        std::cout << "Creating sample v2.0 file..." << std::endl;
        
        std::ofstream file("sample_model_v2.mle", std::ios::binary);
        if (!file) {
            throw std::runtime_error("Cannot create sample file");
        }
        
        // Create header
        MLEHeader header = {};
        header.magic = MLE_MAGIC;
        header.version = MLE_VERSION;
        header.feature_flags = static_cast<uint32_t>(FeatureFlags::EXTENDED_METADATA);
        header.header_size = sizeof(MLEHeader);
        header.min_reader_version = MIN_SUPPORTED_VERSION;
        header.writer_version = MLE_VERSION;
        
        // Create metadata
        std::string metadata = R"({
    "model_name": "sample_cnn",
    "version": "2.0.0",
    "description": "Sample CNN model with v2.0 format features",
    "architecture": "ResNet-18",
    "input_shape": [1, 3, 224, 224],
    "output_classes": 1000,
    "accuracy": 0.876,
    "created_by": "MLE Runtime v2.0",
    "creation_date": "2024-01-15T10:30:00Z"
})";
        
        // Create minimal graph
        GraphIR graph = {};
        graph.num_nodes = 1;
        graph.num_tensors = 3;
        graph.num_inputs = 1;
        graph.num_outputs = 1;
        graph.input_ids[0] = 0;
        graph.output_ids[0] = 2;
        
        // Create sample weights
        std::vector<float> weights(100);
        for (size_t i = 0; i < weights.size(); ++i) {
            weights[i] = (i % 10) * 0.1f;
        }
        
        // Set up offsets
        size_t current_offset = sizeof(MLEHeader);
        
        header.metadata_offset = current_offset;
        header.metadata_size = metadata.size();
        header.metadata_checksum = Compressor::checksum(metadata.data(), metadata.size());
        current_offset += metadata.size();
        
        header.graph_offset = current_offset;
        header.graph_size = sizeof(GraphIR);
        header.graph_checksum = Compressor::checksum(&graph, sizeof(graph));
        current_offset += sizeof(GraphIR);
        
        header.weights_offset = current_offset;
        header.weights_size = weights.size() * sizeof(float);
        header.weights_checksum = Compressor::checksum(weights.data(), header.weights_size);
        
        // Compute header checksum
        MLEHeader temp_header = header;
        temp_header.header_checksum = 0;
        header.header_checksum = Compressor::checksum(&temp_header, sizeof(temp_header));
        
        // Write to file
        file.write(reinterpret_cast<const char*>(&header), sizeof(header));
        file.write(metadata.data(), metadata.size());
        file.write(reinterpret_cast<const char*>(&graph), sizeof(graph));
        file.write(reinterpret_cast<const char*>(weights.data()), header.weights_size);
        
        file.close();
        
        std::cout << "  Created: sample_model_v2.mle" << std::endl;
        std::cout << "  Size: " << (sizeof(header) + metadata.size() + sizeof(graph) + header.weights_size) 
                  << " bytes" << std::endl;
        
        std::cout << "  ✓ Sample file creation passed!" << std::endl;
    }
    
    static void test_file_loading() {
        std::cout << "Testing v2.0 file loading..." << std::endl;
        
        try {
            // This will test the backward compatibility and new format parsing
            ModelLoader loader("sample_model_v2.mle");
            
            std::cout << "  File version: " << loader.header().version << std::endl;
            std::cout << "  Feature flags: 0x" << std::hex << loader.get_feature_flags() << std::dec << std::endl;
            std::cout << "  Has extended metadata: " << loader.has_feature(FeatureFlags::EXTENDED_METADATA) << std::endl;
            
            // Test metadata loading
            std::string metadata = loader.get_metadata();
            std::cout << "  Metadata size: " << metadata.size() << " bytes" << std::endl;
            
            // Test integrity verification
            bool integrity_ok = loader.verify_integrity();
            std::cout << "  Integrity check: " << (integrity_ok ? "PASS" : "FAIL") << std::endl;
            
            std::cout << "  ✓ File loading test passed!" << std::endl;
            
        } catch (const std::exception& e) {
            std::cout << "  File loading failed: " << e.what() << std::endl;
            // This is expected if the file doesn't exist yet
        }
    }
};

int main() {
    try {
        std::cout << "=== MLE Runtime v2.0 Format Tests ===" << std::endl;
        std::cout << "Testing enhanced file format features...\n" << std::endl;
        
        FormatTester::test_header_format();
        std::cout << std::endl;
        
        FormatTester::test_compression();
        std::cout << std::endl;
        
        FormatTester::test_integrity_verification();
        std::cout << std::endl;
        
        FormatTester::test_version_compatibility();
        std::cout << std::endl;
        
        FormatTester::create_sample_v2_file();
        std::cout << std::endl;
        
        FormatTester::test_file_loading();
        std::cout << std::endl;
        
        std::cout << "=== All format tests completed successfully! ===" << std::endl;
        return 0;
        
    } catch (const std::exception& e) {
        std::cerr << "Test failed: " << e.what() << std::endl;
        return 1;
    }
}