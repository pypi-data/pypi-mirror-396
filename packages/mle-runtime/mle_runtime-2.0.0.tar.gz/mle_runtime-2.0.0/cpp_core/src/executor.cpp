#include "executor.h"
#include <algorithm>
#include <set>
#include <stdexcept>

namespace mle {

ExecutionPlan MemoryPlanner::plan(const GraphIR& graph, const TensorDesc* tensors) {
    ExecutionPlan plan;
    
    // Compute lifetimes
    auto intervals = compute_lifetimes(graph, tensors);
    
    // Assign memory offsets using interval scheduling
    std::unordered_map<uint32_t, size_t> offsets;
    plan.total_memory_required = assign_offsets(intervals, offsets);
    
    // Build allocation list
    for (const auto& interval : intervals) {
        ExecutionPlan::Allocation alloc;
        alloc.tensor_id = interval.tensor_id;
        alloc.size = interval.size;
        alloc.offset = offsets[interval.tensor_id];
        alloc.lifetime_start = interval.start;
        alloc.lifetime_end = interval.end;
        plan.allocations.push_back(alloc);
    }
    
    // Execution order is just sequential for now
    for (uint32_t i = 0; i < graph.num_nodes; ++i) {
        plan.execution_order.push_back(i);
    }
    
    return plan;
}

std::vector<MemoryPlanner::Interval> MemoryPlanner::compute_lifetimes(
    const GraphIR& graph, const TensorDesc* tensors) {
    
    std::vector<Interval> intervals;
    std::unordered_map<uint32_t, Interval> tensor_intervals;
    
    const GraphNode* nodes = reinterpret_cast<const GraphNode*>(tensors + graph.num_tensors);
    
    // First pass: find first and last use of each tensor
    for (uint32_t node_idx = 0; node_idx < graph.num_nodes; ++node_idx) {
        const auto& node = nodes[node_idx];
        
        // Process inputs
        for (uint16_t i = 0; i < node.num_inputs; ++i) {
            uint32_t tid = node.input_ids[i];
            if (tensor_intervals.find(tid) == tensor_intervals.end()) {
                tensor_intervals[tid] = {node_idx, node_idx, 0, tid};
            } else {
                tensor_intervals[tid].end = node_idx;
            }
        }
        
        // Process outputs
        for (uint16_t i = 0; i < node.num_outputs; ++i) {
            uint32_t tid = node.output_ids[i];
            if (tensor_intervals.find(tid) == tensor_intervals.end()) {
                tensor_intervals[tid] = {node_idx, node_idx, 0, tid};
            } else {
                tensor_intervals[tid].end = node_idx;
            }
        }
    }
    
    // Add sizes
    for (auto& [tid, interval] : tensor_intervals) {
        if (tid < graph.num_tensors) {
            interval.size = tensors[tid].size;
        }
        intervals.push_back(interval);
    }
    
    return intervals;
}

size_t MemoryPlanner::assign_offsets(std::vector<Interval>& intervals,
                                     std::unordered_map<uint32_t, size_t>& offsets) {
    // Sort by start time, then by size (larger first)
    std::sort(intervals.begin(), intervals.end(), [](const Interval& a, const Interval& b) {
        if (a.start != b.start) return a.start < b.start;
        return a.size > b.size;
    });
    
    // Track active intervals and their offsets
    struct ActiveSlot {
        size_t offset;
        size_t size;
        uint32_t end_time;
    };
    
    std::vector<ActiveSlot> active_slots;
    size_t peak_memory = 0;
    
    for (const auto& interval : intervals) {
        // Remove expired slots
        active_slots.erase(
            std::remove_if(active_slots.begin(), active_slots.end(),
                [&](const ActiveSlot& slot) { return slot.end_time < interval.start; }),
            active_slots.end()
        );
        
        // Sort slots by offset
        std::sort(active_slots.begin(), active_slots.end(),
            [](const ActiveSlot& a, const ActiveSlot& b) { return a.offset < b.offset; });
        
        // Find first fit
        size_t offset = 0;
        bool found = false;
        
        for (size_t i = 0; i < active_slots.size(); ++i) {
            size_t gap_start = (i == 0) ? 0 : (active_slots[i-1].offset + active_slots[i-1].size);
            size_t gap_end = active_slots[i].offset;
            
            if (gap_end - gap_start >= interval.size) {
                offset = gap_start;
                found = true;
                break;
            }
        }
        
        if (!found) {
            // Allocate at the end
            offset = active_slots.empty() ? 0 : 
                     (active_slots.back().offset + active_slots.back().size);
        }
        
        offsets[interval.tensor_id] = offset;
        active_slots.push_back({offset, interval.size, interval.end});
        
        peak_memory = std::max(peak_memory, offset + interval.size);
    }
    
    return peak_memory;
}

GraphExecutor::GraphExecutor(Device device) : device_(device) {}

GraphExecutor::~GraphExecutor() {
    if (memory_pool_) {
        if (device_ == Device::CPU) {
#ifdef _MSC_VER
            _aligned_free(memory_pool_);
#else
            free(memory_pool_);
#endif
        } else {
#ifdef ENABLE_CUDA
            cudaFree(memory_pool_);
#endif
        }
    }
}

void GraphExecutor::load_model(const std::string& path) {
    loader_ = std::make_unique<ModelLoader>(path);
    
    const auto& graph = loader_->graph();
    const TensorDesc* tensors = reinterpret_cast<const TensorDesc*>(&graph + 1);
    
    // Create execution plan
    MemoryPlanner planner;
    plan_ = planner.plan(graph, tensors);
    
    // Allocate memory pool
    pool_size_ = plan_.total_memory_required;
    
    if (device_ == Device::CPU) {
#ifdef _MSC_VER
        memory_pool_ = _aligned_malloc(pool_size_, 64);
#else
        memory_pool_ = aligned_alloc(64, pool_size_);
#endif
    } else {
#ifdef ENABLE_CUDA
        cudaMalloc(&memory_pool_, pool_size_);
#endif
    }
    
    if (!memory_pool_) {
        throw std::bad_alloc();
    }
    
    // Build offset map
    for (const auto& alloc : plan_.allocations) {
        tensor_offsets_[alloc.tensor_id] = alloc.offset;
    }
}

std::vector<std::shared_ptr<TensorView>> GraphExecutor::execute(
    const std::vector<std::shared_ptr<TensorView>>& inputs) {
    
    const auto& graph = loader_->graph();
    
    // Set inputs
    for (uint32_t i = 0; i < graph.num_inputs && i < inputs.size(); ++i) {
        uint32_t tid = graph.input_ids[i];
        tensor_cache_[tid] = inputs[i];
    }
    
    // Execute nodes in order
    for (uint32_t node_idx : plan_.execution_order) {
        execute_node(node_idx);
    }
    
    // Collect outputs
    std::vector<std::shared_ptr<TensorView>> outputs;
    for (uint32_t i = 0; i < graph.num_outputs; ++i) {
        uint32_t tid = graph.output_ids[i];
        outputs.push_back(tensor_cache_[tid]);
    }
    
    return outputs;
}

void GraphExecutor::execute_node(uint32_t node_idx) {
    // Similar to Engine::execute_node but uses memory pool
    // Implementation details omitted for brevity
    // Would call ops::linear_cpu/cuda, ops::relu_cpu/cuda, etc.
}

void* GraphExecutor::get_tensor_ptr(uint32_t tensor_id) {
    if (tensor_offsets_.find(tensor_id) != tensor_offsets_.end()) {
        return static_cast<uint8_t*>(memory_pool_) + tensor_offsets_[tensor_id];
    }
    return nullptr;
}

} // namespace mle
