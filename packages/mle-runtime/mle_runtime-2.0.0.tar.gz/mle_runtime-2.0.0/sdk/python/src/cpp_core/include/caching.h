#pragma once

#include "tensor_view.h"
#include <memory>
#include <string>
#include <unordered_map>
#include <chrono>

namespace mle {

// Intelligent model cache (better than joblib's Memory)
class ModelCache {
public:
    explicit ModelCache(
        const std::string& cache_dir,
        size_t max_size_mb = 1024
    );
    
    // Cache a model
    void cache_model(
        const std::string& key,
        const std::string& model_path
    );
    
    // Get cached model path
    std::string get_cached(const std::string& key) const;
    
    // Check if cached
    bool is_cached(const std::string& key) const;
    
    // Invalidate cache entry
    void invalidate(const std::string& key);
    
    // Clear all cache
    void clear();
    
    // Get cache statistics
    struct CacheStats {
        size_t total_size_bytes;
        size_t num_entries;
        size_t hits;
        size_t misses;
        float hit_rate;
    };
    CacheStats get_stats() const;
    
    // Automatic cache eviction (LRU)
    void evict_lru();

private:
    struct CacheEntry {
        std::string path;
        size_t size_bytes;
        std::chrono::system_clock::time_point last_access;
        uint64_t access_count;
    };
    
    std::string cache_dir_;
    size_t max_size_mb_;
    std::unordered_map<std::string, CacheEntry> entries_;
    size_t hits_ = 0;
    size_t misses_ = 0;
};

// Result caching for inference
class InferenceCache {
public:
    explicit InferenceCache(size_t max_entries = 1000);
    
    // Cache inference result
    void cache_result(
        const std::string& input_hash,
        const std::vector<std::shared_ptr<TensorView>>& outputs
    );
    
    // Get cached result
    bool get_result(
        const std::string& input_hash,
        std::vector<std::shared_ptr<TensorView>>& outputs
    ) const;
    
    // Compute input hash
    static std::string hash_inputs(
        const std::vector<std::shared_ptr<TensorView>>& inputs
    );
    
    // Clear cache
    void clear();
    
    // Get statistics
    struct Stats {
        size_t hits;
        size_t misses;
        float hit_rate;
        size_t memory_usage_bytes;
    };
    Stats get_stats() const;

private:
    size_t max_entries_;
    std::unordered_map<std::string, std::vector<std::shared_ptr<TensorView>>> cache_;
    size_t hits_ = 0;
    size_t misses_ = 0;
};

} // namespace mle
