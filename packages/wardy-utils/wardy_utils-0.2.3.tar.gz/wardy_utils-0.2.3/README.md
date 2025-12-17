# Wardy Utils

**Wardy Utils** is a collection of general-purpose utilities designed to simplify and enhance your Python scripting experience. This library provides reusable components that can be integrated into your projects to save time and effort.

## Features

### HTTP Utilities

- **`http`**: A high-level HTTP client built on top of `httpx` and `hishel`, setting some caching and timeout comment settings.

## Installation

To install Wardy Utils, use pip:

```bash
pip install wardy-utils
```

## Usage

### HTTP Client Example

```python
from wardy_utils.web import CachedClient

client = CachedClient()
response = client.get("https://example.com")
print(response.text)
```

## Requirements

- Python 3.13.3 or higher

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve the library.

## License

This project is licensed under the MIT License.

## Author

Created by **Wardy**  
Email: [wardy3+gitlab@gmail.com](mailto:wardy3+gitlab@gmail.com)
