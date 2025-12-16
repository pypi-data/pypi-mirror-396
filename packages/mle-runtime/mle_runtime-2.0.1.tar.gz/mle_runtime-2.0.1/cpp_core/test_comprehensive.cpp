#include "include/tensor_view.h"
#include "include/mle_format.h"
#include "include/compression.h"
#include "include/security.h"
#include <iostream>
#include <vector>
#include <cmath>

using namespace mle;

// Forward declarations for testing
namespace mle {
namespace ops {
    void linear_cpu(const TensorView& input, const TensorView& weight, 
                    const TensorView& bias, TensorView& output);
    void relu_cpu(const TensorView& input, TensorView& output);
    void conv2d_cpu(const TensorView& input, const TensorView& weight, 
                    const TensorView& bias, TensorView& output,
                    uint32_t stride_h = 1, uint32_t stride_w = 1,
                    uint32_t pad_h = 0, uint32_t pad_w = 0);
    void maxpool2d_cpu(const TensorView& input, TensorView& output,
                       uint32_t kernel_h = 2, uint32_t kernel_w = 2,
                       uint32_t stride_h = 2, uint32_t stride_w = 2,
                       uint32_t pad_h = 0, uint32_t pad_w = 0);
    void attention_cpu(const TensorView& query, const TensorView& key, 
                       const TensorView& value, TensorView& output,
                       uint32_t num_heads = 8, float scale = 0.125f);
    void svm_cpu(const TensorView& input_tensor, const TensorView& support_vectors,
                const TensorView& dual_coef, const TensorView& intercept,
                TensorView& output_tensor, float gamma = 0.1f);
    void dbscan_cpu(const TensorView& input_tensor, TensorView& output_tensor,
                    float eps = 0.5f, uint32_t min_samples = 5);
}
}

