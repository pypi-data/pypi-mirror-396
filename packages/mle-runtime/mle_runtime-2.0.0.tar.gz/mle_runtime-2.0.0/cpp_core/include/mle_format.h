#pragma once

#include <cstdint>
#include <cstring>

// Platform-specific packing macros
#ifdef _MSC_VER
    #define PACK_BEGIN __pragma(pack(push, 1))
    #define PACK_END __pragma(pack(pop))
    #define PACKED
#else
    #define PACK_BEGIN
    #define PACK_END
    #define PACKED __attribute__((packed))
#endif

namespace mle {

// Magic number: "MLE\0"
constexpr uint32_t MLE_MAGIC = 0x00454C4D;
constexpr uint32_t MLE_VERSION = 2;  // Incremented for new features

// Version compatibility
constexpr uint32_t MIN_SUPPORTED_VERSION = 1;
constexpr uint32_t MAX_SUPPORTED_VERSION = 2;

// Feature flags for backward compatibility
enum class FeatureFlags : uint32_t {
    NONE = 0x00000000,
    COMPRESSION = 0x00000001,
    ENCRYPTION = 0x00000002,
    SIGNING = 0x00000004,
    STREAMING = 0x00000008,
    QUANTIZATION = 0x00000010,
    EXTENDED_METADATA = 0x00000020,
    CHUNKED_WEIGHTS = 0x00000040,
    MEMORY_MAPPING = 0x00000080,
};

// Compression types
enum class CompressionType : uint8_t {
    NONE = 0,
    LZ4 = 1,
    ZSTD = 2,
    BROTLI = 3,
    QUANTIZE_INT8 = 4,
    QUANTIZE_FP16 = 5,
};

// Operator types
enum class OpType : uint16_t {
    LINEAR = 1,
    RELU = 2,
    GELU = 3,
    SOFTMAX = 4,
    LAYERNORM = 5,
    MATMUL = 6,
    ADD = 7,
    MUL = 8,
    CONV2D = 9,
    MAXPOOL2D = 10,
    BATCHNORM = 11,
    DROPOUT = 12,
    EMBEDDING = 13,
    ATTENTION = 14,
    // Additional neural network operations
    AVGPOOL2D = 15,
    CONV1D = 16,
    MAXPOOL1D = 17,
    AVGPOOL1D = 18,
    FLATTEN = 19,
    RESHAPE = 20,
    TRANSPOSE = 21,
    CONCAT = 22,
    SPLIT = 23,
    SLICE = 24,
    PAD = 25,
    // Sklearn-specific operations
    DECISION_TREE = 26,
    TREE_ENSEMBLE = 27,
    GRADIENT_BOOSTING = 28,
    SVM = 29,
    NAIVE_BAYES = 30,
    KNN = 31,
    CLUSTERING = 32,
    DBSCAN = 33,
    DECOMPOSITION = 34,
    // Advanced operations
    TRANSFORMER_BLOCK = 35,
    MULTI_HEAD_ATTENTION = 36,
    POSITIONAL_ENCODING = 37,
    CROSS_ATTENTION = 38,
};

// Data types
enum class DType : uint8_t {
    FP32 = 0,
    FP16 = 1,
    INT8 = 2,
    INT32 = 3,
};

// Extended file header (128 bytes, aligned)
PACK_BEGIN
struct PACKED MLEHeader {
    uint32_t magic;              // MLE_MAGIC (4 bytes)
    uint32_t version;            // MLE_VERSION (4 bytes)
    uint32_t feature_flags;      // FeatureFlags bitmask (4 bytes)
    uint32_t header_size;        // Size of this header (4 bytes)
    
    // Section offsets and sizes (no size limits)
    uint64_t metadata_offset;    // Offset to JSON metadata (8 bytes)
    uint64_t metadata_size;      // Size of JSON metadata (8 bytes)
    uint64_t graph_offset;       // Offset to graph IR (8 bytes)
    uint64_t graph_size;         // Size of graph IR (8 bytes)
    uint64_t weights_offset;     // Offset to weight data (8 bytes)
    uint64_t weights_size;       // Size of weight data (8 bytes)
    
