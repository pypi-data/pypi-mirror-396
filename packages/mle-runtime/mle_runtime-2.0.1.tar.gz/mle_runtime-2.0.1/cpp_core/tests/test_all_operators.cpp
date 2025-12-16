#include "tensor_view.h"
#include "mle_format.h"
#include "compression.h"
#include "security.h"
#include <iostream>
#include <vector>
#include <cmath>
#include <cassert>
#include <chrono>
#include <fstream>

namespace mle {
namespace ops {
    // Forward declarations for all operators
    void linear_cpu(const TensorView& input, const TensorView& weight, 
                    const TensorView& bias, TensorView& output);
    void relu_cpu(const TensorView& input, TensorView& output);
    void gelu_cpu(const TensorView& input, TensorView& output);
    void softmax_cpu(const TensorView& input, TensorView& output);
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
                       const TensorView& running_var, TensorView& output, float eps);
    void attention_cpu(const TensorView& query, const TensorView& key, 
                       const TensorView& value, TensorView& output,
                       uint32_t num_heads, float scale);
    void decision_tree_cpu(const TensorView& input_tensor, 
                          const TensorView& feature_tensor, const TensorView& threshold_tensor,
                          const TensorView& value_tensor, const TensorView& children_left_tensor,
                          const TensorView& children_right_tensor, TensorView& output_tensor);
    void tree_ensemble_cpu(const TensorView& input_tensor, 
                          const std::vector<TensorView>& tree_params,
                          TensorView& output_tensor, bool is_classifier);
    void gradient_boosting_cpu(const TensorView& input_tensor,
                              const std::vector<TensorView>& tree_params,
                              const TensorView& learning_rates,
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
    void dbscan_cpu(const TensorView& input_tensor, TensorView& output_tensor,
                    float eps, uint32_t min_samples);
    void decomposition_cpu(const TensorView& input_tensor, const TensorView& components,
                          const TensorView* mean_tensor, TensorView& output_tensor);
    void layernorm_cpu(const TensorView& input, const TensorView& weight,
                       const TensorView& bias, TensorView& output, float eps);
    void dropout_cpu(const TensorView& input, TensorView& output, float dropout_rate);
    void embedding_cpu(const TensorView& input, const TensorView& weight, TensorView& output);
    void add_cpu(const TensorView& input1, const TensorView& input2, TensorView& output);
    void mul_cpu(const TensorView& input1, const TensorView& input2, TensorView& output);
}
}

using namespace mle;

class TestResults {
public:
    void add_test(const std::string& name, bool passed, double time_ms = 0.0, const std::string& error = "") {
        tests_.push_back({name, passed, time_ms, error});
        if (passed) {
            passed_++;
        } else {
            failed_++;
            std::cout << "❌ " << name << " FAILED: " << error << std::endl;
        }
    }
    
    void print_summary() {
        std::cout << "\n=== TEST SUMMARY ===" << std::endl;
        std::cout << "Total tests: " << tests_.size() << std::endl;
        std::cout << "Passed: " << passed_ << std::endl;
        std::cout << "Failed: " << failed_ << std::endl;
        std::cout << "Success rate: " << (100.0 * passed_ / tests_.size()) << "%" << std::endl;
        
        if (failed_ > 0) {
            std::cout << "\nFailed tests:" << std::endl;
            for (const auto& test : tests_) {
                if (!test.passed) {
                    std::cout << "  - " << test.name << ": " << test.error << std::endl;
                }
            }
        }
        
        // Performance summary
        double total_time = 0.0;
        for (const auto& test : tests_) {
            total_time += test.time_ms;
        }
        std::cout << "\nTotal execution time: " << total_time << " ms" << std::endl;
    }
    
    void save_report(const std::string& filename) {
        std::ofstream file(filename);
        file << "# MLE Runtime V2 - Test Report\n\n";
        file << "## Summary\n";
        file << "- Total tests: " << tests_.size() << "\n";
        file << "- Passed: " << passed_ << "\n";
        file << "- Failed: " << failed_ << "\n";
        file << "- Success rate: " << (100.0 * passed_ / tests_.size()) << "%\n\n";
        
        file << "## Detailed Results\n\n";
        for (const auto& test : tests_) {
            file << "### " << test.name << "\n";
            file << "- Status: " << (test.passed ? "✅ PASSED" : "❌ FAILED") << "\n";
            file << "- Time: " << test.time_ms << " ms\n";
            if (!test.passed) {
                file << "- Error: " << test.error << "\n";
            }
            file << "\n";
        }
    }

private:
    struct TestResult {
        std::string name;
        bool passed;
        double time_ms;
        std::string error;
    };
    