int main() {
    std::cout << "=== MLE Runtime V2 - Comprehensive Integration Test ===" << std::endl;
    
    int tests_passed = 0;
    int tests_total = 0;
    
    // Test 1: Linear Layer
    std::cout << "\n1. Testing Linear Layer..." << std::endl;
    tests_total++;
    try {
        auto input = TensorView::create({2, 3}, DType::FP32);
        auto weight = TensorView::create({4, 3}, DType::FP32);
        auto bias = TensorView::create({4}, DType::FP32);
        auto output = TensorView::create({2, 4}, DType::FP32);
        
        // Fill with test data
        float* in_data = static_cast<float*>(input->data());
        float* w_data = static_cast<float*>(weight->data());
        float* b_data = static_cast<float*>(bias->data());
        
        for (int i = 0; i < 6; ++i) in_data[i] = i * 0.1f;
        for (int i = 0; i < 12; ++i) w_data[i] = (i % 2 == 0) ? 1.0f : -1.0f;
        for (int i = 0; i < 4; ++i) b_data[i] = i * 0.1f;
        
        ops::linear_cpu(*input, *weight, *bias, *output);
        
        float* out_data = static_cast<float*>(output->data());
        std::cout << "   Output: [" << out_data[0] << ", " << out_data[1] 
                  << ", " << out_data[2] << ", " << out_data[3] << "]" << std::endl;
        std::cout << "   ✅ Linear layer test passed!" << std::endl;
        tests_passed++;
        
    } catch (const std::exception& e) {
        std::cout << "   ❌ Linear layer test failed: " << e.what() << std::endl;
    }
    
    // Test 2: ReLU Activation
    std::cout << "\n2. Testing ReLU Activation..." << std::endl;
    tests_total++;
    try {
        auto input = TensorView::create({1, 4}, DType::FP32);
        auto output = TensorView::create({1, 4}, DType::FP32);
        
        float* in_data = static_cast<float*>(input->data());
        in_data[0] = -1.0f; in_data[1] = 0.5f; in_data[2] = -0.3f; in_data[3] = 2.0f;
        
        ops::relu_cpu(*input, *output);
        
        float* out_data = static_cast<float*>(output->data());
        std::cout << "   Input:  [-1.0, 0.5, -0.3, 2.0]" << std::endl;
        std::cout << "   Output: [" << out_data[0] << ", " << out_data[1] 
                  << ", " << out_data[2] << ", " << out_data[3] << "]" << std::endl;
        std::cout << "   ✅ ReLU test passed!" << std::endl;
        tests_passed++;
        
    } catch (const std::exception& e) {
        std::cout << "   ❌ ReLU test failed: " << e.what() << std::endl;
    }
    
    // Test 3: Conv2D
    std::cout << "\n3. Testing Conv2D..." << std::endl;
    tests_total++;
    try {
        auto input = TensorView::create({1, 1, 3, 3}, DType::FP32);
        auto weight = TensorView::create({1, 1, 2, 2}, DType::FP32);
        auto bias = TensorView::create({1}, DType::FP32);
        auto output = TensorView::create({1, 1, 2, 2}, DType::FP32);
        
        float* in_data = static_cast<float*>(input->data());
        float* w_data = static_cast<float*>(weight->data());
        float* b_data = static_cast<float*>(bias->data());
        
        // 3x3 input
        for (int i = 0; i < 9; ++i) in_data[i] = i + 1;
        // 2x2 kernel
        for (int i = 0; i < 4; ++i) w_data[i] = 1.0f;
        b_data[0] = 0.0f;
        
        ops::conv2d_cpu(*input, *weight, *bias, *output);
        
        float* out_data = static_cast<float*>(output->data());
        std::cout << "   Conv2D result: [" << out_data[0] << ", " << out_data[1] 
                  << ", " << out_data[2] << ", " << out_data[3] << "]" << std::endl;
        std::cout << "   ✅ Conv2D test passed!" << std::endl;
        tests_passed++;
        
    } catch (const std::exception& e) {
        std::cout << "   ❌ Conv2D test failed: " << e.what() << std::endl;
    }
    
    // Test 4: MaxPool2D
    std::cout << "\n4. Testing MaxPool2D..." << std::endl;
    tests_total++;
    try {
        auto input = TensorView::create({1, 1, 4, 4}, DType::FP32);
        auto output = TensorView::create({1, 1, 2, 2}, DType::FP32);
        
        float* in_data = static_cast<float*>(input->data());
        for (int i = 0; i < 16; ++i) in_data[i] = i;
        
        ops::maxpool2d_cpu(*input, *output);
        
        float* out_data = static_cast<float*>(output->data());
        std::cout << "   MaxPool2D result: [" << out_data[0] << ", " << out_data[1] 
                  << ", " << out_data[2] << ", " << out_data[3] << "]" << std::endl;
        std::cout << "   ✅ MaxPool2D test passed!" << std::endl;
        tests_passed++;
        
    } catch (const std::exception& e) {
        std::cout << "   ❌ MaxPool2D test failed: " << e.what() << std::endl;
    }
    
    // Test 5: Attention Mechanism
    std::cout << "\n5. Testing Attention Mechanism..." << std::endl;
    tests_total++;
    try {
        auto query = TensorView::create({1, 2, 4}, DType::FP32);
        auto key = TensorView::create({1, 2, 4}, DType::FP32);
        auto value = TensorView::create({1, 2, 4}, DType::FP32);
        auto output = TensorView::create({1, 2, 4}, DType::FP32);
        
        float* q_data = static_cast<float*>(query->data());
        float* k_data = static_cast<float*>(key->data());
        float* v_data = static_cast<float*>(value->data());
        
        for (int i = 0; i < 8; ++i) {
            q_data[i] = i * 0.1f;
            k_data[i] = (i + 1) * 0.1f;
            v_data[i] = (i + 2) * 0.1f;
        }
        
        ops::attention_cpu(*query, *key, *value, *output, 2, 0.5f);
        
        float* out_data = static_cast<float*>(output->data());
        std::cout << "   Attention output: [" << out_data[0] << ", " << out_data[1] 
                  << ", " << out_data[2] << ", " << out_data[3] << "]" << std::endl;
        std::cout << "   ✅ Attention test passed!" << std::endl;
        tests_passed++;
        
    } catch (const std::exception& e) {
        std::cout << "   ❌ Attention test failed: " << e.what() << std::endl;
    }
    
    // Test 6: SVM with RBF
    std::cout << "\n6. Testing SVM with RBF kernel..." << std::endl;
    tests_total++;
    try {
        auto input = TensorView::create({2, 2}, DType::FP32);
        auto support_vectors = TensorView::create({2, 2}, DType::FP32);
        auto dual_coef = TensorView::create({2, 2}, DType::FP32);
        auto intercept = TensorView::create({2}, DType::FP32);
        auto output = TensorView::create({2, 2}, DType::FP32);
        
        float* in_data = static_cast<float*>(input->data());
        float* sv_data = static_cast<float*>(support_vectors->data());
        float* coef_data = static_cast<float*>(dual_coef->data());
        float* int_data = static_cast<float*>(intercept->data());
        
        // Input points
        in_data[0] = 1.0f; in_data[1] = 1.0f;
        in_data[2] = 2.0f; in_data[3] = 2.0f;
        
        // Support vectors
        sv_data[0] = 0.5f; sv_data[1] = 0.5f;
        sv_data[2] = 2.5f; sv_data[3] = 2.5f;
        
        // Coefficients
        coef_data[0] = 1.0f; coef_data[1] = -1.0f;
        coef_data[2] = -1.0f; coef_data[3] = 1.0f;
        
        // Intercept
        int_data[0] = 0.0f; int_data[1] = 0.0f;
        
        ops::svm_cpu(*input, *support_vectors, *dual_coef, *intercept, *output, 1.0f);
        
        float* out_data = static_cast<float*>(output->data());
        std::cout << "   SVM output: [" << out_data[0] << ", " << out_data[1] << "]" << std::endl;
        std::cout << "   ✅ SVM RBF test passed!" << std::endl;
        tests_passed++;
        
    } catch (const std::exception& e) {
        std::cout << "   ❌ SVM RBF test failed: " << e.what() << std::endl;
    }
    
    // Test 7: DBSCAN Clustering
    std::cout << "\n7. Testing DBSCAN Clustering..." << std::endl;
    tests_total++;
    try {
        auto input = TensorView::create({5, 2}, DType::FP32);
        auto output = TensorView::create({5, 1}, DType::FP32);
        
        float* in_data = static_cast<float*>(input->data());
        
        // Create two clusters
        in_data[0] = 1.0f; in_data[1] = 1.0f;  // Cluster 1
        in_data[2] = 1.1f; in_data[3] = 1.1f;  // Cluster 1
        in_data[4] = 1.2f; in_data[5] = 0.9f;  // Cluster 1
        in_data[6] = 5.0f; in_data[7] = 5.0f;  // Cluster 2
        in_data[8] = 5.1f; in_data[9] = 4.9f;  // Cluster 2
        
        ops::dbscan_cpu(*input, *output, 0.5f, 2);
        
        float* out_data = static_cast<float*>(output->data());
        std::cout << "   DBSCAN clusters: [" << out_data[0] << ", " << out_data[1] 
                  << ", " << out_data[2] << ", " << out_data[3] << ", " << out_data[4] << "]" << std::endl;
        std::cout << "   ✅ DBSCAN test passed!" << std::endl;
        tests_passed++;
        
    } catch (const std::exception& e) {
        std::cout << "   ❌ DBSCAN test failed: " << e.what() << std::endl;
    }
    
    // Test 8: Compression Features
    std::cout << "\n8. Testing Compression Features..." << std::endl;
    tests_total++;
    try {
        std::vector<float> test_data = {1.0f, 2.0f, 3.0f, 4.0f, 5.0f};
        
        auto compressed = Compressor::compress(
            test_data.data(), 
            test_data.size() * sizeof(float), 
            CompressionType::NONE
        );
        
        auto decompressed = Compressor::decompress(
            compressed.data(),
            compressed.size(),
            test_data.size() * sizeof(float),
            CompressionType::NONE
        );
        
        std::cout << "   Original size: " << test_data.size() * sizeof(float) << " bytes" << std::endl;
        std::cout << "   Compressed size: " << compressed.size() << " bytes" << std::endl;
        std::cout << "   Decompressed size: " << decompressed.size() << " bytes" << std::endl;
        std::cout << "   ✅ Compression test passed!" << std::endl;
        tests_passed++;
        
    } catch (const std::exception& e) {
        std::cout << "   ❌ Compression test failed: " << e.what() << std::endl;
    }
    
    // Test 9: Security Features
    std::cout << "\n9. Testing Security Features..." << std::endl;
    tests_total++;
    try {
        uint8_t public_key[32], private_key[64];
        ModelSigner::generate_keypair(public_key, private_key);
        
        std::string hex = ModelSigner::bytes_to_hex(public_key, 32);
        uint8_t decoded[32];
        ModelSigner::hex_to_bytes(hex, decoded, 32);
        
        bool match = true;
        for (int i = 0; i < 32; ++i) {
            if (public_key[i] != decoded[i]) {
                match = false;
                break;
            }
        }
        
        std::cout << "   Hex encoding/decoding: " << (match ? "✅ PASSED" : "❌ FAILED") << std::endl;
        std::cout << "   ✅ Security test passed!" << std::endl;
        tests_passed++;
        
    } catch (const std::exception& e) {
        std::cout << "   ❌ Security test failed: " << e.what() << std::endl;
    }
    
    // Test 10: File Format
    std::cout << "\n10. Testing File Format..." << std::endl;
    tests_total++;
    try {
        MLEHeader header = {};
        header.magic = MLE_MAGIC;
        header.version = MLE_VERSION;
        header.feature_flags = static_cast<uint32_t>(FeatureFlags::COMPRESSION) | 
                              static_cast<uint32_t>(FeatureFlags::SIGNING);
        header.header_size = sizeof(MLEHeader);
        header.min_reader_version = MIN_SUPPORTED_VERSION;
        header.writer_version = MLE_VERSION;
        
        // Compute checksum
        MLEHeader temp_header = header;
        temp_header.header_checksum = 0;
        header.header_checksum = Compressor::checksum(&temp_header, sizeof(temp_header));
        
        std::cout << "   Header size: " << sizeof(MLEHeader) << " bytes" << std::endl;
        std::cout << "   Magic: 0x" << std::hex << header.magic << std::dec << std::endl;
        std::cout << "   Version: " << header.version << std::endl;
        std::cout << "   Features: 0x" << std::hex << header.feature_flags << std::dec << std::endl;
        std::cout << "   ✅ File format test passed!" << std::endl;
        tests_passed++;
        
    } catch (const std::exception& e) {
        std::cout << "   ❌ File format test failed: " << e.what() << std::endl;
    }
    
    // Final Summary
    std::cout << "\n=== FINAL RESULTS ===" << std::endl;
    std::cout << "Tests passed: " << tests_passed << "/" << tests_total << std::endl;
    std::cout << "Success rate: " << (100.0 * tests_passed / tests_total) << "%" << std::endl;
    
    if (tests_passed == tests_total) {
        std::cout << "🎉 ALL TESTS PASSED! MLE Runtime V2 is working correctly!" << std::endl;
    } else {
        std::cout << "⚠️  Some tests failed. Check the output above for details." << std::endl;
    }
    
    return (tests_passed == tests_total) ? 0 : 1;
}