"""
MLE Runtime V2 - Enhanced Python SDK
Provides access to all new operators, compression, security, and backward compatibility features.
"""

import numpy as np
import json
import struct
import hashlib
import zlib
from typing import Dict, List, Optional, Union, Tuple, Any
from pathlib import Path
import warnings

# Import the core runtime (assuming it exists)
try:
    from . import _mle_core as core_runtime
    HAS_CORE = True
except ImportError:
    HAS_CORE = False
    warnings.warn("Core C++ runtime not available. Using Python fallback implementations.")

class MLEFormat:
    """Enhanced MLE file format with V2 features"""
    
    # Magic number and version
    MLE_MAGIC = 0x00454C4D
    MLE_VERSION = 2
    MIN_SUPPORTED_VERSION = 1
    MAX_SUPPORTED_VERSION = 2
    
    # Feature flags
    FEATURE_NONE = 0x00000000
    FEATURE_COMPRESSION = 0x00000001
    FEATURE_ENCRYPTION = 0x00000002
    FEATURE_SIGNING = 0x00000004
    FEATURE_STREAMING = 0x00000008
    FEATURE_QUANTIZATION = 0x00000010
    FEATURE_EXTENDED_METADATA = 0x00000020
    
    # Compression types
    COMPRESSION_NONE = 0
    COMPRESSION_LZ4 = 1
    COMPRESSION_ZSTD = 2
    COMPRESSION_BROTLI = 3
    COMPRESSION_QUANTIZE_INT8 = 4
    COMPRESSION_QUANTIZE_FP16 = 5
    
    # Operator types (extended)
    OP_LINEAR = 1
    OP_RELU = 2
    OP_GELU = 3
    OP_SOFTMAX = 4
    OP_LAYERNORM = 5
    OP_MATMUL = 6
    OP_ADD = 7
    OP_MUL = 8
    OP_CONV2D = 9
    OP_MAXPOOL2D = 10
    OP_BATCHNORM = 11
    OP_DROPOUT = 12
    OP_EMBEDDING = 13
    OP_ATTENTION = 14
    OP_DECISION_TREE = 26
    OP_TREE_ENSEMBLE = 27
    OP_GRADIENT_BOOSTING = 28
    OP_SVM = 29
    OP_NAIVE_BAYES = 30
    OP_KNN = 31
    OP_CLUSTERING = 32
    OP_DBSCAN = 33
    OP_DECOMPOSITION = 34

class CompressionUtils:
    """Utilities for model compression and quantization"""
    
    @staticmethod
    def quantize_weights_int8(weights: np.ndarray) -> Tuple[np.ndarray, float, int]:
        """Quantize FP32 weights to INT8 with scale and zero point"""
        min_val = weights.min()
        max_val = weights.max()
        
        scale = (max_val - min_val) / 255.0
        zero_point = int(np.round(-min_val / scale))
        zero_point = np.clip(zero_point, 0, 255)
        
        quantized = np.round(weights / scale + zero_point)
        quantized = np.clip(quantized, 0, 255).astype(np.uint8)
        
        return quantized, scale, zero_point
    
    @staticmethod
    def dequantize_weights_int8(quantized: np.ndarray, scale: float, zero_point: int) -> np.ndarray:
        """Dequantize INT8 weights back to FP32"""
        return (quantized.astype(np.float32) - zero_point) * scale
    
    @staticmethod
    def quantize_weights_fp16(weights: np.ndarray) -> np.ndarray:
        """Quantize FP32 weights to FP16"""
        return weights.astype(np.float16)
    
    @staticmethod
    def dequantize_weights_fp16(quantized: np.ndarray) -> np.ndarray:
        """Dequantize FP16 weights back to FP32"""
        return quantized.astype(np.float32)
    
    @staticmethod
    def compress_data(data: bytes, compression_type: int = 0) -> bytes:
        """Compress data using specified algorithm"""
        if compression_type == 0:  # COMPRESSION_NONE
            return data
        elif compression_type == 2:  # COMPRESSION_ZSTD
            # Fallback to zlib if zstd not available
            return zlib.compress(data)
        else:
            raise ValueError(f"Unsupported compression type: {compression_type}")
    
    @staticmethod
    def decompress_data(data: bytes, compression_type: int, uncompressed_size: int) -> bytes:
        """Decompress data using specified algorithm"""
        if compression_type == 0:  # COMPRESSION_NONE
            return data
        elif compression_type == 2:  # COMPRESSION_ZSTD
            # Fallback to zlib if zstd not available
            return zlib.decompress(data)
        else:
            raise ValueError(f"Unsupported compression type: {compression_type}")

