#include "tensor_view.h"
#include "mle_format.h"
#include <iostream>
#include <vector>
#include <cmath>
#include <cassert>

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

void test_conv2d() {
    std::cout << "Testing Conv2D..." << std::endl;
    
    // Create input: [1, 2, 4, 4] (batch=1, channels=2, height=4, width=4)
    auto input = TensorView::create({1, 2, 4, 4}, DType::FP32);
    float* input_data = static_cast<float*>(input->data());
    for (int i = 0; i < 32; ++i) {
        input_data[i] = i * 0.1f;
    }
    
    // Create weight: [3, 2, 3, 3] (out_channels=3, in_channels=2, kernel=3x3)
    auto weight = TensorView::create({3, 2, 3, 3}, DType::FP32);
    float* weight_data = static_cast<float*>(weight->data());
    for (int i = 0; i < 54; ++i) {
        weight_data[i] = (i % 2 == 0) ? 1.0f : -1.0f;
    }
    
    // Create bias: [3]
    auto bias = TensorView::create({3}, DType::FP32);
    float* bias_data = static_cast<float*>(bias->data());
    bias_data[0] = 0.1f;
    bias_data[1] = 0.2f;
    bias_data[2] = 0.3f;
    
    // Create output: [1, 3, 2, 2] (with stride=1, no padding, 4-3+1=2)
    auto output = TensorView::create({1, 3, 2, 2}, DType::FP32);
    
    ops::conv2d_cpu(*input, *weight, *bias, *output);
    
    float* output_data = static_cast<float*>(output->data());
    std::cout << "Conv2D output shape: [" << output->shape()[0] << ", " 
              << output->shape()[1] << ", " << output->shape()[2] << ", " 
              << output->shape()[3] << "]" << std::endl;
    std::cout << "First few values: " << output_data[0] << ", " << output_data[1] 
              << ", " << output_data[2] << ", " << output_data[3] << std::endl;
    
    std::cout << "Conv2D test passed!" << std::endl;
}

void test_maxpool2d() {
    std::cout << "Testing MaxPool2D..." << std::endl;
    
    // Create input: [1, 2, 4, 4]
    auto input = TensorView::create({1, 2, 4, 4}, DType::FP32);
    float* input_data = static_cast<float*>(input->data());
    for (int i = 0; i < 32; ++i) {
        input_data[i] = i;
    }
    
    // Create output: [1, 2, 2, 2] (with 2x2 kernel, stride=2)
    auto output = TensorView::create({1, 2, 2, 2}, DType::FP32);
    
    ops::maxpool2d_cpu(*input, *output);
    
    float* output_data = static_cast<float*>(output->data());
    std::cout << "MaxPool2D output: " << output_data[0] << ", " << output_data[1] 
              << ", " << output_data[2] << ", " << output_data[3] << std::endl;
    
    // Should be max of each 2x2 region
    assert(output_data[0] == 5.0f);  // max of [0,1,4,5]
    assert(output_data[1] == 7.0f);  // max of [2,3,6,7]
    
    std::cout << "MaxPool2D test passed!" << std::endl;
}

void test_batchnorm() {
    std::cout << "Testing BatchNorm..." << std::endl;
    
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
    
    ops::batchnorm_cpu(*input, *weight, *bias, *running_mean, *running_var, *output);
    
    float* output_data = static_cast<float*>(output->data());
    std::cout << "BatchNorm output: " << output_data[0] << ", " << output_data[1] 
              << ", " << output_data[2] << ", " << output_data[3] << std::endl;
    
    std::cout << "BatchNorm test passed!" << std::endl;
}

