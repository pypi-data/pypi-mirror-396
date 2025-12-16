#pragma once

#include "mle_format.h"
#include <cstdint>
#include <vector>
#include <memory>

namespace mle {

// Use CompressionType from mle_format.h

// Compression metadata
struct CompressionInfo {
    CompressionType type;
    uint64_t compressed_size;
    uint64_t uncompressed_size;
    uint32_t checksum;  // CRC32
    uint8_t level;      // Compression level (1-9)
};

class Compressor {
public:
    // Compress data
    static std::vector<uint8_t> compress(
        const void* data, 
        size_t size,
        CompressionType type = CompressionType::ZSTD,
        int level = 6
    );
    
    // Decompress data
    static std::vector<uint8_t> decompress(
        const void* data,
        size_t compressed_size,
        size_t uncompressed_size,
        CompressionType type
    );
    
    // Compute checksum
    static uint32_t checksum(const void* data, size_t size);
    
    // Quantize weights (FP32 -> INT8/FP16)
    static std::vector<uint8_t> quantize_weights(
        const float* weights,
        size_t count,
        bool use_fp16 = false  // false = INT8, true = FP16
    );
    
    // Dequantize weights
    static std::vector<float> dequantize_weights(
        const void* data,
        size_t count,
        bool is_fp16
    );

private:
    // Internal compression methods
    static std::vector<uint8_t> compress_lz4(const void* data, size_t size, int level);
    static std::vector<uint8_t> decompress_lz4(const void* data, size_t compressed_size, size_t uncompressed_size);
    static std::vector<uint8_t> compress_zstd(const void* data, size_t size, int level);
    static std::vector<uint8_t> decompress_zstd(const void* data, size_t compressed_size, size_t uncompressed_size);
    static std::vector<uint8_t> compress_brotli(const void* data, size_t size, int level);
    static std::vector<uint8_t> decompress_brotli(const void* data, size_t compressed_size, size_t uncompressed_size);
    
    // Quantization helpers
    static std::vector<uint8_t> dequantize_weights_to_bytes(const void* data, size_t count, bool is_fp16);
    static uint16_t float_to_fp16(float value);
    static float fp16_to_float(uint16_t value);
};

// Streaming decompressor for large models
class StreamDecompressor {
public:
    explicit StreamDecompressor(CompressionType type);
    ~StreamDecompressor();
    
    // Decompress chunk by chunk
    size_t decompress_chunk(
        const void* input,
        size_t input_size,
        void* output,
        size_t output_size
    );
    
    void reset();

private:
    CompressionType type_;
    void* context_ = nullptr;
};

} // namespace mle
