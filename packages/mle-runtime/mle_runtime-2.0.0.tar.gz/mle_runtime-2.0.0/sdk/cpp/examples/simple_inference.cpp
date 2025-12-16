/**
 * Simple inference example using MLE C++ SDK
 */

#include "mle_client.h"
#include <iostream>
#include <vector>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <model.mle>" << std::endl;
        return 1;
    }
    
    try {
        // Create engine
        mle::MLEEngine engine(mle::Device::CPU);
        
        // Load model
        std::cout << "Loading model: " << argv[1] << std::endl;
        engine.load_model(argv[1]);
        
        // Print metadata
        const auto* metadata = engine.metadata();
        if (metadata) {
            std::cout << "Model: " << metadata->model_name << std::endl;
            std::cout << "Framework: " << metadata->framework << std::endl;
        }
        
        // Create input tensor (example: 1x20 features)
        auto input = std::make_shared<mle::Tensor>(
            std::vector<uint32_t>{1, 20},
            mle::DType::FP32
        );
        
        // Fill with sample data
        float* data = static_cast<float*>(input->data());
        for (int i = 0; i < 20; i++) {
            data[i] = static_cast<float>(i) * 0.1f;
        }
        
        // Run inference
        std::cout << "Running inference..." << std::endl;
        auto outputs = engine.run({input});
        
        // Print results
        std::cout << "Output tensor shape: [";
        for (size_t i = 0; i < outputs[0]->shape().size(); i++) {
            std::cout << outputs[0]->shape()[i];
            if (i < outputs[0]->shape().size() - 1) std::cout << ", ";
        }
        std::cout << "]" << std::endl;
        
        float* output_data = static_cast<float*>(outputs[0]->data());
        std::cout << "First output value: " << output_data[0] << std::endl;
        
        std::cout << "Peak memory usage: " 
                  << engine.peak_memory_usage() / 1024.0 
                  << " KB" << std::endl;
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
    
    return 0;
}
