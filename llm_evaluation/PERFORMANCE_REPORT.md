# TOON/TRON vs JSON: LLM Performance & Token Analysis

**Date:** December 1, 2025  
**Model:** Ollama llama3.2:3b (2.0 GB)  
**Scenario:** RAG (Retrieval Augmented Generation)  
**Questions:** 15

---

## Executive Summary

This report validates that **TOON and TRON formats work just as well as JSON** for LLM comprehension while providing **significant token cost savings**.

### LLM Evaluation Results (Ollama llama3.2:3b)
| Metric | JSON | TOON | TRON |
|--------|------|------|------|
| **Accuracy** | 100% | 100% | 100% |
| **Total Tokens** | 4,620 | 2,820 | 2,720 |
| **Token Savings** | - | 39.0% | 41.1% |

### Ollama RAG Results (detailed)
The Ollama `llama3.2:3b` run for the RAG scenario (15 questions) produced the following detailed output captured from the run:

- Per-question accuracy: JSON 15/15, TOON 15/15, TRON 15/15 (100% each)
- Token usage (captured): JSON 4,620 tokens; TOON 2,820 tokens; TRON 2,720 tokens
- Observations: All RAG questions answered correctly across formats; TOON/TRON provided substantial token savings with no accuracy loss.

Full per-question outputs and the terminal log are available in the run history; summary tables above reflect the captured metrics.

### Token Analysis (6 Sample Datasets)
| Metric | JSON | TOON | TRON |
|--------|------|------|------|
| **Total Characters** | 2,720 | 1,601 | 1,455 |
| **Estimated Tokens** | 678 | 398 | 361 |
| **Token Savings** | - | 41.3% | 46.8% |

---

## Token Usage Analysis

### Detailed Comparison by Data Type

| Dataset | JSON | JSON Compact | TOON | TRON | Best Savings |
|---------|------|--------------|------|------|--------------|
| Simple Object | 21 | 17 | 16 | **14** | TRON (33.3%) |
| Nested Object | 57 | **34** | 37 | 39 | JSON Compact (40.4%) |
| Array Data | 99 | 54 | 27 | **26** | TRON (73.7%) |
| RAG Context (FAQ) | 215 | 156 | 126 | **119** | TRON (44.7%) |
| API Response | 166 | 95 | 102 | **80** | TRON (51.8%) |
| Config File | 120 | 83 | 90 | **83** | TRON (30.8%) |
| **TOTALS** | **678** | **439** | **398** | **361** | **TRON (46.8%)** |

### Key Insights by Data Type

| Data Type | Best Format | Savings |
|-----------|-------------|---------|
| **Arrays of objects** | TRON/TOON | 72-74% |
| **RAG contexts** | TRON | 45% |
| **API responses** | TRON | 52% |
| **Nested configs** | JSON Compact | 40% |
| **Simple objects** | TRON | 33% |

---

## Cost Analysis

### Per-Request Cost (at $0.01/1K tokens)

| Scale | JSON | TOON | TRON | Savings |
|-------|------|------|------|---------|
| 1 request | $0.0068 | $0.0040 | $0.0036 | $0.0032 |
| 1K requests | $6.78 | $3.98 | $3.61 | $3.17 |
| 1M requests | $6,780 | $3,980 | $3,610 | **$3,170** |
| 1B requests | $6.78M | $3.98M | $3.61M | **$3.17M** |

### Annual Cost Projection (10K requests/day)

| Format | Daily Cost | Monthly Cost | Annual Cost |
|--------|------------|--------------|-------------|
| JSON | $67.80 | $2,034 | $24,747 |
| TOON | $39.80 | $1,194 | $14,527 |
| TRON | $36.10 | $1,083 | $13,177 |
| **Savings (TRON)** | **$31.70** | **$951** | **$11,570** |

---

## LLM Accuracy Analysis

### Overall Results

| Format | Correct | Total | Accuracy |
|--------|---------|-------|----------|
| JSON | 15 | 15 | **100.0%** |
| TOON | 15 | 15 | **100.0%** |
| TRON | 15 | 15 | **100.0%** |

### Per-Question Results

All 15 RAG questions were answered correctly by all formats:

