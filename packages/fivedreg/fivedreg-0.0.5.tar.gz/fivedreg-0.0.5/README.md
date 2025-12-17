# Dummy Package Project

This is an example Python package structure with a simple dummy module and class.

## Project Structure

```
dummy_package_project/
├── dummy_package/
│   ├── __init__.py
│   └── dummy_module/
│       ├── __init__.py
│       └── dummy_class.py
├── README.md
```

## Installation

Clone this repository, navigate to the `dummy_package_project` folder and you can install the package locally:

```bash
pip install .
```

## Usage

Example usage of the `DummyClass`:

```python
from dummy_package.dummy_module import DummyClass

obj = DummyClass()
print(obj.__name__)  # Output: DummyClass
print(obj.age)       # Output: Not very old
print(obj.sum(2, 3)) # Output: 5
```

## Package Contents

- **dummy_package.dummy_module.dummy_class.DummyClass**
  A dummy class with a `sum(a, b)` method and example attributes.

## Development

To install development dependencies:

```bash
pip install -r requirements.txt
```

## License

This project is provided for demonstration purposes.
