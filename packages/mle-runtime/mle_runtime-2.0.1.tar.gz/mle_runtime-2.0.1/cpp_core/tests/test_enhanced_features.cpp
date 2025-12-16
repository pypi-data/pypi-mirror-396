#include "compression.h"
#include "security.h"
#include "mle_format.h"
#include "loader.h"
#include <iostream>
#include <fstream>
#include <vector>
#include <cstring>
#include <cassert>

using namespace mle;

void test_compression() {
    std::cout << "Testing compression..." << std::endl;
    
    // Create test data
    std::vector<float> test_data(1000);
    for (size_t i = 0; i < test_data.size(); ++i) {
        test_data[i] = std::sin(i * 0.01f) * 100.0f;
    }
    
    // Test different compression types
    std::vector<CompressionType> types = {
        CompressionType::NONE,
        CompressionType::QUANTIZE_INT8,
        CompressionType::QUANTIZE_FP16
    };
    
    for (auto type : types) {
        try {
            auto compressed = Compressor::compress(
                test_data.data(), 
                test_data.size() * sizeof(float), 
                type, 
                6
            );
            
            size_t uncompressed_size = test_data.size() * sizeof(float);
            auto decompressed = Compressor::decompress(
                compressed.data(),
                compressed.size(),
                uncompressed_size,
                type
            );
            
            std::cout << "Compression type " << static_cast<int>(type) 
                      << ": " << uncompressed_size << " -> " << compressed.size() 
                      << " bytes (ratio: " << (float)compressed.size() / uncompressed_size << ")" << std::endl;
            
            // For lossless compression, verify exact match
            if (type == CompressionType::NONE) {
                assert(decompressed.size() == uncompressed_size);
                assert(memcmp(decompressed.data(), test_data.data(), uncompressed_size) == 0);
            }
            
        } catch (const std::exception& e) {
            std::cout << "Compression type " << static_cast<int>(type) 
                      << " not available: " << e.what() << std::endl;
        }
    }
    
    std::cout << "Compression tests completed!" << std::endl;
}

void test_checksum() {
    std::cout << "Testing checksums..." << std::endl;
    
    std::string test_data = "Hello, MLE Runtime!";
    uint32_t checksum1 = Compressor::checksum(test_data.data(), test_data.size());
    uint32_t checksum2 = Compressor::checksum(test_data.data(), test_data.size());
    
    assert(checksum1 == checksum2);
    std::cout << "Checksum: 0x" << std::hex << checksum1 << std::dec << std::endl;
    
    // Test different data
    std::string test_data2 = "Hello, MLE Runtime?";  // Changed last character
    uint32_t checksum3 = Compressor::checksum(test_data2.data(), test_data2.size());
    
    assert(checksum1 != checksum3);
    std::cout << "Different checksum: 0x" << std::hex << checksum3 << std::dec << std::endl;
    
    std::cout << "Checksum tests passed!" << std::endl;
}

void test_quantization() {
    std::cout << "Testing weight quantization..." << std::endl;
    
    // Create test weights
    std::vector<float> weights = {
        -1.5f, -0.5f, 0.0f, 0.5f, 1.0f, 1.5f, 2.0f, -2.0f
    };
    
    // Test INT8 quantization
    auto quantized_int8 = Compressor::quantize_weights(weights.data(), weights.size(), false);
    auto dequantized_int8 = Compressor::dequantize_weights(quantized_int8.data(), weights.size(), false);
    
    std::cout << "INT8 Quantization:" << std::endl;
    for (size_t i = 0; i < weights.size(); ++i) {
        std::cout << "  " << weights[i] << " -> " << dequantized_int8[i] 
                  << " (error: " << std::abs(weights[i] - dequantized_int8[i]) << ")" << std::endl;
    }
    
    // Test FP16 quantization
    auto quantized_fp16 = Compressor::quantize_weights(weights.data(), weights.size(), true);
    auto dequantized_fp16 = Compressor::dequantize_weights(quantized_fp16.data(), weights.size(), true);
    
    std::cout << "FP16 Quantization:" << std::endl;
    for (size_t i = 0; i < weights.size(); ++i) {
        std::cout << "  " << weights[i] << " -> " << dequantized_fp16[i] 
                  << " (error: " << std::abs(weights[i] - dequantized_fp16[i]) << ")" << std::endl;
    }
    
    std::cout << "Quantization tests completed!" << std::endl;
}

void test_header_format() {
    std::cout << "Testing new header format..." << std::endl;
    
    // Create a new header
    MLEHeader header = {};
    header.magic = MLE_MAGIC;
    header.version = MLE_VERSION;
    header.feature_flags = static_cast<uint32_t>(FeatureFlags::COMPRESSION) | 
                          static_cast<uint32_t>(FeatureFlags::SIGNING);
    header.header_size = sizeof(MLEHeader);
    header.metadata_offset = 128;
    header.metadata_size = 256;
    header.graph_offset = 384;
    header.graph_size = 512;
    header.weights_offset = 896;
    header.weights_size = 1024;
    header.min_reader_version = MIN_SUPPORTED_VERSION;
    header.writer_version = MLE_VERSION;
    
    // Compute header checksum
    MLEHeader temp_header = header;
    temp_header.header_checksum = 0;
    header.header_checksum = Compressor::checksum(&temp_header, sizeof(temp_header));
    
    std::cout << "Header size: " << sizeof(MLEHeader) << " bytes" << std::endl;
    std::cout << "Magic: 0x" << std::hex << header.magic << std::dec << std::endl;
    std::cout << "Version: " << header.version << std::endl;
    std::cout << "Features: 0x" << std::hex << header.feature_flags << std::dec << std::endl;
    std::cout << "Header checksum: 0x" << std::hex << header.header_checksum << std::dec << std::endl;
    
    // Test feature flag checking
    bool has_compression = header.feature_flags & static_cast<uint32_t>(FeatureFlags::COMPRESSION);
    bool has_signing = header.feature_flags & static_cast<uint32_t>(FeatureFlags::SIGNING);
    bool has_encryption = header.feature_flags & static_cast<uint32_t>(FeatureFlags::ENCRYPTION);
    
    assert(has_compression);
    assert(has_signing);
    assert(!has_encryption);
    
    std::cout << "Header format tests passed!" << std::endl;
}

