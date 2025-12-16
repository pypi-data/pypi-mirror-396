#include <gtest/gtest.h>
#include "loader.h"
#include "mle_format.h"
#include <fstream>

using namespace mle;

class LoaderTest : public ::testing::Test {
protected:
    void SetUp() override {
        // Create a minimal valid .mle file for testing
        test_file_ = "test_model.mle";
        create_test_mle();
    }
    
    void TearDown() override {
        std::remove(test_file_.c_str());
    }
    
    void create_test_mle() {
        std::ofstream f(test_file_, std::ios::binary);
        
        // Header
        MLEHeader header = {};
        header.magic = MLE_MAGIC;
        header.version = MLE_VERSION;
        header.metadata_offset = 64;
        header.metadata_size = 2;
        header.graph_offset = 66;
        header.graph_size = sizeof(GraphIR);
        header.weights_offset = 66 + sizeof(GraphIR);
        header.weights_size = 0;
        header.signature_offset = 0;
        
        f.write(reinterpret_cast<const char*>(&header), sizeof(header));
        
        // Metadata
        f.write("{}", 2);
        
        // Graph IR
        GraphIR graph = {};
        graph.num_nodes = 0;
        graph.num_tensors = 0;
        graph.num_inputs = 0;
        graph.num_outputs = 0;
        
        f.write(reinterpret_cast<const char*>(&graph), sizeof(graph));
        
        f.close();
    }
    
    std::string test_file_;
};

TEST_F(LoaderTest, LoadValidFile) {
    EXPECT_NO_THROW({
        ModelLoader loader(test_file_);
        EXPECT_EQ(loader.header().magic, MLE_MAGIC);
        EXPECT_EQ(loader.header().version, MLE_VERSION);
    });
}

TEST_F(LoaderTest, InvalidFile) {
    EXPECT_THROW({
        ModelLoader loader("nonexistent.mle");
    }, std::runtime_error);
}

TEST_F(LoaderTest, GetMetadata) {
    ModelLoader loader(test_file_);
    std::string metadata = loader.get_metadata();
    EXPECT_EQ(metadata, "{}");
}
