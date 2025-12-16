cmake_minimum_required(VERSION 3.15)
project(mle_cpp_sdk VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Options
option(BUILD_EXAMPLES "Build example programs" ON)
option(BUILD_TESTS "Build tests" OFF)

# Include directories
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/../../cpp_core/include
)

# Link to core library
link_directories(${CMAKE_CURRENT_SOURCE_DIR}/../../cpp_core/build)

# Header-only library target
add_library(mle_client INTERFACE)
target_include_directories(mle_client INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

# Examples
if(BUILD_EXAMPLES)
    add_subdirectory(examples)
endif()

# Install
install(DIRECTORY include/ DESTINATION include)
install(TARGETS mle_client EXPORT MLETargets)
