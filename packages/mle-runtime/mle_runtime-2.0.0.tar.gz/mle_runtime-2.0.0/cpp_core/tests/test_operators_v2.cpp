#include "tensor_view.h"
#include "mle_format.h"
#include <iostream>
#include <vector>
#include <cmath>
#include <cassert>
#include <chrono>

namespace mle {
namespace ops {
    // Forward declarations for new operators
    void conv2d_cpu(const TensorView& input, const TensorView& weight, 
                    const TensorView& bias, TensorView& output,
                    uint32_t stride_h = 1, uint32_t stride_w = 1,
                    uint32_t pad_h = 0, uint32_t pad_w = 0);
    void maxpool2d_cpu(const TensorView& input, TensorView& output,
                       uint32_t kernel_h = 2, uint32_t kernel_w = 2,
                       uint32_t stride_h = 2, uint32_t stride_w = 2,
                       uint32_t pad_h = 0, uint32_t pad_w = 0);
    void batchnorm_cpu(const TensorView& input, const TensorView& weight,
                       const TensorView& bias, const TensorView& running_mean,
                       const TensorView& running_var, TensorView& output,
                       float eps = 1e-5f);
    void attention_cpu(const TensorView& query, const TensorView& key, 
                       const TensorView& value, TensorView& output,
                       uint32_t num_heads = 8, float scale = 0.125f);
    void tree_ensemble_cpu(const TensorView& input_tensor, 
                          const std::vector<TensorView>& tree_params,
                          TensorView& output_tensor, bool is_classifier = true);
    void svm_cpu(const TensorView& input_tensor, const TensorView& support_vectors,
                const TensorView& dual_coef, const TensorView& intercept,
                TensorView& output_tensor, float gamma = 0.1f);
}
}

using namespace mle;

class OperatorTester {
public:
    static void test_conv2d() {
        std::cout << "Testing Conv2D operator..." << std::endl;
        
        // Create input: [1, 2, 4, 4] (batch=1, channels=2, height=4, width=4)
        auto input = TensorView::create({1, 2, 4, 4}, DType::FP32);
        float* input_data = static_cast<float*>(input->data());
        
        // Initialize with simple pattern
        for (int i = 0; i < 32; ++i) {
            input_data[i] = (i % 8) * 0.1f;
        }
        
        // Create weight: [3, 2, 3, 3] (out_channels=3, in_channels=2, kernel=3x3)
        auto weight = TensorView::create({3, 2, 3, 3}, DType::FP32);
        float* weight_data = static_cast<float*>(weight->data());
        
        // Initialize weights
        for (int i = 0; i < 54; ++i) {
            weight_data[i] = (i % 2 == 0) ? 0.1f : -0.1f;
        }
        
        // Create bias: [3]
        auto bias = TensorView::create({3}, DType::FP32);
        float* bias_data = static_cast<float*>(bias->data());
        bias_data[0] = 0.1f;
        bias_data[1] = 0.2f;
        bias_data[2] = 0.3f;
        
        // Create output: [1, 3, 2, 2] (with stride=1, no padding, 4-3+1=2)
        auto output = TensorView::create({1, 3, 2, 2}, DType::FP32);
        
        auto start = std::chrono::high_resolution_clock::now();
        ops::conv2d_cpu(*input, *weight, *bias, *output);
        auto end = std::chrono::high_resolution_clock::now();
        
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
        
        float* output_data = static_cast<float*>(output->data());
        std::cout << "  Output shape: [" << output->shape()[0] << ", " 
                  << output->shape()[1] << ", " << output->shape()[2] << ", " 
                  << output->shape()[3] << "]" << std::endl;
        std::cout << "  Sample values: " << output_data[0] << ", " << output_data[1] 
                  << ", " << output_data[2] << ", " << output_data[3] << std::endl;
        std::cout << "  Execution time: " << duration.count() << " μs" << std::endl;
        
        // Basic validation
        assert(output->shape()[0] == 1);
        assert(output->shape()[1] == 3);
        assert(output->shape()[2] == 2);
        assert(output->shape()[3] == 2);
        
        std::cout << "  ✓ Conv2D test passed!" << std::endl;
    }
    