class SecurityUtils:
    """Utilities for model security and integrity"""
    
    @staticmethod
    def compute_checksum(data: bytes) -> int:
        """Compute CRC32 checksum"""
        return zlib.crc32(data) & 0xffffffff
    
    @staticmethod
    def compute_hash(data: bytes) -> str:
        """Compute SHA256 hash"""
        return hashlib.sha256(data).hexdigest()
    
    @staticmethod
    def generate_keypair() -> Tuple[bytes, bytes]:
        """Generate ED25519 key pair (placeholder implementation)"""
        # This is a placeholder - real implementation would use cryptographic library
        import os
        public_key = os.urandom(32)
        private_key = os.urandom(64)
        return public_key, private_key
    
    @staticmethod
    def sign_data(data: bytes, private_key: bytes) -> bytes:
        """Sign data with ED25519 (placeholder implementation)"""
        # This is a placeholder - real implementation would use cryptographic library
        return hashlib.sha256(data + private_key).digest()[:64]
    
    @staticmethod
    def verify_signature(data: bytes, signature: bytes, public_key: bytes) -> bool:
        """Verify ED25519 signature (placeholder implementation)"""
        # This is a placeholder - real implementation would use cryptographic library
        expected = hashlib.sha256(data + public_key).digest()[:64]
        return signature == expected

