#include "compression.h"
#include <stdexcept>
#include <cstring>
#include <algorithm>
#include <cmath>
#include <iostream>

// For CRC32 calculation
#ifdef ENABLE_ZLIB
#include <zlib.h>
#else
// Fallback CRC32 implementation
static uint32_t crc32_fallback(uint32_t crc, const uint8_t* buf, size_t len) {
    static const uint32_t crc_table[256] = {
        0x00000000, 0x77073096, 0xee0e612c, 0x990951ba, 0x076dc419, 0x706af48f,
        0xe963a535, 0x9e6495a3, 0x0edb8832, 0x79dcb8a4, 0xe0d5e91e, 0x97d2d988,
        // ... (truncated for brevity, full table would be here)
    };
    
    crc = crc ^ 0xffffffff;
    for (size_t i = 0; i < len; i++) {
        crc = crc_table[(crc ^ buf[i]) & 0xff] ^ (crc >> 8);
    }
    return crc ^ 0xffffffff;
}
#define crc32 crc32_fallback
#endif

// Compression libraries
#ifdef ENABLE_LZ4
#include <lz4.h>
#include <lz4hc.h>
#endif

#ifdef ENABLE_ZSTD
#include <zstd.h>
#endif

#ifdef ENABLE_BROTLI
#include <brotli/encode.h>
#include <brotli/decode.h>
#endif