    // Security and compression
    uint64_t signature_offset;   // Offset to ED25519 signature (8 bytes)
    uint64_t signature_size;     // Size of signature data (8 bytes)
    uint64_t compression_offset; // Offset to compression metadata (8 bytes)
    uint64_t compression_size;   // Size of compression metadata (8 bytes)
    
    // Checksums for integrity
    uint32_t metadata_checksum;  // CRC32 of metadata (4 bytes)
    uint32_t graph_checksum;     // CRC32 of graph IR (4 bytes)
    uint32_t weights_checksum;   // CRC32 of weights (4 bytes)
    uint32_t header_checksum;    // CRC32 of header (excluding this field) (4 bytes)
    
    // Backward compatibility
    uint32_t min_reader_version; // Minimum version required to read (4 bytes)
    uint32_t writer_version;     // Version that wrote this file (4 bytes)
    
    uint8_t reserved[24];        // Reserved for future use (24 bytes) - Total: 128 bytes
};
PACK_END

// Compression metadata
PACK_BEGIN
struct PACKED CompressionHeader {
    CompressionType type;        // Compression algorithm (1 byte)
    uint8_t level;              // Compression level 1-9 (1 byte)
    uint16_t reserved;          // Padding (2 bytes)
    uint64_t uncompressed_size; // Original size (8 bytes)
    uint32_t checksum;          // CRC32 of uncompressed data (4 bytes)
    uint8_t quantization_bits;  // Bits per weight (for quantization) (1 byte)
    uint8_t padding[3];         // Padding (3 bytes) - Total: 20 bytes
};
PACK_END

// Signature metadata
PACK_BEGIN
struct PACKED SignatureHeader {
    uint8_t algorithm;          // Signature algorithm (1 = ED25519) (1 byte)
    uint8_t hash_algorithm;     // Hash algorithm (1 = SHA256) (1 byte)
    uint16_t reserved;          // Padding (2 bytes)
    uint64_t timestamp;         // Signing timestamp (8 bytes)
    uint8_t public_key[32];     // ED25519 public key (32 bytes)
    uint8_t signature[64];      // ED25519 signature (64 bytes)
    uint8_t model_hash[32];     // SHA256 hash of model content (32 bytes)
    // Total: 140 bytes
};
PACK_END

// Note: Size check disabled for MSVC compatibility
// static_assert(sizeof(MLEHeader) == 64, "MLEHeader must be 64 bytes");

// Tensor descriptor
PACK_BEGIN
struct PACKED TensorDesc {
    uint64_t offset;             // Offset from weights_offset
    uint64_t size;               // Size in bytes
    uint32_t ndim;               // Number of dimensions
    uint32_t shape[8];           // Max 8 dimensions
    DType dtype;                 // Data type
    uint8_t reserved[3];         // Padding
};
PACK_END

// Graph node (operator)
PACK_BEGIN
struct PACKED GraphNode {
    OpType op_type;              // Operation type
    uint16_t num_inputs;         // Number of input tensors
    uint16_t num_outputs;        // Number of output tensors
    uint16_t num_params;         // Number of parameter tensors
    uint32_t input_ids[16];      // Input tensor IDs
    uint32_t output_ids[16];     // Output tensor IDs
    uint32_t param_ids[16];      // Parameter tensor IDs
    uint32_t attr_offset;        // Offset to attributes (JSON)
    uint32_t attr_size;          // Size of attributes
};
PACK_END

// Graph IR header
PACK_BEGIN
struct PACKED GraphIR {
    uint32_t num_nodes;          // Number of nodes
    uint32_t num_tensors;        // Number of tensors
    uint32_t num_inputs;         // Number of graph inputs
    uint32_t num_outputs;        // Number of graph outputs
    uint32_t input_ids[16];      // Graph input tensor IDs
    uint32_t output_ids[16];     // Graph output tensor IDs
    // Followed by: TensorDesc[num_tensors], GraphNode[num_nodes]
};
PACK_END

} // namespace mle
