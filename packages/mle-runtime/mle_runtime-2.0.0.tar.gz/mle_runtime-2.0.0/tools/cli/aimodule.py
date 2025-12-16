#!/usr/bin/env python3
"""
AIModule CLI - Inspect and validate .mle files
"""

import argparse
import struct
import json
import sys
from pathlib import Path

MLE_MAGIC = 0x00454C4D
MLE_VERSION = 1

def inspect_mle(path: str):
    """Inspect .mle file and print information"""
    with open(path, 'rb') as f:
        # Read header (80 bytes: 2*uint32 + 7*uint64 + 16 reserved)
        header_data = f.read(80)
        if len(header_data) < 80:
            print("Error: File too small")
            return False
        
        data = struct.unpack('II QQQQQQQ 16s', header_data)
        magic, version, meta_off, meta_size, graph_off, graph_size, \
        weights_off, weights_size, sig_off = data[:9]
        
        if magic != MLE_MAGIC:
            print(f"Error: Invalid magic number: 0x{magic:08x}")
            return False
        
        if version != MLE_VERSION:
            print(f"Error: Unsupported version: {version}")
            return False
        
        print(f"✓ Valid .mle file")
        print(f"\nHeader Information:")
        print(f"  Version: {version}")
        print(f"  Metadata offset: {meta_off}, size: {meta_size}")
        print(f"  Graph offset: {graph_off}, size: {graph_size}")
        print(f"  Weights offset: {weights_off}, size: {weights_size}")
        print(f"  Signature offset: {sig_off}")
        
        # Read metadata
        if meta_size > 0:
            f.seek(meta_off)
            meta_bytes = f.read(meta_size)
            try:
                metadata = json.loads(meta_bytes.decode('utf-8'))
                print(f"\nMetadata:")
                print(json.dumps(metadata, indent=2))
            except:
                print(f"\nMetadata: (binary, {meta_size} bytes)")
        
        # Read graph IR
        f.seek(graph_off)
        num_nodes, num_tensors, num_inputs, num_outputs = struct.unpack('IIII', f.read(16))
        
        print(f"\nGraph Information:")
        print(f"  Nodes: {num_nodes}")
        print(f"  Tensors: {num_tensors}")
        print(f"  Inputs: {num_inputs}")
        print(f"  Outputs: {num_outputs}")
        
        # Signature verification
        if sig_off > 0:
            print(f"\n✓ Model is signed")
        else:
            print(f"\n⚠ Model is not signed")
        
        return True

def validate_mle(path: str):
    """Validate .mle file structure"""
    try:
        result = inspect_mle(path)
        if result:
            print(f"\n✓ Validation passed")
            return 0
        else:
            print(f"\n✗ Validation failed")
            return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

def main():
    parser = argparse.ArgumentParser(description='AIModule CLI')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Inspect command
    inspect_parser = subparsers.add_parser('inspect', help='Inspect .mle file')
    inspect_parser.add_argument('file', help='.mle file path')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate .mle file')
    validate_parser.add_argument('file', help='.mle file path')
    
    # Export command (redirect to exporter)
    export_parser = subparsers.add_parser('export', help='Export PyTorch model to .mle')
    export_parser.add_argument('--model', help='PyTorch model path')
    export_parser.add_argument('--out', required=True, help='Output .mle path')
    export_parser.add_argument('--input-shape', default='1,128', help='Input shape')
    
    args = parser.parse_args()
    
    if args.command == 'inspect':
        sys.exit(0 if inspect_mle(args.file) else 1)
    elif args.command == 'validate':
        sys.exit(validate_mle(args.file))
    elif args.command == 'export':
        # Call exporter
        import subprocess
        cmd = [
            sys.executable,
            str(Path(__file__).parent.parent / 'exporter' / 'pytorch_to_mle.py'),
            '--out', args.out,
            '--input-shape', args.input_shape
        ]
        if args.model:
            cmd.extend(['--model', args.model])
        sys.exit(subprocess.call(cmd))
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
