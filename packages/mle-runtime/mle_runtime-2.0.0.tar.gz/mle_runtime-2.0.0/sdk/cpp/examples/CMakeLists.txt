cmake_minimum_required(VERSION 3.15)

# Simple inference example
add_executable(simple_inference simple_inference.cpp)
target_link_libraries(simple_inference PRIVATE mle_core)

# Install examples
install(TARGETS simple_inference DESTINATION bin)
