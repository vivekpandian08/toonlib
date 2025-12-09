# Tests

Test suite for toonstream library.

## Running Tests

### Run all tests
```bash
pytest tests/
```


### Run specific test file
```bash
pytest tests/test_toonstream.py
pytest tests/test_auto_mode_api.py
pytest tests/test_both_modes.py
pytest tests/test_tensor_utils.py
pytest tests/test_tron.py
```

### Run with coverage
```bash
pytest tests/ --cov=toonstream --cov-report=html
```


## Test Files

- `test_toonstream.py` - Comprehensive unit tests for TOON format
- `test_auto_mode_api.py` - Tests for auto_mode parameter
- `test_both_modes.py` - Tests for both normal and auto_mode
- `test_tensor_utils.py` - PyTorch tensor support tests
- `test_tron.py` - Comprehensive unit tests for TRON format

## Test Coverage

Tests cover:
- ✓ All Python data types (str, int, float, bool, None, list, dict)
- ✓ Nested structures
- ✓ Edge cases (empty values, special characters)
- ✓ Smart optimization (tabular arrays)
- ✓ Round-trip encoding/decoding
- ✓ Error handling and exceptions
- ✓ Unicode and special characters

## Adding Tests

When adding new features:
1. Add tests to appropriate test file
2. Test both encoding and decoding
3. Test edge cases
4. Ensure round-trip correctness
5. Run full test suite before committing


## Test Results

All tests should pass:
```
===== test session starts =====
collected 186 items

tests/test_auto_mode_api.py ...................
tests/test_both_modes.py .........................................
tests/test_tensor_utils.py ...................
tests/test_toonstream.py ...............................................
....
tests/test_tron.py .....................................................
...

===== 186 passed in X.XXs =====
```