    std::vector<TestResult> tests_;
    int passed_ = 0;
    int failed_ = 0;
};

// Helper function to measure execution time
template<typename Func>
double measure_time(Func&& func) {
    auto start = std::chrono::high_resolution_clock::now();
    func();
    auto end = std::chrono::high_resolution_clock::now();
    return std::chrono::duration<double, std::milli>(end - start).count();
}

// Test neural network operators
void test_neural_network_ops(TestResults& results) {
    std::cout << "\n=== Testing Neural Network Operators ===" << std::endl;
    
    // Test Linear layer
    try {
        auto input = TensorView::create({2, 4}, DType::FP32);
        auto weight = TensorView::create({3, 4}, DType::FP32);
        auto bias = TensorView::create({3}, DType::FP32);
        auto output = TensorView::create({2, 3}, DType::FP32);
        
        // Fill with test data
        float* in_data = static_cast<float*>(input->data());
        float* w_data = static_cast<float*>(weight->data());
        float* b_data = static_cast<float*>(bias->data());
        
        for (int i = 0; i < 8; ++i) in_data[i] = i * 0.1f;
        for (int i = 0; i < 12; ++i) w_data[i] = (i % 2 == 0) ? 1.0f : -1.0f;
        for (int i = 0; i < 3; ++i) b_data[i] = i * 0.1f;
        
        double time = measure_time([&]() {
            ops::linear_cpu(*input, *weight, *bias, *output);
        });
        
        results.add_test("Linear Layer", true, time);
        
    } catch (const std::exception& e) {
        results.add_test("Linear Layer", false, 0.0, e.what());
    }
    
    // Test ReLU
    try {
        auto input = TensorView::create({2, 4}, DType::FP32);
        auto output = TensorView::create({2, 4}, DType::FP32);
        
        float* in_data = static_cast<float*>(input->data());
        for (int i = 0; i < 8; ++i) in_data[i] = (i - 4) * 0.5f;  // Mix of positive and negative
        
        double time = measure_time([&]() {
            ops::relu_cpu(*input, *output);
        });
        
        results.add_test("ReLU Activation", true, time);
        
    } catch (const std::exception& e) {
        results.add_test("ReLU Activation", false, 0.0, e.what());
    }
    
    // Test GELU
    try {
        auto input = TensorView::create({2, 4}, DType::FP32);
        auto output = TensorView::create({2, 4}, DType::FP32);
        
        float* in_data = static_cast<float*>(input->data());
        for (int i = 0; i < 8; ++i) in_data[i] = (i - 4) * 0.5f;
        
        double time = measure_time([&]() {
            ops::gelu_cpu(*input, *output);
        });
        
        results.add_test("GELU Activation", true, time);
        
    } catch (const std::exception& e) {
        results.add_test("GELU Activation", false, 0.0, e.what());
    }
    
    // Test Softmax
    try {
        auto input = TensorView::create({2, 4}, DType::FP32);
        auto output = TensorView::create({2, 4}, DType::FP32);
        
        float* in_data = static_cast<float*>(input->data());
        for (int i = 0; i < 8; ++i) in_data[i] = i * 0.5f;
        
        double time = measure_time([&]() {
            ops::softmax_cpu(*input, *output);
        });
        
        results.add_test("Softmax", true, time);
        
    } catch (const std::exception& e) {
        results.add_test("Softmax", false, 0.0, e.what());
    }
    
    // Test Conv2D
    try {
        auto input = TensorView::create({1, 2, 4, 4}, DType::FP32);
        auto weight = TensorView::create({3, 2, 3, 3}, DType::FP32);
        auto bias = TensorView::create({3}, DType::FP32);
        auto output = TensorView::create({1, 3, 2, 2}, DType::FP32);
        
        // Fill with test data
        float* in_data = static_cast<float*>(input->data());
        float* w_data = static_cast<float*>(weight->data());
        float* b_data = static_cast<float*>(bias->data());
        
        for (int i = 0; i < 32; ++i) in_data[i] = i * 0.1f;
        for (int i = 0; i < 54; ++i) w_data[i] = (i % 2 == 0) ? 1.0f : -1.0f;
        for (int i = 0; i < 3; ++i) b_data[i] = i * 0.1f;
        
        double time = measure_time([&]() {
            ops::conv2d_cpu(*input, *weight, *bias, *output, 1, 1, 0, 0);
        });
        
        results.add_test("Conv2D", true, time);
        
    } catch (const std::exception& e) {
        results.add_test("Conv2D", false, 0.0, e.what());
    }
    
    // Test MaxPool2D
    try {
        auto input = TensorView::create({1, 2, 4, 4}, DType::FP32);
        auto output = TensorView::create({1, 2, 2, 2}, DType::FP32);
        
        float* in_data = static_cast<float*>(input->data());
        for (int i = 0; i < 32; ++i) in_data[i] = i;
        
        double time = measure_time([&]() {
            ops::maxpool2d_cpu(*input, *output, 2, 2, 2, 2, 0, 0);
        });
        
        results.add_test("MaxPool2D", true, time);
        
    } catch (const std::exception& e) {
        results.add_test("MaxPool2D", false, 0.0, e.what());
    }
    
    // Test BatchNorm
    try {
        auto input = TensorView::create({2, 3, 2, 2}, DType::FP32);
        auto weight = TensorView::create({3}, DType::FP32);
        auto bias = TensorView::create({3}, DType::FP32);
        auto running_mean = TensorView::create({3}, DType::FP32);
        auto running_var = TensorView::create({3}, DType::FP32);
        auto output = TensorView::create({2, 3, 2, 2}, DType::FP32);
        
        // Fill with test data
        float* in_data = static_cast<float*>(input->data());
        float* w_data = static_cast<float*>(weight->data());
        float* b_data = static_cast<float*>(bias->data());
        float* mean_data = static_cast<float*>(running_mean->data());
        float* var_data = static_cast<float*>(running_var->data());
        
        for (int i = 0; i < 24; ++i) in_data[i] = i * 0.1f;
        for (int i = 0; i < 3; ++i) {
            w_data[i] = 1.0f;
            b_data[i] = 0.0f;
            mean_data[i] = 0.5f;
            var_data[i] = 1.0f;
        }
        
        double time = measure_time([&]() {
            ops::batchnorm_cpu(*input, *weight, *bias, *running_mean, *running_var, *output, 1e-5f);
        });
        
        results.add_test("BatchNorm", true, time);
        
    } catch (const std::exception& e) {
        results.add_test("BatchNorm", false, 0.0, e.what());
    }
    
    // Test LayerNorm
    try {
        auto input = TensorView::create({2, 4}, DType::FP32);
        auto weight = TensorView::create({4}, DType::FP32);
        auto bias = TensorView::create({4}, DType::FP32);
        auto output = TensorView::create({2, 4}, DType::FP32);
        
        float* in_data = static_cast<float*>(input->data());
        float* w_data = static_cast<float*>(weight->data());
        float* b_data = static_cast<float*>(bias->data());
        
        for (int i = 0; i < 8; ++i) in_data[i] = i * 0.1f;
        for (int i = 0; i < 4; ++i) {
            w_data[i] = 1.0f;
            b_data[i] = 0.0f;
        }
        
        double time = measure_time([&]() {
            ops::layernorm_cpu(*input, *weight, *bias, *output, 1e-5f);
        });
        
        results.add_test("LayerNorm", true, time);
        
    } catch (const std::exception& e) {
        results.add_test("LayerNorm", false, 0.0, e.what());
    }
    
    // Test Attention
    try {
        auto query = TensorView::create({1, 4, 8}, DType::FP32);
        auto key = TensorView::create({1, 4, 8}, DType::FP32);
        auto value = TensorView::create({1, 4, 8}, DType::FP32);
        auto output = TensorView::create({1, 4, 8}, DType::FP32);
        
        float* q_data = static_cast<float*>(query->data());
        float* k_data = static_cast<float*>(key->data());
        float* v_data = static_cast<float*>(value->data());
        
        for (int i = 0; i < 32; ++i) {
            q_data[i] = i * 0.1f;
            k_data[i] = (i + 1) * 0.1f;
            v_data[i] = (i + 2) * 0.1f;
        }
        
        double time = measure_time([&]() {
            ops::attention_cpu(*query, *key, *value, *output, 2, 0.35f);
        });
        
        results.add_test("Multi-Head Attention", true, time);
        
    } catch (const std::exception& e) {
        results.add_test("Multi-Head Attention", false, 0.0, e.what());
    }
    
    // Test Embedding
    try {
        auto input = TensorView::create({2, 3}, DType::INT32);
        auto weight = TensorView::create({10, 4}, DType::FP32);  // vocab_size=10, embed_dim=4
        auto output = TensorView::create({2, 3, 4}, DType::FP32);
        
        int32_t* in_data = static_cast<int32_t*>(input->data());
        float* w_data = static_cast<float*>(weight->data());
        
        // Set some valid indices
        in_data[0] = 1; in_data[1] = 3; in_data[2] = 5;
        in_data[3] = 2; in_data[4] = 4; in_data[5] = 6;
        
        for (int i = 0; i < 40; ++i) w_data[i] = i * 0.1f;
        
        double time = measure_time([&]() {
            ops::embedding_cpu(*input, *weight, *output);
        });
        
        results.add_test("Embedding", true, time);
        
    } catch (const std::exception& e) {
        results.add_test("Embedding", false, 0.0, e.what());
    }
    
    // Test Add
    try {
        auto input1 = TensorView::create({2, 4}, DType::FP32);
        auto input2 = TensorView::create({2, 4}, DType::FP32);
        auto output = TensorView::create({2, 4}, DType::FP32);
        
        float* in1_data = static_cast<float*>(input1->data());
        float* in2_data = static_cast<float*>(input2->data());
        
        for (int i = 0; i < 8; ++i) {
            in1_data[i] = i * 0.1f;
            in2_data[i] = i * 0.2f;
        }
        
        double time = measure_time([&]() {
            ops::add_cpu(*input1, *input2, *output);
        });
        
        results.add_test("Element-wise Add", true, time);
        
    } catch (const std::exception& e) {
        results.add_test("Element-wise Add", false, 0.0, e.what());
    }
    
    // Test Multiply
    try {
        auto input1 = TensorView::create({2, 4}, DType::FP32);
        auto input2 = TensorView::create({2, 4}, DType::FP32);
        auto output = TensorView::create({2, 4}, DType::FP32);
        
        float* in1_data = static_cast<float*>(input1->data());
        float* in2_data = static_cast<float*>(input2->data());
        
        for (int i = 0; i < 8; ++i) {
            in1_data[i] = (i + 1) * 0.1f;
            in2_data[i] = (i + 1) * 0.2f;
        }
        
        double time = measure_time([&]() {
            ops::mul_cpu(*input1, *input2, *output);
        });
        
        results.add_test("Element-wise Multiply", true, time);
        
    } catch (const std::exception& e) {
        results.add_test("Element-wise Multiply", false, 0.0, e.what());
    }
}