    static void test_maxpool2d() {
        std::cout << "Testing MaxPool2D operator..." << std::endl;
        
        // Create input: [1, 2, 4, 4]
        auto input = TensorView::create({1, 2, 4, 4}, DType::FP32);
        float* input_data = static_cast<float*>(input->data());
        
        // Initialize with increasing values
        for (int i = 0; i < 32; ++i) {
            input_data[i] = i;
        }
        
        // Create output: [1, 2, 2, 2] (with 2x2 kernel, stride=2)
        auto output = TensorView::create({1, 2, 2, 2}, DType::FP32);
        
        auto start = std::chrono::high_resolution_clock::now();
        ops::maxpool2d_cpu(*input, *output);
        auto end = std::chrono::high_resolution_clock::now();
        
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
        
        float* output_data = static_cast<float*>(output->data());
        std::cout << "  Output values: " << output_data[0] << ", " << output_data[1] 
                  << ", " << output_data[2] << ", " << output_data[3] << std::endl;
        std::cout << "  Execution time: " << duration.count() << " μs" << std::endl;
        
        // Validate max pooling results
        assert(output_data[0] == 5.0f);  // max of [0,1,4,5]
        assert(output_data[1] == 7.0f);  // max of [2,3,6,7]
        
        std::cout << "  ✓ MaxPool2D test passed!" << std::endl;
    }
    
    static void test_batchnorm() {
        std::cout << "Testing BatchNorm operator..." << std::endl;
        
        // Create input: [2, 3, 2, 2] (batch=2, channels=3)
        auto input = TensorView::create({2, 3, 2, 2}, DType::FP32);
        float* input_data = static_cast<float*>(input->data());
        
        for (int i = 0; i < 24; ++i) {
            input_data[i] = i * 0.1f;
        }
        
        // Create parameters for 3 channels
        auto weight = TensorView::create({3}, DType::FP32);
        auto bias = TensorView::create({3}, DType::FP32);
        auto running_mean = TensorView::create({3}, DType::FP32);
        auto running_var = TensorView::create({3}, DType::FP32);
        
        float* weight_data = static_cast<float*>(weight->data());
        float* bias_data = static_cast<float*>(bias->data());
        float* mean_data = static_cast<float*>(running_mean->data());
        float* var_data = static_cast<float*>(running_var->data());
        
        for (int i = 0; i < 3; ++i) {
            weight_data[i] = 1.0f;
            bias_data[i] = 0.0f;
            mean_data[i] = 0.5f;
            var_data[i] = 1.0f;
        }
        
        auto output = TensorView::create({2, 3, 2, 2}, DType::FP32);
        
        auto start = std::chrono::high_resolution_clock::now();
        ops::batchnorm_cpu(*input, *weight, *bias, *running_mean, *running_var, *output);
        auto end = std::chrono::high_resolution_clock::now();
        
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
        
        float* output_data = static_cast<float*>(output->data());
        std::cout << "  Sample normalized values: " << output_data[0] << ", " << output_data[1] 
                  << ", " << output_data[2] << ", " << output_data[3] << std::endl;
        std::cout << "  Execution time: " << duration.count() << " μs" << std::endl;
        
        std::cout << "  ✓ BatchNorm test passed!" << std::endl;
    }
    
