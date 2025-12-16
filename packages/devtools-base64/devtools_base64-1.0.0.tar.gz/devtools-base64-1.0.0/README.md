# Base64 Encoder/Decoder

Base64 encoder/decoder with UTF-8 support.

## Online Tool

Use this tool online at **[DevTools.at](https://devtools.at/tools/base64)** - Free, fast, and no registration required!

## Installation

```bash
pip install devtools-base64
```

## Usage

```python
from devtools_base64 import encode, decode

# Encode
encoded = encode("Hello, World!")
print(encoded)  # SGVsbG8sIFdvcmxkIQ==

# Decode
decoded = decode("SGVsbG8sIFdvcmxkIQ==")
print(decoded)  # Hello, World!
```

## License

MIT License

---

Made with love by [DevTools.at](https://devtools.at)
