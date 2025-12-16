#include <gtest/gtest.h>
#include "engine.h"

using namespace mle;

TEST(EngineTest, CreateEngine) {
    EXPECT_NO_THROW({
        Engine engine(Device::CPU);
    });
}

#ifdef ENABLE_CUDA
TEST(EngineTest, CreateCUDAEngine) {
    EXPECT_NO_THROW({
        Engine engine(Device::CUDA);
    });
}
#endif

// Integration test with actual .mle file would go here
// Requires running the Python exporter first