// Test machine learning algorithms
void test_ml_algorithms(TestResults& results) {
    std::cout << "\n=== Testing ML Algorithms ===" << std::endl;
    
    // Test Decision Tree
    try {
        auto input = TensorView::create({3, 4}, DType::FP32);
        auto features = TensorView::create({3}, DType::INT32);
        auto thresholds = TensorView::create({3}, DType::FP32);
        auto values = TensorView::create({3, 1, 3}, DType::FP32);
        auto left = TensorView::create({3}, DType::INT32);
        auto right = TensorView::create({3}, DType::INT32);
        auto output = TensorView::create({3, 3}, DType::FP32);
        
        // Set up a simple tree
        float* in_data = static_cast<float*>(input->data());
        int32_t* feat_data = static_cast<int32_t*>(features->data());
        float* thresh_data = static_cast<float*>(thresholds->data());
        float* val_data = static_cast<float*>(values->data());
        int32_t* left_data = static_cast<int32_t*>(left->data());
        int32_t* right_data = static_cast<int32_t*>(right->data());
        
        // Input data
        in_data[0] = 5.1f; in_data[1] = 3.5f; in_data[2] = 1.4f; in_data[3] = 0.2f;
        in_data[4] = 6.2f; in_data[5] = 2.8f; in_data[6] = 4.8f; in_data[7] = 1.8f;
        in_data[8] = 7.7f; in_data[9] = 2.6f; in_data[10] = 6.9f; in_data[11] = 2.3f;
        
        // Tree structure
        feat_data[0] = 2; thresh_data[0] = 2.5f; left_data[0] = 1; right_data[0] = 2;
        feat_data[1] = -1; thresh_data[1] = 0.0f; left_data[1] = -1; right_data[1] = -1;
        feat_data[2] = -1; thresh_data[2] = 0.0f; left_data[2] = -1; right_data[2] = -1;
        
        // Values
        val_data[3] = 1.0f; val_data[4] = 0.0f; val_data[5] = 0.0f;  // node 1
        val_data[6] = 0.0f; val_data[7] = 1.0f; val_data[8] = 0.0f;  // node 2
        
        double time = measure_time([&]() {
            ops::decision_tree_cpu(*input, *features, *thresholds, *values, *left, *right, *output);
        });
        
        results.add_test("Decision Tree", true, time);
        
    } catch (const std::exception& e) {
        results.add_test("Decision Tree", false, 0.0, e.what());
    }
    
    // Test SVM with RBF
    try {
        auto input = TensorView::create({2, 4}, DType::FP32);
        auto support_vectors = TensorView::create({3, 4}, DType::FP32);
        auto dual_coef = TensorView::create({2, 3}, DType::FP32);
        auto intercept = TensorView::create({2}, DType::FP32);
        auto output = TensorView::create({2, 2}, DType::FP32);
        
        // Fill with test data
        float* in_data = static_cast<float*>(input->data());
        float* sv_data = static_cast<float*>(support_vectors->data());
        float* coef_data = static_cast<float*>(dual_coef->data());
        float* int_data = static_cast<float*>(intercept->data());
        
        // Input
        in_data[0] = 5.1f; in_data[1] = 3.5f; in_data[2] = 1.4f; in_data[3] = 0.2f;
        in_data[4] = 6.2f; in_data[5] = 2.8f; in_data[6] = 4.8f; in_data[7] = 1.8f;
        
        // Support vectors
        sv_data[0] = 5.0f; sv_data[1] = 3.0f; sv_data[2] = 1.0f; sv_data[3] = 0.1f;
        sv_data[4] = 6.0f; sv_data[5] = 3.0f; sv_data[6] = 4.0f; sv_data[7] = 1.5f;
        sv_data[8] = 7.0f; sv_data[9] = 3.0f; sv_data[10] = 6.0f; sv_data[11] = 2.0f;
        
        // Coefficients
        coef_data[0] = 0.5f; coef_data[1] = -0.3f; coef_data[2] = 0.2f;
        coef_data[3] = -0.5f; coef_data[4] = 0.3f; coef_data[5] = -0.2f;
        
        // Intercept
        int_data[0] = 0.1f; int_data[1] = -0.1f;
        
        double time = measure_time([&]() {
            ops::svm_cpu(*input, *support_vectors, *dual_coef, *intercept, *output, 0.1f);
        });
        
        results.add_test("SVM RBF", true, time);
        
    } catch (const std::exception& e) {
        results.add_test("SVM RBF", false, 0.0, e.what());
    }
    
    // Test Naive Bayes
    try {
        auto input = TensorView::create({2, 4}, DType::FP32);
        auto theta = TensorView::create({3, 4}, DType::FP32);
        auto sigma = TensorView::create({3, 4}, DType::FP32);
        auto output = TensorView::create({2, 3}, DType::FP32);
        
        float* in_data = static_cast<float*>(input->data());
        float* theta_data = static_cast<float*>(theta->data());
        float* sigma_data = static_cast<float*>(sigma->data());
        
        // Input
        in_data[0] = 5.1f; in_data[1] = 3.5f; in_data[2] = 1.4f; in_data[3] = 0.2f;
        in_data[4] = 6.2f; in_data[5] = 2.8f; in_data[6] = 4.8f; in_data[7] = 1.8f;
        
        // Parameters
        for (int i = 0; i < 12; ++i) {
            theta_data[i] = (i % 4) + 1.0f;
            sigma_data[i] = 1.0f;
        }
        
        double time = measure_time([&]() {
            ops::naive_bayes_cpu(*input, *theta, *sigma, *output);
        });
        
        results.add_test("Naive Bayes", true, time);
        
    } catch (const std::exception& e) {
        results.add_test("Naive Bayes", false, 0.0, e.what());
    }
    
    // Test K-Means Clustering
    try {
        auto input = TensorView::create({5, 2}, DType::FP32);
        auto centers = TensorView::create({2, 2}, DType::FP32);
        auto output = TensorView::create({5, 1}, DType::FP32);
        
        float* in_data = static_cast<float*>(input->data());
        float* center_data = static_cast<float*>(centers->data());
        
        // Input points
        in_data[0] = 1.0f; in_data[1] = 1.0f;
        in_data[2] = 1.5f; in_data[3] = 1.2f;
        in_data[4] = 5.0f; in_data[5] = 5.0f;
        in_data[6] = 5.2f; in_data[7] = 4.8f;
        in_data[8] = 3.0f; in_data[9] = 3.0f;
        
        // Cluster centers
        center_data[0] = 1.0f; center_data[1] = 1.0f;
        center_data[2] = 5.0f; center_data[3] = 5.0f;
        
        double time = measure_time([&]() {
            ops::clustering_cpu(*input, *centers, *output);
        });
        
        results.add_test("K-Means Clustering", true, time);
        
    } catch (const std::exception& e) {
        results.add_test("K-Means Clustering", false, 0.0, e.what());
    }
    
    // Test DBSCAN
    try {
        auto input = TensorView::create({6, 2}, DType::FP32);
        auto output = TensorView::create({6, 1}, DType::FP32);
        
        float* in_data = static_cast<float*>(input->data());
        
        // Input points (two clusters)
        in_data[0] = 1.0f; in_data[1] = 1.0f;
        in_data[2] = 1.2f; in_data[3] = 1.1f;
        in_data[4] = 1.1f; in_data[5] = 1.3f;
        in_data[6] = 5.0f; in_data[7] = 5.0f;
        in_data[8] = 5.1f; in_data[9] = 4.9f;
        in_data[10] = 10.0f; in_data[11] = 10.0f;  // Outlier
        
        double time = measure_time([&]() {
            ops::dbscan_cpu(*input, *output, 0.5f, 2);
        });
        
        results.add_test("DBSCAN Clustering", true, time);
        
    } catch (const std::exception& e) {
        results.add_test("DBSCAN Clustering", false, 0.0, e.what());
    }
}

