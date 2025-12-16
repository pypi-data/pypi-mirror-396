# BasicReturns 🐍

[![PyPI Version](https://img.shields.io/pypi/v/BasicReturns.svg)](https://pypi.org/project/BasicReturns/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/BasicReturns?labelColor=black&color=orange)](https://pypi.org/project/BasicReturns/)
[![PyPI - License](https://img.shields.io/pypi/l/BasicReturns?logoColor=orange&labelColor=black&color=orange)
](https://opensource.org/licenses/MIT)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/BasicReturns?period=total&units=NONE&left_color=BLACK&right_color=ORANGE&left_text=downloads)](https://pepy.tech/projects/BasicReturns)

**Standardizes function return values across Python applications to enhance code consistency, readability, and maintainability.**

## 📦 Installation

```bash
pip install BasicReturns
```

## 🚀 Quick Start

```python
from BasicReturns import BasicReturn, DataAndMsgReturn

def divide_numbers(a: float, b: float) -> DataAndMsgReturn:
    """Safely divide two numbers with unified return structure."""
    response = DataAndMsgReturn()

    try:
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        response.data = a / b
        response.msg = "Division completed successfully"
    except Exception as e:
        response.ok = False
        response.error = e
        response.msg = "Division failed"

    return response

# Usage example
result = divide_numbers(10, 2)

if result.ok:
    print(f"{result.msg}: {result.data}")  # Division completed successfully: 5.0
else:
    print(f"{result.msg}: {result.error}")  # Division failed: Cannot divide by zero
```

## 🛠️ Practical Examples

### File Operations Utility

Here's how to implement a file utility class using unified returns:

```python
from io import TextIOWrapper
from pathlib import Path
import json
from typing import Any
from BasicReturns import BaseReturn, DataAndMsgReturn

class FilesUtils:
    @staticmethod
    def file_exists(filename: str) -> bool:
        return Path(filename).is_file()

    @staticmethod
    def read_file(filename: str) -> DataAndMsgReturn:
        """Read file content with unified return structure."""
        response = DataAndMsgReturn()

        try:
            if not FilesUtils.file_exists(filename):
                response.ok = False
                response.error = FileNotFoundError(f"File '{filename}' not found")
                response.msg = "File does not exist"
                return response

            with open(filename, 'r', encoding='utf-8') as file:
                response.data = file.read()
                response.msg = f"Successfully read file: {filename}"
        except Exception as e:
            response.ok = False
            response.error = e
            response.msg = f"Error reading file: {filename}"

        return response

    @staticmethod
    def read_json(filename: str) -> DataAndMsgReturn:
        """Read and parse JSON file with unified error handling."""
        response = DataAndMsgReturn()
        file_result = FilesUtils.read_file(filename)

        if not file_result.ok:
            # Propagate the error from read_file
            response.ok = file_result.ok
            response.error = file_result.error
            response.msg = file_result.msg
            return response

        try:
            response.data = json.loads(file_result.data)
            response.msg = f"Successfully parsed JSON from: {filename}"
        except json.JSONDecodeError as e:
            response.ok = False
            response.error = e
            response.msg = f"Invalid JSON format in file: {filename}"

        return response

    @staticmethod
    def write_json(filename: str, data: dict) -> BaseReturn:
        """Write dictionary to JSON file with atomic operation handling."""
        response = BaseReturn()

        try:
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, sort_keys=True, ensure_ascii=False)
            response.msg = f"Successfully wrote JSON to: {filename}"
        except Exception as e:
            response.ok = False
            response.error = e
            response.msg = f"Failed to write JSON file: {filename}"

        return response
```

### Usage in Application

```python
# Read configuration file
config_result = FilesUtils.read_json("config.json")

if config_result.ok:
    config = config_result.data
    print("Configuration loaded:", config)
else:
    print("Error loading config:", config_result.error)
    # Fallback to default configuration
    config = {"default": "settings"}

# Save user data
user_data = {"name": "John Doe", "email": "john@example.com"}
save_result = FilesUtils.write_json("users/john.json", user_data)

if save_result.ok:
    print("User data saved successfully")
else:
    print("Failed to save user data:", save_result.error)
    # Handle the error appropriately
```

## 🌟 Best Practices

### 1. Consistent Error Handling

```python
def process_data(data: Any) -> DataAndMsgReturn:
    response = DataAndMsgReturn()

    if not data:
        response.ok = False
        response.error = ValueError("Empty data provided")
        response.msg = "Validation failed"
        return response

    # Process data...
    response.data = processed_data
    response.msg = "Data processed successfully"
    return response
```

### 2. Chaining Operations

```python
def load_and_validate_config() -> DataAndMsgReturn:
    config_result = FilesUtils.read_json("config.json")

    if not config_result.ok:
        return config_result  # Return the error immediately

    validation_result = validate_config(config_result.data)

    if not validation_result.ok:
        return DataAndMsgReturn(
            ok=False,
            error=validation_result.error,
            msg=f"Configuration validation failed: {validation_result.msg}"
        )

    return DataAndMsgReturn(
        data=config_result.data,
        msg="Configuration loaded and validated successfully"
    )
```

### 3. API Integration

```python
import requests
from BasicReturns import DataAndMsgReturn

def fetch_api_data(url: str) -> DataAndMsgReturn:
    response = DataAndMsgReturn()

    try:
        api_response = requests.get(url, timeout=10)
        api_response.raise_for_status()

        response.data = api_response.json()
        response.msg = f"Successfully fetched data from {url}"
    except requests.exceptions.RequestException as e:
        response.ok = False
        response.error = e
        response.msg = f"API request failed: {url}"

    return response
```

## 📊 Benefits

✅ **Consistent Error Handling** - No more guessing return types or error formats  
✅ **Improved Readability** - Clear success/failure states with contextual messages  
✅ **Better Debugging** - Structured error information with stack traces when needed  
✅ **Type Safety** - Full MyPy compatibility with proper type annotations  
✅ **Seamless Integration** - Works with any Python framework or application  
✅ **Serialization Ready** - Built-in `to_dict()` method for JSON/API responses

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

1. Fork the repository
2. Create your feature branch (`git switch -c feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a pull request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

**Made with ❤️ for Python developers who value clean, consistent code**
