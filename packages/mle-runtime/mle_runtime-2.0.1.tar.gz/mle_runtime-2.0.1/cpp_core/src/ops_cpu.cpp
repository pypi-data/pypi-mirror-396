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

// Conv2D: 2D Convolution
void conv2d_cpu(const TensorView& input, const TensorView& weight, 
                const TensorView& bias, TensorView& output,
                uint32_t stride_h = 1, uint32_t stride_w = 1,
                uint32_t pad_h = 0, uint32_t pad_w = 0) {
    if (input.dtype() != DType::FP32) {
        throw std::runtime_error("Only FP32 supported for Conv2D");
    }
    
    const auto& in_shape = input.shape();   // [N, C_in, H_in, W_in]
    const auto& w_shape = weight.shape();   // [C_out, C_in, K_h, K_w]
    const auto& out_shape = output.shape(); // [N, C_out, H_out, W_out]
    
    if (in_shape.size() != 4 || w_shape.size() != 4 || out_shape.size() != 4) {
        throw std::runtime_error("Conv2D expects 4D tensors");
    }
    
    uint32_t N = in_shape[0];
    uint32_t C_in = in_shape[1];
    uint32_t H_in = in_shape[2];
    uint32_t W_in = in_shape[3];
    
    uint32_t C_out = w_shape[0];
    uint32_t K_h = w_shape[2];
    uint32_t K_w = w_shape[3];
    
    uint32_t H_out = out_shape[2];
    uint32_t W_out = out_shape[3];
    
    const float* x = static_cast<const float*>(input.data());
    const float* w = static_cast<const float*>(weight.data());
    const float* b = static_cast<const float*>(bias.data());
    float* y = static_cast<float*>(output.data());
    
    // Initialize output with bias
    for (uint32_t n = 0; n < N; ++n) {
        for (uint32_t c_out = 0; c_out < C_out; ++c_out) {
            for (uint32_t h = 0; h < H_out; ++h) {
                for (uint32_t w = 0; w < W_out; ++w) {
                    uint32_t out_idx = n * C_out * H_out * W_out + 
                                      c_out * H_out * W_out + 
                                      h * W_out + w;
                    y[out_idx] = b[c_out];
                }
            }
        }
    }
    
    // Convolution
    for (uint32_t n = 0; n < N; ++n) {
        for (uint32_t c_out = 0; c_out < C_out; ++c_out) {
            for (uint32_t h_out = 0; h_out < H_out; ++h_out) {
                for (uint32_t w_out = 0; w_out < W_out; ++w_out) {
                    uint32_t out_idx = n * C_out * H_out * W_out + 
                                      c_out * H_out * W_out + 
                                      h_out * W_out + w_out;
                    
                    for (uint32_t c_in = 0; c_in < C_in; ++c_in) {
                        for (uint32_t k_h = 0; k_h < K_h; ++k_h) {
                            for (uint32_t k_w = 0; k_w < K_w; ++k_w) {
                                int32_t h_in = h_out * stride_h + k_h - pad_h;
                                int32_t w_in = w_out * stride_w + k_w - pad_w;
                                
                                if (h_in >= 0 && h_in < (int32_t)H_in && 
                                    w_in >= 0 && w_in < (int32_t)W_in) {
                                    uint32_t in_idx = n * C_in * H_in * W_in + 
                                                     c_in * H_in * W_in + 
                                                     h_in * W_in + w_in;
                                    uint32_t w_idx = c_out * C_in * K_h * K_w + 
                                                    c_in * K_h * K_w + 
                                                    k_h * K_w + k_w;
                                    
                                    y[out_idx] += x[in_idx] * w[w_idx];
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

// MaxPool2D: 2D Max Pooling
void maxpool2d_cpu(const TensorView& input, TensorView& output,
                   uint32_t kernel_h = 2, uint32_t kernel_w = 2,
                   uint32_t stride_h = 2, uint32_t stride_w = 2,
                   uint32_t pad_h = 0, uint32_t pad_w = 0) {
    if (input.dtype() != DType::FP32) {
        throw std::runtime_error("Only FP32 supported for MaxPool2D");
    }
    
    const auto& in_shape = input.shape();   // [N, C, H_in, W_in]
    const auto& out_shape = output.shape(); // [N, C, H_out, W_out]
    
    if (in_shape.size() != 4 || out_shape.size() != 4) {
        throw std::runtime_error("MaxPool2D expects 4D tensors");
    }
    
    uint32_t N = in_shape[0];
    uint32_t C = in_shape[1];
    uint32_t H_in = in_shape[2];
    uint32_t W_in = in_shape[3];
    
    uint32_t H_out = out_shape[2];
    uint32_t W_out = out_shape[3];
    
    const float* x = static_cast<const float*>(input.data());
    float* y = static_cast<float*>(output.data());
    
    for (uint32_t n = 0; n < N; ++n) {
        for (uint32_t c = 0; c < C; ++c) {
            for (uint32_t h_out = 0; h_out < H_out; ++h_out) {
                for (uint32_t w_out = 0; w_out < W_out; ++w_out) {
                    float max_val = -std::numeric_limits<float>::infinity();
                    
                    for (uint32_t k_h = 0; k_h < kernel_h; ++k_h) {
                        for (uint32_t k_w = 0; k_w < kernel_w; ++k_w) {
                            int32_t h_in = h_out * stride_h + k_h - pad_h;
                            int32_t w_in = w_out * stride_w + k_w - pad_w;
                            
                            if (h_in >= 0 && h_in < (int32_t)H_in && 
                                w_in >= 0 && w_in < (int32_t)W_in) {
                                uint32_t in_idx = n * C * H_in * W_in + 
                                                 c * H_in * W_in + 
                                                 h_in * W_in + w_in;
                                max_val = std::max(max_val, x[in_idx]);
                            }
                        }
                    }
                    
                    uint32_t out_idx = n * C * H_out * W_out + 
                                      c * H_out * W_out + 
                                      h_out * W_out + w_out;
                    y[out_idx] = max_val;
                }
            }
        }
    }
}

// BatchNorm: Batch Normalization
void batchnorm_cpu(const TensorView& input, const TensorView& weight,
                   const TensorView& bias, const TensorView& running_mean,
                   const TensorView& running_var, TensorView& output,
                   float eps = 1e-5f) {
    if (input.dtype() != DType::FP32) {
        throw std::runtime_error("Only FP32 supported for BatchNorm");
    }
    
    const auto& in_shape = input.shape();
    uint32_t N = in_shape[0];
    uint32_t C = in_shape[1];
    
    const float* x = static_cast<const float*>(input.data());
    const float* gamma = static_cast<const float*>(weight.data());
    const float* beta = static_cast<const float*>(bias.data());
    const float* mean = static_cast<const float*>(running_mean.data());
    const float* var = static_cast<const float*>(running_var.data());
    float* y = static_cast<float*>(output.data());
    
    size_t spatial_size = input.numel() / (N * C);
    
    for (uint32_t n = 0; n < N; ++n) {
        for (uint32_t c = 0; c < C; ++c) {
            float channel_mean = mean[c];
            float channel_var = var[c];
            float inv_std = 1.0f / std::sqrt(channel_var + eps);
            
            for (size_t s = 0; s < spatial_size; ++s) {
                size_t idx = n * C * spatial_size + c * spatial_size + s;
                y[idx] = gamma[c] * (x[idx] - channel_mean) * inv_std + beta[c];
            }
        }
    }
}

// Attention: Multi-Head Self-Attention (simplified)
void attention_cpu(const TensorView& query, const TensorView& key, 
                   const TensorView& value, TensorView& output,
                   uint32_t num_heads = 8, float scale = 0.125f) {
    if (query.dtype() != DType::FP32) {
        throw std::runtime_error("Only FP32 supported for Attention");
    }
    
    const auto& q_shape = query.shape();    // [batch, seq_len, d_model]
    const auto& k_shape = key.shape();      // [batch, seq_len, d_model]
    const auto& v_shape = value.shape();    // [batch, seq_len, d_model]
    
    if (q_shape.size() != 3 || k_shape.size() != 3 || v_shape.size() != 3) {
        throw std::runtime_error("Attention expects 3D tensors");
    }
    
    uint32_t batch = q_shape[0];
    uint32_t seq_len = q_shape[1];
    uint32_t d_model = q_shape[2];
    uint32_t d_head = d_model / num_heads;
    
    const float* q = static_cast<const float*>(query.data());
    const float* k = static_cast<const float*>(key.data());
    const float* v = static_cast<const float*>(value.data());
    float* out = static_cast<float*>(output.data());
    
    // Temporary storage for attention scores
    std::vector<float> scores(seq_len * seq_len);
    std::vector<float> head_out(seq_len * d_head);
    
    for (uint32_t b = 0; b < batch; ++b) {
        for (uint32_t h = 0; h < num_heads; ++h) {
            // Extract head slices
            const float* q_head = q + b * seq_len * d_model + h * d_head;
            const float* k_head = k + b * seq_len * d_model + h * d_head;
            const float* v_head = v + b * seq_len * d_model + h * d_head;
            
            // Compute attention scores: Q @ K^T
            for (uint32_t i = 0; i < seq_len; ++i) {
                for (uint32_t j = 0; j < seq_len; ++j) {
                    float score = 0.0f;
                    for (uint32_t d = 0; d < d_head; ++d) {
                        score += q_head[i * d_model + d] * k_head[j * d_model + d];
                    }
                    scores[i * seq_len + j] = score * scale;
                }
            }
            
            // Apply softmax to each row
            for (uint32_t i = 0; i < seq_len; ++i) {
                float max_score = scores[i * seq_len];
                for (uint32_t j = 1; j < seq_len; ++j) {
                    max_score = std::max(max_score, scores[i * seq_len + j]);
                }
                
                float sum = 0.0f;
                for (uint32_t j = 0; j < seq_len; ++j) {
                    scores[i * seq_len + j] = std::exp(scores[i * seq_len + j] - max_score);
                    sum += scores[i * seq_len + j];
                }
                
                for (uint32_t j = 0; j < seq_len; ++j) {
                    scores[i * seq_len + j] /= sum;
                }
            }
            
            // Apply attention to values: Attention @ V
            for (uint32_t i = 0; i < seq_len; ++i) {
                for (uint32_t d = 0; d < d_head; ++d) {
                    float sum = 0.0f;
                    for (uint32_t j = 0; j < seq_len; ++j) {
                        sum += scores[i * seq_len + j] * v_head[j * d_model + d];
                    }
                    head_out[i * d_head + d] = sum;
                }
            }
            
            // Copy head output to final output
            float* out_head = out + b * seq_len * d_model + h * d_head;
            for (uint32_t i = 0; i < seq_len; ++i) {
                for (uint32_t d = 0; d < d_head; ++d) {
                    out_head[i * d_model + d] = head_out[i * d_head + d];
                }
            }
        }
    }
}

// Gradient Boosting Trees
void gradient_boosting_cpu(const TensorView& input_tensor,
                          const std::vector<TensorView>& tree_params,
                          const TensorView& learning_rates,
                          TensorView& output_tensor,
                          bool is_classifier = false) {
    if (input_tensor.dtype() != DType::FP32) {
        throw std::runtime_error("Only FP32 supported for gradient boosting");
    }
    
    const auto& in_shape = input_tensor.shape();
    const auto& out_shape = output_tensor.shape();
    
    uint32_t batch_size = in_shape[0];
    uint32_t n_outputs = out_shape[1];
    
    const float* x = static_cast<const float*>(input_tensor.data());
    const float* lr = static_cast<const float*>(learning_rates.data());
    float* y = static_cast<float*>(output_tensor.data());
    
    // Initialize output to zero
    std::fill(y, y + batch_size * n_outputs, 0.0f);
    
    // Number of trees (5 params per tree)
    uint32_t n_trees = tree_params.size() / 5;
    
    // Process each tree with learning rate
    for (uint32_t t = 0; t < n_trees; ++t) {
        const int32_t* features = static_cast<const int32_t*>(tree_params[t * 5 + 0].data());
        const float* thresholds = static_cast<const float*>(tree_params[t * 5 + 1].data());
        const float* values = static_cast<const float*>(tree_params[t * 5 + 2].data());
        const int32_t* left = static_cast<const int32_t*>(tree_params[t * 5 + 3].data());
        const int32_t* right = static_cast<const int32_t*>(tree_params[t * 5 + 4].data());
        
        const auto& value_shape = tree_params[t * 5 + 2].shape();
        uint32_t value_stride = (value_shape.size() == 3) ? (value_shape[1] * value_shape[2]) : 
                               (value_shape.size() == 2) ? value_shape[1] : 1;
        
        float tree_lr = (t < learning_rates.numel()) ? lr[t] : 0.1f;  // Default learning rate
        
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
            
            // Add weighted tree prediction
            const float* node_value = values + node * value_stride;
            for (uint32_t j = 0; j < n_outputs; ++j) {
                y[i * n_outputs + j] += tree_lr * node_value[j];
            }
        }
    }
    
    // Apply final transformation for classification
    if (is_classifier && n_outputs > 1) {
        for (uint32_t i = 0; i < batch_size; ++i) {
            // Apply softmax
            float max_val = y[i * n_outputs];
            for (uint32_t j = 1; j < n_outputs; ++j) {
                max_val = std::max(max_val, y[i * n_outputs + j]);
            }
            
            float sum = 0.0f;
            for (uint32_t j = 0; j < n_outputs; ++j) {
                y[i * n_outputs + j] = std::exp(y[i * n_outputs + j] - max_val);
                sum += y[i * n_outputs + j];
            }
            
            for (uint32_t j = 0; j < n_outputs; ++j) {
                y[i * n_outputs + j] /= sum;
            }
        }
    }
}

// DBSCAN Clustering
void dbscan_cpu(const TensorView& input_tensor,
                TensorView& output_tensor,
                float eps = 0.5f,
                uint32_t min_samples = 5) {
    const auto& in_shape = input_tensor.shape();
    uint32_t n_samples = in_shape[0];
    uint32_t n_features = in_shape[1];
    
    const float* x = static_cast<const float*>(input_tensor.data());
    float* labels = static_cast<float*>(output_tensor.data());
    
    // Initialize all points as unvisited (-1)
    std::vector<int32_t> cluster_labels(n_samples, -1);
    std::vector<bool> visited(n_samples, false);
    
    int32_t cluster_id = 0;
    
    for (uint32_t i = 0; i < n_samples; ++i) {
        if (visited[i]) continue;
        
        visited[i] = true;
        
        // Find neighbors
        std::vector<uint32_t> neighbors;
        for (uint32_t j = 0; j < n_samples; ++j) {
            if (i == j) continue;
            
            // Compute Euclidean distance
            float dist = 0.0f;
            for (uint32_t f = 0; f < n_features; ++f) {
                float diff = x[i * n_features + f] - x[j * n_features + f];
                dist += diff * diff;
            }
            dist = std::sqrt(dist);
            
            if (dist <= eps) {
                neighbors.push_back(j);
            }
        }
        
        if (neighbors.size() < min_samples) {
            cluster_labels[i] = -1;  // Noise point
        } else {
            // Start new cluster
            cluster_labels[i] = cluster_id;
            
            // Expand cluster
            for (size_t n = 0; n < neighbors.size(); ++n) {
                uint32_t neighbor = neighbors[n];
                
                if (!visited[neighbor]) {
                    visited[neighbor] = true;
                    
                    // Find neighbor's neighbors
                    std::vector<uint32_t> neighbor_neighbors;
                    for (uint32_t k = 0; k < n_samples; ++k) {
                        if (neighbor == k) continue;
                        
                        float dist = 0.0f;
                        for (uint32_t f = 0; f < n_features; ++f) {
                            float diff = x[neighbor * n_features + f] - x[k * n_features + f];
                            dist += diff * diff;
                        }
                        dist = std::sqrt(dist);
                        
                        if (dist <= eps) {
                            neighbor_neighbors.push_back(k);
                        }
                    }
                    
                    if (neighbor_neighbors.size() >= min_samples) {
                        // Add new neighbors to expansion list
                        for (uint32_t nn : neighbor_neighbors) {
                            bool already_in = false;
                            for (uint32_t existing : neighbors) {
                                if (existing == nn) {
                                    already_in = true;
                                    break;
                                }
                            }
                            if (!already_in) {
                                neighbors.push_back(nn);
                            }
                        }
                    }
                }
                
                if (cluster_labels[neighbor] == -1) {
                    cluster_labels[neighbor] = cluster_id;
                }
            }
            
            cluster_id++;
        }
    }
    
    // Copy results to output
    for (uint32_t i = 0; i < n_samples; ++i) {
        labels[i] = static_cast<float>(cluster_labels[i]);
    }
}

// Layer Normalization
void layernorm_cpu(const TensorView& input, const TensorView& weight,
                   const TensorView& bias, TensorView& output,
                   float eps = 1e-5f) {
    if (input.dtype() != DType::FP32) {
        throw std::runtime_error("Only FP32 supported for LayerNorm");
    }
    
    const auto& in_shape = input.shape();
    uint32_t batch_size = in_shape[0];
    uint32_t feature_size = in_shape[1];
    
    const float* x = static_cast<const float*>(input.data());
    const float* gamma = static_cast<const float*>(weight.data());
    const float* beta = static_cast<const float*>(bias.data());
    float* y = static_cast<float*>(output.data());
    
    for (uint32_t b = 0; b < batch_size; ++b) {
        const float* x_batch = x + b * feature_size;
        float* y_batch = y + b * feature_size;
        
        // Compute mean
        float mean = 0.0f;
        for (uint32_t f = 0; f < feature_size; ++f) {
            mean += x_batch[f];
        }
        mean /= feature_size;
        
        // Compute variance
        float var = 0.0f;
        for (uint32_t f = 0; f < feature_size; ++f) {
            float diff = x_batch[f] - mean;
            var += diff * diff;
        }
        var /= feature_size;
        
        // Normalize
        float inv_std = 1.0f / std::sqrt(var + eps);
        for (uint32_t f = 0; f < feature_size; ++f) {
            y_batch[f] = gamma[f] * (x_batch[f] - mean) * inv_std + beta[f];
        }
    }
}

// Dropout (inference mode - pass through)
void dropout_cpu(const TensorView& input, TensorView& output, float dropout_rate = 0.0f) {
    // In inference mode, dropout is just a pass-through
    size_t numel = input.numel();
    const float* in = static_cast<const float*>(input.data());
    float* out = static_cast<float*>(output.data());
    
    // Apply scaling factor (1 - dropout_rate) for inference
    float scale = 1.0f - dropout_rate;
    for (size_t i = 0; i < numel; ++i) {
        out[i] = in[i] * scale;
    }
}

// Embedding layer
void embedding_cpu(const TensorView& input, const TensorView& weight, TensorView& output) {
    if (input.dtype() != DType::INT32) {
        throw std::runtime_error("Input must be INT32 for embedding");
    }
    
    const auto& in_shape = input.shape();
    const auto& w_shape = weight.shape();
    
    uint32_t batch_size = in_shape[0];
    uint32_t seq_len = in_shape[1];
    uint32_t vocab_size = w_shape[0];
    uint32_t embed_dim = w_shape[1];
    
    const int32_t* indices = static_cast<const int32_t*>(input.data());
    const float* embeddings = static_cast<const float*>(weight.data());
    float* out = static_cast<float*>(output.data());
    
    for (uint32_t b = 0; b < batch_size; ++b) {
        for (uint32_t s = 0; s < seq_len; ++s) {
            int32_t idx = indices[b * seq_len + s];
            if (idx >= 0 && idx < (int32_t)vocab_size) {
                const float* embed_vec = embeddings + idx * embed_dim;
                float* out_vec = out + (b * seq_len + s) * embed_dim;
                
                for (uint32_t d = 0; d < embed_dim; ++d) {
                    out_vec[d] = embed_vec[d];
                }
            } else {
                // Zero out invalid indices
                float* out_vec = out + (b * seq_len + s) * embed_dim;
                for (uint32_t d = 0; d < embed_dim; ++d) {
                    out_vec[d] = 0.0f;
                }
            }
        }
    }
}

// Add/Element-wise addition
void add_cpu(const TensorView& input1, const TensorView& input2, TensorView& output) {
    if (input1.dtype() != DType::FP32 || input2.dtype() != DType::FP32) {
        throw std::runtime_error("Only FP32 supported for add");
    }
    
    size_t numel = input1.numel();
    if (input2.numel() != numel || output.numel() != numel) {
        throw std::runtime_error("Tensor size mismatch in add operation");
    }
    
    const float* a = static_cast<const float*>(input1.data());
    const float* b = static_cast<const float*>(input2.data());
    float* c = static_cast<float*>(output.data());
    
    for (size_t i = 0; i < numel; ++i) {
        c[i] = a[i] + b[i];
    }
}

// Multiply/Element-wise multiplication
void mul_cpu(const TensorView& input1, const TensorView& input2, TensorView& output) {
    if (input1.dtype() != DType::FP32 || input2.dtype() != DType::FP32) {
        throw std::runtime_error("Only FP32 supported for mul");
    }
    
    size_t numel = input1.numel();
    if (input2.numel() != numel || output.numel() != numel) {
        throw std::runtime_error("Tensor size mismatch in mul operation");
    }
    
    const float* a = static_cast<const float*>(input1.data());
    const float* b = static_cast<const float*>(input2.data());
    float* c = static_cast<float*>(output.data());
    
    for (size_t i = 0; i < numel; ++i) {
        c[i] = a[i] * b[i];
    }
}

} // namespace ops
} // namespace mle
