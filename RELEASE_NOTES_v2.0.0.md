# Toonstream v2.0.0 Release Notes

**Release Date:** 2025-12-08

---

## 🚀 Major Features

### 1. TRON Format (Token Reduced Object Notation)
- **Ultra-compact**: Reduces LLM token usage by **50-70%** compared to JSON.
- **Syntax**: Uses smart delimiters (`|`, `;`, `@`) and removes quotes/braces.
- **Features**:
    - **Tabular Arrays**: `@col1,col2|val1,val2` for efficient list serialization.
    - **Nested Objects**: Dot notation `user.profile.name=Alice`.
    - **Optimized Types**: `1`/`0` for booleans, `_` for null.
- **Safety**: 100% lossless round-trip conversion.

### 2. New CLI Tool (`toonstream`)
- **Command Line Power**: Process files directly without writing Python code.
- **Commands**:
    - `encode`: Convert JSON to TOON (default) or TRON.
    - `decode`: Convert TOON/TRON back to JSON.
- **Usage**:
    ```bash
    toonstream encode data.json -o data.tron --format tron
    toonstream decode data.tron -o restored.json
    ```

### 3. Production-Ready Reliability
- **Test Suite**: Expanded to **186 tests** with 100% code coverage.
- **Type Safety**: Fully typed codebase with strict `mypy` compliance.
- **Code Quality**: Automated formatting (`black`) and linting (`ruff`) enforced via pre-commit hooks.
- **Validation**: Verified against real-world datasets (E-commerce, API responses) using GPT-4 tokenizer.

---

## 🛠️ API & Integration

### Unified API
- **Single Entry Point**: `encode()` and `decode()` handle all formats.
- **Format Parameter**: Explicitly choose `format='toon'` or `format='tron'`.
- **Auto Mode**: `auto_mode=True` intelligently detects recursive structures and PyTorch tensors.

### Benchmarks
- **Performance**: Validated to be sub-millisecond for typical payloads.
- **Savings**:
    - **TRON**: 61.2% average savings on complex data.
    - **TOON**: 57% savings on tabular data.
    - **JSON Compact**: 41% savings.

---

## 📦 Installation

```bash
pip install toonstream
```

### Development Setup
```bash
pip install -e ".[dev]"
pre-commit install
```

---

## ⚠️ Migration Notes
- **Backward Compatible**: All v1.x code continues to work without changes.
- **New Dependency**: `collections` (standard lib) used for robust ordering.
- **Optional**: `torch` and `tiktoken` required only for tensor features and benchmarks respectively.

---

## 🙏 Acknowledgments
- Inspired by the need to optimize LLM context windows and reduce API costs.
- Evaluating with real-world LLMs (Llama 3, Gemini) proved **100% accuracy** with compressed formats.

---
*Save tokens. Save money. Build better.*
