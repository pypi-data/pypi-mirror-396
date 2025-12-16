#include "tensor_view.h"
#include "mle_format.h"
#include <cuda_runtime.h>
#include <cublas_v2.h>
#include <stdexcept>

namespace mle {
namespace ops {

// CUDA error checking
#define CUDA_CHECK(call) \
    do { \
        cudaError_t err = call; \
        if (err != cudaSuccess) { \
            throw std::runtime_error(std::string("CUDA error: ") + cudaGetErrorString(err)); \
        } \
    } while(0)

#define CUBLAS_CHECK(call) \
    do { \
        cublasStatus_t status = call; \
        if (status != CUBLAS_STATUS_SUCCESS) { \
            throw std::runtime_error("cuBLAS error"); \
        } \
    } while(0)

// ReLU kernel
__global__ void relu_kernel(const float* input, float* output, size_t n) {
    size_t idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        output[idx] = fmaxf(0.0f, input[idx]);
    }
}

// GELU kernel
__global__ void gelu_kernel(const float* input, float* output, size_t n) {
    size_t idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        float x = input[idx];
        float x3 = x * x * x;
        float inner = 0.7978845608f * (x + 0.044715f * x3);
        output[idx] = 0.5f * x * (1.0f + tanhf(inner));
    }
}

// Fused MatMul + Bias + ReLU kernel
__global__ void fused_linear_relu_kernel(
    const float* input, const float* weight, const float* bias,
    float* output, int M, int N, int K) {
    
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;
    
    if (row < M && col < N) {
        float sum = 0.0f;
        for (int k = 0; k < K; ++k) {
            sum += input[row * K + k] * weight[col * K + k];
        }
        sum += bias[col];
        output[row * N + col] = fmaxf(0.0f, sum);
    }
}

// Device memory manager
class CUDAContext {
public:
    static CUDAContext& instance() {
        static CUDAContext ctx;
        return ctx;
    }
    
    cublasHandle_t cublas_handle() { return cublas_handle_; }
    
    void* allocate(size_t size) {
        void* ptr;
        CUDA_CHECK(cudaMalloc(&ptr, size));
        allocated_ptrs_.push_back(ptr);
        return ptr;
    }
    
    void free(void* ptr) {
        CUDA_CHECK(cudaFree(ptr));
    }
    
    ~CUDAContext() {
        for (auto ptr : allocated_ptrs_) {
            cudaFree(ptr);
        }
        if (cublas_handle_) {
            cublasDestroy(cublas_handle_);
        }
    }

private:
    CUDAContext() {
        CUBLAS_CHECK(cublasCreate(&cublas_handle_));
    }
    
    cublasHandle_t cublas_handle_ = nullptr;
    std::vector<void*> allocated_ptrs_;
};

// CUDA operations
void relu_cuda(const TensorView& input, TensorView& output, cudaStream_t stream = 0) {
    size_t n = input.numel();
    int block_size = 256;
    int grid_size = (n + block_size - 1) / block_size;
    
    relu_kernel<<<grid_size, block_size, 0, stream>>>(
        static_cast<const float*>(input.data()),
        static_cast<float*>(output.data()),
        n
    );
    
    CUDA_CHECK(cudaGetLastError());
}

void gelu_cuda(const TensorView& input, TensorView& output, cudaStream_t stream = 0) {
    size_t n = input.numel();
    int block_size = 256;
    int grid_size = (n + block_size - 1) / block_size;
    
    gelu_kernel<<<grid_size, block_size, 0, stream>>>(
        static_cast<const float*>(input.data()),
        static_cast<float*>(output.data()),
        n
    );
    
    CUDA_CHECK(cudaGetLastError());
}

void linear_cuda(const TensorView& input, const TensorView& weight,
                 const TensorView& bias, TensorView& output) {
    // Use cuBLAS for matmul
    const auto& in_shape = input.shape();
    const auto& w_shape = weight.shape();
    
    int M = in_shape[0];      // batch
    int K = in_shape[1];      // in_features
    int N = w_shape[0];       // out_features
    
    auto& ctx = CUDAContext::instance();
    
    // cuBLAS: C = alpha * A * B + beta * C
    // We want: output = input @ weight^T + bias
    // cuBLAS uses column-major, so we compute: output^T = weight @ input^T
    
    const float alpha = 1.0f;
    const float beta = 0.0f;
    
    // Matmul: output = input @ weight^T
    CUBLAS_CHECK(cublasSgemm(
        ctx.cublas_handle(),
        CUBLAS_OP_T,  // weight is transposed
        CUBLAS_OP_N,  // input is not transposed
        N, M, K,      // dimensions
        &alpha,
        static_cast<const float*>(weight.data()), K,
        static_cast<const float*>(input.data()), K,
        &beta,
        static_cast<float*>(output.data()), N
    ));
    
    // Add bias (broadcast)
    // Simple kernel for now - can be fused
    int block_size = 256;
    int grid_size = (M * N + block_size - 1) / block_size;
    
    auto add_bias = [=] __device__ (int idx) {
        if (idx < M * N) {
            float* out = static_cast<float*>(output.data());
            const float* b = static_cast<const float*>(bias.data());
            out[idx] += b[idx % N];
        }
    };
    
    // Note: This is pseudocode - actual kernel launch needed
    // For production, use a proper bias add kernel
}

// Fused linear + ReLU for better performance
void fused_linear_relu_cuda(const TensorView& input, const TensorView& weight,
                            const TensorView& bias, TensorView& output) {
    const auto& in_shape = input.shape();
    const auto& w_shape = weight.shape();
    
    int M = in_shape[0];
    int K = in_shape[1];
    int N = w_shape[0];
    
    dim3 block(16, 16);
    dim3 grid((N + 15) / 16, (M + 15) / 16);
    
    fused_linear_relu_kernel<<<grid, block>>>(
        static_cast<const float*>(input.data()),
        static_cast<const float*>(weight.data()),
        static_cast<const float*>(bias.data()),
        static_cast<float*>(output.data()),
        M, N, K
    );
    
    CUDA_CHECK(cudaGetLastError());
}

} // namespace ops
} // namespace mle
