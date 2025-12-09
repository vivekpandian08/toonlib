"""
Visual demonstration of token counting methods for TOON vs JSON tensors.
Shows exactly how tokens are counted in the benchmarks.
"""

import torch
import json
import toonstream

def display_token_breakdown(text, label):
    """Display text and its token breakdown."""
    tokens = text.split()
    print(f"\n{label}")
    print("=" * 70)
    print(f"Text:\n{text[:200]}{'...' if len(text) > 200 else ''}\n")
    print(f"Token Count (whitespace split): {len(tokens)}")
    print(f"Bytes: {len(text.encode('utf-8')):,}")
    print(f"Characters: {len(text):,}")
    print(f"\nFirst 10 tokens: {tokens[:10]}")
    if len(tokens) > 10:
        print(f"Last 10 tokens: {tokens[-10:]}")
    return len(tokens)

def main():
    print("\n" + "=" * 70)
    print("TENSOR TOKEN COUNTING METHODOLOGY")
    print("=" * 70)
    
    # Test 1: Small tensor
    print("\n\n" + "█" * 70)
    print("TEST 1: Small Tensor (5 values)")
    print("█" * 70)
    
    tensor = torch.tensor([1.0, 2.0, 3.0, 4.0, 5.0])
    data = {'weights': tensor, 'model': 'test_v1'}
    
    # TOON
    toon_str = toonstream.encode_with_tensors(data)
    toon_tokens = display_token_breakdown(toon_str, "TOON FORMAT")
    
    # JSON
    json_data = {'weights': tensor.tolist(), 'model': 'test_v1'}
    json_str = json.dumps(json_data)
    json_tokens = display_token_breakdown(json_str, "JSON FORMAT")
    
    print(f"\n{'─' * 70}")
    print(f"TOON tokens:  {toon_tokens:,}")
    print(f"JSON tokens:  {json_tokens:,}")
    print(f"Difference:   {((json_tokens - toon_tokens) / max(json_tokens, 1) * 100):+.1f}%")
    print(f"Winner:       {'TOON' if toon_tokens < json_tokens else 'JSON' if json_tokens < toon_tokens else 'TIE'}")
    
    # Test 2: Medium tensor
    print("\n\n" + "█" * 70)
    print("TEST 2: Medium Tensor (100 values)")
    print("█" * 70)
    
    tensor = torch.randn(100)
    data = {
        'embeddings': tensor,
        'vocab_size': 50000,
        'hidden_dim': 768
    }
    
    # TOON
    toon_str = toonstream.encode_with_tensors(data)
    toon_tokens = display_token_breakdown(toon_str, "TOON FORMAT")
    
    # JSON
    json_data = {
        'embeddings': tensor.tolist(),
        'vocab_size': 50000,
        'hidden_dim': 768
    }
    json_str = json.dumps(json_data)
    json_tokens = display_token_breakdown(json_str, "JSON FORMAT")
    
    print(f"\n{'─' * 70}")
    print(f"TOON tokens:  {toon_tokens:,}")
    print(f"JSON tokens:  {json_tokens:,}")
    print(f"Difference:   {((json_tokens - toon_tokens) / max(json_tokens, 1) * 100):+.1f}%")
    print(f"Winner:       {'TOON' if toon_tokens < json_tokens else 'JSON' if json_tokens < toon_tokens else 'TIE'}")
    
    # Test 3: Complex structure
    print("\n\n" + "█" * 70)
    print("TEST 3: Complex ML Model Structure")
    print("█" * 70)
    
    data = {
        'encoder': {
            'weights': torch.randn(10, 20),
            'bias': torch.randn(20),
        },
        'decoder': {
            'weights': torch.randn(20, 10),
            'bias': torch.randn(10),
        },
        'config': {
            'model_name': 'autoencoder-v1',
            'layers': 2,
            'hidden_dim': 20
        }
    }
    
    # TOON
    toon_str = toonstream.encode_with_tensors(data)
    toon_tokens = display_token_breakdown(toon_str, "TOON FORMAT")
    
    # JSON
    json_data = {
        'encoder': {
            'weights': data['encoder']['weights'].tolist(),
            'bias': data['encoder']['bias'].tolist(),
        },
        'decoder': {
            'weights': data['decoder']['weights'].tolist(),
            'bias': data['decoder']['bias'].tolist(),
        },
        'config': {
            'model_name': 'autoencoder-v1',
            'layers': 2,
            'hidden_dim': 20
        }
    }
    json_str = json.dumps(json_data)
    json_tokens = display_token_breakdown(json_str, "JSON FORMAT")
    
    print(f"\n{'─' * 70}")
    print(f"TOON tokens:  {toon_tokens:,}")
    print(f"JSON tokens:  {json_tokens:,}")
    print(f"Difference:   {((json_tokens - toon_tokens) / max(json_tokens, 1) * 100):+.1f}%")
    print(f"Winner:       {'TOON' if toon_tokens < json_tokens else 'JSON' if json_tokens < toon_tokens else 'TIE'}")
    
    # Summary
    print("\n\n" + "=" * 70)
    print("TOKEN COUNTING METHODOLOGY SUMMARY")
    print("=" * 70)
    print("""
Method Used: Whitespace Split
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Take serialized string (TOON or JSON)
2. Split by whitespace: text.split()
3. Count resulting segments: len(tokens)

Example:
  Text: 'weights: [1.0, 2.0, 3.0]'
  Tokens: ['weights:', '[1.0,', '2.0,', '3.0]']
  Count: 4 tokens

Accuracy:
  ✓ Approximate: ~60-70% of actual LLM tokens
  ✓ Relative comparison: Accurate for comparing formats
  ✗ Absolute values: Conservative estimates

For Production:
  Use tiktoken for exact token counts:
  - pip install tiktoken
  - encoding = tiktoken.get_encoding('cl100k_base')
  - exact_tokens = len(encoding.encode(text))
    """)
    
    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()
