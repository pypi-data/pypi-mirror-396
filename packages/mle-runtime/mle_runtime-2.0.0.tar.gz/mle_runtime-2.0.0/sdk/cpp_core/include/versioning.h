#pragma once

#include <string>
#include <vector>
#include <cstdint>

namespace mle {

// Model versioning and metadata
struct ModelVersion {
    uint32_t major;
    uint32_t minor;
    uint32_t patch;
    std::string git_hash;
    uint64_t timestamp;  // Unix timestamp
    std::string author;
    std::string description;
};

// Model lineage tracking
struct ModelLineage {
    std::string parent_model_hash;  // SHA256 of parent model
    std::string training_dataset;
    std::string framework_version;
    std::vector<std::string> dependencies;
    std::string training_script_hash;
};

// Performance metadata
struct PerformanceMetrics {
    float accuracy;
    float f1_score;
    float inference_time_ms;
    size_t model_size_bytes;
    std::string hardware_profile;  // "cpu", "cuda", "tpu"
};

// Complete model metadata (extends basic JSON metadata)
struct ModelMetadata {
    ModelVersion version;
    ModelLineage lineage;
    PerformanceMetrics metrics;
    std::string license;
    std::vector<std::string> tags;
    
    // Serialize to JSON
    std::string to_json() const;
    
    // Deserialize from JSON
    static ModelMetadata from_json(const std::string& json);
};

// Model registry for version management
class ModelRegistry {
public:
    // Register a model version
    void register_model(
        const std::string& name,
        const std::string& path,
        const ModelMetadata& metadata
    );
    
    // Get latest version
    std::string get_latest(const std::string& name) const;
    
    // Get specific version
    std::string get_version(
        const std::string& name,
        uint32_t major,
        uint32_t minor,
        uint32_t patch
    ) const;
    
    // List all versions
    std::vector<ModelVersion> list_versions(const std::string& name) const;
    
    // Compare models
    bool is_compatible(
        const std::string& model1,
        const std::string& model2
    ) const;

private:
    std::string registry_path_;
};

} // namespace mle
