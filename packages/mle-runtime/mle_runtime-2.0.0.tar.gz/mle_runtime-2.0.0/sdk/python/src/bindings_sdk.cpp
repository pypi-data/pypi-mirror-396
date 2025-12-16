#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include "engine.h"
#include "executor.h"
#include <cstddef>

namespace py = pybind11;

// MSVC doesn't have ssize_t in global namespace
#ifdef _MSC_VER
using ssize_t = py::ssize_t;
#endif

namespace mle {

// Convert numpy array to TensorView (zero-copy if possible)
std::shared_ptr<TensorView> numpy_to_tensor(py::array arr) {
    py::buffer_info buf = arr.request();
    
    std::vector<uint32_t> shape;
    for (auto dim : buf.shape) {
        shape.push_back(static_cast<uint32_t>(dim));
    }
    
    DType dtype;
    if (buf.format == py::format_descriptor<float>::format()) {
        dtype = DType::FP32;
    } else if (buf.format == py::format_descriptor<int32_t>::format()) {
        dtype = DType::INT32;
    } else {
        throw std::runtime_error("Unsupported dtype");
    }
    
    // Create view (no copy)
    return std::make_shared<TensorView>(buf.ptr, shape, dtype);
}

// Convert TensorView to numpy array (with copy for now - TODO: zero-copy with capsule)
py::array tensor_to_numpy(std::shared_ptr<TensorView> tensor) {
    std::vector<ssize_t> shape;
    for (auto dim : tensor->shape()) {
        shape.push_back(dim);
    }
    
    py::dtype dt;
    if (tensor->dtype() == DType::FP32) {
        dt = py::dtype::of<float>();
    } else if (tensor->dtype() == DType::INT32) {
        dt = py::dtype::of<int32_t>();
    } else {
        throw std::runtime_error("Unsupported dtype");
    }
    
    // Create numpy array and copy data
    py::array result(dt, shape);
    std::memcpy(result.mutable_data(), tensor->data(), tensor->size());
    
    return result;
}

} // namespace mle

PYBIND11_MODULE(_mle_core, m) {
    m.doc() = "MLE Runtime Python Bindings";
    
    py::enum_<mle::Device>(m, "Device")
        .value("CPU", mle::Device::CPU)
        .value("CUDA", mle::Device::CUDA);
    
    py::enum_<mle::DType>(m, "DType")
        .value("FP32", mle::DType::FP32)
        .value("FP16", mle::DType::FP16)
        .value("INT8", mle::DType::INT8)
        .value("INT32", mle::DType::INT32);
    
    py::class_<mle::Engine>(m, "Engine")
        .def(py::init<mle::Device>(), py::arg("device") = mle::Device::CPU)
        .def("load_model", &mle::Engine::load_model)
        .def("run", [](mle::Engine& self, py::list inputs) {
            std::vector<std::shared_ptr<mle::TensorView>> input_tensors;
            for (auto item : inputs) {
                py::array arr = item.cast<py::array>();
                input_tensors.push_back(mle::numpy_to_tensor(arr));
            }
            
            auto outputs = self.run(input_tensors);
            
            py::list result;
            for (auto& tensor : outputs) {
                result.append(mle::tensor_to_numpy(tensor));
            }
            return result;
        })
        .def("peak_memory_usage", &mle::Engine::peak_memory_usage);
    
    py::class_<mle::GraphExecutor>(m, "GraphExecutor")
        .def(py::init<mle::Device>(), py::arg("device") = mle::Device::CPU)
        .def("load_model", &mle::GraphExecutor::load_model)
        .def("execute", [](mle::GraphExecutor& self, py::list inputs) {
            std::vector<std::shared_ptr<mle::TensorView>> input_tensors;
            for (auto item : inputs) {
                py::array arr = item.cast<py::array>();
                input_tensors.push_back(mle::numpy_to_tensor(arr));
            }
            
            auto outputs = self.execute(input_tensors);
            
            py::list result;
            for (auto& tensor : outputs) {
                result.append(mle::tensor_to_numpy(tensor));
            }
            return result;
        })
        .def("peak_memory", &mle::GraphExecutor::peak_memory);
    
    py::class_<mle::ModelLoader>(m, "ModelLoader")
        .def(py::init<const std::string&>())
        .def("get_metadata", &mle::ModelLoader::get_metadata);
}
