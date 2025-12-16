cmake_minimum_required(VERSION 3.22)
project(mle_core VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

option(ENABLE_CUDA "Enable CUDA support" OFF)
option(BUILD_TESTS "Build tests" ON)
option(ENABLE_COMPRESSION "Enable compression support" ON)
option(ENABLE_CRYPTO "Enable cryptographic features" OFF)

# Core library
add_library(mle_core STATIC
    src/loader.cpp
    src/engine.cpp
    src/ops_cpu.cpp
    src/compression.cpp
    src/security_simple.cpp
)

target_include_directories(mle_core PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_compile_options(mle_core PRIVATE
    $<$<CXX_COMPILER_ID:MSVC>:/W4 /O2>
    $<$<NOT:$<CXX_COMPILER_ID:MSVC>>:-Wall -Wextra -O3 -march=native>
)

# Compression support
if(ENABLE_COMPRESSION)
    find_package(PkgConfig)
    
    # Try to find compression libraries
    find_library(ZLIB_LIBRARY z)
    if(ZLIB_LIBRARY)
        target_link_libraries(mle_core PRIVATE ${ZLIB_LIBRARY})
        target_compile_definitions(mle_core PRIVATE ENABLE_ZLIB)
    endif()
    
    # Optional: LZ4, ZSTD, Brotli
    find_library(LZ4_LIBRARY lz4)
    if(LZ4_LIBRARY)
        target_link_libraries(mle_core PRIVATE ${LZ4_LIBRARY})
        target_compile_definitions(mle_core PRIVATE ENABLE_LZ4)
    endif()
    
    find_library(ZSTD_LIBRARY zstd)
    if(ZSTD_LIBRARY)
        target_link_libraries(mle_core PRIVATE ${ZSTD_LIBRARY})
        target_compile_definitions(mle_core PRIVATE ENABLE_ZSTD)
    endif()
    
    find_library(BROTLI_ENC_LIBRARY brotlienc)
    find_library(BROTLI_DEC_LIBRARY brotlidec)
    if(BROTLI_ENC_LIBRARY AND BROTLI_DEC_LIBRARY)
        target_link_libraries(mle_core PRIVATE ${BROTLI_ENC_LIBRARY} ${BROTLI_DEC_LIBRARY})
        target_compile_definitions(mle_core PRIVATE ENABLE_BROTLI)
    endif()
endif()

# Cryptographic support
if(ENABLE_CRYPTO)
    find_package(OpenSSL REQUIRED)
    target_link_libraries(mle_core PRIVATE OpenSSL::SSL OpenSSL::Crypto)
    target_compile_definitions(mle_core PRIVATE ENABLE_CRYPTO)
    
    # Try to find ed25519 library
    find_library(ED25519_LIBRARY ed25519)
    if(ED25519_LIBRARY)
        target_link_libraries(mle_core PRIVATE ${ED25519_LIBRARY})
    endif()
endif()

# CUDA support
if(ENABLE_CUDA)
    enable_language(CUDA)
    find_package(CUDAToolkit REQUIRED)
    
    target_sources(mle_core PRIVATE
        src/ops_cuda.cu
        src/cuda_context.cpp
    )
    
    target_link_libraries(mle_core PUBLIC
        CUDA::cudart
        CUDA::cublas
    )
    
    target_compile_definitions(mle_core PUBLIC ENABLE_CUDA)
    
    set_target_properties(mle_core PROPERTIES
        CUDA_SEPARABLE_COMPILATION ON
        CUDA_ARCHITECTURES "75;80;86;89"
    )
endif()

# Tests
if(BUILD_TESTS)
    enable_testing()
    find_package(GTest)
    
    if(GTest_FOUND)
        add_executable(mle_tests
            tests/test_loader.cpp
            tests/test_ops.cpp
            tests/test_engine.cpp
        )
        
        target_link_libraries(mle_tests PRIVATE
            mle_core
            GTest::gtest
            GTest::gtest_main
        )
        
        add_test(NAME mle_tests COMMAND mle_tests)
    endif()
    
    # Standalone tests (no GTest dependency)
    add_executable(test_operators_v2
        tests/test_operators_v2.cpp
    )
    target_link_libraries(test_operators_v2 PRIVATE mle_core)
    add_test(NAME test_operators_v2 COMMAND test_operators_v2)
    
    add_executable(test_format_v2
        tests/test_format_v2.cpp
    )
    target_link_libraries(test_format_v2 PRIVATE mle_core)
    add_test(NAME test_format_v2 COMMAND test_format_v2)
endif()

# Install
install(TARGETS mle_core
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
)

install(DIRECTORY include/
    DESTINATION include/mle
)
    add_executable(test_comprehensive
        test_comprehensive.cpp
    )
    
    target_link_libraries(test_comprehensive PRIVATE
        mle_core
    )
    
    add_executable(test_all_operators
        tests/test_all_operators.cpp
    )
    
    target_link_libraries(test_all_operators PRIVATE
        mle_core
    )