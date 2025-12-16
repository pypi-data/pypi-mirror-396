{
  "targets": [
    {
      "target_name": "mle_runtime",
      "sources": [
        "src/bindings.cpp",
        "../../cpp_core/src/loader.cpp",
        "../../cpp_core/src/engine.cpp",
        "../../cpp_core/src/ops_cpu.cpp",
        "../../cpp_core/src/executor.cpp"
      ],
      "include_dirs": [
        "<!@(node -p \"require('node-addon-api').include\")",
        "../../cpp_core/include"
      ],
      "dependencies": [
        "<!(node -p \"require('node-addon-api').gyp\")"
      ],
      "cflags!": [ "-fno-exceptions" ],
      "cflags_cc!": [ "-fno-exceptions" ],
      "cflags_cc": [ "-std=c++20", "-O3" ],
      "defines": [ "NAPI_DISABLE_CPP_EXCEPTIONS" ],
      "conditions": [
        ["OS=='win'", {
          "msvs_settings": {
            "VCCLCompilerTool": {
              "ExceptionHandling": 1,
              "AdditionalOptions": [ "/std:c++20" ]
            }
          }
        }]
      ]
    }
  ]
}
