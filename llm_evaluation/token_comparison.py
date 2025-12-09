#!/usr/bin/env python3
"""
Token Comparison Tool for TOON/TRON vs JSON

This script provides detailed token analysis and comparison between
JSON, TOON, and TRON formats using various sample data structures.
"""

import json
import os
import sys

# Add parent directory to path for toonstream imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from toonstream import encode, encode_tron


def toon_encode(data):
    """Encode data to TOON format."""
    return encode(data, format="toon")


def tron_encode(data):
    """Encode data to TRON format."""
    return encode_tron(data)


def estimate_tokens(text: str) -> int:
    """
    Estimate token count using a simple approximation.
    Most LLMs use ~4 characters per token on average.
    """
    # Simple estimation: ~4 chars per token, with adjustment for whitespace
    return max(1, len(text) // 4)


def precise_token_count(text: str) -> int:
    """
    More precise token estimation accounting for:
    - Whitespace typically gets its own token
    - Punctuation often gets separate tokens
    - Numbers and special chars vary
    """
    import re

    # Count different token types
    words = len(re.findall(r"\b\w+\b", text))
    punctuation = len(re.findall(r"[^\w\s]", text))
    numbers = len(re.findall(r"\d+", text))
    whitespace_blocks = len(re.findall(r"\s+", text))

    # Rough estimation based on tokenizer behavior
    return words + punctuation + whitespace_blocks


def compare_formats(data: dict, name: str = "Sample") -> dict:
    """Compare token usage across JSON, TOON, and TRON formats."""

    # Generate all formats
    json_str = json.dumps(data, indent=2)
    json_compact = json.dumps(data, separators=(",", ":"))
    toon_str = toon_encode(data)
    tron_str = tron_encode(data)

    # Calculate metrics
    results = {
        "name": name,
        "formats": {
            "JSON (pretty)": {
                "text": json_str,
                "chars": len(json_str),
                "lines": json_str.count("\n") + 1,
                "tokens_est": estimate_tokens(json_str),
            },
            "JSON (compact)": {
                "text": json_compact,
                "chars": len(json_compact),
                "lines": 1,
                "tokens_est": estimate_tokens(json_compact),
            },
            "TOON": {
                "text": toon_str,
                "chars": len(toon_str),
                "lines": toon_str.count("\n") + 1,
                "tokens_est": estimate_tokens(toon_str),
            },
            "TRON": {
                "text": tron_str,
                "chars": len(tron_str),
                "lines": tron_str.count("\n") + 1,
                "tokens_est": estimate_tokens(tron_str),
            },
        },
    }

    # Calculate savings vs JSON pretty
    json_tokens = results["formats"]["JSON (pretty)"]["tokens_est"]
    for fmt, data in results["formats"].items():
        if fmt != "JSON (pretty)":
            savings = ((json_tokens - data["tokens_est"]) / json_tokens) * 100
            data["savings_vs_json"] = savings

    return results


def print_comparison(results: dict):
    """Print a formatted comparison table."""
    print(f"\n{'='*70}")
    print(f"Dataset: {results['name']}")
    print("=" * 70)

    # Header
    print(f"\n{'Format':<18} {'Chars':>10} {'Lines':>8} {'Tokens':>10} {'Savings':>12}")
    print("-" * 60)

    for fmt, data in results["formats"].items():
        savings = data.get("savings_vs_json", 0)
        savings_str = f"{savings:+.1f}%" if savings != 0 else "baseline"
        print(
            f"{fmt:<18} {data['chars']:>10,} {data['lines']:>8} {data['tokens_est']:>10,} {savings_str:>12}"
        )

    print()


def print_format_samples(results: dict, max_lines: int = 10):
    """Print sample output from each format."""
    print(f"\n{'='*70}")
    print("FORMAT SAMPLES (first 10 lines each)")
    print("=" * 70)

    for fmt, data in results["formats"].items():
        print(f"\n### {fmt}:")
        lines = data["text"].split("\n")[:max_lines]
        for line in lines:
            print(f"  {line}")
        if len(data["text"].split("\n")) > max_lines:
            print(f"  ... ({data['lines'] - max_lines} more lines)")


# Sample datasets for comparison
SAMPLE_DATASETS = {
    "simple_object": {
        "name": "Simple Object",
        "data": {"name": "John Doe", "age": 30, "email": "john@example.com", "active": True},
    },
    "nested_object": {
        "name": "Nested Object",
        "data": {
            "user": {
                "profile": {
                    "name": "Alice Smith",
                    "location": {"city": "New York", "country": "USA"},
                },
                "settings": {"theme": "dark", "notifications": True},
            }
        },
    },
    "array_data": {
        "name": "Array Data",
        "data": {
            "products": [
                {"id": 1, "name": "Laptop", "price": 999.99},
                {"id": 2, "name": "Mouse", "price": 29.99},
                {"id": 3, "name": "Keyboard", "price": 79.99},
                {"id": 4, "name": "Monitor", "price": 399.99},
                {"id": 5, "name": "Headphones", "price": 149.99},
            ]
        },
    },
    "rag_context": {
        "name": "RAG Context (FAQ)",
        "data": {
            "documents": [
                {
                    "id": "faq-001",
                    "category": "returns",
                    "question": "What is your return policy?",
                    "answer": "You can return items within 30 days of purchase for a full refund.",
                    "metadata": {"views": 1250, "helpful": 892},
                },
                {
                    "id": "faq-002",
                    "category": "shipping",
                    "question": "How long does shipping take?",
                    "answer": "Standard shipping takes 5-7 business days. Express shipping is 2-3 days.",
                    "metadata": {"views": 2100, "helpful": 1567},
                },
                {
                    "id": "faq-003",
                    "category": "payment",
                    "question": "What payment methods do you accept?",
                    "answer": "We accept Visa, MasterCard, American Express, PayPal, and Apple Pay.",
                    "metadata": {"views": 890, "helpful": 654},
                },
            ]
        },
    },
    "api_response": {
        "name": "API Response",
        "data": {
            "status": "success",
            "code": 200,
            "data": {
                "users": [
                    {
                        "id": "usr_123",
                        "username": "alice",
                        "email": "alice@example.com",
                        "role": "admin",
                        "permissions": ["read", "write", "delete", "admin"],
                    },
                    {
                        "id": "usr_456",
                        "username": "bob",
                        "email": "bob@example.com",
                        "role": "user",
                        "permissions": ["read", "write"],
                    },
                ],
                "pagination": {"page": 1, "per_page": 10, "total": 2, "total_pages": 1},
            },
            "timestamp": "2025-12-01T10:30:00Z",
        },
    },
    "config_file": {
        "name": "Configuration File",
        "data": {
            "app": {"name": "MyApplication", "version": "2.0.0", "environment": "production"},
            "database": {
                "host": "db.example.com",
                "port": 5432,
                "name": "myapp_prod",
                "pool_size": 20,
                "ssl": True,
            },
            "cache": {
                "enabled": True,
                "ttl": 3600,
                "provider": "redis",
                "host": "cache.example.com",
            },
            "logging": {
                "level": "info",
                "format": "json",
                "outputs": ["console", "file", "syslog"],
            },
        },
    },
}


def run_all_comparisons():
    """Run comparisons on all sample datasets."""
    print("\n" + "=" * 70)
    print("TOKEN COMPARISON: JSON vs TOON vs TRON")
    print("=" * 70)

    all_results = []
    totals = {
        "JSON (pretty)": {"chars": 0, "tokens": 0},
        "JSON (compact)": {"chars": 0, "tokens": 0},
        "TOON": {"chars": 0, "tokens": 0},
        "TRON": {"chars": 0, "tokens": 0},
    }

    for key, sample in SAMPLE_DATASETS.items():
        results = compare_formats(sample["data"], sample["name"])
        all_results.append(results)
        print_comparison(results)

        # Accumulate totals
        for fmt, data in results["formats"].items():
            totals[fmt]["chars"] += data["chars"]
            totals[fmt]["tokens"] += data["tokens_est"]

    # Print totals
    print("\n" + "=" * 70)
    print("TOTALS ACROSS ALL DATASETS")
    print("=" * 70)

    json_tokens = totals["JSON (pretty)"]["tokens"]
    print(f"\n{'Format':<18} {'Total Chars':>12} {'Total Tokens':>14} {'Savings':>12}")
    print("-" * 60)

    for fmt, data in totals.items():
        if fmt == "JSON (pretty)":
            savings_str = "baseline"
        else:
            savings = ((json_tokens - data["tokens"]) / json_tokens) * 100
            savings_str = f"{savings:+.1f}%"
        print(f"{fmt:<18} {data['chars']:>12,} {data['tokens']:>14,} {savings_str:>12}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    toon_savings = ((json_tokens - totals["TOON"]["tokens"]) / json_tokens) * 100
    tron_savings = ((json_tokens - totals["TRON"]["tokens"]) / json_tokens) * 100

    print(
        f"""
Key Findings:
  • TOON saves {toon_savings:.1f}% tokens compared to JSON (pretty)
  • TRON saves {tron_savings:.1f}% tokens compared to JSON (pretty)
  • JSON compact is ~{((json_tokens - totals['JSON (compact)']['tokens']) / json_tokens) * 100:.1f}% smaller than JSON pretty

Cost Implications (at $0.01/1K tokens):
  • JSON (pretty): ${totals['JSON (pretty)']['tokens'] * 0.00001:.4f} per batch
  • TOON:          ${totals['TOON']['tokens'] * 0.00001:.4f} per batch
  • TRON:          ${totals['TRON']['tokens'] * 0.00001:.4f} per batch

For 1 million requests:
  • JSON cost:  ${totals['JSON (pretty)']['tokens'] * 0.01:.2f}
  • TOON cost:  ${totals['TOON']['tokens'] * 0.01:.2f} (saves ${(totals['JSON (pretty)']['tokens'] - totals['TOON']['tokens']) * 0.01:.2f})
  • TRON cost:  ${totals['TRON']['tokens'] * 0.01:.2f} (saves ${(totals['JSON (pretty)']['tokens'] - totals['TRON']['tokens']) * 0.01:.2f})
"""
    )

    return all_results


def show_format_examples():
    """Show detailed format examples."""
    print("\n" + "=" * 70)
    print("FORMAT EXAMPLES")
    print("=" * 70)

    sample = SAMPLE_DATASETS["rag_context"]
    results = compare_formats(sample["data"], sample["name"])
    print_format_samples(results, max_lines=20)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Token comparison tool for TOON/TRON vs JSON")
    parser.add_argument("--examples", action="store_true", help="Show format examples")
    parser.add_argument(
        "--dataset", choices=list(SAMPLE_DATASETS.keys()), help="Run comparison on specific dataset"
    )
    args = parser.parse_args()

    if args.examples:
        show_format_examples()
    elif args.dataset:
        sample = SAMPLE_DATASETS[args.dataset]
        results = compare_formats(sample["data"], sample["name"])
        print_comparison(results)
        print_format_samples(results)
    else:
        run_all_comparisons()
        print("\nRun with --examples to see format samples")
        print("Run with --dataset <name> to analyze a specific dataset")