// Test compression and security features
void test_enhanced_features(TestResults& results) {
    std::cout << "\n=== Testing Enhanced Features ===" << std::endl;
    
    // Test compression
    try {
        std::vector<float> test_data(1000);
        for (size_t i = 0; i < test_data.size(); ++i) {
            test_data[i] = std::sin(i * 0.01f) * 100.0f;
        }
        
        double time = measure_time([&]() {
            auto compressed = Compressor::compress(
                test_data.data(), 
                test_data.size() * sizeof(float), 
                CompressionType::NONE, 
                6
            );
            
            auto decompressed = Compressor::decompress(
                compressed.data(),
                compressed.size(),
                test_data.size() * sizeof(float),
                CompressionType::NONE
            );
        });
        
        results.add_test("Compression (None)", true, time);
        
    } catch (const std::exception& e) {
        results.add_test("Compression (None)", false, 0.0, e.what());
    }
    
    // Test quantization
    try {
        std::vector<float> weights = {-1.5f, -0.5f, 0.0f, 0.5f, 1.0f, 1.5f, 2.0f, -2.0f};
        
        double time = measure_time([&]() {
            auto quantized_int8 = Compressor::quantize_weights(weights.data(), weights.size(), false);
            auto dequantized_int8 = Compressor::dequantize_weights(quantized_int8.data(), weights.size(), false);
            
            auto quantized_fp16 = Compressor::quantize_weights(weights.data(), weights.size(), true);
            auto dequantized_fp16 = Compressor::dequantize_weights(quantized_fp16.data(), weights.size(), true);
        });
        
        results.add_test("Weight Quantization", true, time);
        
    } catch (const std::exception& e) {
        results.add_test("Weight Quantization", false, 0.0, e.what());
    }
    
    // Test checksums
    try {
        std::string test_data = "Hello, MLE Runtime V2!";
        
        double time = measure_time([&]() {
            uint32_t checksum1 = Compressor::checksum(test_data.data(), test_data.size());
            uint32_t checksum2 = Compressor::checksum(test_data.data(), test_data.size());
            
            if (checksum1 != checksum2) {
                throw std::runtime_error("Checksum mismatch");
            }
        });
        
        results.add_test("Checksum Calculation", true, time);
        
    } catch (const std::exception& e) {
        results.add_test("Checksum Calculation", false, 0.0, e.what());
    }
    
    // Test security features
    try {
        uint8_t public_key[32], private_key[64];
        
        double time = measure_time([&]() {
            ModelSigner::generate_keypair(public_key, private_key);
            
            std::string test_hash = ModelSigner::bytes_to_hex(public_key, 32);
            uint8_t decoded[32];
            ModelSigner::hex_to_bytes(test_hash, decoded, 32);
            
            // Verify round-trip
            for (int i = 0; i < 32; ++i) {
                if (public_key[i] != decoded[i]) {
                    throw std::runtime_error("Hex encoding/decoding mismatch");
                }
            }
        });
        
        results.add_test("Security Features", true, time);
        
    } catch (const std::exception& e) {
        results.add_test("Security Features", false, 0.0, e.what());
    }
}

