#include "engine.h"
#include <stdexcept>
#include <chrono>

namespace mle {
namespace ops {
    // Forward declarations
    void linear_cpu(const TensorView& input, const TensorView& weight, 
                    const TensorView& bias, TensorView& output);
    void relu_cpu(const TensorView& input, TensorView& output);
    void gelu_cpu(const TensorView& input, TensorView& output);
    void softmax_cpu(const TensorView& input, TensorView& output);
    void matmul_cpu(const TensorView& A, const TensorView& B, TensorView& C);
    void decision_tree_cpu(const TensorView& input_tensor, 
                          const TensorView& feature_tensor, const TensorView& threshold_tensor,
                          const TensorView& value_tensor, const TensorView& children_left_tensor,
                          const TensorView& children_right_tensor, TensorView& output_tensor);
    void tree_ensemble_cpu(const TensorView& input_tensor, 
                          const std::vector<TensorView>& tree_params,
                          TensorView& output_tensor, bool is_classifier);
    void svm_cpu(const TensorView& input_tensor, const TensorView& support_vectors,
                const TensorView& dual_coef, const TensorView& intercept,
                TensorView& output_tensor, float gamma);
    void naive_bayes_cpu(const TensorView& input_tensor, const TensorView& theta,
                        const TensorView& sigma, TensorView& output_tensor);
    void knn_cpu(const TensorView& input_tensor, const TensorView& fit_X,
                const TensorView& fit_y, TensorView& output_tensor, uint32_t k);
    void clustering_cpu(const TensorView& input_tensor, const TensorView& cluster_centers,
                       TensorView& output_tensor);
    void decomposition_cpu(const TensorView& input_tensor, const TensorView& components,
                          const TensorView* mean_tensor, TensorView& output_tensor);
    
    // New operators
    void conv2d_cpu(const TensorView& input, const TensorView& weight, 
                    const TensorView& bias, TensorView& output,
                    uint32_t stride_h, uint32_t stride_w,
                    uint32_t pad_h, uint32_t pad_w);
    void maxpool2d_cpu(const TensorView& input, TensorView& output,
                       uint32_t kernel_h, uint32_t kernel_w,
                       uint32_t stride_h, uint32_t stride_w,
                       uint32_t pad_h, uint32_t pad_w);
    void batchnorm_cpu(const TensorView& input, const TensorView& weight,
                       const TensorView& bias, const TensorView& running_mean,
                       const TensorView& running_var, TensorView& output,
                       float eps);
    void attention_cpu(const TensorView& query, const TensorView& key, 
                       const TensorView& value, TensorView& output,
                       uint32_t num_heads, float scale);
    