class MLERuntime:
    """Enhanced MLE Runtime with V2 features"""
    
    def __init__(self, device: str = "cpu"):
        self.device = device
        self.model_data = None
        self.metadata = {}
        self.compression_info = {}
        self.security_info = {}
        
        # Initialize core runtime if available
        if HAS_CORE:
            # Convert string device to enum
            if device.lower() == "cpu":
                device_enum = core_runtime.Device.CPU
            elif device.lower() == "cuda":
                device_enum = core_runtime.Device.CUDA
            else:
                device_enum = core_runtime.Device.CPU
            self.core_engine = core_runtime.Engine(device_enum)
        else:
            self.core_engine = None
    
    def load_model(self, path: Union[str, Path], verify_signature: bool = False, 
                   public_key: Optional[bytes] = None) -> Dict[str, Any]:
        """Load MLE model with enhanced features"""
        path = Path(path)
        
        with open(path, 'rb') as f:
            # Read header
            header_data = f.read(144)  # V2 header is 144 bytes
            header = self._parse_header(header_data)
            
            # Verify version compatibility
            if header['version'] < MLEFormat.MIN_SUPPORTED_VERSION or \
               header['version'] > MLEFormat.MAX_SUPPORTED_VERSION:
                raise ValueError(f"Unsupported model version: {header['version']}")
            
            # Handle backward compatibility
            if header['version'] == 1:
                return self._load_legacy_model(f, header)
            
            # Load V2 model
            return self._load_model(f, header, verify_signature, public_key)
    
    def _parse_header(self, header_data: bytes) -> Dict[str, Any]:
        """Parse MLE header"""
        if len(header_data) < 16:
            raise ValueError("Invalid header size")
        
        magic, version = struct.unpack('<II', header_data[:8])
        
        if magic != MLEFormat.MLE_MAGIC:
            raise ValueError(f"Invalid magic number: 0x{magic:08x}")
        
        if len(header_data) >= 144:  # V2 header
            # V2 header: 4+4+4+4 + 8*10 + 4*6 = 16 + 80 + 24 = 120 bytes minimum
            # Let's be more careful with the unpacking
            try:
                fields = struct.unpack('<IIIIQQQQQQQQQIIIII', header_data[:120])
                return {
                    'magic': fields[0],
                    'version': fields[1],
                    'feature_flags': fields[2],
                    'header_size': fields[3],
                    'metadata_offset': fields[4],
                    'metadata_size': fields[5],
                    'graph_offset': fields[6],
                    'graph_size': fields[7],
                    'weights_offset': fields[8],
                    'weights_size': fields[9],
                    'signature_offset': fields[10],
                    'signature_size': fields[11],
                    'compression_offset': fields[12],
                    'compression_size': fields[13],
                    'metadata_checksum': fields[14],
                    'graph_checksum': fields[15],
                    'weights_checksum': fields[16],
                    'header_checksum': fields[17],
                    'min_reader_version': fields[18],
                    'writer_version': fields[19]
                }
            except struct.error:
                # Fallback to simpler parsing
                magic, version = struct.unpack('<II', header_data[:8])
                return {
                    'magic': magic,
                    'version': version,
                    'feature_flags': 0,
                    'header_size': len(header_data),
                    'metadata_offset': 0,
                    'metadata_size': 0,
                    'graph_offset': 0,
                    'graph_size': 0,
                    'weights_offset': 0,
                    'weights_size': 0,
                    'signature_offset': 0,
                    'signature_size': 0
                }
        else:  # V1 header (64 bytes)
            try:
                fields = struct.unpack('<IIQQQQQQ', header_data[:56])  # 8 + 6*8 = 56 bytes
                return {
                    'magic': fields[0],
                    'version': fields[1],
                    'feature_flags': 0,
                    'metadata_offset': fields[2],
                    'metadata_size': fields[3],
                    'graph_offset': fields[4],
                    'graph_size': fields[5],
                    'weights_offset': fields[6],
                    'weights_size': fields[7],
                    'signature_offset': 0,
                    'signature_size': 0
                }
            except struct.error:
                # Minimal fallback
                magic, version = struct.unpack('<II', header_data[:8])
                return {
                    'magic': magic,
                    'version': version,
                    'feature_flags': 0,
                    'metadata_offset': 0,
                    'metadata_size': 0,
                    'graph_offset': 0,
                    'graph_size': 0,
                    'weights_offset': 0,
                    'weights_size': 0,
                    'signature_offset': 0,
                    'signature_size': 0
                }
    
    def _load_model(self, f, header: Dict[str, Any], verify_signature: bool, 
                       public_key: Optional[bytes]) -> Dict[str, Any]:
        """Load V2 model with enhanced features"""
        
        # Verify header integrity
        if header.get('header_checksum', 0) != 0:
            header_copy = header.copy()
            header_copy['header_checksum'] = 0
            header_bytes = self._serialize_header(header_copy)
            computed_checksum = SecurityUtils.compute_checksum(header_bytes)
            if computed_checksum != header['header_checksum']:
                raise ValueError("Header integrity check failed")
        
        # Load metadata
        metadata = {}
        if header['metadata_size'] > 0:
            f.seek(header['metadata_offset'])
            metadata_data = f.read(header['metadata_size'])
            
            # Verify metadata checksum
            if header.get('metadata_checksum', 0) != 0:
                computed_checksum = SecurityUtils.compute_checksum(metadata_data)
                if computed_checksum != header['metadata_checksum']:
                    raise ValueError("Metadata integrity check failed")
            
            metadata = json.loads(metadata_data.decode('utf-8'))
        
        # Load compression info
        compression_info = {}
        if header.get('compression_size', 0) > 0:
            f.seek(header['compression_offset'])
            comp_data = f.read(header['compression_size'])
            compression_info = self._parse_compression_header(comp_data)
        
        # Load and decompress weights
        weights_data = None
        if header['weights_size'] > 0:
            f.seek(header['weights_offset'])
            weights_data = f.read(header['weights_size'])
            
            # Decompress if needed
            if header['feature_flags'] & 0x00000001:  # FEATURE_COMPRESSION
                weights_data = CompressionUtils.decompress_data(
                    weights_data, 
                    compression_info.get('type', 0),  # COMPRESSION_NONE
                    compression_info.get('uncompressed_size', len(weights_data))
                )
            
            # Verify weights checksum
            if header.get('weights_checksum', 0) != 0:
                computed_checksum = SecurityUtils.compute_checksum(weights_data)
                if computed_checksum != header['weights_checksum']:
                    raise ValueError("Weights integrity check failed")
        
        # Verify signature if requested
        if verify_signature and (header['feature_flags'] & 0x00000004):  # FEATURE_SIGNING
            if not public_key:
                raise ValueError("Public key required for signature verification")
            
            f.seek(header['signature_offset'])
            signature_data = f.read(header['signature_size'])
            
            # Compute model hash (excluding signature)
            model_data = self._get_model_data_for_signing(f, header)
            if not SecurityUtils.verify_signature(model_data, signature_data, public_key):
                raise ValueError("Signature verification failed")
        
        # Load graph
        f.seek(header['graph_offset'])
        graph_data = f.read(header['graph_size'])
        
        # Verify graph checksum
        if header.get('graph_checksum', 0) != 0:
            computed_checksum = SecurityUtils.compute_checksum(graph_data)
            if computed_checksum != header['graph_checksum']:
                raise ValueError("Graph integrity check failed")
        
        # Store model data
        self.model_data = {
            'header': header,
            'metadata': metadata,
            'graph': graph_data,
            'weights': weights_data,
            'compression_info': compression_info
        }
        
        return {
            'version': header['version'],
            'features': header['feature_flags'],
            'metadata': metadata,
            'compression_info': compression_info,
            'model_size': len(weights_data) if weights_data else 0,
            'compressed_size': header['weights_size'],
            'compression_ratio': header['weights_size'] / len(weights_data) if weights_data else 1.0
        }
    
    def _load_legacy_model(self, f, header: Dict[str, Any]) -> Dict[str, Any]:
        """Load legacy V1 model with backward compatibility"""
        print(f"Loading legacy model (version {header['version']}) with backward compatibility")
        
        # Load metadata
        metadata = {}
        if header['metadata_size'] > 0:
            f.seek(header['metadata_offset'])
            metadata_data = f.read(header['metadata_size'])
            metadata = json.loads(metadata_data.decode('utf-8'))
        
        # Load weights
        weights_data = None
        if header['weights_size'] > 0:
            f.seek(header['weights_offset'])
            weights_data = f.read(header['weights_size'])
        
        # Load graph
        f.seek(header['graph_offset'])
        graph_data = f.read(header['graph_size'])
        
        # Store model data
        self.model_data = {
            'header': header,
            'metadata': metadata,
            'graph': graph_data,
            'weights': weights_data,
            'compression_info': {}
        }
        
        return {
            'version': header['version'],
            'features': 0,
            'metadata': metadata,
            'compression_info': {},
            'model_size': len(weights_data) if weights_data else 0,
            'compressed_size': header['weights_size'],
            'compression_ratio': 1.0
        }
    
    def _parse_compression_header(self, data: bytes) -> Dict[str, Any]:
        """Parse compression header"""
        if len(data) < 20:
            return {}
        
        fields = struct.unpack('<BBHQIB', data[:20])
        return {
            'type': fields[0],
            'level': fields[1],
            'uncompressed_size': fields[3],
            'checksum': fields[4],
            'quantization_bits': fields[5]
        }
    
    def _serialize_header(self, header: Dict[str, Any]) -> bytes:
        """Serialize header for checksum calculation"""
        # This is a simplified version - real implementation would be more complete
        return struct.pack('<IIIIQQQQQQQQQIIIII',
            header['magic'], header['version'], header['feature_flags'], header['header_size'],
            header['metadata_offset'], header['metadata_size'], header['graph_offset'], header['graph_size'],
            header['weights_offset'], header['weights_size'], header['signature_offset'], header['signature_size'],
            header['compression_offset'], header['compression_size'], header['metadata_checksum'],
            header['graph_checksum'], header['weights_checksum'], header['header_checksum'],
            header['min_reader_version'], header['writer_version']
        )
    
    def _get_model_data_for_signing(self, f, header: Dict[str, Any]) -> bytes:
        """Get model data for signature verification (excluding signature section)"""
        # This is a simplified version - real implementation would exclude signature section
        f.seek(0)
        return f.read()
    
    def run(self, inputs: List[np.ndarray]) -> List[np.ndarray]:
        """Run inference on the loaded model"""
        if not self.model_data:
            raise ValueError("No model loaded")
        
        if self.core_engine and HAS_CORE:
            # Use C++ core engine
            return self.core_engine.run(inputs)
        else:
            # Fallback to Python implementation
            return self._run_python_fallback(inputs)
    
    def _run_python_fallback(self, inputs: List[np.ndarray]) -> List[np.ndarray]:
        """Python fallback implementation for basic operators"""
        # This is a simplified fallback - real implementation would parse graph and execute operators
        warnings.warn("Using Python fallback implementation. Performance may be limited.")
        
        # For demonstration, just return the inputs
        return inputs
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get comprehensive model information"""
        if not self.model_data:
            raise ValueError("No model loaded")
        
        header = self.model_data['header']
        
        # Feature analysis
        features = []
        if header.get('feature_flags', 0) & 0x00000001:  # FEATURE_COMPRESSION
            features.append("Compression")
        if header.get('feature_flags', 0) & 0x00000004:  # FEATURE_SIGNING
            features.append("Digital Signing")
        if header.get('feature_flags', 0) & 0x00000002:  # FEATURE_ENCRYPTION
            features.append("Encryption")
        if header.get('feature_flags', 0) & 0x00000010:  # FEATURE_QUANTIZATION
            features.append("Quantization")
        
        return {
            'version': header['version'],
            'features': features,
            'metadata': self.model_data['metadata'],
            'model_size_bytes': len(self.model_data['weights']) if self.model_data['weights'] else 0,
            'compressed_size_bytes': header['weights_size'],
            'compression_ratio': header['weights_size'] / len(self.model_data['weights']) if self.model_data['weights'] else 1.0,
            'compression_info': self.model_data['compression_info'],
            'header_size': header.get('header_size', 64),
            'backward_compatible': header['version'] >= MLEFormat.MIN_SUPPORTED_VERSION
        }
    
    def benchmark(self, inputs: List[np.ndarray], num_runs: int = 100) -> Dict[str, float]:
        """Benchmark model performance"""
        if not self.model_data:
            raise ValueError("No model loaded")
        
        import time
        
        # Warmup
        for _ in range(5):
            self.run(inputs)
        
        # Benchmark
        times = []
        for _ in range(num_runs):
            start = time.perf_counter()
            outputs = self.run(inputs)
            end = time.perf_counter()
            times.append((end - start) * 1000)  # Convert to ms
        
        return {
            'mean_time_ms': np.mean(times),
            'std_time_ms': np.std(times),
            'min_time_ms': np.min(times),
            'max_time_ms': np.max(times),
            'median_time_ms': np.median(times),
            'throughput_samples_per_sec': 1000.0 / np.mean(times) if inputs else 0
        }

# Convenience functions
def load_model(path: Union[str, Path], device: str = "cpu", **kwargs) -> 'MLERuntime':
    """Load MLE model with enhanced features"""
    runtime = MLERuntime(device=device)
    runtime.load_model(path, **kwargs)
    return runtime

def inspect_model(path: Union[str, Path]) -> Dict[str, Any]:
    """Inspect MLE model and return comprehensive information"""
    runtime = MLERuntime()
    model_info = runtime.load_model(path)
    return runtime.get_model_info()

class ModelInspector:
    """Advanced model inspection utilities"""
    
    @staticmethod
    def analyze_model(path: Union[str, Path]) -> Dict[str, Any]:
        """Comprehensive model analysis"""
        runtime = MLERuntime()
        model_info = runtime.load_model(path)
        
        return {
            'basic_info': runtime.get_model_info(),
            'supported_operators': get_supported_operators(),
            'version_info': get_version_info(),
            'file_size': Path(path).stat().st_size,
            'recommendations': ModelInspector._get_recommendations(runtime.get_model_info())
        }
    
    @staticmethod
    def _get_recommendations(model_info: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        if model_info['compression_ratio'] == 1.0:
            recommendations.append("Consider enabling compression to reduce model size")
        
        if 'Digital Signing' not in model_info['features']:
            recommendations.append("Consider adding digital signatures for security")
        
        if model_info['version'] == 1:
            recommendations.append("Consider upgrading to V2 format for enhanced features")
        
        return recommendations

def get_supported_operators() -> List[str]:
    """Get list of supported operators in V2"""
    return [
        # Neural network operators
        "Linear", "ReLU", "GELU", "Softmax", "LayerNorm", "MatMul", "Add", "Mul",
        "Conv2D", "MaxPool2D", "BatchNorm", "Dropout", "Embedding", "Attention",
        
        # ML algorithms
        "DecisionTree", "TreeEnsemble", "GradientBoosting", "SVM", "NaiveBayes",
        "KNN", "Clustering", "DBSCAN", "Decomposition"
    ]

def get_version_info() -> Dict[str, Any]:
    """Get MLE Runtime version information"""
    return {
        'version': '2.0.0',
        'format_version': MLEFormat.MLE_VERSION,
        'supported_versions': list(range(MLEFormat.MIN_SUPPORTED_VERSION, MLEFormat.MAX_SUPPORTED_VERSION + 1)),
        'features': [
            'Compression', 'Digital Signing', 'Backward Compatibility',
            'Enhanced Operators', 'Quantization', 'Security'
        ],
        'operators': len(get_supported_operators()),
        'has_core_runtime': HAS_CORE
    }

# Export supported operators list
__supported_operators__ = get_supported_operators()