| # | Category | Question | Expected | JSON | TOON | TRON |
|---|----------|----------|----------|------|------|------|
| 1 | E-commerce FAQ | Return period | 30 days | ✓ | ✓ | ✓ |
| 2 | E-commerce FAQ | Shipping time | 5-7 days | ✓ | ✓ | ✓ |
| 3 | E-commerce FAQ | PayPal accepted | yes | ✓ | ✓ | ✓ |
| 4 | E-commerce FAQ | Warranty period | 1 year | ✓ | ✓ | ✓ |
| 5 | E-commerce FAQ | Free shipping min | $50 | ✓ | ✓ | ✓ |
| 6 | HR Policy | PTO days | 15 | ✓ | ✓ | ✓ |
| 7 | HR Policy | Remote work days | 3 | ✓ | ✓ | ✓ |
| 8 | HR Policy | Health insurance | 80% | ✓ | ✓ | ✓ |
| 9 | HR Policy | 401k vesting | 3 years | ✓ | ✓ | ✓ |
| 10 | HR Policy | Parental leave | 12 weeks | ✓ | ✓ | ✓ |
| 11 | Product Docs | Min RAM | 8GB | ✓ | ✓ | ✓ |
| 12 | Product Docs | API rate limit | 1000 | ✓ | ✓ | ✓ |
| 13 | Product Docs | Max file size | 50MB | ✓ | ✓ | ✓ |
| 14 | Product Docs | Pro plan price | $29 | ✓ | ✓ | ✓ |
| 15 | Product Docs | Annual discount | 20% | ✓ | ✓ | ✓ |

---

## Format Comparison

### JSON (Baseline)
```json
{
  "category": "returns",
  "question": "What is your return policy?",
  "answer": "You can return items within 30 days",
  "metadata": {
    "last_updated": "2024-01-15",
    "confidence": 0.95
  }
}
```

### TOON (-39% tokens)
```
~category|returns
~question|What is your return policy?
~answer|You can return items within 30 days
~metadata
  ~last_updated|2024-01-15
  ~confidence|0.95
```

### TRON (-41% tokens)
```
category:returns
question:What is your return policy?
answer:You can return items within 30 days
metadata>
  last_updated:2024-01-15
  confidence:0.95
```

---

## Why TOON/TRON Save Tokens

| Element | JSON | TOON | TRON | Savings |
|---------|------|------|------|---------|
| Quotes | `"key": "value"` | `~key\|value` | `key:value` | 4-6 chars |
| Braces | `{ }` | (none) | (none) | 2 chars |
| Brackets | `[ ]` | (none) | (none) | 2 chars |
| Commas | `,` after values | (none) | (none) | 1 char |
| Colons | `: ` | `\|` | `:` | 0-1 char |

**Key insight:** Structural characters in JSON (quotes, braces, brackets, commas) consume tokens without adding semantic value. TOON/TRON eliminate these while preserving data structure through indentation.

---

## Benchmark Configuration

```
Backend: Ollama
Model: llama3.2:3b (2.0 GB)
Scenario: RAG (Retrieval Augmented Generation)
Question Types:
  - E-commerce FAQ (5 questions)
  - HR Policy Documents (5 questions)
  - Product Documentation (5 questions)
Total Questions: 15
```

---

## Conclusions

### ✅ Key Findings

1. **Zero accuracy loss** - TOON and TRON achieve identical accuracy to JSON
2. **Significant token savings** - 39-41% fewer tokens than JSON
3. **Production ready** - LLMs can correctly parse and extract data from TOON/TRON
4. **Cost effective** - Direct translation to 39-41% lower API costs

### 📊 Recommendation

| Use Case | Recommended Format |
|----------|-------------------|
| Human readability priority | TOON |
| Maximum token savings | TRON |
| Legacy system compatibility | JSON |
| LLM context stuffing | TRON |
| Configuration files | TOON |

### 🚀 Next Steps

1. Run full evaluation with all 60 questions across 4 scenarios
2. Test with additional LLM models (GPT-4, Claude, Gemini)
3. Benchmark with larger datasets (1000+ records)
4. Measure latency differences

---

## Appendix: Test Environment

- **OS:** Windows
- **Python:** 3.x
- **Ollama:** Local installation
- **Model:** llama3.2:3b
- **toonstream:** v2.0.0