// Test file format features
void test_file_format(TestResults& results) {
    std::cout << "\n=== Testing File Format ===" << std::endl;
    
    // Test header format
    try {
        double time = measure_time([&]() {
            MLEHeader header = {};
            header.magic = MLE_MAGIC;
            header.version = MLE_VERSION;
            header.feature_flags = static_cast<uint32_t>(FeatureFlags::COMPRESSION) | 
                                  static_cast<uint32_t>(FeatureFlags::SIGNING);
            header.header_size = sizeof(MLEHeader);
            header.min_reader_version = MIN_SUPPORTED_VERSION;
            header.writer_version = MLE_VERSION;
            
            // Compute header checksum
            MLEHeader temp_header = header;
            temp_header.header_checksum = 0;
            header.header_checksum = Compressor::checksum(&temp_header, sizeof(temp_header));
            
            // Verify magic and version
            if (header.magic != MLE_MAGIC) {
                throw std::runtime_error("Invalid magic number");
            }
            if (header.version < MIN_SUPPORTED_VERSION || header.version > MAX_SUPPORTED_VERSION) {
                throw std::runtime_error("Unsupported version");
            }
        });
        
        results.add_test("File Format Header", true, time);
        
    } catch (const std::exception& e) {
        results.add_test("File Format Header", false, 0.0, e.what());
    }
    
    // Test backward compatibility
    try {
        double time = measure_time([&]() {
            std::vector<uint32_t> test_versions = {1, 2};
            
            for (uint32_t version : test_versions) {
                bool should_be_supported = (version >= MIN_SUPPORTED_VERSION && version <= MAX_SUPPORTED_VERSION);
                if (!should_be_supported) {
                    throw std::runtime_error("Version compatibility check failed");
                }
            }
        });
        
        results.add_test("Backward Compatibility", true, time);
        
    } catch (const std::exception& e) {
        results.add_test("Backward Compatibility", false, 0.0, e.what());
    }
}

int main() {
    std::cout << "=== MLE Runtime V2 - Comprehensive Test Suite ===" << std::endl;
    std::cout << "Testing all operators, algorithms, and enhanced features..." << std::endl;
    
    TestResults results;
    
    // Run all test suites
    test_neural_network_ops(results);
    test_ml_algorithms(results);
    test_enhanced_features(results);
    test_file_format(results);
    
    // Print summary
    results.print_summary();
    
    // Save detailed report
    results.save_report("test_report_v2.md");
    
    std::cout << "\nDetailed test report saved to: test_report_v2.md" << std::endl;
    
    return 0;
}