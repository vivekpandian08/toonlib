"""
Benchmark comparing TOON vs JSON for PyTorch tensor serialization.

This script evaluates token efficiency and performance for different tensor formats.
Uses tiktoken for accurate GPT-3.5-turbo token counting.
"""

import json
import time
from typing import Any, Dict

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("PyTorch not installed. Install with: pip install torch")
    exit(1)

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    print("[!] tiktoken not installed. Install with: pip install tiktoken")
    print("[!] Using approximate token counting (whitespace split) instead.")

import sys
sys.path.insert(0, '/root/toonstream')
import toonstream


def count_tokens(text: str) -> int:
    """
    Count tokens using tiktoken (GPT-3.5-turbo encoding) if available,
    otherwise fall back to approximate whitespace split.
    
    Args:
        text: Text to count tokens for
        
    Returns:
        Number of tokens
    """
    if TIKTOKEN_AVAILABLE:
        # Use exact tiktoken counting (GPT-3.5-turbo)
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    else:
        # Fallback to approximate whitespace count
        return len(text.split())


def benchmark_tensor_formats():
    """Benchmark TOON vs JSON for tensor data."""
    
    print("=" * 70)
    print("TENSOR FORMAT COMPARISON: TOON vs JSON")
    print("=" * 70)
    print()
    
    # Show which tokenizer is being used
    if TIKTOKEN_AVAILABLE:
        print("[*] Using tiktoken (GPT-3.5-turbo cl100k_base) - 99%+ accuracy")
    else:
        print("[!] Using whitespace split - ~60-70% accuracy (install tiktoken for exact counts)")
    print()
    
    # Test 1: Small 1D Tensor
    print("TEST 1: Small 1D Tensor (100 elements)")
    print("-" * 70)
    tensor_1d = torch.randn(100)
    data_1d = {'weights': tensor_1d, 'name': 'layer_1', 'type': 'embedding'}
    
    # TOON encoding
    start = time.time()
    toon_str = toonstream.encode_with_tensors(data_1d)
    toon_time = time.time() - start
    toon_tokens = count_tokens(toon_str)
    
    # JSON encoding (serialize tensor as list)
    start = time.time()
    json_data = {
        'weights': tensor_1d.tolist(),
        'name': 'layer_1',
        'type': 'embedding'
    }
    json_str = json.dumps(json_data)
    json_time = time.time() - start
    json_tokens = count_tokens(json_str)
    
    toon_bytes = len(toon_str.encode('utf-8'))
    json_bytes = len(json_str.encode('utf-8'))
    
    print(f"TOON tokens:       {toon_tokens:,}")
    print(f"JSON tokens:       {json_tokens:,}")
    print(f"Token savings:     {((json_tokens - toon_tokens) / json_tokens * 100):.1f}%")
    print(f"TOON bytes:        {toon_bytes:,}")
    print(f"JSON bytes:        {json_bytes:,}")
    print(f"Byte savings:      {((json_bytes - toon_bytes) / json_bytes * 100):.1f}%")
    print(f"TOON encode time:  {toon_time*1000:.2f}ms")
    print(f"JSON encode time:  {json_time*1000:.2f}ms")
    print()
    
    # Test 2: 2D Tensor (embeddings matrix)
    print("TEST 2: 2D Tensor (1000x768) - Embedding Matrix")
    print("-" * 70)
    tensor_2d = torch.randn(1000, 768)
    data_2d = {
        'embeddings': tensor_2d,
        'vocab_size': 50000,
        'hidden_dim': 768,
        'model': 'bert-base'
    }
    
    # TOON encoding
    start = time.time()
    toon_str = toonstream.encode_with_tensors(data_2d)
    toon_time = time.time() - start
    toon_tokens = count_tokens(toon_str)
    
    # JSON encoding
    start = time.time()
    json_data = {
        'embeddings': tensor_2d.tolist(),
        'vocab_size': 50000,
        'hidden_dim': 768,
        'model': 'bert-base'
    }
    json_str = json.dumps(json_data)
    json_time = time.time() - start
    json_tokens = count_tokens(json_str)
    
    toon_bytes = len(toon_str.encode('utf-8'))
    json_bytes = len(json_str.encode('utf-8'))
    
    print(f"TOON tokens:       {toon_tokens:,}")
    print(f"JSON tokens:       {json_tokens:,}")
    print(f"Token savings:     {((json_tokens - toon_tokens) / json_tokens * 100):.1f}%")
    print(f"TOON bytes:        {toon_bytes:,}")
    print(f"JSON bytes:        {json_bytes:,}")
    print(f"Byte savings:      {((json_bytes - toon_bytes) / json_bytes * 100):.1f}%")
    print(f"TOON encode time:  {toon_time*1000:.2f}ms")
    print(f"JSON encode time:  {json_time*1000:.2f}ms")
    print()
    
    # Test 3: Multiple tensors (model weights)
    print("TEST 3: Multiple Tensors (5 weight matrices)")
    print("-" * 70)
    data_multi = {
        'layer_1_weights': torch.randn(512, 256),
        'layer_1_bias': torch.randn(256),
        'layer_2_weights': torch.randn(256, 128),
        'layer_2_bias': torch.randn(128),
        'output_weights': torch.randn(128, 10),
        'model_type': 'mlp',
        'version': '1.0'
    }
    
    # TOON encoding
    start = time.time()
    toon_str = toonstream.encode_with_tensors(data_multi)
    toon_time = time.time() - start
    toon_tokens = count_tokens(toon_str)
    
    # JSON encoding
    start = time.time()
    json_data = {
        'layer_1_weights': data_multi['layer_1_weights'].tolist(),
        'layer_1_bias': data_multi['layer_1_bias'].tolist(),
        'layer_2_weights': data_multi['layer_2_weights'].tolist(),
        'layer_2_bias': data_multi['layer_2_bias'].tolist(),
        'output_weights': data_multi['output_weights'].tolist(),
        'model_type': 'mlp',
        'version': '1.0'
    }
    json_str = json.dumps(json_data)
    json_time = time.time() - start
    json_tokens = count_tokens(json_str)
    
    toon_bytes = len(toon_str.encode('utf-8'))
    json_bytes = len(json_str.encode('utf-8'))
    
    print(f"TOON tokens:       {toon_tokens:,}")
    print(f"JSON tokens:       {json_tokens:,}")
    print(f"Token savings:     {((json_tokens - toon_tokens) / json_tokens * 100):.1f}%")
    print(f"TOON bytes:        {toon_bytes:,}")
    print(f"JSON bytes:        {json_bytes:,}")
    print(f"Byte savings:      {((json_bytes - toon_bytes) / json_bytes * 100):.1f}%")
    print(f"TOON encode time:  {toon_time*1000:.2f}ms")
    print(f"JSON encode time:  {json_time*1000:.2f}ms")
    print()
    
    # Test 4: Complex nested structure
    print("TEST 4: Complex Nested Structure")
    print("-" * 70)
    data_complex = {
        'encoder': {
            'embeddings': torch.randn(100, 384),
            'attention_weights': torch.randn(12, 64, 64),
        },
        'decoder': {
            'weights': torch.randn(512, 256),
            'bias': torch.randn(256),
        },
        'metadata': {
            'vocab_size': 50000,
            'max_seq_len': 512,
            'hidden_size': 384,
            'num_heads': 12
        }
    }
    
    # TOON encoding
    start = time.time()
    toon_str = toonstream.encode_with_tensors(data_complex)
    toon_time = time.time() - start
    toon_tokens = count_tokens(toon_str)
    
    # JSON encoding
    start = time.time()
    json_data = {
        'encoder': {
            'embeddings': data_complex['encoder']['embeddings'].tolist(),
            'attention_weights': data_complex['encoder']['attention_weights'].tolist(),
        },
        'decoder': {
            'weights': data_complex['decoder']['weights'].tolist(),
            'bias': data_complex['decoder']['bias'].tolist(),
        },
        'metadata': {
            'vocab_size': 50000,
            'max_seq_len': 512,
            'hidden_size': 384,
            'num_heads': 12
        }
    }
    json_str = json.dumps(json_data)
    json_time = time.time() - start
    json_tokens = count_tokens(json_str)
    
    toon_bytes = len(toon_str.encode('utf-8'))
    json_bytes = len(json_str.encode('utf-8'))
    
    print(f"TOON tokens:       {toon_tokens:,}")
    print(f"JSON tokens:       {json_tokens:,}")
    print(f"Token savings:     {((json_tokens - toon_tokens) / json_tokens * 100):.1f}%")
    print(f"TOON bytes:        {toon_bytes:,}")
    print(f"JSON bytes:        {json_bytes:,}")
    print(f"Byte savings:      {((json_bytes - toon_bytes) / json_bytes * 100):.1f}%")
    print(f"TOON encode time:  {toon_time*1000:.2f}ms")
    print(f"JSON encode time:  {json_time*1000:.2f}ms")
    print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("""
TOON Format for Tensors:
  ✓ Better for LLM token efficiency (reduces token consumption)
  ✓ Automatically handles tensor metadata (dtype, device, shape)
  ✓ Preserves exact tensor types during round-trip
  ✓ Optimized for tabular data representation
  
JSON Format for Tensors:
  ✓ Universal, widely supported format
  ✓ Simple to parse in any language
  ✓ No special dependencies required
  ✗ Higher token overhead (embeds all array brackets/commas)
  ✗ Loses dtype information (treats all numbers as JSON numbers)
  
RECOMMENDATION:
  Use TOON for tensor data when:
    - Token efficiency matters (LLM applications, API costs)
    - Tensor metadata preservation is important
    - Working with large arrays
    
  Use JSON for tensor data when:
    - Universal compatibility is needed
    - Interoperating with non-Python systems
    - Tensor metadata is not important
""")


if __name__ == '__main__':
    benchmark_tensor_formats()
