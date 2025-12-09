# 🎨 ToonStream

**Token-Oriented Object Notation (TOON) & Token Reduced Object Notation (TRON) - Reduce LLM token usage by up to 73% with lossless data serialization**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-2.0.0-brightgreen.svg)](https://github.com/vivekpandian08/toonstream/releases/tag/v2.0.0)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-186%2F186-brightgreen.svg)](tests/)

---

## 📖 What is ToonStream?

**ToonStream** is a Python library for encoding structured data in a token-efficient format designed for Large Language Models (LLMs). It converts repetitive JSON structures into compact, tabular representations that dramatically reduce token count while maintaining 100% lossless conversion.

### The Problem

LLMs charge by tokens. Verbose JSON wastes tokens and money:

```json
[
  {"id": 1, "name": "Alice", "dept": "Engineering", "salary": 95000},
  {"id": 2, "name": "Bob", "dept": "Sales", "salary": 75000},
  {"id": 3, "name": "Carol", "dept": "Engineering", "salary": 105000}
]
```
**Cost:** 80 tokens

### The Solution

**TOON format** eliminates redundancy:

```
employees[3]{id,name,dept,salary}:
1,Alice,Engineering,95000
2,Bob,Sales,75000
3,Carol,Engineering,105000
```
**Cost:** 38 tokens (**-52.5%** reduction)

**TRON format** (NEW in v2.0.0) - ultra-compact:

```
@id,name,dept,salary|1,Alice,Engineering,95000|2,Bob,Sales,75000|3,Carol,Engineering,105000
```
**Cost:** 28 tokens (**-65%** reduction)

### Why ToonStream?

✅ **Save Money** - Reduce API costs by up to 73% on structured data  
✅ **Two Formats** - TOON (tabular) and TRON (ultra-compact)  
✅ **100% Lossless** - Perfect round-trip conversion, no data loss  
✅ **Zero Dependencies** - Pure Python, no external packages required  
✅ **Fast** - Sub-millisecond encoding/decoding  
✅ **Smart** - Automatic optimization, only improves when beneficial  
✅ **Simple API** - `encode(data, format='tron')` and `decode(data, format='tron')`  

---

## 🚀 Installation

```bash
pip install toonstream
```

Or from source:

```bash
git clone https://github.com/vivekpandian08/toonstream.git
cd toonstream
pip install -e .
```

**Requirements:**
- Python 3.8 or higher
- No external dependencies (tiktoken optional for benchmarks)

### Basic Usage

```python
import toonstream

# Your data
data = {
    "name": "Alice",
    "age": 30,
    "skills": ["Python", "JavaScript", "SQL"]
}

# Encode to TOON
toon_str = toonstream.encode(data)
print(toon_str)
```

**Output:**
```
name: "Alice"
age: 30
skills: [
  - "Python"
  - "JavaScript"
  - "SQL"
]
```

## 🖥️ CLI Tool

ToonStream includes a command-line interface for easy file conversion.

```bash
# Convert JSON to TOON (default)
toonstream encode input.json -o output.toon

# Convert JSON to TRON
toonstream encode input.json --format tron -o output.tron

# Decode TOON/TRON back to JSON
toonstream decode output.toon -o restored.json
```

---

## ⚡ Quick Start

### TOON Format (Tabular)

```python
from toonstream import encode, decode

# Your data
data = {
    "employees": [
        {"id": 1, "name": "Alice", "dept": "Engineering"},
        {"id": 2, "name": "Bob", "dept": "Sales"},
        {"id": 3, "name": "Carol", "dept": "Engineering"}
    ]
}

# Encode to TOON format (default)
toon_str = encode(data)
print(toon_str)
# Output:
# employees[3]{id,name,dept}:
# 1,Alice,Engineering
# 2,Bob,Sales
# 3,Carol,Engineering

# Decode back to Python
decoded = decode(toon_str)
assert decoded == data  # ✓ Perfect round-trip!
```

### TRON Format (Ultra-Compact) - NEW in v2.0.0

```python
from toonstream import encode, decode

# Simple object
data = {"name": "Alice", "age": 30, "active": True}

# Encode to TRON format
tron_str = encode(data, format='tron')
print(tron_str)
# Output: name=Alice;age=30;active=1

# Nested objects use dot notation
nested = {"user": {"profile": {"name": "Bob", "city": "NYC"}}}
print(encode(nested, format='tron'))
# Output: user.profile.name=Bob;user.profile.city=NYC

# Tabular data uses @header|row format
employees = [
    {"id": 1, "name": "Alice", "dept": "Engineering"},
    {"id": 2, "name": "Bob", "dept": "Sales"},
]
print(encode(employees, format='tron'))
# Output: @id,name,dept|1,Alice,Engineering|2,Bob,Sales

# Decode TRON back to Python
decoded = decode(tron_str, format='tron')
assert decoded == data  # ✓ Perfect round-trip!
```

### Smart Mode Selection with `auto_mode`

**New in v1.1.0:** Single parameter for intelligent mode detection

```python
# Auto mode - automatically detects tensor data
toon_str = encode(data, auto_mode=True)
decoded = decode(toon_str, auto_mode=True)

# With PyTorch tensors (auto_mode detects and preserves them)
import torch
data_with_tensors = {
    'embeddings': torch.randn(10, 768),
    'labels': [0, 1, 0],
    'metadata': {'model': 'bert-base'}
}

# auto_mode automatically handles tensor serialization
encoded = encode(data_with_tensors, auto_mode=True)
decoded = decode(encoded, auto_mode=True)
# ✓ Tensors preserved with metadata (dtype, device, shape)
```

### Advanced Options

```python
# Compact mode (minimize whitespace)
compact = encode(data, compact=True)

# Disable smart optimization (always use tabular)
always_tabular = encode(data, smart_optimize=False)

# Pretty print with indentation
pretty = encode(data, indent=2)

# Sort dictionary keys
sorted_output = encode(data, sort_keys=True)

# Combine with auto_mode
combined = encode(data, auto_mode=True, compact=True)
```

---

## 🤔 Which Format Should I Use?

| Feature | JSON | TOON | TRON |
| :--- | :---: | :---: | :---: |
| **Human Readable** | ⭐⭐⭐ | ⭐⭐ | ⭐ |
| **Token Efficiency** | ⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Parsing Speed** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Typical Savings** | 0% | 40-55% | 50-70% |

### 📋 JSON
**Use when:**
*   Human readability is the #1 priority.
*   Debugging raw payloads manually.
*   Interoperating with systems that strictly require JSON.

### 📊 TOON (Tabular)
**Use when:**
*   You have **lists of objects** (e.g., database rows, logs, CSV-like data).
*   You want significant compression but still want to be able to read the data reasonably well.
*   *Example:* User lists, product catalogs, transaction histories.

### 🚀 TRON (Compact)
**Use when:**
*   **Token cost** or **Context Window** space is critical.
*   Sending large contexts to LLMs (RAG, long histories).
*   Data has deep nesting or mixed types.
*   *Example:* Complex configs, API responses, arbitrary object trees.

---

## 📊 Performance Benchmarks

Real-world results using tiktoken (GPT-3.5/GPT-4 tokenizer):

### Format Comparison (45 Complex Examples)

| Format | Total Tokens | vs JSON | Best For |
|--------|-------------|---------|----------|
| **JSON (pretty)** | 16,583 | -- | Human readability |
| **JSON Compact** | 9,713 | -41% | Network transmission |
| **TOON** | 7,144 | -57% | Large tabular data |
| **TRON** | 6,431 | **-61%** | Most use cases |

### Detailed Results by Data Type

| Data Type | JSON | Compact | TOON | TRON | TRON Savings |
|-----------|------|---------|------|------|--------------|
| Simple Object | 41 | 26 | 28 | **24** | +41.5% |
| Employee Records (5) | 168 | 88 | 56 | **52** | +69.0% |
| User Records (20) | 842 | 482 | **252** | 288 | +65.8% |
| Nested Object | 58 | 29 | 38 | **27** | +53.4% |
| Mixed Structure | 81 | 40 | 33 | **28** | +65.4% |
| Products (50) | 2,116 | 1,216 | **677** | 723 | +65.8% |

### When to Use Each Format

| Use Case | Best Format | Token Savings |
|----------|-------------|---------------|
| Simple key-value objects | **TRON** | 40%+ |
| Nested configurations | **TRON** | 50%+ |
| Large tabular data (50+ rows) | **TOON** | 45%+ |
| Mixed nested + arrays | **TRON** | 65%+ |
| Streaming to LLMs | **TRON** | 60%+ |

**🟢 TRON wins 87% of benchmarks** - use it for most LLM applications!
- Small datasets (<3 items)

### Speed

All operations complete in **under 1 millisecond** for typical datasets:
- 50 records: 0.41ms
- 100 records: 0.83ms
- Decode: <1ms

---

## 🎯 Use Cases

### 1. LLM Context Optimization

3. **Install in development mode:**
```bash
pip install -e .
```

4. **Install development dependencies (optional):**
```bash
pip install -e ".[dev]"
```

This includes:
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `tiktoken` - Token counting
- `black` - Code formatting

### Verify Installation

```bash
# Run tests
pytest tests/test_toonstream.py

# Run benchmarks
python benchmarks/run_all_comparisons.py

# Try the tutorial
jupyter notebook examples/toonstream_tutorial.ipynb
```

### Project Structure

```
toonstream/
├── toonstream/           # Core library
│   ├── __init__.py       # Public API exports
│   ├── encoder.py        # TOON encoder
│   ├── decoder.py        # TOON decoder
│   ├── tron_encoder.py   # TRON encoder (NEW in v2.0.0)
│   ├── tron_decoder.py   # TRON decoder (NEW in v2.0.0)
│   ├── unified_api.py    # Unified encode/decode API
│   ├── cli.py            # CLI implementation (NEW v2.0.0)
│   ├── exceptions.py     # Exception hierarchy
│   └── pickle_utils.py   # Pickle integration
├── benchmarks/           # Performance tests
├── tests/                # Test suite (186 tests, 100% passing)
├── examples/             # Usage examples
├── data/                 # Benchmark datasets
├── results/              # Benchmark results
├── README.md             # This file
├── PICKLE_USAGE.md       # Pickle utilities guide
├── pyproject.toml        # Modern package configuration
├── .pre-commit-config.yaml # Code quality hooks
├── setup.py              # Package configuration
└── requirements.txt      # Dependencies
```

### 1. LLM Context Optimization

```python
import toonstream

# Pass structured data to LLM
context = {
    "users": [...],  # 100 user records
    "products": [...],  # 50 products
    "orders": [...]  # 200 orders
}

# Reduce prompt tokens by 40%
toon_context = toonstream.encode(context)
response = llm.complete(f"Analyze this data:\n{toon_context}")
```

### 2. Pickle Integration

Save data with TOON encoding for additional compression:

```python
from toonstream import save_toon_pickle, load_toon_pickle

# Save with TOON encoding
data = {"users": [...], "logs": [...]}
save_toon_pickle(data, 'data.toon.pkl')

# Load back
loaded = load_toon_pickle('data.toon.pkl')

# 11.4% smaller than regular pickle!
```

### 3. API Response Optimization

```python
from toonstream import encode
from flask import Flask, Response

app = Flask(__name__)

@app.route('/api/employees')
def get_employees():
    employees = db.query("SELECT * FROM employees")
    toon_data = encode(employees)
    return Response(toon_data, mimetype='text/plain')

# Clients get 55% smaller responses
```

### 4. Configuration Files

```python
import toonstream

config = {
    "database": {"host": "localhost", "port": 5432},
    "cache": {"ttl": 3600, "max_size": 1000}
}

# Save human-readable config
with open('config.toon', 'w') as f:
    f.write(toonstream.encode(config, indent=2))

# Load config
with open('config.toon') as f:
    config = toonstream.decode(f.read())
```

---

## 🛠️ API Reference

### Core Functions

#### `encode(obj, format='toon', auto_mode=False, compact=False, smart_optimize=True, indent=None, sort_keys=False)`

Convert Python object to TOON or TRON format.

**Parameters:**
- `obj` (Any): Python object (dict, list, primitive)
- `format` (str): Output format - `'toon'` (default) or `'tron'`. **New in v2.0.0!**
- `auto_mode` (bool): Auto-detect mode (tensor vs normal). (default: False)
- `compact` (bool): Minimize whitespace (default: False)
- `smart_optimize` (bool): Auto-detect best format (default: True)
- `indent` (int): Indentation spaces, None for compact (default: None)
- `sort_keys` (bool): Sort dictionary keys alphabetically (default: False)

**Returns:** `str` - TOON or TRON formatted string

**Raises:** `ToonEncodeError` - If encoding fails

```python
# Basic encoding (TOON format - default)
toon = encode(data)

# TRON format - ultra-compact (New in v2.0.0!)
tron = encode(data, format='tron')

# Auto mode - automatically detects and handles tensors
toon = encode(data, auto_mode=True)

# Compact output
toon = encode(data, compact=True)

# Sort dictionary keys
toon = encode(data, sort_keys=True)

# Always use tabular (no optimization)
toon = encode(data, smart_optimize=False)

# Pretty print with 2-space indent
toon = encode(data, indent=2)

# Combine parameters
toon = encode(data, auto_mode=True, compact=True, sort_keys=True)
```

#### `decode(data_str, format='toon', auto_mode=False, strict=True)`

Convert TOON or TRON format to Python object.

**Parameters:**
- `data_str` (str): TOON or TRON formatted string
- `format` (str): Input format - `'toon'` (default), `'tron'`, or `'auto'`. **New in v2.0.0!**
- `auto_mode` (bool): Auto-detect mode for decoding. (default: False)
- `strict` (bool): Enforce strict validation (default: True)

**Returns:** `Any` - Python object

**Raises:** `ToonDecodeError` or `TronDecodeError` - If decoding fails

```python
# Decode TOON string (default)
data = decode(toon_str)

# Decode TRON string (New in v2.0.0!)
data = decode(tron_str, format='tron')

# Auto mode - automatically detects and reconstructs tensors
data = decode(toon_str, auto_mode=True)

# Lenient mode (allows minor format issues)
data = decode(toon_str, strict=False)

# Combine parameters
data = decode(toon_str, auto_mode=True, strict=True)
```

### TRON-Specific Functions (New in v2.0.0!)

#### `tron_encode(obj)`

Encode Python object directly to TRON format.

```python
from toonstream import tron_encode

tron = tron_encode({"name": "Alice", "age": 30})
# Output: name=Alice;age=30
```

#### `tron_decode(tron_str)`

Decode TRON string directly to Python object.

```python
from toonstream import tron_decode

data = tron_decode("name=Alice;age=30")
# Output: {'name': 'Alice', 'age': 30}
```

### Pickle Functions

#### `save_toon_pickle(data, filepath, smart_optimize=True, protocol=HIGHEST_PROTOCOL)`

Save data as TOON-encoded pickle file.

**Parameters:**
- `data` (Any): Python object to save
- `filepath` (str): Output file path
- `smart_optimize` (bool): Use TOON optimization (default: True)
- `protocol` (int): Pickle protocol version (default: HIGHEST_PROTOCOL)

```python
from toonstream import save_toon_pickle

save_toon_pickle(data, 'data.toon.pkl')
```

#### `load_toon_pickle(filepath, strict=True)`

Load TOON-encoded pickle file.

**Parameters:**
- `filepath` (str): Input file path
- `strict` (bool): Enforce strict TOON validation (default: True)

**Returns:** `Any` - Loaded Python object

```python
from toonstream import load_toon_pickle

data = load_toon_pickle('data.toon.pkl')
```

### Exceptions

- `ToonError` - Base exception
- `ToonEncodeError` - Encoding failures (unsupported types, NaN, Infinity)
- `ToonDecodeError` - Decoding failures (invalid format, syntax errors)
- `ToonValidationError` - Validation failures
- `ToonPickleError` - Pickle operation failures

---

## 🧪 Development & Testing

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests (130 tests, all passing)
pytest tests/ -v

# Run specific test file
pytest tests/test_both_modes.py -v

# Run with coverage
pytest tests/ --cov=toonstream --cov-report=html

# Open coverage report
open htmlcov/index.html
```

### Running Benchmarks

```bash
# Run all benchmarks
python benchmarks/run_all_comparisons.py

# Results appear in terminal and save to results/
```

### Project Structure

```
toonstream/
├── toonstream/               # Core library
│   ├── __init__.py           # Public API exports
│   ├── encoder.py            # TOON encoder
│   ├── decoder.py            # TOON decoder
│   ├── tron_encoder.py       # TRON encoder (NEW v2.0.0)
│   ├── tron_decoder.py       # TRON decoder (NEW v2.0.0)
│   ├── tensor_utils.py       # PyTorch tensor support
│   ├── pickle_utils.py       # Pickle integration
│   ├── exceptions.py         # Exception hierarchy
│   └── unified_api.py        # Unified encode/decode with format parameter
├── benchmarks/               # Performance benchmarks
│   ├── run_all_comparisons.py
│   ├── compare_tron_formats.py  # 4-format comparison (NEW v2.0.0)
│   ├── complex_benchmarks.py    # 45 test cases (NEW v2.0.0)
│   ├── token_counters.py        # tiktoken integration (NEW v2.0.0)
│   └── config.json
├── tests/                    # Test suite (186 tests, 100% passing)
│   ├── test_toonstream.py    # Core functionality
│   ├── test_tron.py          # TRON format tests (56 tests - NEW v2.0.0)
│   └── ...
├── examples/                 # Usage examples
│   ├── basic_example.py      # Simple encoding/decoding
│   ├── tron_example.py       # TRON format usage (NEW v2.0.0)
│   ├── tron_tutorial.ipynb   # Interactive TRON tutorial (NEW v2.0.0)
│   ├── tensor_example.py     # PyTorch integration
│   └── README.md
├── .github/workflows/        # CI/CD workflows
│   ├── tests.yml             # Automated testing
│   ├── publish.yml           # Release & PyPI publishing
│   └── release-checklist.yml # Pre-release validation
├── data/                     # Benchmark datasets
├── results/                  # Benchmark results
├── README.md                 # This file
├── PICKLE_USAGE.md           # Pickle utilities guide
├── pyproject.toml            # Modern package configuration
├── setup.py                  # Package configuration
└── requirements.txt          # Dependencies
```

---

## 📖 Examples

See the `examples/` directory for complete examples:

- **basic_example.py** - Getting started guide
- **tron_example.py** - Using TRON format **(NEW in v2.0.0)**
- **tron_tutorial.ipynb** - Interactive TRON tutorial **(NEW in v2.0.0)**
- **tensor_example.py** - PyTorch tensor integration
- **README.md** - Examples documentation

Run them:

```bash
python examples/basic_example.py
python examples/tron_example.py
python examples/tensor_example.py  # Requires PyTorch
```

### What's New in v2.0.0?

**TRON Format (Token Reduced Object Notation):**
- 🚀 Ultra-compact serialization reducing token usage by **50-70%**.
- 📊 **65% savings** vs JSON for typical datasets.
- 🔄 100% loss-less round-trip conversion.

**New CLI Tool:**
- 🖥️ Process files directly: `toonstream encode data.json -o data.tron`
- 🛠️ Easy integration into data pipelines.

**Production Reliability:**
- ✅ Expanded test suite (**186 tests**, 100% coverage).
- 🔒 Full type safety with strict `mypy` compliance.
- ⚡ Sub-millisecond performance.

**Key Features:**
- `tron_encode()` / `tron_decode()` specific APIs.
- Tabular optimization for arrays (`@col1,col2|val1,val2`).
- Dot notation for nested structures (`key.subkey=value`).
- Full backward compatibility with v1.1.0.

**Previous: v1.1.0 (Auto Mode):**
- Single `auto_mode` parameter (simpler API)
- Automatic tensor mode detection
- 130 tests, all passing

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:

1. **Additional Features** - Streaming encoder, additional format options
2. **Performance** - C extension for faster encoding/decoding
3. **Documentation** - More examples, integration guides
4. **Language Bindings** - JavaScript, Go, Rust implementations

### Development Setup

```bash
# Fork and clone
git clone https://github.com/vivekpandian08/toonstream.git
cd toonstream

# Create branch
git checkout -b feature/your-feature

# Install dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Make changes and test
pytest tests/

# Submit PR
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

## 🙏 Acknowledgments

- Inspired by CSV efficiency for tabular data
- Built for the LLM era where tokens = money
- Tested with real-world production datasets

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/vivekpandian08/toonstream/issues)
- **Discussions:** [GitHub Discussions](https://github.com/vivekpandian08/toonstream/discussions)
- **Documentation:** See `PICKLE_USAGE.md` and `results/OPTIMIZATION_GUIDE.md`

---

## 🔗 Links

- **PyPI:** https://pypi.org/project/toonstream/
- **GitHub:** https://github.com/vivekpandian08/toonstream
- **Repository:** https://github.com/vivekpandian08/toonstream
- **Issues:** https://github.com/vivekpandian08/toonstream/issues

---

**Made with ❤️ for the LLM community**

*Save tokens. Save money. Build better.*
