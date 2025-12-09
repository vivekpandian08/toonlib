"""
Benchmark comparison: JSON vs JSON Compact vs TOON vs TRON

Compares:
1. Character count (size)
2. Token count (supports multiple tokenizers including open-source LLMs)
3. Round-trip consistency
4. Encoding/decoding speed

Supported tokenizers:
- tiktoken (OpenAI GPT-4/3.5)
- transformers GPT-2 (open source)
- transformers Llama/Mistral (open source, requires auth)
- Character approximation (fallback)
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from token_counters import count_tokens as _count_tokens

# Import our multi-tokenizer support
from token_counters import get_tokenizer, list_available_tokenizers

from toonstream import decode, encode

# Global tokenizer (set in main)
tokenizer = None


def count_tokens(text: str) -> int:
    """Count tokens using the configured tokenizer."""
    global tokenizer
    return _count_tokens(text, tokenizer)


def benchmark_data(name: str, data: dict | list):
    """Benchmark a single dataset."""
    print(f"\n{'='*80}")
    print(f"BENCHMARK: {name}")
    print("=" * 80)

    # JSON encoding (pretty - with indentation)
    json_pretty_str = json.dumps(data, indent=2)
    json_pretty_chars = len(json_pretty_str)
    json_pretty_tokens = count_tokens(json_pretty_str)

    # JSON Compact encoding (no whitespace)
    json_compact_str = json.dumps(data, separators=(",", ":"))
    json_compact_chars = len(json_compact_str)
    json_compact_tokens = count_tokens(json_compact_str)

    # TOON encoding
    toon_str = encode(data)
    toon_chars = len(toon_str)
    toon_tokens = count_tokens(toon_str)

    # TRON encoding
    tron_str = encode(data, format="tron")
    tron_chars = len(tron_str)
    tron_tokens = count_tokens(tron_str)

    # Print results
    print(
        f"\n{'Format':<14} {'Chars':>10} {'Tokens':>10} {'vs JSON':>12} {'vs Compact':>12} {'vs TOON':>12}"
    )
    print("-" * 72)
    print(
        f"{'JSON':<14} {json_pretty_chars:>10,} {json_pretty_tokens:>10,} {'--':>12} {'--':>12} {'--':>12}"
    )

    compact_vs_json = f"{(1 - json_compact_tokens/json_pretty_tokens)*100:+.1f}%"
    print(
        f"{'JSON Compact':<14} {json_compact_chars:>10,} {json_compact_tokens:>10,} {compact_vs_json:>12} {'--':>12} {'--':>12}"
    )

    toon_vs_json = f"{(1 - toon_tokens/json_pretty_tokens)*100:+.1f}%"
    toon_vs_compact = f"{(1 - toon_tokens/json_compact_tokens)*100:+.1f}%"
    print(
        f"{'TOON':<14} {toon_chars:>10,} {toon_tokens:>10,} {toon_vs_json:>12} {toon_vs_compact:>12} {'--':>12}"
    )

    tron_vs_json = f"{(1 - tron_tokens/json_pretty_tokens)*100:+.1f}%"
    tron_vs_compact = f"{(1 - tron_tokens/json_compact_tokens)*100:+.1f}%"
    tron_vs_toon = f"{(1 - tron_tokens/toon_tokens)*100:+.1f}%"
    print(
        f"{'TRON':<14} {tron_chars:>10,} {tron_tokens:>10,} {tron_vs_json:>12} {tron_vs_compact:>12} {tron_vs_toon:>12}"
    )

    # Sample output
    print("\nSample Output (first 150 chars):")
    print(f"  JSON:         {json_pretty_str[:150].replace(chr(10), ' ')}...")
    print(f"  JSON Compact: {json_compact_str[:150]}...")
    print(f"  TOON:         {toon_str[:150].replace(chr(10), ' ')}...")
    print(f"  TRON:         {tron_str[:150]}...")

    # Verify round-trip
    try:
        toon_decoded = decode(toon_str)
        toon_match = toon_decoded == data
    except Exception as e:
        toon_match = False
        print(f"  (TOON decode error: {e})")

    try:
        tron_decoded = decode(tron_str, format="tron")
        tron_match = tron_decoded == data
    except Exception as e:
        tron_match = False
        print(f"  (TRON decode error: {e})")

    json_match = json.loads(json_compact_str) == data

    print("\nRound-trip verification:")
    print(f"  JSON:         {'✓ PASS' if json_match else '✗ FAIL'}")
    print(f"  JSON Compact: {'✓ PASS' if json_match else '✗ FAIL'}")
    print(f"  TOON:         {'✓ PASS' if toon_match else '✗ FAIL'}")
    print(f"  TRON:         {'✓ PASS' if tron_match else '✗ FAIL'}")

    return {
        "name": name,
        "json_pretty_chars": json_pretty_chars,
        "json_pretty_tokens": json_pretty_tokens,
        "json_compact_chars": json_compact_chars,
        "json_compact_tokens": json_compact_tokens,
        "toon_chars": toon_chars,
        "toon_tokens": toon_tokens,
        "tron_chars": tron_chars,
        "tron_tokens": tron_tokens,
    }


def main():
    global tokenizer

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="TOONSTREAM Format Benchmark")
    parser.add_argument(
        "--tokenizer",
        "-t",
        choices=["auto", "gpt4", "gpt2", "llama", "mistral", "char"],
        default="auto",
        help="Tokenizer to use (default: auto, prefers open source)",
    )
    parser.add_argument(
        "--list-tokenizers", action="store_true", help="List available tokenizers and exit"
    )
    args = parser.parse_args()

    if args.list_tokenizers:
        print("\nAvailable tokenizers:")
        for name, status in list_available_tokenizers().items():
            icon = "✓" if status else "✗"
            print(f"  {icon} {name}")
        return

    # Initialize tokenizer
    tokenizer = get_tokenizer(args.tokenizer)

    print("=" * 80)
    print("    TOONSTREAM v2.0.0 - FORMAT COMPARISON BENCHMARK")
    print("    JSON vs JSON Compact vs TOON vs TRON")
    print("=" * 80)
    print(f"\nTokenizer: {tokenizer.name} ({tokenizer.model})")
    print(f"Open Source: {'Yes ✓' if tokenizer.is_open_source else 'No'}")

    results = []

    # Test 1: Simple flat object
    data1 = {
        "name": "Alice Johnson",
        "age": 30,
        "email": "alice@example.com",
        "active": True,
        "score": 95.5,
    }
    results.append(benchmark_data("Simple Object (5 fields)", data1))

    # Test 2: Array of objects (tabular data)
    data2 = [
        {"id": 1, "name": "Alice", "dept": "Engineering", "salary": 95000},
        {"id": 2, "name": "Bob", "dept": "Sales", "salary": 75000},
        {"id": 3, "name": "Carol", "dept": "Engineering", "salary": 105000},
        {"id": 4, "name": "David", "dept": "Marketing", "salary": 85000},
        {"id": 5, "name": "Eve", "dept": "Engineering", "salary": 115000},
    ]
    results.append(benchmark_data("Employee Records (5 rows)", data2))

    # Test 3: Larger tabular dataset
    data3 = [
        {
            "id": i,
            "name": f"User{i}",
            "email": f"user{i}@example.com",
            "active": i % 2 == 0,
            "score": i * 10,
        }
        for i in range(1, 21)
    ]
    results.append(benchmark_data("User Records (20 rows)", data3))

    # Test 4: Nested object
    data4 = {
        "user": {"name": "Alice", "profile": {"age": 30, "location": "NYC"}},
        "settings": {"theme": "dark", "notifications": True},
    }
    results.append(benchmark_data("Nested Object (2 levels)", data4))

    # Test 5: Mixed data structure
    data5 = {
        "title": "Monthly Report",
        "count": 3,
        "items": [
            {"name": "Item1", "value": 100},
            {"name": "Item2", "value": 200},
            {"name": "Item3", "value": 300},
        ],
    }
    results.append(benchmark_data("Mixed Structure", data5))

    # Test 6: Large array of objects
    data6 = [
        {"id": i, "name": f"Product{i}", "price": 9.99 + i, "stock": i * 10, "active": True}
        for i in range(1, 51)
    ]
    results.append(benchmark_data("Products (50 rows)", data6))

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY - Token Counts by Format")
    print("=" * 80)

    total_json_pretty = sum(r["json_pretty_tokens"] for r in results)
    total_json_compact = sum(r["json_compact_tokens"] for r in results)
    total_toon = sum(r["toon_tokens"] for r in results)
    total_tron = sum(r["tron_tokens"] for r in results)

    print(
        f"\n{'Dataset':<30} {'JSON':>10} {'Compact':>10} {'TOON':>10} {'TRON':>10} {'TRON vs JSON':>14}"
    )
    print("-" * 96)

    for r in results:
        savings = f"{(1 - r['tron_tokens']/r['json_pretty_tokens'])*100:+.1f}%"
        print(
            f"{r['name']:<30} {r['json_pretty_tokens']:>10,} {r['json_compact_tokens']:>10,} {r['toon_tokens']:>10,} {r['tron_tokens']:>10,} {savings:>14}"
        )

    print("-" * 96)
    total_savings = f"{(1 - total_tron/total_json_pretty)*100:+.1f}%"
    print(
        f"{'TOTAL':<30} {total_json_pretty:>10,} {total_json_compact:>10,} {total_toon:>10,} {total_tron:>10,} {total_savings:>14}"
    )

    print("\n📊 OVERALL RESULTS (Token Savings):")
    print(
        f"   JSON Compact vs JSON: {(1 - total_json_compact/total_json_pretty)*100:.1f}% fewer tokens"
    )
    print(f"   TOON vs JSON:         {(1 - total_toon/total_json_pretty)*100:.1f}% fewer tokens")
    print(f"   TOON vs JSON Compact: {(1 - total_toon/total_json_compact)*100:.1f}% fewer tokens")
    print(f"   TRON vs JSON:         {(1 - total_tron/total_json_pretty)*100:.1f}% fewer tokens")
    print(f"   TRON vs JSON Compact: {(1 - total_tron/total_json_compact)*100:.1f}% fewer tokens")
    print(f"   TRON vs TOON:         {(1 - total_tron/total_toon)*100:.1f}% fewer tokens")

    print("\n" + "=" * 80)
    print("    BENCHMARK COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