namespace mle {

std::vector<uint8_t> Compressor::compress(
    const void* data, 
    size_t size,
    CompressionType type,
    int level) {
    
    if (!data || size == 0) {
        return {};
    }
    
    switch (type) {
        case CompressionType::NONE:
            return std::vector<uint8_t>(
                static_cast<const uint8_t*>(data),
                static_cast<const uint8_t*>(data) + size
            );
            
        case CompressionType::LZ4:
            return compress_lz4(data, size, level);
            
        case CompressionType::ZSTD:
            return compress_zstd(data, size, level);
            
        case CompressionType::BROTLI:
            return compress_brotli(data, size, level);
            
        case CompressionType::QUANTIZE_INT8:
            return quantize_weights(static_cast<const float*>(data), size / sizeof(float), false);
            
        case CompressionType::QUANTIZE_FP16:
            return quantize_weights(static_cast<const float*>(data), size / sizeof(float), true);
            
        default:
            throw std::runtime_error("Unsupported compression type");
    }
}

std::vector<uint8_t> Compressor::decompress(
    const void* data,
    size_t compressed_size,
    size_t uncompressed_size,
    CompressionType type) {
    
    if (!data || compressed_size == 0) {
        return {};
    }
    
    switch (type) {
        case CompressionType::NONE:
            return std::vector<uint8_t>(
                static_cast<const uint8_t*>(data),
                static_cast<const uint8_t*>(data) + compressed_size
            );
            
        case CompressionType::LZ4:
            return decompress_lz4(data, compressed_size, uncompressed_size);
            
        case CompressionType::ZSTD:
            return decompress_zstd(data, compressed_size, uncompressed_size);
            
        case CompressionType::BROTLI:
            return decompress_brotli(data, compressed_size, uncompressed_size);
            
        case CompressionType::QUANTIZE_INT8:
            return dequantize_weights_to_bytes(data, compressed_size / 1, false);  // 1 byte per weight
            
        case CompressionType::QUANTIZE_FP16:
            return dequantize_weights_to_bytes(data, compressed_size / 2, true);   // 2 bytes per weight
            
        default:
            throw std::runtime_error("Unsupported compression type");
    }
}

uint32_t Compressor::checksum(const void* data, size_t size) {
    if (!data || size == 0) {
        return 0;
    }
#ifdef ENABLE_ZLIB
    return crc32(0L, static_cast<const Bytef*>(data), size);
#else
    return crc32_fallback(0, static_cast<const uint8_t*>(data), size);
#endif
}

std::vector<uint8_t> Compressor::compress_lz4(const void* data, size_t size, int level) {
#ifdef ENABLE_LZ4
    int max_compressed_size = LZ4_compressBound(size);
    std::vector<uint8_t> compressed(max_compressed_size);
    
    int compressed_size;
    if (level <= 3) {
        compressed_size = LZ4_compress_default(
            static_cast<const char*>(data),
            reinterpret_cast<char*>(compressed.data()),
            size,
            max_compressed_size
        );
    } else {
        compressed_size = LZ4_compress_HC(
            static_cast<const char*>(data),
            reinterpret_cast<char*>(compressed.data()),
            size,
            max_compressed_size,
            level
        );
    }
    
    if (compressed_size <= 0) {
        throw std::runtime_error("LZ4 compression failed");
    }
    
    compressed.resize(compressed_size);
    return compressed;
#else
    throw std::runtime_error("LZ4 support not compiled");
#endif
}

std::vector<uint8_t> Compressor::decompress_lz4(const void* data, size_t compressed_size, size_t uncompressed_size) {
#ifdef ENABLE_LZ4
    std::vector<uint8_t> decompressed(uncompressed_size);
    
    int result = LZ4_decompress_safe(
        static_cast<const char*>(data),
        reinterpret_cast<char*>(decompressed.data()),
        compressed_size,
        uncompressed_size
    );
    
    if (result < 0) {
        throw std::runtime_error("LZ4 decompression failed");
    }
    
    return decompressed;
#else
    throw std::runtime_error("LZ4 support not compiled");
#endif
}

std::vector<uint8_t> Compressor::compress_zstd(const void* data, size_t size, int level) {
#ifdef ENABLE_ZSTD
    size_t max_compressed_size = ZSTD_compressBound(size);
    std::vector<uint8_t> compressed(max_compressed_size);
    
    size_t compressed_size = ZSTD_compress(
        compressed.data(),
        max_compressed_size,
        data,
        size,
        level
    );
    
    if (ZSTD_isError(compressed_size)) {
        throw std::runtime_error("ZSTD compression failed: " + std::string(ZSTD_getErrorName(compressed_size)));
    }
    
    compressed.resize(compressed_size);
    return compressed;
#else
    throw std::runtime_error("ZSTD support not compiled");
#endif
}

std::vector<uint8_t> Compressor::decompress_zstd(const void* data, size_t compressed_size, size_t uncompressed_size) {
#ifdef ENABLE_ZSTD
    std::vector<uint8_t> decompressed(uncompressed_size);
    
    size_t result = ZSTD_decompress(
        decompressed.data(),
        uncompressed_size,
        data,
        compressed_size
    );
    
    if (ZSTD_isError(result)) {
        throw std::runtime_error("ZSTD decompression failed: " + std::string(ZSTD_getErrorName(result)));
    }
    
    return decompressed;
#else
    throw std::runtime_error("ZSTD support not compiled");
#endif
}

std::vector<uint8_t> Compressor::compress_brotli(const void* data, size_t size, int level) {
#ifdef ENABLE_BROTLI
    size_t max_compressed_size = BrotliEncoderMaxCompressedSize(size);
    std::vector<uint8_t> compressed(max_compressed_size);
    
    size_t compressed_size = max_compressed_size;
    BROTLI_BOOL result = BrotliEncoderCompress(
        level,
        BROTLI_DEFAULT_WINDOW,
        BROTLI_DEFAULT_MODE,
        size,
        static_cast<const uint8_t*>(data),
        &compressed_size,
        compressed.data()
    );
    
    if (result != BROTLI_TRUE) {
        throw std::runtime_error("Brotli compression failed");
    }
    
    compressed.resize(compressed_size);
    return compressed;
#else
    throw std::runtime_error("Brotli support not compiled");
#endif
}

std::vector<uint8_t> Compressor::decompress_brotli(const void* data, size_t compressed_size, size_t uncompressed_size) {
#ifdef ENABLE_BROTLI
    std::vector<uint8_t> decompressed(uncompressed_size);
    
    size_t decoded_size = uncompressed_size;
    BrotliDecoderResult result = BrotliDecoderDecompress(
        compressed_size,
        static_cast<const uint8_t*>(data),
        &decoded_size,
        decompressed.data()
    );
    
    if (result != BROTLI_DECODER_RESULT_SUCCESS) {
        throw std::runtime_error("Brotli decompression failed");
    }
    
    return decompressed;
#else
    throw std::runtime_error("Brotli support not compiled");
#endif
}

std::vector<uint8_t> Compressor::quantize_weights(const float* weights, size_t count, bool use_fp16) {
    if (!weights || count == 0) {
        return {};
    }
    
    if (use_fp16) {
        // FP16 quantization
        std::vector<uint8_t> quantized(count * 2);
        uint16_t* fp16_data = reinterpret_cast<uint16_t*>(quantized.data());
        
        for (size_t i = 0; i < count; ++i) {
            fp16_data[i] = float_to_fp16(weights[i]);
        }
        
        return quantized;
    } else {
        // INT8 quantization with scale and zero point
        std::vector<uint8_t> quantized(count + 8);  // +8 for scale and zero_point
        
        // Find min/max for quantization range
        float min_val = weights[0];
        float max_val = weights[0];
        for (size_t i = 1; i < count; ++i) {
            min_val = std::min(min_val, weights[i]);
            max_val = std::max(max_val, weights[i]);
        }
        
        // Calculate scale and zero point
        float scale = (max_val - min_val) / 255.0f;
        float zero_point = -min_val / scale;
        float clamped_zp = std::max(0.0f, std::min(255.0f, zero_point));
        uint8_t zero_point_int = static_cast<uint8_t>(clamped_zp + 0.5f);
        
        // Store scale and zero point at the beginning
        memcpy(quantized.data(), &scale, sizeof(float));
        memcpy(quantized.data() + 4, &zero_point_int, sizeof(uint8_t));
        
        // Quantize weights
        for (size_t i = 0; i < count; ++i) {
            float quantized_val = weights[i] / scale + zero_point_int;
            float clamped_val = std::max(0.0f, std::min(255.0f, quantized_val));
            quantized[i + 8] = static_cast<uint8_t>(clamped_val + 0.5f);  // Simple rounding
        }
        
        return quantized;
    }
}

std::vector<float> Compressor::dequantize_weights(const void* data, size_t count, bool is_fp16) {
    if (!data || count == 0) {
        return {};
    }
    
    std::vector<float> weights(count);
    
    if (is_fp16) {
        const uint16_t* fp16_data = static_cast<const uint16_t*>(data);
        for (size_t i = 0; i < count; ++i) {
            weights[i] = fp16_to_float(fp16_data[i]);
        }
    } else {
        const uint8_t* quantized_data = static_cast<const uint8_t*>(data);
        
        // Extract scale and zero point
        float scale;
        uint8_t zero_point;
        memcpy(&scale, quantized_data, sizeof(float));
        memcpy(&zero_point, quantized_data + 4, sizeof(uint8_t));
        
        // Dequantize weights
        for (size_t i = 0; i < count; ++i) {
            weights[i] = (quantized_data[i + 8] - zero_point) * scale;
        }
    }
    
    return weights;
}

std::vector<uint8_t> Compressor::dequantize_weights_to_bytes(const void* data, size_t count, bool is_fp16) {
    auto weights = dequantize_weights(data, count, is_fp16);
    std::vector<uint8_t> bytes(weights.size() * sizeof(float));
    memcpy(bytes.data(), weights.data(), bytes.size());
    return bytes;
}

uint16_t Compressor::float_to_fp16(float value) {
    // Simple FP32 to FP16 conversion
    union { float f; uint32_t i; } u = { value };
    uint32_t i = u.i;
    
    uint32_t sign = (i >> 16) & 0x8000;
    int32_t exp = ((i >> 23) & 0xff) - 127 + 15;
    uint32_t mant = i & 0x7fffff;
    
    if (exp <= 0) {
        // Underflow
        return sign;
    } else if (exp >= 31) {
        // Overflow
        return sign | 0x7c00;
    } else {
        return sign | (exp << 10) | (mant >> 13);
    }
}

float Compressor::fp16_to_float(uint16_t value) {
    // Simple FP16 to FP32 conversion
    uint32_t sign = (value & 0x8000) << 16;
    int32_t exp = (value >> 10) & 0x1f;
    uint32_t mant = value & 0x3ff;
    
    if (exp == 0) {
        // Zero or denormal
        return 0.0f;
    } else if (exp == 31) {
        // Infinity or NaN
        union { float f; uint32_t i; } u = { 0 };
        u.i = sign | 0x7f800000 | (mant << 13);
        return u.f;
    } else {
        // Normal number
        exp = exp - 15 + 127;
        union { float f; uint32_t i; } u = { 0 };
        u.i = sign | (exp << 23) | (mant << 13);
        return u.f;
    }
}

// Stream decompressor implementation
StreamDecompressor::StreamDecompressor(CompressionType type) : type_(type) {
    switch (type_) {
#ifdef ENABLE_ZSTD
        case CompressionType::ZSTD:
            context_ = ZSTD_createDStream();
            if (!context_) {
                throw std::runtime_error("Failed to create ZSTD decompression context");
            }
            break;
#endif
        default:
            // Other types don't need streaming context
            break;
    }
}

StreamDecompressor::~StreamDecompressor() {
    if (context_) {
#ifdef ENABLE_ZSTD
        if (type_ == CompressionType::ZSTD) {
            ZSTD_freeDStream(static_cast<ZSTD_DStream*>(context_));
        }
#endif
    }
}

size_t StreamDecompressor::decompress_chunk(
    const void* input,
    size_t input_size,
    void* output,
    size_t output_size) {
    
    switch (type_) {
#ifdef ENABLE_ZSTD
        case CompressionType::ZSTD: {
            ZSTD_inBuffer in_buf = { input, input_size, 0 };
            ZSTD_outBuffer out_buf = { output, output_size, 0 };
            
            size_t result = ZSTD_decompressStream(static_cast<ZSTD_DStream*>(context_), &out_buf, &in_buf);
            if (ZSTD_isError(result)) {
                throw std::runtime_error("ZSTD streaming decompression failed");
            }
            
            return out_buf.pos;
        }
#endif
        default:
            throw std::runtime_error("Streaming not supported for this compression type");
    }
}

void StreamDecompressor::reset() {
    if (context_) {
#ifdef ENABLE_ZSTD
        if (type_ == CompressionType::ZSTD) {
            ZSTD_resetDStream(static_cast<ZSTD_DStream*>(context_));
        }
#endif
    }
}

} // namespace mle