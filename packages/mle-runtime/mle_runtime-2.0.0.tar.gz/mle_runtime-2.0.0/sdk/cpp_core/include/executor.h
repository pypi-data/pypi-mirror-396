#pragma once

#include "engine.h"
#include "loader.h"
#include "tensor_view.h"
#include <vector>
#include <memory>
#include <unordered_map>

namespace mle {

// Execution plan with memory reuse
struct ExecutionPlan {
    struct Allocation {
        uint32_t tensor_id;
        size_t size;
        size_t offset;      // Offset in memory pool
        uint32_t lifetime_start;  // First node that uses it
        uint32_t lifetime_end;    // Last node that uses it
    };
    
    std::vector<Allocation> allocations;
    size_t total_memory_required;
    std::vector<uint32_t> execution_order;
};

class MemoryPlanner {
public:
    // Analyze graph and create execution plan
    ExecutionPlan plan(const GraphIR& graph, const TensorDesc* tensors);

private:
    struct Interval {
        uint32_t start;
        uint32_t end;
        size_t size;
        uint32_t tensor_id;
    };
    
    // Compute tensor lifetimes
    std::vector<Interval> compute_lifetimes(const GraphIR& graph, const TensorDesc* tensors);
    
    // Greedy interval scheduling for memory reuse
    size_t assign_offsets(std::vector<Interval>& intervals, 
                         std::unordered_map<uint32_t, size_t>& offsets);
};

class GraphExecutor {
public:
    explicit GraphExecutor(Device device);
    ~GraphExecutor();
    
    // Load model and create execution plan
    void load_model(const std::string& path);
    
    // Execute with memory reuse
    std::vector<std::shared_ptr<TensorView>> execute(
        const std::vector<std::shared_ptr<TensorView>>& inputs);
    
    // Get execution plan
    const ExecutionPlan& plan() const { return plan_; }
    
    // Memory stats
    size_t peak_memory() const { return plan_.total_memory_required; }

private:
    void execute_node(uint32_t node_idx);
    void* get_tensor_ptr(uint32_t tensor_id);
    
    Device device_;
    std::unique_ptr<ModelLoader> loader_;
    ExecutionPlan plan_;
    
    // Memory pool
    void* memory_pool_ = nullptr;
    size_t pool_size_ = 0;
    
    // Tensor ID to memory offset mapping
    std::unordered_map<uint32_t, size_t> tensor_offsets_;
    
    // Runtime tensor cache (for inputs/outputs)
    std::unordered_map<uint32_t, std::shared_ptr<TensorView>> tensor_cache_;
};

} // namespace mle
