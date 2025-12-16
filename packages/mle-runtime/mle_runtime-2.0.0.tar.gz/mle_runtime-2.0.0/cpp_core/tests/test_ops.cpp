#include <gtest/gtest.h>
#include "tensor_view.h"
#include <cmath>

using namespace mle;

namespace mle {
namespace ops {
    void linear_cpu(const TensorView& input, const TensorView& weight, 
                    const TensorView& bias, TensorView& output);
    void relu_cpu(const TensorView& input, TensorView& output);
    void gelu_cpu(const TensorView& input, TensorView& output);
}
}

TEST(OpsTest, ReLU) {
    std::vector<uint32_t> shape = {2, 3};
    auto input = TensorView::create(shape, DType::FP32);
    auto output = TensorView::create(shape, DType::FP32);
    
    float* in_data = static_cast<float*>(input->data());
    in_data[0] = -1.0f;
    in_data[1] = 0.0f;
    in_data[2] = 1.0f;
    in_data[3] = -2.0f;
    in_data[4] = 2.0f;
    in_data[5] = -0.5f;
    
    ops::relu_cpu(*input, *output);
    
    float* out_data = static_cast<float*>(output->data());
    EXPECT_FLOAT_EQ(out_data[0], 0.0f);
    EXPECT_FLOAT_EQ(out_data[1], 0.0f);
    EXPECT_FLOAT_EQ(out_data[2], 1.0f);
    EXPECT_FLOAT_EQ(out_data[3], 0.0f);
    EXPECT_FLOAT_EQ(out_data[4], 2.0f);
    EXPECT_FLOAT_EQ(out_data[5], 0.0f);
}

TEST(OpsTest, Linear) {
    // Input: [1, 2], Weight: [3, 2], Bias: [3]
    // Output: [1, 3]
    auto input = TensorView::create({1, 2}, DType::FP32);
    auto weight = TensorView::create({3, 2}, DType::FP32);
    auto bias = TensorView::create({3}, DType::FP32);
    auto output = TensorView::create({1, 3}, DType::FP32);
    
    float* in_data = static_cast<float*>(input->data());
    in_data[0] = 1.0f;
    in_data[1] = 2.0f;
    
    float* w_data = static_cast<float*>(weight->data());
    w_data[0] = 1.0f; w_data[1] = 0.0f;  // Row 0
    w_data[2] = 0.0f; w_data[3] = 1.0f;  // Row 1
    w_data[4] = 1.0f; w_data[5] = 1.0f;  // Row 2
    
    float* b_data = static_cast<float*>(bias->data());
    b_data[0] = 0.5f;
    b_data[1] = 0.5f;
    b_data[2] = 0.5f;
    
    ops::linear_cpu(*input, *weight, *bias, *output);
    
    float* out_data = static_cast<float*>(output->data());
    EXPECT_FLOAT_EQ(out_data[0], 1.5f);  // 1*1 + 2*0 + 0.5
    EXPECT_FLOAT_EQ(out_data[1], 2.5f);  // 1*0 + 2*1 + 0.5
    EXPECT_FLOAT_EQ(out_data[2], 3.5f);  // 1*1 + 2*1 + 0.5
}

TEST(OpsTest, GELU) {
    auto input = TensorView::create({3}, DType::FP32);
    auto output = TensorView::create({3}, DType::FP32);
    
    float* in_data = static_cast<float*>(input->data());
    in_data[0] = 0.0f;
    in_data[1] = 1.0f;
    in_data[2] = -1.0f;
    
    ops::gelu_cpu(*input, *output);
    
    float* out_data = static_cast<float*>(output->data());
    EXPECT_NEAR(out_data[0], 0.0f, 1e-5);
    EXPECT_NEAR(out_data[1], 0.8411f, 1e-3);  // GELU(1.0) ≈ 0.8411
    EXPECT_NEAR(out_data[2], -0.1588f, 1e-3); // GELU(-1.0) ≈ -0.1588
}
