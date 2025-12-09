"""
Complex Benchmark: 45 diverse JSON examples
Tests JSON vs JSON Compact vs TOON vs TRON across various data patterns.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from token_counters import count_tokens as _count_tokens
from token_counters import get_tokenizer

from toonstream import encode

tokenizer = None


def count_tokens(text: str) -> int:
    global tokenizer
    return _count_tokens(text, tokenizer)


def benchmark_single(name: str, data, show_samples=False):
    """Benchmark a single dataset and return results."""
    # JSON (pretty)
    json_pretty = json.dumps(data, indent=2)
    json_pretty_tokens = count_tokens(json_pretty)

    # JSON Compact
    json_compact = json.dumps(data, separators=(",", ":"))
    json_compact_tokens = count_tokens(json_compact)

    # TOON
    try:
        toon_str = encode(data, format="toon")
        toon_tokens = count_tokens(toon_str)
        toon_ok = True
    except Exception:
        toon_str = ""
        toon_tokens = json_compact_tokens
        toon_ok = False

    # TRON
    try:
        tron_str = encode(data, format="tron")
        tron_tokens = count_tokens(tron_str)
        tron_ok = True
    except Exception:
        tron_str = ""
        tron_tokens = json_compact_tokens
        tron_ok = False

    # Find best format
    tokens = {
        "JSON": json_pretty_tokens,
        "Compact": json_compact_tokens,
        "TOON": toon_tokens,
        "TRON": tron_tokens,
    }
    best = min(tokens, key=tokens.get)

    if show_samples:
        print("\n  Sample outputs:")
        print(f"    JSON Compact: {json_compact[:80]}...")
        print(f"    TOON: {toon_str[:80]}..." if toon_ok else "    TOON: ERROR")
        print(f"    TRON: {tron_str[:80]}..." if tron_ok else "    TRON: ERROR")

    return {
        "name": name,
        "json_pretty": json_pretty_tokens,
        "json_compact": json_compact_tokens,
        "toon": toon_tokens,
        "tron": tron_tokens,
        "best": best,
        "savings_vs_json": (1 - min(toon_tokens, tron_tokens) / json_pretty_tokens) * 100,
    }


# ============================================================================
# 45 COMPLEX JSON EXAMPLES
# ============================================================================


def get_test_cases():
    """Generate 45 diverse test cases."""
    cases = []

    # Category 1: Simple Objects (5 cases)
    cases.append(
        (
            "1. Simple user",
            {
                "id": 12345,
                "username": "johndoe",
                "email": "john.doe@example.com",
                "verified": True,
                "age": 28,
            },
        )
    )

    cases.append(
        (
            "2. Product info",
            {
                "sku": "PRD-001-BLU",
                "name": "Wireless Headphones",
                "price": 79.99,
                "inStock": True,
                "quantity": 150,
            },
        )
    )

    cases.append(
        (
            "3. Location data",
            {
                "latitude": 40.7128,
                "longitude": -74.0060,
                "city": "New York",
                "country": "USA",
                "timezone": "America/New_York",
            },
        )
    )

    cases.append(
        (
            "4. API response",
            {
                "status": "success",
                "code": 200,
                "message": "Data retrieved successfully",
                "timestamp": "2025-12-01T10:30:00Z",
                "requestId": "req-abc123",
            },
        )
    )

    cases.append(
        (
            "5. Config simple",
            {
                "debug": False,
                "maxRetries": 3,
                "timeout": 30000,
                "logLevel": "info",
                "enabled": True,
            },
        )
    )

    # Category 2: Nested Objects (5 cases)
    cases.append(
        (
            "6. User profile",
            {
                "user": {
                    "name": "Alice Smith",
                    "contact": {"email": "alice@example.com", "phone": "+1-555-0123"},
                },
                "preferences": {"theme": "dark", "language": "en-US"},
            },
        )
    )

    cases.append(
        (
            "7. Company org",
            {
                "company": {
                    "name": "TechCorp Inc",
                    "headquarters": {
                        "address": "123 Tech Street",
                        "city": "San Francisco",
                        "state": "CA",
                    },
                },
                "employees": 500,
            },
        )
    )

    cases.append(
        (
            "8. API config",
            {
                "api": {
                    "baseUrl": "https://api.example.com",
                    "version": "v2",
                    "auth": {"type": "bearer", "tokenExpiry": 3600},
                },
                "retry": {"maxAttempts": 3, "backoff": "exponential"},
            },
        )
    )

    cases.append(
        (
            "9. Deep nested",
            {"level1": {"level2": {"level3": {"level4": {"value": "deep", "count": 42}}}}},
        )
    )

    cases.append(
        (
            "10. ML model config",
            {
                "model": {
                    "architecture": "transformer",
                    "layers": {
                        "encoder": {"heads": 8, "dim": 512},
                        "decoder": {"heads": 8, "dim": 512},
                    },
                },
                "training": {"optimizer": "adam", "lr": 0.001},
            },
        )
    )

    # Category 3: Arrays (5 cases)
    cases.append(
        (
            "11. String array",
            {"tags": ["python", "machine-learning", "nlp", "transformers", "pytorch"]},
        )
    )

    cases.append(("12. Number array", {"scores": [95, 87, 92, 78, 88, 91, 85, 93, 89, 90]}))

    cases.append(
        ("13. Mixed array", {"data": [1, "two", 3.0, True, None, "six", 7, False, 9.5, "ten"]})
    )

    cases.append(
        (
            "14. Boolean array",
            {"flags": [True, False, True, True, False, False, True, False, True, True]},
        )
    )

    cases.append(("15. Nested arrays", {"matrix": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]}))

    # Category 4: Tabular Data (10 cases)
    cases.append(
        (
            "16. Employees (10)",
            [
                {
                    "id": i,
                    "name": f"Employee{i}",
                    "dept": ["Eng", "Sales", "HR"][i % 3],
                    "salary": 50000 + i * 5000,
                }
                for i in range(1, 11)
            ],
        )
    )

    cases.append(
        (
            "17. Products (15)",
            [
                {
                    "sku": f"SKU-{i:04d}",
                    "name": f"Product {i}",
                    "price": 9.99 + i * 2,
                    "qty": i * 10,
                }
                for i in range(1, 16)
            ],
        )
    )

    cases.append(
        (
            "18. Orders (20)",
            [
                {
                    "orderId": f"ORD-{i:05d}",
                    "customer": f"Cust{i}",
                    "total": 99.99 + i * 10,
                    "status": ["pending", "shipped", "delivered"][i % 3],
                }
                for i in range(1, 21)
            ],
        )
    )

    cases.append(
        (
            "19. Users (25)",
            [
                {"id": i, "email": f"user{i}@mail.com", "active": i % 2 == 0, "score": i * 4}
                for i in range(1, 26)
            ],
        )
    )

    cases.append(
        (
            "20. Logs (30)",
            [
                {
                    "ts": f"2025-12-01T{10 + i // 60:02d}:{i % 60:02d}:00Z",
                    "level": ["INFO", "WARN", "ERROR"][i % 3],
                    "msg": f"Event {i}",
                }
                for i in range(30)
            ],
        )
    )

    cases.append(
        (
            "21. Metrics (50)",
            [
                {"t": i, "cpu": 20 + (i % 30), "mem": 40 + (i % 20), "disk": 60 + (i % 10)}
                for i in range(50)
            ],
        )
    )

    cases.append(
        (
            "22. Transactions (40)",
            [
                {
                    "txId": f"TX{i:06d}",
                    "amt": 10.50 + i * 1.5,
                    "type": ["credit", "debit"][i % 2],
                    "ts": f"2025-12-01T12:{i % 60:02d}:00Z",
                }
                for i in range(40)
            ],
        )
    )

    cases.append(
        (
            "23. Inventory (35)",
            [
                {
                    "item": f"Item-{i}",
                    "loc": f"W{(i % 5) + 1}",
                    "qty": 100 + i * 5,
                    "reorder": i * 2,
                }
                for i in range(35)
            ],
        )
    )

    cases.append(
        (
            "24. Events (45)",
            [
                {
                    "eventId": i,
                    "type": ["click", "view", "submit", "scroll"][i % 4],
                    "page": f"/page{i % 10}",
                    "duration": i * 100,
                }
                for i in range(45)
            ],
        )
    )

    cases.append(
        (
            "25. Sensors (60)",
            [
                {
                    "sensorId": f"S{i:03d}",
                    "temp": 20.0 + (i % 15),
                    "humidity": 40 + (i % 30),
                    "pressure": 1000 + i,
                }
                for i in range(60)
            ],
        )
    )

    # Category 5: Complex Mixed Structures (10 cases)
    cases.append(
        (
            "26. E-commerce order",
            {
                "orderId": "ORD-2025-12345",
                "customer": {
                    "name": "John Smith",
                    "email": "john@example.com",
                    "address": {"street": "123 Main St", "city": "Boston", "zip": "02101"},
                },
                "items": [
                    {"sku": "LAPTOP-001", "name": "Laptop Pro", "price": 1299.99, "qty": 1},
                    {"sku": "MOUSE-002", "name": "Wireless Mouse", "price": 49.99, "qty": 2},
                    {"sku": "KEYBD-003", "name": "Mechanical Keyboard", "price": 129.99, "qty": 1},
                ],
                "total": 1529.96,
                "status": "processing",
            },
        )
    )

    cases.append(
        (
            "27. Blog post",
            {
                "id": 1001,
                "title": "Introduction to Machine Learning",
                "author": {"id": 42, "name": "Dr. Jane Doe", "bio": "AI Researcher"},
                "content": "Machine learning is a subset of artificial intelligence...",
                "tags": ["AI", "ML", "tutorial", "beginner"],
                "comments": [
                    {"user": "reader1", "text": "Great article!", "likes": 15},
                    {"user": "reader2", "text": "Very helpful", "likes": 8},
                ],
                "published": True,
                "views": 5432,
            },
        )
    )

    cases.append(
        (
            "28. API paginated",
            {
                "data": [{"id": i, "value": f"item_{i}"} for i in range(1, 11)],
                "pagination": {"page": 1, "perPage": 10, "total": 100, "totalPages": 10},
                "meta": {"requestId": "req-xyz789", "timestamp": "2025-12-01T15:30:00Z"},
            },
        )
    )

    cases.append(
        (
            "29. Dashboard data",
            {
                "summary": {"totalUsers": 15234, "activeToday": 892, "revenue": 125678.50},
                "charts": {
                    "daily": [120, 135, 142, 128, 156, 167, 145],
                    "weekly": [850, 920, 880, 910],
                },
                "topProducts": [
                    {"name": "Product A", "sales": 1234},
                    {"name": "Product B", "sales": 987},
                    {"name": "Product C", "sales": 756},
                ],
                "alerts": [
                    {"level": "warning", "message": "Low inventory on SKU-123"},
                    {"level": "info", "message": "New feature deployed"},
                ],
            },
        )
    )

    cases.append(
        (
            "30. User session",
            {
                "sessionId": "sess-abc123xyz",
                "user": {
                    "id": 98765,
                    "username": "poweruser",
                    "roles": ["admin", "editor", "viewer"],
                    "permissions": {"read": True, "write": True, "delete": False},
                },
                "activity": [
                    {"action": "login", "ts": "2025-12-01T09:00:00Z"},
                    {"action": "view_dashboard", "ts": "2025-12-01T09:01:30Z"},
                    {"action": "edit_profile", "ts": "2025-12-01T09:05:45Z"},
                ],
                "expiresAt": "2025-12-01T21:00:00Z",
            },
        )
    )

    cases.append(
        (
            "31. ML training run",
            {
                "runId": "run-2025-001",
                "model": "bert-base-uncased",
                "hyperparameters": {
                    "learningRate": 0.00002,
                    "batchSize": 32,
                    "epochs": 10,
                    "warmupSteps": 500,
                },
                "metrics": [
                    {"epoch": 1, "loss": 0.823, "accuracy": 0.721},
                    {"epoch": 2, "loss": 0.654, "accuracy": 0.798},
                    {"epoch": 3, "loss": 0.521, "accuracy": 0.845},
                ],
                "status": "completed",
                "duration": 3600,
            },
        )
    )

    cases.append(
        (
            "32. IoT device data",
            {
                "deviceId": "IOT-SENSOR-001",
                "location": {"building": "HQ", "floor": 3, "room": "Server Room A"},
                "readings": [
                    {"ts": "2025-12-01T12:00:00Z", "temp": 22.5, "humidity": 45, "power": 1250},
                    {"ts": "2025-12-01T12:05:00Z", "temp": 22.7, "humidity": 44, "power": 1280},
                    {"ts": "2025-12-01T12:10:00Z", "temp": 23.0, "humidity": 43, "power": 1320},
                ],
                "alerts": [],
                "status": "online",
            },
        )
    )

    cases.append(
        (
            "33. Survey response",
            {
                "surveyId": "SRV-2025-Q4",
                "respondent": {
                    "id": "R12345",
                    "demographic": {"age": "25-34", "region": "Northeast"},
                },
                "answers": [
                    {"q": 1, "response": "Strongly Agree", "score": 5},
                    {"q": 2, "response": "Agree", "score": 4},
                    {"q": 3, "response": "Neutral", "score": 3},
                    {"q": 4, "response": "Disagree", "score": 2},
                    {"q": 5, "response": "Strongly Agree", "score": 5},
                ],
                "completedAt": "2025-12-01T14:22:30Z",
            },
        )
    )

    cases.append(
        (
            "34. Recipe data",
            {
                "name": "Chocolate Chip Cookies",
                "prepTime": 15,
                "cookTime": 12,
                "servings": 24,
                "ingredients": [
                    {"item": "flour", "amount": 2.25, "unit": "cups"},
                    {"item": "butter", "amount": 1, "unit": "cup"},
                    {"item": "sugar", "amount": 0.75, "unit": "cups"},
                    {"item": "eggs", "amount": 2, "unit": "large"},
                    {"item": "chocolate chips", "amount": 2, "unit": "cups"},
                ],
                "instructions": [
                    "Preheat oven to 375°F",
                    "Mix dry ingredients",
                    "Cream butter and sugar",
                    "Combine and bake",
                ],
                "nutrition": {"calories": 150, "fat": 7, "carbs": 20},
            },
        )
    )

    cases.append(
        (
            "35. Flight booking",
            {
                "bookingRef": "ABC123",
                "passenger": {
                    "name": "Alice Johnson",
                    "passport": "X12345678",
                    "nationality": "USA",
                },
                "flights": [
                    {
                        "flight": "AA100",
                        "from": "JFK",
                        "to": "LAX",
                        "dep": "2025-12-15T08:00",
                        "arr": "2025-12-15T11:30",
                    },
                    {
                        "flight": "AA201",
                        "from": "LAX",
                        "to": "JFK",
                        "dep": "2025-12-20T14:00",
                        "arr": "2025-12-20T22:30",
                    },
                ],
                "class": "Economy",
                "price": 450.00,
                "status": "confirmed",
            },
        )
    )

    # Category 6: Edge Cases and Special Patterns (10 cases)
    cases.append(
        (
            "36. Unicode text",
            {
                "greeting": "Hello, 世界! 🌍",
                "languages": ["English", "中文", "日本語", "한국어", "العربية"],
                "emoji": "🚀💻🎉✨🔥",
            },
        )
    )

    cases.append(
        (
            "37. Large numbers",
            {
                "bigInt": 9007199254740991,
                "scientific": 1.23e10,
                "precise": 3.141592653589793,
                "negative": -999999999,
                "zero": 0,
            },
        )
    )

    cases.append(
        (
            "38. Empty structures",
            {
                "emptyObject": {},
                "emptyArray": [],
                "emptyString": "",
                "nullValue": None,
                "hasData": True,
            },
        )
    )

    cases.append(
        (
            "39. Long strings",
            {
                "description": "This is a very long description that contains multiple sentences. "
                * 5,
                "shortKey": "x",
                "mediumText": "A medium length text field with some content",
            },
        )
    )

    cases.append(
        (
            "40. Special chars",
            {
                "path": "C:\\Users\\Admin\\Documents",
                "url": "https://example.com/path?query=value&other=123",
                "regex": "^[a-zA-Z0-9]+$",
                "json_in_string": '{"nested":"json"}',
            },
        )
    )

    cases.append(
        (
            "41. Boolean heavy",
            {
                "feature1": True,
                "feature2": False,
                "feature3": True,
                "feature4": False,
                "feature5": True,
                "feature6": True,
                "feature7": False,
                "feature8": True,
                "feature9": False,
                "feature10": True,
            },
        )
    )

    cases.append(
        (
            "42. Null heavy",
            {
                "field1": None,
                "field2": "value",
                "field3": None,
                "field4": 123,
                "field5": None,
                "field6": True,
                "field7": None,
                "field8": None,
                "field9": "data",
                "field10": None,
            },
        )
    )

    cases.append(
        (
            "43. Deeply nested array",
            {
                "data": [
                    [[[1, 2], [3, 4]], [[5, 6], [7, 8]]],
                    [[[9, 10], [11, 12]], [[13, 14], [15, 16]]],
                ]
            },
        )
    )

    cases.append(("44. Wide object (20 keys)", {f"key{i}": f"value{i}" for i in range(1, 21)}))

    cases.append(
        (
            "45. Real-world API",
            {
                "status": "success",
                "data": {
                    "users": [
                        {
                            "id": i,
                            "name": f"User {i}",
                            "email": f"user{i}@company.com",
                            "role": ["admin", "user", "guest"][i % 3],
                        }
                        for i in range(1, 11)
                    ],
                    "total": 10,
                    "hasMore": True,
                },
                "meta": {
                    "version": "2.0.0",
                    "requestId": "req-abcd1234",
                    "timestamp": "2025-12-01T16:45:00Z",
                    "server": "api-server-01",
                },
            },
        )
    )

    return cases


def main():
    global tokenizer

    parser = argparse.ArgumentParser(description="Complex JSON Benchmark (45 examples)")
    parser.add_argument(
        "--tokenizer",
        "-t",
        choices=["auto", "gpt4", "gpt2", "char"],
        default="gpt4",
        help="Tokenizer to use (default: gpt4/tiktoken)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Show sample outputs")
    args = parser.parse_args()

    tokenizer = get_tokenizer(args.tokenizer)

    print("=" * 100)
    print("    TOONSTREAM v2.0.0 - COMPLEX BENCHMARK (45 Examples)")
    print("    JSON vs JSON Compact vs TOON vs TRON")
    print("=" * 100)
    print(f"\nTokenizer: {tokenizer.name} ({tokenizer.model})")
    print()

    cases = get_test_cases()
    results = []

    # Category summaries
    categories = {
        "Simple Objects (1-5)": [],
        "Nested Objects (6-10)": [],
        "Arrays (11-15)": [],
        "Tabular Data (16-25)": [],
        "Complex Mixed (26-35)": [],
        "Edge Cases (36-45)": [],
    }

    print(
        f"{'#':<4} {'Test Case':<30} {'JSON':>8} {'Compact':>8} {'TOON':>8} {'TRON':>8} {'Best':>8} {'Savings':>8}"
    )
    print("-" * 100)

    for i, (name, data) in enumerate(cases, 1):
        result = benchmark_single(name, data, args.verbose)
        results.append(result)

        # Assign to category
        if i <= 5:
            categories["Simple Objects (1-5)"].append(result)
        elif i <= 10:
            categories["Nested Objects (6-10)"].append(result)
        elif i <= 15:
            categories["Arrays (11-15)"].append(result)
        elif i <= 25:
            categories["Tabular Data (16-25)"].append(result)
        elif i <= 35:
            categories["Complex Mixed (26-35)"].append(result)
        else:
            categories["Edge Cases (36-45)"].append(result)

        savings = f"+{result['savings_vs_json']:.1f}%"
        print(
            f"{i:<4} {result['name']:<30} {result['json_pretty']:>8} {result['json_compact']:>8} {result['toon']:>8} {result['tron']:>8} {result['best']:>8} {savings:>8}"
        )

    # Category Summary
    print("\n" + "=" * 100)
    print("CATEGORY SUMMARY")
    print("=" * 100)

    print(
        f"\n{'Category':<30} {'JSON':>10} {'Compact':>10} {'TOON':>10} {'TRON':>10} {'Best Format':>12}"
    )
    print("-" * 84)

    for cat_name, cat_results in categories.items():
        json_sum = sum(r["json_pretty"] for r in cat_results)
        compact_sum = sum(r["json_compact"] for r in cat_results)
        toon_sum = sum(r["toon"] for r in cat_results)
        tron_sum = sum(r["tron"] for r in cat_results)

        tokens = {"JSON": json_sum, "Compact": compact_sum, "TOON": toon_sum, "TRON": tron_sum}
        best = min(tokens, key=tokens.get)

        print(
            f"{cat_name:<30} {json_sum:>10} {compact_sum:>10} {toon_sum:>10} {tron_sum:>10} {best:>12}"
        )

    # Overall Summary
    print("\n" + "=" * 100)
    print("OVERALL SUMMARY")
    print("=" * 100)

    total_json = sum(r["json_pretty"] for r in results)
    total_compact = sum(r["json_compact"] for r in results)
    total_toon = sum(r["toon"] for r in results)
    total_tron = sum(r["tron"] for r in results)

    print("\nTotal Tokens Across 45 Examples:")
    print(f"  JSON (pretty):   {total_json:>8,} tokens")
    print(f"  JSON Compact:    {total_compact:>8,} tokens")
    print(f"  TOON:            {total_toon:>8,} tokens")
    print(f"  TRON:            {total_tron:>8,} tokens")

    print("\n📊 TOKEN SAVINGS:")
    print(f"  JSON Compact vs JSON: {(1 - total_compact/total_json)*100:.1f}% fewer tokens")
    print(f"  TOON vs JSON:         {(1 - total_toon/total_json)*100:.1f}% fewer tokens")
    print(f"  TOON vs JSON Compact: {(1 - total_toon/total_compact)*100:.1f}% fewer tokens")
    print(f"  TRON vs JSON:         {(1 - total_tron/total_json)*100:.1f}% fewer tokens")
    print(f"  TRON vs JSON Compact: {(1 - total_tron/total_compact)*100:.1f}% fewer tokens")

    # Best format count
    best_counts = {"JSON": 0, "Compact": 0, "TOON": 0, "TRON": 0}
    for r in results:
        best_counts[r["best"]] += 1

    print("\n🏆 BEST FORMAT BY COUNT (out of 45):")
    for fmt, count in sorted(best_counts.items(), key=lambda x: -x[1]):
        pct = count / 45 * 100
        bar = "█" * int(pct / 5)
        print(f"  {fmt:<8}: {count:>2} wins ({pct:>5.1f}%) {bar}")

    print("\n" + "=" * 100)
    print("    BENCHMARK COMPLETE")
    print("=" * 100)


if __name__ == "__main__":
    main()
