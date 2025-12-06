# 🎨 ToonStream

**Token-Oriented Object Notation (TOON) - Reduce LLM token usage by up to 55% with lossless data serialization**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-1.1.0-brightgreen.svg)](https://github.com/vivekpandian08/toonstream/releases/tag/v1.1.0)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-130%2F130-brightgreen.svg)](tests/)

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

TOON format eliminates redundancy:

```
employees[3]{id,name,dept,salary}:
1,Alice,Engineering,95000
2,Bob,Sales,75000
3,Carol,Engineering,105000
```
**Cost:** 38 tokens (**-52.5%** reduction)

### Why ToonStream?

✅ **Save Money** - Reduce API costs by up to 55% on structured data  
✅ **100% Lossless** - Perfect round-trip conversion, no data loss  
✅ **Zero Dependencies** - Pure Python, no external packages required  
✅ **Fast** - Sub-millisecond encoding/decoding  
✅ **Smart** - Automatic optimization, only improves when beneficial  
✅ **Simple API** - Two functions: `encode()` and `decode()`  

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

---

## ⚡ Quick Start

### Basic Usage

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

# Encode to TOON format (normal mode - default)
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

## 📊 Performance Benchmarks

Real-world results from production datasets:

| Data Type | JSON Tokens | TOON Tokens | Reduction | Use Case |
|-----------|-------------|-------------|-----------|----------|
| **Employee Records** (50) | 3,914 | 1,733 | **-55.7%** | HR systems, payroll |
| **GitHub Repos** (100) | 14,102 | 8,712 | **-38.2%** | API responses |
| **Order History** (10) | 2,926 | 2,915 | **-0.4%** | E-commerce |
| **Config Files** (20) | 7,393 | 7,393 | **0.0%** | Microservices |

### When to Use TOON

**🟢 Excellent Results (30-55% savings):**
- Arrays of similar objects (users, products, logs)
- Tabular data (CSV-like structures)
- Database query results
- Time-series data

**🟡 Good Results (10-30% savings):**
- Mixed nested structures
- API responses with arrays
- Semi-structured documents

**🔴 Neutral Results (±5%):**
- Deeply nested JSON (5+ levels)
- Unique object structures
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
│   ├── encoder.py        # TOON encoder (485 lines)
│   ├── decoder.py        # TOON decoder (533 lines)
│   ├── exceptions.py     # Exception hierarchy (60 lines)
│   └── pickle_utils.py   # Pickle integration (177 lines)
├── benchmarks/           # Performance tests
├── tests/                # Test suite (51 tests, 100% passing)
├── examples/             # Usage examples
├── data/                 # Benchmark datasets
├── results/              # Benchmark results
├── README.md             # This file
├── PICKLE_USAGE.md       # Pickle utilities guide
├── pyproject.toml        # Modern package configuration
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

#### `encode(obj, auto_mode=False, compact=False, smart_optimize=True, indent=None, sort_keys=False)`

Convert Python object to TOON format.

**Parameters:**
- `obj` (Any): Python object (dict, list, primitive)
- `auto_mode` (bool): Auto-detect mode (tensor vs normal). **New in v1.1.0!** (default: False)
- `compact` (bool): Minimize whitespace (default: False)
- `smart_optimize` (bool): Auto-detect best format (default: True)
- `indent` (int): Indentation spaces, None for compact (default: None)
- `sort_keys` (bool): Sort dictionary keys alphabetically (default: False)

**Returns:** `str` - TOON formatted string

**Raises:** `ToonEncodeError` - If encoding fails

```python
# Basic encoding (normal mode)
toon = encode(data)

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

#### `decode(toon_str, auto_mode=False, strict=True)`

Convert TOON format to Python object.

**Parameters:**
- `toon_str` (str): TOON formatted string
- `auto_mode` (bool): Auto-detect mode for decoding. **New in v1.1.0!** (default: False)
- `strict` (bool): Enforce strict validation (default: True)

**Returns:** `Any` - Python object

**Raises:** `ToonDecodeError` - If decoding fails

```python
# Decode TOON string (normal mode)
data = decode(toon_str)

# Auto mode - automatically detects and reconstructs tensors
data = decode(toon_str, auto_mode=True)

# Lenient mode (allows minor format issues)
data = decode(toon_str, strict=False)

# Combine parameters
data = decode(toon_str, auto_mode=True, strict=True)
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
│   ├── tensor_utils.py       # PyTorch tensor support
│   ├── pickle_utils.py       # Pickle integration
│   ├── exceptions.py         # Exception hierarchy
│   └── unified_api.py        # Unified encode/decode with auto_mode (NEW v1.1.0)
├── benchmarks/               # Performance benchmarks
│   ├── run_all_comparisons.py
│   └── config.json
├── tests/                    # Test suite (130 tests, 100% passing)
│   ├── test_toonstream.py    # Core functionality (51 tests)
│   ├── test_auto_mode_api.py # Auto mode parameter (19 tests)
│   ├── test_both_modes.py    # Comparison tests (41 tests) - NEW v1.1.0
│   └── test_tensor_utils.py  # Tensor support (19 tests)
├── examples/                 # Usage examples
│   ├── basic_example.py      # Simple encoding/decoding
│   ├── auto_mode_example.py  # Auto mode usage (NEW v1.1.0)
│   ├── tensor_example.py     # PyTorch integration
│   └── README.md
├── .github/workflows/        # CI/CD workflows (NEW v1.1.0)
│   ├── tests.yml             # Automated testing
│   ├── publish.yml           # Release & PyPI publishing
│   └── release-checklist.yml # Pre-release validation
├── data/                     # Benchmark datasets
├── results/                  # Benchmark results
├── README.md                 # This file
├── RELEASE_NOTES_v1.1.0.md   # What's new in v1.1.0 (NEW)
├── PICKLE_USAGE.md           # Pickle utilities guide
├── pyproject.toml            # Modern package configuration
├── setup.py                  # Package configuration
└── requirements.txt          # Dependencies
```

---

## 📖 Examples

See the `examples/` directory for complete examples:

- **basic_example.py** - Getting started guide
- **auto_mode_example.py** - Using auto_mode parameter **(NEW in v1.1.0)**
- **tensor_example.py** - PyTorch tensor integration
- **README.md** - Examples documentation

Run them:

```bash
python examples/basic_example.py
python examples/auto_mode_example.py
python examples/tensor_example.py  # Requires PyTorch
```

### What's New in v1.1.0?

**Key improvements:**
- ✅ Single `auto_mode` parameter (simpler API)
- ✅ 41 new comprehensive tests
- ✅ 130 total tests, all passing
- ✅ Automatic tensor mode detection
- ✅ Enhanced CI/CD workflows
- ✅ Full backward compatibility

See [RELEASE_NOTES_v1.1.0.md](RELEASE_NOTES_v1.1.0.md) for full details.

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:

1. **Additional Features** - CLI tool, streaming encoder, additional format options
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