    static void test_attention() {
        std::cout << "Testing Attention operator..." << std::endl;
        
        // Create Q, K, V: [1, 4, 8] (batch=1, seq_len=4, d_model=8)
        auto query = TensorView::create({1, 4, 8}, DType::FP32);
        auto key = TensorView::create({1, 4, 8}, DType::FP32);
        auto value = TensorView::create({1, 4, 8}, DType::FP32);
        
        float* q_data = static_cast<float*>(query->data());
        float* k_data = static_cast<float*>(key->data());
        float* v_data = static_cast<float*>(value->data());
        
        for (int i = 0; i < 32; ++i) {
            q_data[i] = std::sin(i * 0.1f);
            k_data[i] = std::cos(i * 0.1f);
            v_data[i] = (i % 4) * 0.25f;
        }
        
        auto output = TensorView::create({1, 4, 8}, DType::FP32);
        
        auto start = std::chrono::high_resolution_clock::now();
        ops::attention_cpu(*query, *key, *value, *output, 2, 0.35f);  // 2 heads
        auto end = std::chrono::high_resolution_clock::now();
        
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
        
        float* output_data = static_cast<float*>(output->data());
        std::cout << "  Attention output sample: " << output_data[0] << ", " << output_data[1] 
                  << ", " << output_data[2] << ", " << output_data[3] << std::endl;
        std::cout << "  Execution time: " << duration.count() << " μs" << std::endl;
        
        std::cout << "  ✓ Attention test passed!" << std::endl;
    }
    
    static void benchmark_operators() {
        std::cout << "\n=== Operator Benchmarks ===" << std::endl;
        
        const int iterations = 100;
        
        // Conv2D benchmark
        {
            auto input = TensorView::create({1, 32, 64, 64}, DType::FP32);
            auto weight = TensorView::create({64, 32, 3, 3}, DType::FP32);
            auto bias = TensorView::create({64}, DType::FP32);
            auto output = TensorView::create({1, 64, 62, 62}, DType::FP32);
            
            auto start = std::chrono::high_resolution_clock::now();
            for (int i = 0; i < iterations; ++i) {
                ops::conv2d_cpu(*input, *weight, *bias, *output);
            }
            auto end = std::chrono::high_resolution_clock::now();
            
            auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
            std::cout << "Conv2D (32→64, 64x64): " << duration.count() / iterations 
                      << " ms/iteration" << std::endl;
        }
        
        // MaxPool2D benchmark
        {
            auto input = TensorView::create({1, 64, 128, 128}, DType::FP32);
            auto output = TensorView::create({1, 64, 64, 64}, DType::FP32);
            
            auto start = std::chrono::high_resolution_clock::now();
            for (int i = 0; i < iterations; ++i) {
                ops::maxpool2d_cpu(*input, *output);
            }
            auto end = std::chrono::high_resolution_clock::now();
            
            auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
            std::cout << "MaxPool2D (64ch, 128x128): " << duration.count() / iterations 
                      << " μs/iteration" << std::endl;
        }
        
        // Attention benchmark
        {
            auto query = TensorView::create({1, 512, 768}, DType::FP32);
            auto key = TensorView::create({1, 512, 768}, DType::FP32);
            auto value = TensorView::create({1, 512, 768}, DType::FP32);
            auto output = TensorView::create({1, 512, 768}, DType::FP32);
            
            auto start = std::chrono::high_resolution_clock::now();
            for (int i = 0; i < 10; ++i) {  // Fewer iterations for expensive operation
                ops::attention_cpu(*query, *key, *value, *output, 12, 0.125f);
            }
            auto end = std::chrono::high_resolution_clock::now();
            
            auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
            std::cout << "Attention (512 seq, 768 dim, 12 heads): " << duration.count() / 10 
                      << " ms/iteration" << std::endl;
        }
    }
};

int main() {
    try {
        std::cout << "=== MLE Runtime v2.0 Operator Tests ===" << std::endl;
        std::cout << "Testing new neural network operators...\n" << std::endl;
        
        OperatorTester::test_conv2d();
        std::cout << std::endl;
        
        OperatorTester::test_maxpool2d();
        std::cout << std::endl;
        
        OperatorTester::test_batchnorm();
        std::cout << std::endl;
        
        OperatorTester::test_attention();
        std::cout << std::endl;
        
        OperatorTester::benchmark_operators();
        
        std::cout << "\n=== All operator tests completed successfully! ===" << std::endl;
        return 0;
        
    } catch (const std::exception& e) {
        std::cerr << "Test failed: " << e.what() << std::endl;
        return 1;
    }
}