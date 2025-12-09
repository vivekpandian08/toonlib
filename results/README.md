# Results

Benchmark results and performance comparisons for TOONSTREAM v2.0.0.

## Formats Compared

| Format | Description |
|--------|-------------|
| **JSON** | Standard JSON with indentation (pretty-printed) |
| **JSON Compact** | Minified JSON (no whitespace) |
| **TOON** | Token-Optimized Object Notation (tabular format) |
| **TRON** | Token Reduced Object Notation (ultra-compact syntax) |

## Latest Benchmark Results

### Using tiktoken (GPT-3.5/GPT-4 Tokenizer - cl100k_base)

| Dataset | JSON | Compact | TOON | TRON | TRON Savings |
|---------|------|---------|------|------|--------------|
| Simple Object (5 fields) | 41 | 26 | 28 | **24** | +41.5% |
| Employee Records (5 rows) | 168 | 88 | 56 | **52** | +69.0% |
| User Records (20 rows) | 842 | 482 | **252** | 288 | +65.8% |
| Nested Object (2 levels) | 58 | 29 | 38 | **27** | +53.4% |
| Mixed Structure | 81 | 40 | 33 | **28** | +65.4% |
| Products (50 rows) | 2,116 | 1,216 | **677** | 723 | +65.8% |
| **TOTAL** | **3,306** | **1,881** | **1,084** | **1,142** | **+65.5%** |

### Overall Token Savings (GPT-3.5/GPT-4)

| Comparison | Savings |
|------------|---------|
| JSON Compact vs JSON | 43.1% fewer tokens |
| **TOON vs JSON** | **67.2% fewer tokens** |
| TOON vs JSON Compact | 42.4% fewer tokens |
| **TRON vs JSON** | **65.5% fewer tokens** |
| TRON vs JSON Compact | 39.3% fewer tokens |
| TRON vs TOON | -5.4% fewer tokens |

## Best Format for Each Use Case

| Use Case | Best Format | Why |
|----------|-------------|-----|
| **Human readability** | JSON | Indentation and spacing for easy reading |
| **Config files** | JSON | Standard format, editor support |
| **Network/API transmission** | JSON Compact | Widely supported, minimal size |
| **Large tabular data** (100+ rows) | TOON | 40-47% savings on repeated structures |
| **Employee/user records** | TOON | Tabular format excels at homogeneous arrays |
| **Simple key-value objects** | TRON | 40%+ savings, minimal punctuation |
| **Nested configurations** | TRON | Dot notation: `user.profile.name=Alice` |
| **Mixed structures** | TRON | 65% savings on complex nested+array data |
| **LLM context optimization** | TOON/TRON | Both save 65-70% tokens vs JSON |
| **Streaming to LLMs** | TRON | Single-line format, easy to parse |
| **ML model configs** | TRON | Compact nested structure support |
| **Database exports** | TOON | CSV-like tabular format |
| **Logging/telemetry** | TRON | Minimal overhead per record |

## Quick Decision Guide

```
Is human readability critical?
  └─ YES → JSON (pretty)
  └─ NO → Continue...

Is it tabular data (array of similar objects)?
  └─ YES, large (50+ rows) → TOON (best compression)
  └─ YES, small (<50 rows) → TRON (simpler syntax)
  └─ NO → Continue...

Is it nested/hierarchical data?
  └─ YES → TRON (dot notation is efficient)
  └─ NO → Continue...

Simple flat object?
  └─ YES → TRON (most compact)
  └─ NO → JSON Compact (safest fallback)
```

## When to Use Each Format

| Format | Best For |
|--------|----------|
| **JSON** | Human readability, debugging |
| **JSON Compact** | Network transmission, storage |
| **TOON** | Large tabular datasets (many rows) |
| **TRON** | Simple objects, nested structures, minimal tokens |

## Files

- `comparison_results_*.json` - JSON format results from benchmark runs
- `comparison_results_*.md` - Human-readable markdown reports

## Regenerating Results

```bash
# With GPT-2 (open source) tokenizer
python benchmarks/compare_tron_formats.py --tokenizer gpt2

# With GPT-4 tokenizer (requires tiktoken)
python benchmarks/compare_tron_formats.py --tokenizer gpt4

# List available tokenizers
python benchmarks/compare_tron_formats.py --list-tokenizers
```
