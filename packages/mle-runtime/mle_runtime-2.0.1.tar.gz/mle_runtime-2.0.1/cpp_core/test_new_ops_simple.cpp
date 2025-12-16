#include "include/tensor_view.h"
#include "include/mle_format.h"
#include <iostream>
#include <vector>
#include <cmath>

using namespace mle;

// Forward declarations
namespace mle {
namespace ops {
    void conv2d_cpu(const TensorView& input, const TensorView& weight, 
                    const TensorView& bias, TensorView& output,
                    uint32_t stride_h = 1, uint32_t stride_w = 1,
                    uint32_t pad_h = 0, uint32_t pad_w = 0);
    void maxpool2d_cpu(const TensorView& input, TensorView& output,
                       uint32_t kernel_h = 2, uint32_t kernel_w = 2,
                       uint32_t stride_h = 2, uint32_t stride_w = 2,
                       uint32_t pad_h = 0, uint32_t pad_w = 0);
}
}

int main() {
    try {
        std::cout << "Testing new operators..." << std::endl;
        
        // Test Conv2D
        std::cout << "Testing Conv2D..." << std::endl;
        auto input = TensorView::create({1, 1, 3, 3}, DType::FP32);
        auto weight = TensorView::create({1, 1, 2, 2}, DType::FP32);
        auto bias = TensorView::create({1}, DType::FP32);
        auto output = TensorView::create({1, 1, 2, 2}, DType::FP32);
        
        // Fill with simple values
        float* input_data = static_cast<float*>(input->data());
        for (int i = 0; i < 9; ++i) input_data[i] = i + 1;
        
        float* weight_data = static_cast<float*>(weight->data());
        for (int i = 0; i < 4; ++i) weight_data[i] = 1.0f;
        
        float* bias_data = static_cast<float*>(bias->data());
        bias_data[0] = 0.0f;
        
        ops::conv2d_cpu(*input, *weight, *bias, *output);
        
        float* output_data = static_cast<float*>(output->data());
        std::cout << "Conv2D result: " << output_data[0] << ", " << output_data[1] 
                  << ", " << output_data[2] << ", " << output_data[3] << std::endl;
        
        // Test MaxPool2D
        std::cout << "Testing MaxPool2D..." << std::endl;
        auto pool_input = TensorView::create({1, 1, 4, 4}, DType::FP32);
        auto pool_output = TensorView::create({1, 1, 2, 2}, DType::FP32);
        
        float* pool_input_data = static_cast<float*>(pool_input->data());
        for (int i = 0; i < 16; ++i) pool_input_data[i] = i;
        
        ops::maxpool2d_cpu(*pool_input, *pool_output);
        
        float* pool_output_data = static_cast<float*>(pool_output->data());
        std::cout << "MaxPool2D result: " << pool_output_data[0] << ", " << pool_output_data[1] 
                  << ", " << pool_output_data[2] << ", " << pool_output_data[3] << std::endl;
        
        std::cout << "All tests completed successfully!" << std::endl;
        return 0;
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
}