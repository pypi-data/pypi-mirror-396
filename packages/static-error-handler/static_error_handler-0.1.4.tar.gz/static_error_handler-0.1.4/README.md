# static_error_handler

A minimal Python adaptation of Rust's `Result` type. Provides `Ok` and `Err`
classes with helper methods for error handling.

## Installation

Once published on PyPI you can install the library with:

```bash
pip install static_error_handler
```

## Usage

```python
from static_error_handler import Ok, Err, Result

def divide(a: int, b: int) -> Result[int, str]:
    if b == 0:
        return Err("division by zero")
    return Ok(a // b)

result = divide(10, 2)
print(result.unwrap())  # 5
```
