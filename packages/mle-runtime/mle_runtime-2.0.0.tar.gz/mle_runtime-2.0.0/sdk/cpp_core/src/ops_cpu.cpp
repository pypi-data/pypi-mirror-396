#include "tensor_view.h"
#include "mle_format.h"
#include <cmath>
#include <algorithm>
#include <stdexcept>
#include <vector>
#include <limits>

namespace mle {
namespace ops {

// CPU MatMul: C = A @ B
void matmul_cpu(const TensorView& A, const TensorView& B, TensorView& C) {
    if (A.dtype() != DType::FP32 || B.dtype() != DType::FP32 || C.dtype() != DType::FP32) {
        throw std::runtime_error("Only FP32 supported for CPU matmul");
    }
    
    const auto& a_shape = A.shape();
    const auto& b_shape = B.shape();
    const auto& c_shape = C.shape();
    
    // Support 2D: [M, K] @ [K, N] = [M, N]
    if (a_shape.size() != 2 || b_shape.size() != 2) {
        throw std::runtime_error("Only 2D matmul supported");
    }
    
    uint32_t M = a_shape[0];
    uint32_t K = a_shape[1];
    uint32_t N = b_shape[1];
    
    if (b_shape[0] != K || c_shape[0] != M || c_shape[1] != N) {
        throw std::runtime_error("Shape mismatch in matmul");
    }
    
    const float* a = static_cast<const float*>(A.data());
    const float* b = static_cast<const float*>(B.data());
    float* c = static_cast<float*>(C.data());
    
    // Naive implementation - can be optimized with BLAS
    for (uint32_t i = 0; i < M; ++i) {
        for (uint32_t j = 0; j < N; ++j) {
            float sum = 0.0f;
            for (uint32_t k = 0; k < K; ++k) {
                sum += a[i * K + k] * b[k * N + j];
            }
            c[i * N + j] = sum;
        }
    }
}

// Add bias: C = A + b (broadcast)
void add_bias_cpu(const TensorView& A, const TensorView& bias, TensorView& C) {
    if (A.dtype() != DType::FP32) {
        throw std::runtime_error("Only FP32 supported");
    }
    
    const auto& a_shape = A.shape();
    const auto& b_shape = bias.shape();
    
    // Assume bias is 1D and broadcasts to last dimension
    if (b_shape.size() != 1) {
        throw std::runtime_error("Bias must be 1D");
    }
    
    uint32_t N = b_shape[0];
    size_t numel = A.numel();
    
    const float* a = static_cast<const float*>(A.data());
    const float* b = static_cast<const float*>(bias.data());
    float* c = static_cast<float*>(C.data());
    
    for (size_t i = 0; i < numel; ++i) {
        c[i] = a[i] + b[i % N];
    }
}

// ReLU: y = max(0, x)
void relu_cpu(const TensorView& input, TensorView& output) {
    if (input.dtype() != DType::FP32) {
        throw std::runtime_error("Only FP32 supported");
    }
    
    size_t numel = input.numel();
    const float* in = static_cast<const float*>(input.data());
    float* out = static_cast<float*>(output.data());
    
    for (size_t i = 0; i < numel; ++i) {
        out[i] = std::max(0.0f, in[i]);
    }
}

// GELU: y = 0.5 * x * (1 + tanh(sqrt(2/pi) * (x + 0.044715 * x^3)))
void gelu_cpu(const TensorView& input, TensorView& output) {
    if (input.dtype() != DType::FP32) {
        throw std::runtime_error("Only FP32 supported");
    }
    
    size_t numel = input.numel();
    const float* in = static_cast<const float*>(input.data());
    float* out = static_cast<float*>(output.data());
    
    constexpr float sqrt_2_over_pi = 0.7978845608f;
    constexpr float coeff = 0.044715f;
    
    for (size_t i = 0; i < numel; ++i) {
        float x = in[i];
        float x3 = x * x * x;
        float inner = sqrt_2_over_pi * (x + coeff * x3);
        out[i] = 0.5f * x * (1.0f + std::tanh(inner));
    }
}

// Softmax: y_i = exp(x_i) / sum(exp(x_j))
void softmax_cpu(const TensorView& input, TensorView& output) {
    if (input.dtype() != DType::FP32) {
        throw std::runtime_error("Only FP32 supported");
    }
    
    const auto& shape = input.shape();
    const float* in = static_cast<const float*>(input.data());
    float* out = static_cast<float*>(output.data());
    
    // Assume last dimension is the softmax dimension
    // For 2D: [batch, features], softmax over features
    if (shape.size() == 2) {
        uint32_t batch = shape[0];
        uint32_t features = shape[1];
        
        for (uint32_t i = 0; i < batch; ++i) {
            const float* row_in = in + i * features;
            float* row_out = out + i * features;
            
            // Find max for numerical stability
            float max_val = row_in[0];
            for (uint32_t j = 1; j < features; ++j) {
                max_val = std::max(max_val, row_in[j]);
            }
            
            // Compute exp and sum
            float sum = 0.0f;
            for (uint32_t j = 0; j < features; ++j) {
                row_out[j] = std::exp(row_in[j] - max_val);
                sum += row_out[j];
            }
            
            // Normalize
            for (uint32_t j = 0; j < features; ++j) {
                row_out[j] /= sum;
            }
        }
    } else {
        throw std::runtime_error("Softmax only supports 2D tensors");
    }
}

// Linear layer: y = xW^T + b
void linear_cpu(const TensorView& input, const TensorView& weight, 
                const TensorView& bias, TensorView& output) {
    // Weight is [out_features, in_features], need to transpose
    // For simplicity, assume input is [batch, in_features]
    
    const auto& in_shape = input.shape();
    const auto& w_shape = weight.shape();
    
    if (in_shape.size() != 2 || w_shape.size() != 2) {
        throw std::runtime_error("Linear expects 2D tensors");
    }
    
    uint32_t batch = in_shape[0];
    uint32_t in_features = in_shape[1];
    uint32_t out_features = w_shape[0];
    
    if (w_shape[1] != in_features) {
        char error_msg[256];
        snprintf(error_msg, sizeof(error_msg),
                "Shape mismatch in linear: input=[%u,%u], weight=[%u,%u], expected weight=[%u,%u]",
                batch, in_features, w_shape[0], w_shape[1], out_features, in_features);
        throw std::runtime_error(error_msg);
    }
    
    const float* x = static_cast<const float*>(input.data());
    const float* w = static_cast<const float*>(weight.data());
    const float* b = static_cast<const float*>(bias.data());
    float* y = static_cast<float*>(output.data());
    
    // y = x @ W^T
    for (uint32_t i = 0; i < batch; ++i) {
        for (uint32_t j = 0; j < out_features; ++j) {
            float sum = 0.0f;
            for (uint32_t k = 0; k < in_features; ++k) {
                sum += x[i * in_features + k] * w[j * in_features + k];
            }
            y[i * out_features + j] = sum + b[j];
        }
    }
}

// Decision Tree inference
void decision_tree_cpu(const TensorView& input_tensor, 
                       const TensorView& feature_tensor, const TensorView& threshold_tensor,
                       const TensorView& value_tensor, const TensorView& children_left_tensor,
                       const TensorView& children_right_tensor, TensorView& output_tensor) {
    if (input_tensor.dtype() != DType::FP32) {
        throw std::runtime_error("Only FP32 supported for decision tree");
    }
    
    const auto& in_shape = input_tensor.shape();
    const auto& out_shape = output_tensor.shape();
    
    uint32_t batch_size = in_shape[0];
    uint32_t n_features = in_shape[1];
    uint32_t n_outputs = out_shape[1];
    
    const float* x = static_cast<const float*>(input_tensor.data());
    const int32_t* features = static_cast<const int32_t*>(feature_tensor.data());
    const float* thresholds = static_cast<const float*>(threshold_tensor.data());
    const float* values = static_cast<const float*>(value_tensor.data());
    const int32_t* left = static_cast<const int32_t*>(children_left_tensor.data());
    const int32_t* right = static_cast<const int32_t*>(children_right_tensor.data());
    float* y = static_cast<float*>(output_tensor.data());
    
    // Get value shape to understand output structure
    const auto& value_shape = value_tensor.shape();
    uint32_t n_nodes = value_shape[0];
    // value is [n_nodes, 1, n_classes] for sklearn trees
    size_t value_ndim = value_tensor.ndim();
    uint32_t value_stride = (value_ndim == 3) ? (value_shape[1] * value_shape[2]) : 
                           (value_ndim == 2) ? value_shape[1] : 1;
    
    // Process each sample
    for (uint32_t i = 0; i < batch_size; ++i) {
        const float* sample = x + i * n_features;
        
        // Traverse tree
        int32_t node = 0;
        while (left[node] != -1) {  // -1 indicates leaf node
            int32_t feat_idx = features[node];
            float threshold_val = thresholds[node];
            
            if (sample[feat_idx] <= threshold_val) {
                node = left[node];
            } else {
                node = right[node];
            }
        }
        
        // At leaf node, get prediction
        // For sklearn: value is [n_nodes, 1, n_classes], so skip middle dimension
        const float* node_value_base = values + node * value_stride;
        
        // Calculate sum for normalization
        float sum = 0.0f;
        for (uint32_t j = 0; j < n_outputs; ++j) {
            sum += node_value_base[j];
        }
        
        // Normalize and copy to output
        if (sum > 0.0f) {
            for (uint32_t j = 0; j < n_outputs; ++j) {
                y[i * n_outputs + j] = node_value_base[j] / sum;
            }
        } else {
            // Uniform distribution if sum is 0
            float uniform = 1.0f / n_outputs;
            for (uint32_t j = 0; j < n_outputs; ++j) {
                y[i * n_outputs + j] = uniform;
            }
        }
    }
}

// Tree Ensemble (Random Forest, Gradient Boosting)
void tree_ensemble_cpu(const TensorView& input_tensor, 
                       const std::vector<TensorView>& tree_params,
                       TensorView& output_tensor,
                       bool is_classifier) {
    if (input_tensor.dtype() != DType::FP32) {
        throw std::runtime_error("Only FP32 supported for tree ensemble");
    }
    
    const auto& in_shape = input_tensor.shape();
    const auto& out_shape = output_tensor.shape();
    
    uint32_t batch_size = in_shape[0];
    uint32_t n_outputs = out_shape[1];
    
    const float* x = static_cast<const float*>(input_tensor.data());
    float* y = static_cast<float*>(output_tensor.data());
    
    // Initialize output to zero
    std::fill(y, y + batch_size * n_outputs, 0.0f);
    
    // Number of trees
    uint32_t n_trees = tree_params.size() / 5;  // 5 params per tree
    
    // Process each tree
    for (uint32_t t = 0; t < n_trees; ++t) {
        const int32_t* features = static_cast<const int32_t*>(tree_params[t * 5 + 0].data());
        const float* thresholds = static_cast<const float*>(tree_params[t * 5 + 1].data());
        const float* values = static_cast<const float*>(tree_params[t * 5 + 2].data());
        const int32_t* left = static_cast<const int32_t*>(tree_params[t * 5 + 3].data());
        const int32_t* right = static_cast<const int32_t*>(tree_params[t * 5 + 4].data());
        
        const auto& value_shape = tree_params[t * 5 + 2].shape();
        uint32_t value_stride = (value_shape.size() == 3) ? (value_shape[1] * value_shape[2]) : 
                               (value_shape.size() == 2) ? value_shape[1] : 1;
        
        // Process each sample
        for (uint32_t i = 0; i < batch_size; ++i) {
            const float* sample = x + i * in_shape[1];
            
            // Traverse tree
            int32_t node = 0;
            while (left[node] != -1) {
                int32_t feat_idx = features[node];
                if (sample[feat_idx] <= thresholds[node]) {
                    node = left[node];
                } else {
                    node = right[node];
                }
            }
            
            // Add tree prediction to ensemble
            const float* node_value = values + node * value_stride;
            for (uint32_t j = 0; j < n_outputs; ++j) {
                y[i * n_outputs + j] += node_value[j];
            }
        }
    }
    
    // Average predictions for classification, or normalize
    if (is_classifier) {
        for (uint32_t i = 0; i < batch_size; ++i) {
            float sum = 0.0f;
            for (uint32_t j = 0; j < n_outputs; ++j) {
                sum += y[i * n_outputs + j];
            }
            if (sum > 0.0f) {
                for (uint32_t j = 0; j < n_outputs; ++j) {
                    y[i * n_outputs + j] /= sum;
                }
            }
        }
    } else {
        // Average for regression
        for (uint32_t i = 0; i < batch_size * n_outputs; ++i) {
            y[i] /= n_trees;
        }
    }
}

// SVM with RBF kernel
void svm_cpu(const TensorView& input_tensor,
             const TensorView& support_vectors,
             const TensorView& dual_coef,
             const TensorView& intercept,
             TensorView& output_tensor,
             float gamma = 0.1f) {
    const auto& in_shape = input_tensor.shape();
    uint32_t batch_size = in_shape[0];
    uint32_t n_features = in_shape[1];
    
    const auto& sv_shape = support_vectors.shape();
    uint32_t n_support = sv_shape[0];
    
    const float* x = static_cast<const float*>(input_tensor.data());
    const float* sv = static_cast<const float*>(support_vectors.data());
    const float* coef = static_cast<const float*>(dual_coef.data());
    const float* b = static_cast<const float*>(intercept.data());
    float* y = static_cast<float*>(output_tensor.data());
    
    const auto& out_shape = output_tensor.shape();
    uint32_t n_classes = out_shape[1];
    
    // For each sample
    for (uint32_t i = 0; i < batch_size; ++i) {
        const float* sample = x + i * n_features;
        
        // Initialize decision values
        for (uint32_t c = 0; c < n_classes; ++c) {
            float decision = b[c];
            
            // Sum over support vectors
            for (uint32_t s = 0; s < n_support; ++s) {
                const float* sv_vec = sv + s * n_features;
                
                // RBF kernel: exp(-gamma * ||x - sv||^2)
                float dist_sq = 0.0f;
                for (uint32_t f = 0; f < n_features; ++f) {
                    float diff = sample[f] - sv_vec[f];
                    dist_sq += diff * diff;
                }
                float kernel_val = std::exp(-gamma * dist_sq);
                
                decision += coef[c * n_support + s] * kernel_val;
            }
            
            y[i * n_classes + c] = decision;
        }
        
        // Convert to probabilities using softmax
        float max_val = y[i * n_classes];
        for (uint32_t c = 1; c < n_classes; ++c) {
            max_val = std::max(max_val, y[i * n_classes + c]);
        }
        
        float sum = 0.0f;
        for (uint32_t c = 0; c < n_classes; ++c) {
            y[i * n_classes + c] = std::exp(y[i * n_classes + c] - max_val);
            sum += y[i * n_classes + c];
        }
        
        for (uint32_t c = 0; c < n_classes; ++c) {
            y[i * n_classes + c] /= sum;
        }
    }
}

// Gaussian Naive Bayes
void naive_bayes_cpu(const TensorView& input_tensor,
                     const TensorView& theta,
                     const TensorView& sigma,
                     TensorView& output_tensor) {
    const auto& in_shape = input_tensor.shape();
    uint32_t batch_size = in_shape[0];
    uint32_t n_features = in_shape[1];
    
    const auto& theta_shape = theta.shape();
    uint32_t n_classes = theta_shape[0];
    
    const float* x = static_cast<const float*>(input_tensor.data());
    const float* mean = static_cast<const float*>(theta.data());
    const float* var = static_cast<const float*>(sigma.data());
    float* y = static_cast<float*>(output_tensor.data());
    
    constexpr float PI = 3.14159265358979323846f;
    
    for (uint32_t i = 0; i < batch_size; ++i) {
        const float* sample = x + i * n_features;
        
        // Compute log probability for each class
        for (uint32_t c = 0; c < n_classes; ++c) {
            float log_prob = 0.0f;
            
            for (uint32_t f = 0; f < n_features; ++f) {
                float m = mean[c * n_features + f];
                float v = var[c * n_features + f];
                float diff = sample[f] - m;
                
                // Gaussian log probability
                log_prob += -0.5f * std::log(2.0f * PI * v) - (diff * diff) / (2.0f * v);
            }
            
            y[i * n_classes + c] = log_prob;
        }
        
        // Convert log probabilities to probabilities using softmax
        float max_log = y[i * n_classes];
        for (uint32_t c = 1; c < n_classes; ++c) {
            max_log = std::max(max_log, y[i * n_classes + c]);
        }
        
        float sum = 0.0f;
        for (uint32_t c = 0; c < n_classes; ++c) {
            y[i * n_classes + c] = std::exp(y[i * n_classes + c] - max_log);
            sum += y[i * n_classes + c];
        }
        
        for (uint32_t c = 0; c < n_classes; ++c) {
            y[i * n_classes + c] /= sum;
        }
    }
}

// K-Nearest Neighbors
void knn_cpu(const TensorView& input_tensor,
             const TensorView& fit_X,
             const TensorView& fit_y,
             TensorView& output_tensor,
             uint32_t k = 5) {
    const auto& in_shape = input_tensor.shape();
    uint32_t batch_size = in_shape[0];
    uint32_t n_features = in_shape[1];
    
    const auto& fit_shape = fit_X.shape();
    uint32_t n_samples = fit_shape[0];
    
    const float* x = static_cast<const float*>(input_tensor.data());
    const float* train_x = static_cast<const float*>(fit_X.data());
    const float* train_y = static_cast<const float*>(fit_y.data());
    float* y = static_cast<float*>(output_tensor.data());
    
    const auto& out_shape = output_tensor.shape();
    uint32_t n_outputs = out_shape[1];
    
    // Temporary storage for distances
    std::vector<std::pair<float, uint32_t>> distances(n_samples);
    
    for (uint32_t i = 0; i < batch_size; ++i) {
        const float* sample = x + i * n_features;
        
        // Compute distances to all training samples
        for (uint32_t j = 0; j < n_samples; ++j) {
            const float* train_sample = train_x + j * n_features;
            float dist = 0.0f;
            for (uint32_t f = 0; f < n_features; ++f) {
                float diff = sample[f] - train_sample[f];
                dist += diff * diff;
            }
            distances[j] = {dist, j};
        }
        
        // Partial sort to find k nearest
        std::partial_sort(distances.begin(), distances.begin() + k, distances.end());
        
        // Average k nearest labels (for classification, this gives probabilities)
        std::fill(y + i * n_outputs, y + (i + 1) * n_outputs, 0.0f);
        for (uint32_t j = 0; j < k; ++j) {
            uint32_t idx = distances[j].second;
            uint32_t label = static_cast<uint32_t>(train_y[idx]);
            if (label < n_outputs) {
                y[i * n_outputs + label] += 1.0f / k;
            }
        }
    }
}

// K-Means clustering
void clustering_cpu(const TensorView& input_tensor,
                    const TensorView& cluster_centers,
                    TensorView& output_tensor) {
    const auto& in_shape = input_tensor.shape();
    uint32_t batch_size = in_shape[0];
    uint32_t n_features = in_shape[1];
    
    const auto& center_shape = cluster_centers.shape();
    uint32_t n_clusters = center_shape[0];
    
    const float* x = static_cast<const float*>(input_tensor.data());
    const float* centers = static_cast<const float*>(cluster_centers.data());
    float* y = static_cast<float*>(output_tensor.data());
    
    for (uint32_t i = 0; i < batch_size; ++i) {
        const float* sample = x + i * n_features;
        
        // Find nearest cluster
        float min_dist = std::numeric_limits<float>::max();
        uint32_t nearest = 0;
        
        for (uint32_t c = 0; c < n_clusters; ++c) {
            const float* center = centers + c * n_features;
            float dist = 0.0f;
            for (uint32_t f = 0; f < n_features; ++f) {
                float diff = sample[f] - center[f];
                dist += diff * diff;
            }
            if (dist < min_dist) {
                min_dist = dist;
                nearest = c;
            }
        }
        
        y[i] = static_cast<float>(nearest);
    }
}

// PCA decomposition
void decomposition_cpu(const TensorView& input_tensor,
                       const TensorView& components,
                       const TensorView* mean_tensor,
                       TensorView& output_tensor) {
    const auto& in_shape = input_tensor.shape();
    uint32_t batch_size = in_shape[0];
    uint32_t n_features = in_shape[1];
    
    const auto& comp_shape = components.shape();
    uint32_t n_components = comp_shape[0];
    
    const float* x = static_cast<const float*>(input_tensor.data());
    const float* comp = static_cast<const float*>(components.data());
    const float* mean = mean_tensor ? static_cast<const float*>(mean_tensor->data()) : nullptr;
    float* y = static_cast<float*>(output_tensor.data());
    
    for (uint32_t i = 0; i < batch_size; ++i) {
        const float* sample = x + i * n_features;
        
        for (uint32_t c = 0; c < n_components; ++c) {
            const float* component = comp + c * n_features;
            float dot = 0.0f;
            
            for (uint32_t f = 0; f < n_features; ++f) {
                float val = sample[f];
                if (mean) {
                    val -= mean[f];
                }
                dot += val * component[f];
            }
            
            y[i * n_components + c] = dot;
        }
    }
}

} // namespace ops
} // namespace mle