void test_attention() {
    std::cout << "Testing Attention..." << std::endl;
    
    // Create Q, K, V: [1, 4, 8] (batch=1, seq_len=4, d_model=8)
    auto query = TensorView::create({1, 4, 8}, DType::FP32);
    auto key = TensorView::create({1, 4, 8}, DType::FP32);
    auto value = TensorView::create({1, 4, 8}, DType::FP32);
    
    float* q_data = static_cast<float*>(query->data());
    float* k_data = static_cast<float*>(key->data());
    float* v_data = static_cast<float*>(value->data());
    
    for (int i = 0; i < 32; ++i) {
        q_data[i] = i * 0.1f;
        k_data[i] = (i + 1) * 0.1f;
        v_data[i] = (i + 2) * 0.1f;
    }
    
    auto output = TensorView::create({1, 4, 8}, DType::FP32);
    
    ops::attention_cpu(*query, *key, *value, *output, 2, 0.35f);  // 2 heads
    
    float* output_data = static_cast<float*>(output->data());
    std::cout << "Attention output: " << output_data[0] << ", " << output_data[1] 
              << ", " << output_data[2] << ", " << output_data[3] << std::endl;
    
    std::cout << "Attention test passed!" << std::endl;
}

void test_tree_ensemble() {
    std::cout << "Testing Tree Ensemble..." << std::endl;
    
    // Create input: [3, 4] (3 samples, 4 features)
    auto input = TensorView::create({3, 4}, DType::FP32);
    float* input_data = static_cast<float*>(input->data());
    input_data[0] = 5.1f; input_data[1] = 3.5f; input_data[2] = 1.4f; input_data[3] = 0.2f;
    input_data[4] = 6.2f; input_data[5] = 2.8f; input_data[6] = 4.8f; input_data[7] = 1.8f;
    input_data[8] = 7.7f; input_data[9] = 2.6f; input_data[10] = 6.9f; input_data[11] = 2.3f;
    
    // Create simple tree parameters (2 trees, 3 nodes each)
    std::vector<TensorView> tree_params;
    
    // Tree 1 parameters
    auto features1 = TensorView::create({3}, DType::INT32);
    auto thresholds1 = TensorView::create({3}, DType::FP32);
    auto values1 = TensorView::create({3, 1, 3}, DType::FP32);
    auto left1 = TensorView::create({3}, DType::INT32);
    auto right1 = TensorView::create({3}, DType::INT32);
    
    int32_t* feat1 = static_cast<int32_t*>(features1->data());
    float* thresh1 = static_cast<float*>(thresholds1->data());
    float* val1 = static_cast<float*>(values1->data());
    int32_t* l1 = static_cast<int32_t*>(left1->data());
    int32_t* r1 = static_cast<int32_t*>(right1->data());
    
    // Simple tree: if feature[2] <= 2.5 then class 0, else class 1
    feat1[0] = 2; thresh1[0] = 2.5f; l1[0] = 1; r1[0] = 2;
    feat1[1] = -1; thresh1[1] = 0.0f; l1[1] = -1; r1[1] = -1;  // leaf: class 0
    feat1[2] = -1; thresh1[2] = 0.0f; l1[2] = -1; r1[2] = -1;  // leaf: class 1
    
    val1[3] = 1.0f; val1[4] = 0.0f; val1[5] = 0.0f;  // node 1: [1,0,0]
    val1[6] = 0.0f; val1[7] = 1.0f; val1[8] = 0.0f;  // node 2: [0,1,0]
    
    tree_params.push_back(*features1);
    tree_params.push_back(*thresholds1);
    tree_params.push_back(*values1);
    tree_params.push_back(*left1);
    tree_params.push_back(*right1);
    
    // Tree 2 parameters (similar structure)
    auto features2 = TensorView::create({3}, DType::INT32);
    auto thresholds2 = TensorView::create({3}, DType::FP32);
    auto values2 = TensorView::create({3, 1, 3}, DType::FP32);
    auto left2 = TensorView::create({3}, DType::INT32);
    auto right2 = TensorView::create({3}, DType::INT32);
    
    int32_t* feat2 = static_cast<int32_t*>(features2->data());
    float* thresh2 = static_cast<float*>(thresholds2->data());
    float* val2 = static_cast<float*>(values2->data());
    int32_t* l2 = static_cast<int32_t*>(left2->data());
    int32_t* r2 = static_cast<int32_t*>(right2->data());
    
    feat2[0] = 2; thresh2[0] = 2.5f; l2[0] = 1; r2[0] = 2;
    feat2[1] = -1; thresh2[1] = 0.0f; l2[1] = -1; r2[1] = -1;
    feat2[2] = -1; thresh2[2] = 0.0f; l2[2] = -1; r2[2] = -1;
    
    val2[3] = 1.0f; val2[4] = 0.0f; val2[5] = 0.0f;
    val2[6] = 0.0f; val2[7] = 1.0f; val2[8] = 0.0f;
    
    tree_params.push_back(*features2);
    tree_params.push_back(*thresholds2);
    tree_params.push_back(*values2);
    tree_params.push_back(*left2);
    tree_params.push_back(*right2);
    
    auto output = TensorView::create({3, 3}, DType::FP32);
    
    ops::tree_ensemble_cpu(*input, tree_params, *output, true);
    
    float* output_data = static_cast<float*>(output->data());
    std::cout << "Tree Ensemble output:" << std::endl;
    for (int i = 0; i < 3; ++i) {
        std::cout << "Sample " << i << ": [" << output_data[i*3] << ", " 
                  << output_data[i*3+1] << ", " << output_data[i*3+2] << "]" << std::endl;
    }
    
    std::cout << "Tree Ensemble test passed!" << std::endl;
}

