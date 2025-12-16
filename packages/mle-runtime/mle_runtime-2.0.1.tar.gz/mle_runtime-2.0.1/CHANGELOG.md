# MLE Runtime Changelog

## Version 2.0.0 - Enhanced Features Release

### Added
- **New Neural Network Operators**:
  - Conv2D: 2D Convolutional layers with stride and padding support
  - MaxPool2D: 2D Max pooling with configurable kernel size
  - BatchNorm: Batch normalization for training stability
  - Attention: Multi-head self-attention mechanism

- **Enhanced Tree Ensemble Support**:
  - Improved Random Forest implementation
  - Better tree traversal algorithms
  - Support for multiple tree formats

- **Advanced SVM Support**:
  - RBF kernel implementation
  - Support for multi-class classification
  - Optimized kernel computations

### Enhanced
- **File Format (v2.0)**:
  - Extended header with feature flags
  - Compression support (LZ4, ZSTD, Brotli)
  - Integrity checking with CRC32 checksums
  - Digital signature support (ED25519)
  - Backward compatibility with v1.0 files

- **Memory Management**:
  - Improved memory mapping
  - Streaming decompression for large models
  - Better error handling and validation

### Technical Details
- Header size increased from 64 to 128 bytes
- Support for unlimited metadata size
- Feature flags for optional capabilities
- Comprehensive integrity verification

---

## Version 1.0.0 - Initial Release

### Added
- Basic MLE file format
- Core operators (Linear, ReLU, Softmax, etc.)
- Decision tree support
- Memory-mapped file loading
- Cross-platform compatibility