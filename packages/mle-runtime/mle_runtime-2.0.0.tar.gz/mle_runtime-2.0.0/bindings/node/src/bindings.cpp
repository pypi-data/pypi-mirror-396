#include <napi.h>
#include "engine.h"
#include <memory>

class EngineWrapper : public Napi::ObjectWrap<EngineWrapper> {
public:
    static Napi::Object Init(Napi::Env env, Napi::Object exports) {
        Napi::Function func = DefineClass(env, "Engine", {
            InstanceMethod("loadModel", &EngineWrapper::LoadModel),
            InstanceMethod("run", &EngineWrapper::Run),
            InstanceMethod("peakMemory", &EngineWrapper::PeakMemory),
        });
        
        Napi::FunctionReference* constructor = new Napi::FunctionReference();
        *constructor = Napi::Persistent(func);
        env.SetInstanceData(constructor);
        
        exports.Set("Engine", func);
        return exports;
    }
    
    EngineWrapper(const Napi::CallbackInfo& info) : Napi::ObjectWrap<EngineWrapper>(info) {
        Napi::Env env = info.Env();
        
        mle::Device device = mle::Device::CPU;
        if (info.Length() > 0 && info[0].IsString()) {
            std::string device_str = info[0].As<Napi::String>().Utf8Value();
            if (device_str == "cuda") {
                device = mle::Device::CUDA;
            }
        }
        
        engine_ = std::make_unique<mle::Engine>(device);
    }

private:
    Napi::Value LoadModel(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();
        
        if (info.Length() < 1 || !info[0].IsString()) {
            Napi::TypeError::New(env, "String expected").ThrowAsJavaScriptException();
            return env.Null();
        }
        
        std::string path = info[0].As<Napi::String>().Utf8Value();
        
        try {
            engine_->load_model(path);
        } catch (const std::exception& e) {
            Napi::Error::New(env, e.what()).ThrowAsJavaScriptException();
            return env.Null();
        }
        
        return env.Undefined();
    }
    
    Napi::Value Run(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();
        
        if (info.Length() < 1 || !info[0].IsArray()) {
            Napi::TypeError::New(env, "Array expected").ThrowAsJavaScriptException();
            return env.Null();
        }
        
        Napi::Array inputs_array = info[0].As<Napi::Array>();
        std::vector<std::shared_ptr<mle::TensorView>> inputs;
        
        // Convert Buffer inputs to TensorView
        for (uint32_t i = 0; i < inputs_array.Length(); ++i) {
            Napi::Value val = inputs_array[i];
            if (!val.IsBuffer()) {
                Napi::TypeError::New(env, "Buffer expected").ThrowAsJavaScriptException();
                return env.Null();
            }
            
            Napi::Buffer<float> buffer = val.As<Napi::Buffer<float>>();
            
            // Assume 2D: [1, size]
            std::vector<uint32_t> shape = {1, static_cast<uint32_t>(buffer.Length())};
            auto tensor = std::make_shared<mle::TensorView>(
                buffer.Data(), shape, mle::DType::FP32);
            inputs.push_back(tensor);
        }
        
        // Run inference
        std::vector<std::shared_ptr<mle::TensorView>> outputs;
        try {
            outputs = engine_->run(inputs);
        } catch (const std::exception& e) {
            Napi::Error::New(env, e.what()).ThrowAsJavaScriptException();
            return env.Null();
        }
        
        // Convert outputs to Buffers
        Napi::Array result = Napi::Array::New(env, outputs.size());
        for (size_t i = 0; i < outputs.size(); ++i) {
            auto& tensor = outputs[i];
            size_t size = tensor->size();
            
            Napi::Buffer<uint8_t> buffer = Napi::Buffer<uint8_t>::Copy(
                env, static_cast<uint8_t*>(tensor->data()), size);
            result[i] = buffer;
        }
        
        return result;
    }
    
    Napi::Value PeakMemory(const Napi::CallbackInfo& info) {
        Napi::Env env = info.Env();
        return Napi::Number::New(env, engine_->peak_memory_usage());
    }
    
    std::unique_ptr<mle::Engine> engine_;
};

Napi::Object Init(Napi::Env env, Napi::Object exports) {
    return EngineWrapper::Init(env, exports);
}

NODE_API_MODULE(mle_runtime, Init)