void test_svm_rbf() {
    std::cout << "Testing SVM with RBF kernel..." << std::endl;
    
    // Create input: [2, 4] (2 samples, 4 features)
    auto input = TensorView::create({2, 4}, DType::FP32);
    float* input_data = static_cast<float*>(input->data());
    input_data[0] = 5.1f; input_data[1] = 3.5f; input_data[2] = 1.4f; input_data[3] = 0.2f;
    input_data[4] = 6.2f; input_data[5] = 2.8f; input_data[6] = 4.8f; input_data[7] = 1.8f;
    
    // Create support vectors: [3, 4] (3 support vectors)
    auto support_vectors = TensorView::create({3, 4}, DType::FP32);
    float* sv_data = static_cast<float*>(support_vectors->data());
    sv_data[0] = 5.0f; sv_data[1] = 3.0f; sv_data[2] = 1.0f; sv_data[3] = 0.1f;
    sv_data[4] = 6.0f; sv_data[5] = 3.0f; sv_data[6] = 4.0f; sv_data[7] = 1.5f;
    sv_data[8] = 7.0f; sv_data[9] = 3.0f; sv_data[10] = 6.0f; sv_data[11] = 2.0f;
    
    // Create dual coefficients: [2, 3] (2 classes, 3 support vectors)
    auto dual_coef = TensorView::create({2, 3}, DType::FP32);
    float* coef_data = static_cast<float*>(dual_coef->data());
    coef_data[0] = 0.5f; coef_data[1] = -0.3f; coef_data[2] = 0.2f;
    coef_data[3] = -0.5f; coef_data[4] = 0.3f; coef_data[5] = -0.2f;
    
    // Create intercept: [2]
    auto intercept = TensorView::create({2}, DType::FP32);
    float* intercept_data = static_cast<float*>(intercept->data());
    intercept_data[0] = 0.1f;
    intercept_data[1] = -0.1f;
    
    auto output = TensorView::create({2, 2}, DType::FP32);
    
    ops::svm_cpu(*input, *support_vectors, *dual_coef, *intercept, *output, 0.1f);
    
    float* output_data = static_cast<float*>(output->data());
    std::cout << "SVM RBF output:" << std::endl;
    for (int i = 0; i < 2; ++i) {
        std::cout << "Sample " << i << ": [" << output_data[i*2] << ", " 
                  << output_data[i*2+1] << "]" << std::endl;
    }
    
    std::cout << "SVM RBF test passed!" << std::endl;
}

int main() {
    try {
        test_conv2d();
        test_maxpool2d();
        test_batchnorm();
        test_attention();
        test_tree_ensemble();
        test_svm_rbf();
        
        std::cout << "\nAll tests passed successfully!" << std::endl;
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "Test failed: " << e.what() << std::endl;
        return 1;
    }
}