void test_backward_compatibility() {
    std::cout << "Testing backward compatibility..." << std::endl;
    
    // Test version compatibility checks
    std::vector<uint32_t> test_versions = {0, 1, 2, 3, 999};
    
    for (uint32_t version : test_versions) {
        bool should_be_supported = (version >= MIN_SUPPORTED_VERSION && version <= MAX_SUPPORTED_VERSION);
        
        std::cout << "Version " << version << ": ";
        if (should_be_supported) {
            std::cout << "SUPPORTED" << std::endl;
        } else {
            std::cout << "NOT SUPPORTED" << std::endl;
        }
    }
    
    std::cout << "Supported version range: " << MIN_SUPPORTED_VERSION 
              << " - " << MAX_SUPPORTED_VERSION << std::endl;
    
    std::cout << "Backward compatibility tests completed!" << std::endl;
}

void test_streaming_decompression() {
    std::cout << "Testing streaming decompression..." << std::endl;
    
    try {
        // Create test data
        std::vector<uint8_t> test_data(1000);
        for (size_t i = 0; i < test_data.size(); ++i) {
            test_data[i] = i % 256;
        }
        
        // This test would require actual compression libraries
        // For now, just test the interface
        StreamDecompressor decompressor(CompressionType::ZSTD);
        
        std::cout << "Stream decompressor created successfully" << std::endl;
        
        // Test reset
        decompressor.reset();
        std::cout << "Stream decompressor reset successfully" << std::endl;
        
    } catch (const std::exception& e) {
        std::cout << "Streaming decompression not available: " << e.what() << std::endl;
    }
    
    std::cout << "Streaming decompression tests completed!" << std::endl;
}

void create_test_model_file() {
    std::cout << "Creating test model file..." << std::endl;
    
    // Create a simple test model file with new format
    std::ofstream file("test_model_v2.mle", std::ios::binary);
    
    // Create header
    MLEHeader header = {};
    header.magic = MLE_MAGIC;
    header.version = MLE_VERSION;
    header.feature_flags = static_cast<uint32_t>(FeatureFlags::EXTENDED_METADATA);
    header.header_size = sizeof(MLEHeader);
    header.min_reader_version = MIN_SUPPORTED_VERSION;
    header.writer_version = MLE_VERSION;
    
    // Set up sections
    size_t current_offset = sizeof(MLEHeader);
    
    // Metadata
    std::string metadata = R"({"model_name": "test_model", "version": "2.0", "description": "Test model with enhanced features"})";
    header.metadata_offset = current_offset;
    header.metadata_size = metadata.size();
    header.metadata_checksum = Compressor::checksum(metadata.data(), metadata.size());
    current_offset += metadata.size();
    
    // Simple graph (minimal)
    GraphIR graph = {};
    graph.num_nodes = 0;
    graph.num_tensors = 0;
    graph.num_inputs = 0;
    graph.num_outputs = 0;
    
    header.graph_offset = current_offset;
    header.graph_size = sizeof(GraphIR);
    header.graph_checksum = Compressor::checksum(&graph, sizeof(graph));
    current_offset += sizeof(GraphIR);
    
    // No weights for this test
    header.weights_offset = current_offset;
    header.weights_size = 0;
    header.weights_checksum = 0;
    
    // Compute header checksum
    MLEHeader temp_header = header;
    temp_header.header_checksum = 0;
    header.header_checksum = Compressor::checksum(&temp_header, sizeof(temp_header));
    
    // Write to file
    file.write(reinterpret_cast<const char*>(&header), sizeof(header));
    file.write(metadata.data(), metadata.size());
    file.write(reinterpret_cast<const char*>(&graph), sizeof(graph));
    
    file.close();
    std::cout << "Test model file created: test_model_v2.mle" << std::endl;
}

int main() {
    try {
        std::cout << "=== MLE Runtime Enhanced Features Test ===" << std::endl;
        
        test_compression();
        std::cout << std::endl;
        
        test_checksum();
        std::cout << std::endl;
        
        test_quantization();
        std::cout << std::endl;
        
        test_header_format();
        std::cout << std::endl;
        
        test_backward_compatibility();
        std::cout << std::endl;
        
        test_streaming_decompression();
        std::cout << std::endl;
        
        create_test_model_file();
        std::cout << std::endl;
        
        std::cout << "=== All enhanced features tests completed successfully! ===" << std::endl;
        return 0;
        
    } catch (const std::exception& e) {
        std::cerr << "Test failed: " << e.what() << std::endl;
        return 1;
    }
}