    // Additional algorithms
    void gradient_boosting_cpu(const TensorView& input_tensor,
                              const std::vector<TensorView>& tree_params,
                              const TensorView& learning_rates,
                              TensorView& output_tensor, bool is_classifier);
    void dbscan_cpu(const TensorView& input_tensor, TensorView& output_tensor,
                    float eps, uint32_t min_samples);
    void layernorm_cpu(const TensorView& input, const TensorView& weight,
                       const TensorView& bias, TensorView& output, float eps);
    void dropout_cpu(const TensorView& input, TensorView& output, float dropout_rate);
    void embedding_cpu(const TensorView& input, const TensorView& weight, TensorView& output);
    void add_cpu(const TensorView& input1, const TensorView& input2, TensorView& output);
    void mul_cpu(const TensorView& input1, const TensorView& input2, TensorView& output);
}

Engine::Engine(Device device) : device_(device) {
    if (device == Device::CUDA) {
#ifndef ENABLE_CUDA
        throw std::runtime_error("CUDA support not compiled");
#endif
    }
}

Engine::~Engine() = default;

void Engine::load_model(const std::string& path) {
    loader_ = std::make_unique<ModelLoader>(path);
    
    // Don't pre-load tensors - they will be loaded on demand
    // Some tensors are placeholders (inputs/outputs) without data
    // Only parameter tensors (weights/biases) have actual data in the file
}

std::vector<std::shared_ptr<TensorView>> Engine::run(
    const std::vector<std::shared_ptr<TensorView>>& inputs) {
    
    if (!loader_) {
        throw std::runtime_error("No model loaded");
    }
    
    const auto& graph = loader_->graph();
    
    // Set input tensors
    for (uint32_t i = 0; i < graph.num_inputs && i < inputs.size(); ++i) {
        uint32_t tensor_id = graph.input_ids[i];
        tensor_cache_[tensor_id] = inputs[i];
    }
    
    // Execute nodes in order
    const GraphNode* nodes = reinterpret_cast<const GraphNode*>(
        reinterpret_cast<const TensorDesc*>(&graph + 1) + graph.num_tensors);
    
    for (uint32_t i = 0; i < graph.num_nodes; ++i) {
        execute_node(nodes[i]);
    }
    
    // Collect outputs
    std::vector<std::shared_ptr<TensorView>> outputs;
    for (uint32_t i = 0; i < graph.num_outputs; ++i) {
        uint32_t tensor_id = graph.output_ids[i];
        outputs.push_back(tensor_cache_[tensor_id]);
    }
    
    return outputs;
}

std::shared_ptr<TensorView> Engine::get_or_load_tensor(uint32_t tensor_id) {
    // Check cache first
    auto it = tensor_cache_.find(tensor_id);
    if (it != tensor_cache_.end()) {
        return it->second;
    }
    
    // Load from file (for parameter tensors)
    auto tensor = std::make_shared<TensorView>(loader_->get_tensor(tensor_id));
    tensor_cache_[tensor_id] = tensor;
    return tensor;
}

void Engine::execute_node(const GraphNode& node) {
    switch (node.op_type) {
        case OpType::LINEAR: {
            // LINEAR: input, weight, bias -> output
            auto input = get_or_load_tensor(node.input_ids[0]);
            auto weight = get_or_load_tensor(node.param_ids[0]);
            auto bias = get_or_load_tensor(node.param_ids[1]);
            
            // Allocate output
            const auto& in_shape = input->shape();
            std::vector<uint32_t> out_shape = {in_shape[0], weight->shape()[0]};
            auto output = TensorView::create(out_shape, DType::FP32);
            
            if (device_ == Device::CPU) {
                ops::linear_cpu(*input, *weight, *bias, *output);
            } else {
                // TODO: CUDA path
                throw std::runtime_error("CUDA not implemented yet");
            }
            
            tensor_cache_[node.output_ids[0]] = output;
            break;
        }
        
        case OpType::RELU: {
            auto input = get_or_load_tensor(node.input_ids[0]);
            auto output = TensorView::create(input->shape(), input->dtype());
            
            if (device_ == Device::CPU) {
                ops::relu_cpu(*input, *output);
            }
            
            tensor_cache_[node.output_ids[0]] = output;
            break;
        }
        
        case OpType::GELU: {
            auto input = get_or_load_tensor(node.input_ids[0]);
            auto output = TensorView::create(input->shape(), input->dtype());
            
            if (device_ == Device::CPU) {
                ops::gelu_cpu(*input, *output);
            }
            
            tensor_cache_[node.output_ids[0]] = output;
            break;
        }
        
        case OpType::SOFTMAX: {
            auto input = get_or_load_tensor(node.input_ids[0]);
            auto output = TensorView::create(input->shape(), input->dtype());
            
            if (device_ == Device::CPU) {
                ops::softmax_cpu(*input, *output);
            }
            
            tensor_cache_[node.output_ids[0]] = output;
            break;
        }
        
        case OpType::MATMUL: {
            auto A = get_or_load_tensor(node.input_ids[0]);
            auto B = get_or_load_tensor(node.input_ids[1]);
            
            const auto& a_shape = A->shape();
            const auto& b_shape = B->shape();
            std::vector<uint32_t> out_shape = {a_shape[0], b_shape[1]};
            auto output = TensorView::create(out_shape, DType::FP32);
            
            if (device_ == Device::CPU) {
                ops::matmul_cpu(*A, *B, *output);
            }
            
            tensor_cache_[node.output_ids[0]] = output;
            break;
        }
        
        case OpType::DECISION_TREE: {
            auto input = get_or_load_tensor(node.input_ids[0]);
            auto feature = get_or_load_tensor(node.param_ids[0]);
            auto threshold = get_or_load_tensor(node.param_ids[1]);
            auto value = get_or_load_tensor(node.param_ids[2]);
            auto children_left = get_or_load_tensor(node.param_ids[3]);
            auto children_right = get_or_load_tensor(node.param_ids[4]);
            
            // Determine output shape from value tensor
            // sklearn tree.value shape is [n_nodes, 1, n_classes]
            const auto& value_shape = value->shape();
            const auto& in_shape = input->shape();
            uint32_t n_classes = (value_shape.size() == 3) ? value_shape[2] : 
                                (value_shape.size() == 2) ? value_shape[1] : 1;
            std::vector<uint32_t> out_shape = {in_shape[0], n_classes};
            auto output = TensorView::create(out_shape, DType::FP32);
            
            if (device_ == Device::CPU) {
                ops::decision_tree_cpu(*input, *feature, *threshold, *value,
                                      *children_left, *children_right, *output);
            }
            
            tensor_cache_[node.output_ids[0]] = output;
            break;
        }
        
        case OpType::TREE_ENSEMBLE: {
            auto input = get_or_load_tensor(node.input_ids[0]);
            
            // Load all tree parameters
            std::vector<TensorView> tree_params;
            for (uint16_t i = 0; i < node.num_params; ++i) {
                tree_params.push_back(*get_or_load_tensor(node.param_ids[i]));
            }
            
            // Determine output shape (assume first tree's value tensor defines it)
            const auto& in_shape = input->shape();
            uint32_t n_trees = node.num_params / 5;
            const auto& first_value_shape = tree_params[2].shape();
            uint32_t n_classes = (first_value_shape.size() > 2) ? first_value_shape[2] : 
                                (first_value_shape.size() > 1) ? first_value_shape[1] : 1;
            std::vector<uint32_t> out_shape = {in_shape[0], n_classes};
            auto output = TensorView::create(out_shape, DType::FP32);
            
            if (device_ == Device::CPU) {
                ops::tree_ensemble_cpu(*input, tree_params, *output, true);
            }
            
            tensor_cache_[node.output_ids[0]] = output;
            break;
        }
        
        case OpType::SVM: {
            auto input = get_or_load_tensor(node.input_ids[0]);
            auto support_vectors = get_or_load_tensor(node.param_ids[0]);
            auto dual_coef = get_or_load_tensor(node.param_ids[1]);
            auto intercept = get_or_load_tensor(node.param_ids[2]);
            
            const auto& in_shape = input->shape();
            const auto& dual_shape = dual_coef->shape();
            uint32_t n_classes = dual_shape[0];
            std::vector<uint32_t> out_shape = {in_shape[0], n_classes};
            auto output = TensorView::create(out_shape, DType::FP32);
            
            if (device_ == Device::CPU) {
                ops::svm_cpu(*input, *support_vectors, *dual_coef, *intercept, *output, 0.1f);
            }
            
            tensor_cache_[node.output_ids[0]] = output;
            break;
        }
        
        case OpType::NAIVE_BAYES: {
            auto input = get_or_load_tensor(node.input_ids[0]);
            auto theta = get_or_load_tensor(node.param_ids[0]);
            auto sigma = get_or_load_tensor(node.param_ids[1]);
            
            const auto& in_shape = input->shape();
            const auto& theta_shape = theta->shape();
            uint32_t n_classes = theta_shape[0];
            std::vector<uint32_t> out_shape = {in_shape[0], n_classes};
            auto output = TensorView::create(out_shape, DType::FP32);
            
            if (device_ == Device::CPU) {
                ops::naive_bayes_cpu(*input, *theta, *sigma, *output);
            }
            
            tensor_cache_[node.output_ids[0]] = output;
            break;
        }
        
        case OpType::KNN: {
            auto input = get_or_load_tensor(node.input_ids[0]);
            auto fit_X = get_or_load_tensor(node.param_ids[0]);
            auto fit_y = get_or_load_tensor(node.param_ids[1]);
            
            const auto& in_shape = input->shape();
            // Determine n_classes from fit_y
            const float* y_data = static_cast<const float*>(fit_y->data());
            uint32_t n_samples = fit_y->numel();
            uint32_t n_classes = 0;
            for (uint32_t i = 0; i < n_samples; ++i) {
                uint32_t label = static_cast<uint32_t>(y_data[i]);
                if (label >= n_classes) n_classes = label + 1;
            }
            
            std::vector<uint32_t> out_shape = {in_shape[0], n_classes};
            auto output = TensorView::create(out_shape, DType::FP32);
            
            if (device_ == Device::CPU) {
                ops::knn_cpu(*input, *fit_X, *fit_y, *output, 5);
            }
            
            tensor_cache_[node.output_ids[0]] = output;
            break;
        }
        
        case OpType::CLUSTERING: {
            auto input = get_or_load_tensor(node.input_ids[0]);
            auto cluster_centers = get_or_load_tensor(node.param_ids[0]);
            
            const auto& in_shape = input->shape();
            std::vector<uint32_t> out_shape = {in_shape[0], 1};
            auto output = TensorView::create(out_shape, DType::FP32);
            
            if (device_ == Device::CPU) {
                ops::clustering_cpu(*input, *cluster_centers, *output);
            }
            
            tensor_cache_[node.output_ids[0]] = output;
            break;
        }
        
        case OpType::DECOMPOSITION: {
            auto input = get_or_load_tensor(node.input_ids[0]);
            auto components = get_or_load_tensor(node.param_ids[0]);
            TensorView* mean_ptr = nullptr;
            TensorView mean_view;
            if (node.num_params > 1) {
                mean_view = *get_or_load_tensor(node.param_ids[1]);
                mean_ptr = &mean_view;
            }
            
            const auto& in_shape = input->shape();
            const auto& comp_shape = components->shape();
            uint32_t n_components = comp_shape[0];
            std::vector<uint32_t> out_shape = {in_shape[0], n_components};
            auto output = TensorView::create(out_shape, DType::FP32);
            
            if (device_ == Device::CPU) {
                ops::decomposition_cpu(*input, *components, mean_ptr, *output);
            }
            
            tensor_cache_[node.output_ids[0]] = output;
            break;
        }
        
        case OpType::CONV2D: {
            auto input = get_or_load_tensor(node.input_ids[0]);
            auto weight = get_or_load_tensor(node.param_ids[0]);
            auto bias = get_or_load_tensor(node.param_ids[1]);
            
            // Calculate output shape
            const auto& in_shape = input->shape();   // [N, C_in, H_in, W_in]
            const auto& w_shape = weight->shape();   // [C_out, C_in, K_h, K_w]
            
            // Default parameters (can be read from attributes in real implementation)
            uint32_t stride_h = 1, stride_w = 1, pad_h = 0, pad_w = 0;
            
            uint32_t H_out = (in_shape[2] + 2 * pad_h - w_shape[2]) / stride_h + 1;
            uint32_t W_out = (in_shape[3] + 2 * pad_w - w_shape[3]) / stride_w + 1;
            
            std::vector<uint32_t> out_shape = {in_shape[0], w_shape[0], H_out, W_out};
            auto output = TensorView::create(out_shape, DType::FP32);
            
            if (device_ == Device::CPU) {
                ops::conv2d_cpu(*input, *weight, *bias, *output, stride_h, stride_w, pad_h, pad_w);
            }
            
            tensor_cache_[node.output_ids[0]] = output;
            break;
        }
        
        case OpType::MAXPOOL2D: {
            auto input = get_or_load_tensor(node.input_ids[0]);
            
            // Default parameters
            uint32_t kernel_h = 2, kernel_w = 2, stride_h = 2, stride_w = 2, pad_h = 0, pad_w = 0;
            
            const auto& in_shape = input->shape();
            uint32_t H_out = (in_shape[2] + 2 * pad_h - kernel_h) / stride_h + 1;
            uint32_t W_out = (in_shape[3] + 2 * pad_w - kernel_w) / stride_w + 1;
            
            std::vector<uint32_t> out_shape = {in_shape[0], in_shape[1], H_out, W_out};
            auto output = TensorView::create(out_shape, DType::FP32);
            
            if (device_ == Device::CPU) {
                ops::maxpool2d_cpu(*input, *output, kernel_h, kernel_w, stride_h, stride_w, pad_h, pad_w);
            }
            
            tensor_cache_[node.output_ids[0]] = output;
            break;
        }
        
        case OpType::BATCHNORM: {
            auto input = get_or_load_tensor(node.input_ids[0]);
            auto weight = get_or_load_tensor(node.param_ids[0]);
            auto bias = get_or_load_tensor(node.param_ids[1]);
            auto running_mean = get_or_load_tensor(node.param_ids[2]);
            auto running_var = get_or_load_tensor(node.param_ids[3]);
            
            auto output = TensorView::create(input->shape(), input->dtype());
            
            if (device_ == Device::CPU) {
                ops::batchnorm_cpu(*input, *weight, *bias, *running_mean, *running_var, *output, 1e-5f);
            }
            
            tensor_cache_[node.output_ids[0]] = output;
            break;
        }
        
        case OpType::ATTENTION: {
            auto query = get_or_load_tensor(node.input_ids[0]);
            auto key = get_or_load_tensor(node.input_ids[1]);
            auto value = get_or_load_tensor(node.input_ids[2]);
            
            // Default parameters
            uint32_t num_heads = 8;
            float scale = 1.0f / std::sqrt(query->shape()[2] / num_heads);
            
            auto output = TensorView::create(query->shape(), query->dtype());
            
            if (device_ == Device::CPU) {
                ops::attention_cpu(*query, *key, *value, *output, num_heads, scale);
            }
            
            tensor_cache_[node.output_ids[0]] = output;
            break;
        }
        
        case OpType::GRADIENT_BOOSTING: {
            auto input = get_or_load_tensor(node.input_ids[0]);
            auto learning_rates = get_or_load_tensor(node.param_ids[node.num_params - 1]);
            
            // Load all tree parameters (excluding learning rates)
            std::vector<TensorView> tree_params;
            for (uint16_t i = 0; i < node.num_params - 1; ++i) {
                tree_params.push_back(*get_or_load_tensor(node.param_ids[i]));
            }
            
            const auto& in_shape = input->shape();
            uint32_t n_trees = (node.num_params - 1) / 5;
            const auto& first_value_shape = tree_params[2].shape();
            uint32_t n_classes = (first_value_shape.size() > 2) ? first_value_shape[2] : 
                                (first_value_shape.size() > 1) ? first_value_shape[1] : 1;
            std::vector<uint32_t> out_shape = {in_shape[0], n_classes};
            auto output = TensorView::create(out_shape, DType::FP32);
            
            if (device_ == Device::CPU) {
                ops::gradient_boosting_cpu(*input, tree_params, *learning_rates, *output, true);
            }
            
            tensor_cache_[node.output_ids[0]] = output;
            break;
        }
        
        case OpType::DBSCAN: {
            auto input = get_or_load_tensor(node.input_ids[0]);
            
            const auto& in_shape = input->shape();
            std::vector<uint32_t> out_shape = {in_shape[0], 1};
            auto output = TensorView::create(out_shape, DType::FP32);
            
            // Default parameters
            float eps = 0.5f;
            uint32_t min_samples = 5;
            
            if (device_ == Device::CPU) {
                ops::dbscan_cpu(*input, *output, eps, min_samples);
            }
            
            tensor_cache_[node.output_ids[0]] = output;
            break;
        }
        
        case OpType::LAYERNORM: {
            auto input = get_or_load_tensor(node.input_ids[0]);
            auto weight = get_or_load_tensor(node.param_ids[0]);
            auto bias = get_or_load_tensor(node.param_ids[1]);
            
            auto output = TensorView::create(input->shape(), input->dtype());
            
            if (device_ == Device::CPU) {
                ops::layernorm_cpu(*input, *weight, *bias, *output, 1e-5f);
            }
            
            tensor_cache_[node.output_ids[0]] = output;
            break;
        }
        
        case OpType::DROPOUT: {
            auto input = get_or_load_tensor(node.input_ids[0]);
            auto output = TensorView::create(input->shape(), input->dtype());
            
            // Default dropout rate (inference mode)
            float dropout_rate = 0.0f;
            
            if (device_ == Device::CPU) {
                ops::dropout_cpu(*input, *output, dropout_rate);
            }
            
            tensor_cache_[node.output_ids[0]] = output;
            break;
        }
        
        case OpType::EMBEDDING: {
            auto input = get_or_load_tensor(node.input_ids[0]);
            auto weight = get_or_load_tensor(node.param_ids[0]);
            
            const auto& in_shape = input->shape();
            const auto& w_shape = weight->shape();
            std::vector<uint32_t> out_shape = {in_shape[0], in_shape[1], w_shape[1]};
            auto output = TensorView::create(out_shape, DType::FP32);
            
            if (device_ == Device::CPU) {
                ops::embedding_cpu(*input, *weight, *output);
            }
            
            tensor_cache_[node.output_ids[0]] = output;
            break;
        }
        
        case OpType::ADD: {
            auto input1 = get_or_load_tensor(node.input_ids[0]);
            auto input2 = get_or_load_tensor(node.input_ids[1]);
            
            auto output = TensorView::create(input1->shape(), input1->dtype());
            
            if (device_ == Device::CPU) {
                ops::add_cpu(*input1, *input2, *output);
            }
            
            tensor_cache_[node.output_ids[0]] = output;
            break;
        }
        
        case OpType::MUL: {
            auto input1 = get_or_load_tensor(node.input_ids[0]);
            auto input2 = get_or_load_tensor(node.input_ids[1]);
            
            auto output = TensorView::create(input1->shape(), input1->dtype());
            
            if (device_ == Device::CPU) {
                ops::mul_cpu(*input1, *input2, *output);
            }
            
            tensor_cache_[node.output_ids[0]] = output;
            break;
        }
        
        default:
            char error_msg[128];
            snprintf(error_msg, sizeof(error_msg), "Unsupported op type: %d", static_cast<int>(node.op_type));
            throw std::runtime_error(error_msg);
    }
}

std::shared_ptr<TensorView> Engine::allocate_tensor(const TensorDesc& desc) {
    std::vector<uint32_t> shape(desc.shape, desc.shape + desc.ndim);
    return TensorView::create(shape, desc.dtype);
}

} // namespace mle
