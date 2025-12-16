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
constexpr uint32_t MLE_VERSION = 1;

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
    // Sklearn-specific operations
    DECISION_TREE = 26,
    TREE_ENSEMBLE = 27,
    SVM = 28,
    NAIVE_BAYES = 29,
    KNN = 30,
    CLUSTERING = 31,
    DECOMPOSITION = 32,
};

// Data types
enum class DType : uint8_t {
    FP32 = 0,
    FP16 = 1,
    INT8 = 2,
    INT32 = 3,
};

// File header (64 bytes, aligned)
PACK_BEGIN
struct PACKED MLEHeader {
    uint32_t magic;              // MLE_MAGIC (4 bytes)
    uint32_t version;            // MLE_VERSION (4 bytes)
    uint64_t metadata_offset;    // Offset to JSON metadata (8 bytes)
    uint64_t metadata_size;      // Size of JSON metadata (8 bytes)
    uint64_t graph_offset;       // Offset to graph IR (8 bytes)
    uint64_t graph_size;         // Size of graph IR (8 bytes)
    uint64_t weights_offset;     // Offset to weight data (8 bytes)
    uint64_t weights_size;       // Size of weight data (8 bytes)
    uint64_t signature_offset;   // Offset to ED25519 signature (8 bytes)
    uint8_t reserved[8];         // Reserved for future use (8 bytes) - Total: 64 bytes
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
