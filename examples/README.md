# Examples

Practical examples demonstrating ToonStream functionality.

## Files

- `basic_example.py` - Simple encoding/decoding with various data types
- `auto_mode_example.py` - Using the `auto_mode` parameter for automatic mode selection
- `tensor_example.py` - PyTorch tensor serialization (requires PyTorch)

## Running Examples

```bash
# Basic usage
python examples/basic_example.py

# Auto mode (intelligent tensor detection)
python examples/auto_mode_example.py

# Tensor support (requires PyTorch)
python examples/tensor_example.py
```

## Quick Example

```python
import toonstream

# Normal encoding
data = {"name": "Alice", "scores": [95, 87, 92]}
toon_str = toonstream.encode(data)
decoded = toonstream.decode(toon_str)

# Auto mode (detects tensors automatically)
encoded_auto = toonstream.encode(data, auto_mode=True)
decoded_auto = toonstream.decode(encoded_auto, auto_mode=True)
```

### Decoding
```python
data = toonstream.decode(toon_str)
```

## Use Cases

- **API responses** - Reduce payload size
- **Data storage** - Compress JSON files
- **Log files** - Structured logging with less space
- **Configuration** - Readable config files
- **Data exchange** - Efficient data transfer
